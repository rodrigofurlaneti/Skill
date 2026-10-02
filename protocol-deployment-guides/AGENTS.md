# AGENTS.md — Protocolo e Guias de Deploy

Este documento estabelece as regras arquiteturais, convenções de infraestrutura e procedimentos de implantação do sistema. Qualquer agente de IA, desenvolvedor ou assistente automatizado alterando scripts de CI/CD, Nginx ou systemd deve seguir rigorosamente estas diretrizes.

---

## 1. Princípios Fundamentais

1. **Deploy Atômico (Zero Downtime):** O código de produção nunca deve ser sobrescrito diretamente no diretório final. O deploy utiliza links simbólicos atômicos substituídos via `mv -Tf`.
2. **Imutabilidade de Releases:** Cada release gerada reside em um diretório próprio e isolado (`/opt/$APP/releases/$RELEASE_ID`). Releases antigas são imutáveis.
3. **Isolamento e Segurança (FHS):** Segredos e configurações de sistema vivem exclusivamente em `/etc/$APP/`. Nunca aplique permissões recursivas como `chown -R` ou `chmod -R` em pastas do sistema (`/etc`, `/usr`, `/var`, etc.).
4. **Resiliência e Rollback Automático:** Falhas em testes de saúde (*health checks*) durante a publicação devem disparar rollback automático para o link simbólico da versão anterior.

---

## 2. Padrão Universal de Arquivos e Diretórios

Cada aplicação `$APP` (ex: `checkpay`, `syncbar`, `checkvisit`, `dingfood`) deve seguir este layout de caminhos no Linux:

| Caminho | Finalidade | Permissões / Proprietário |
| :--- | :--- | :--- |
| `/opt/$APP/` | Diretório raiz da aplicação. | `root:root` (`755`) |
| `/opt/$APP/releases/$RELEASE_ID/` | Diretório imutável da versão compilada (API e Frontend). | `root:root` (`u=rwX,go=rX`) |
| `/opt/$APP/current` | Link simbólico apontando para a release ativa (`releases/$RELEASE_ID`). | `root:root` |
| `/var/www/$APP-frontend` | Link simbólico apontando para `/opt/$APP/current/frontend`. | `root:root` |
| `/etc/$APP/$APP.env` | Variáveis de ambiente e segredos da aplicação. | `root:root` (`600` ou `644`) |
| `/run/lock/$APP-deploy.lock` | Arquivo de trava para impedir deploys concorrentes. | `root:root` |

---

## 3. Padrão do Serviço Systemd (`/etc/systemd/system/$APP-api.service`)

* **Nome do Serviço:** `$APP-api.service`
* **Usuário:** Executado por usuário não-root ou de sistema dedicado.
* **Porta Local:** Mapeada exclusivamente na interface de loopback (`127.0.0.1`).
* **Variáveis de Ambiente:** Carregadas a partir do arquivo `/etc/$APP/$APP.env`.

### Estrutura Base do Serviço:
```ini
[Unit]
Description=%N API Service
After=network.target

[Service]
Type=notify
WorkingDirectory=/opt/%N/current/api
ExecStart=/usr/bin/dotnet /opt/%N/current/api/App.WebApi.dll --urls=http://127.0.0.1:511X
EnvironmentFile=/etc/%N/%N.env
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 4. Contrato do Script de Deploy (`deploy/deploy.sh`)

O script de deploy deve obrigatoriamente seguir este fluxo de execução:

1. **Validação e Trava (Pre-flight & Lock):**
   * Verificar execução com privilégios de `root`/`sudo`.
   * Obter trava exclusiva via `flock` no arquivo `/run/lock/$APP-deploy.lock`.
   * Garantir que `/etc/$APP/$APP.env` existe e está devidamente preenchido.
2. **Extração Isolada:**
   * Descompactar o pacote em `/opt/$APP/releases/$RELEASE_ID`.
   * Validar a integridade dos artefatos (ex: DLL principal e `index.html`).
3. **Chaveamento Atômico (Atomic Symlink Switch):**
   * Criar link temporário: `ln -sfn "$release" "$base/current.next"`.
   * Substituir o link atual atomicamente: `mv -Tf "$base/current.next" "$base/current"`.
4. **Validação de Health Check e Rollback Automático:**
   * Reiniciar o serviço: `systemctl restart $APP-api`.
   * Testar a rota `/health` com `curl`.
   * Em caso de falha, restaurar o link `$base/current` para a versão anterior (`$previous`), reiniciar a API e retornar código de erro.
5. **Retenção (Housekeeping):**
   * Manter apenas as 5 versões mais recentes em `/opt/$APP/releases/`.

---

## 5. Regras Estritas de Qualidade de Código (Linting & CI)

* **Codificação:** Todos os scripts `.sh` devem ser salvos estritamente em **UTF-8 puro** (sem UTF-8 BOM).
* **Compatibilidade com ShellCheck:**
  * O código deve passar sem erros nas pipelines com `shellcheck`.
  * Diretivas explicítas de supressão de avisos devem ser adicionadas apenas quando justificadas:
    ```bash
    # shellcheck source=/dev/null
    source /etc/$APP/$APP.env

    # shellcheck disable=SC2012
    ls -dt "$base"/releases/* 2>/dev/null | tail -n +$((keep + 1)) | xargs -r -d '\n' rm -rf -- || true
    ```

---

## 6. Proibições Expressas para Agentes (Guardrails de Segurança)

* ❌ **NUNCA** execute comandos de alteração de permissão (`chmod`/`chown`) de forma recursiva (`-R`) no diretório `/etc`.
* ❌ **NUNCA** altere diretamente arquivos dentro de `/opt/$APP/current` ou `/opt/$APP/releases/`.
* ❌ **NUNCA** adicione chaves de API, senhas ou segredos no código-fonte ou scripts versionados.
* ❌ **NUNCA** altere scripts de deploy sem incluir tratamento de erro (`set -Eeuo pipefail`) e mecanismos de rollback.
