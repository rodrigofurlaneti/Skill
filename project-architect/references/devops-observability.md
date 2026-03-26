# DevOps & Observability Guidelines — SRE Agent

Este guia estabelece os padrões para infraestrutura, implantação contínua e monitoramento de aplicações de missão crítica.

## 1. Docker & Containerização (Build de Elite)
- **Multi-stage Build**: Sempre use builds em estágios para garantir imagens finais leves e seguras.
- **Alpine Images**: Utilize imagens base baseadas em `Alpine Linux` para reduzir a superfície de ataque.
- **Non-Root User**: Jamais execute a aplicação como `root` dentro do container.
- **ReadOnly Filesystem**: Sempre que possível, configure o container para rodar com o sistema de arquivos apenas de leitura.

## 2. CI/CD (GitHub Actions)
- **Build & Test**: Todo Push/PR deve disparar um workflow de restauração, build e execução de testes (Unitários e de Arquitetura).
- **Quality Gate**: O merge só é permitido se 100% dos testes passarem e o linting (dotnet format) estiver correto.
- **Artifacts**: Gere artefatos de build apenas em branches protegidas (`main` ou `develop`).

## 3. Observabilidade (O Cérebro da Operação)
- **Logs Estruturados**: Use `Serilog` com saída em JSON. Isso permite que ferramentas como ElasticSearch ou CloudWatch indexem propriedades (ex: `OrderId`, `UserId`) em vez de apenas texto.
- **Health Checks**: Implemente o middleware de Health Checks do .NET.
  - `/health/live`: Liveness probe (o app está vivo?).
  - `/health/ready`: Readiness probe (o app consegue falar com o Banco e Redis?).
- **OpenTelemetry**: Prepare a aplicação para expor métricas e traces distribuídos para ferramentas como Jaeger ou Prometheus.

## 4. Resiliência & Estabilidade
- **Polly Policies**: Chamadas externas (APIs de terceiros ou Banco de Dados) devem implementar políticas de:
  - **Retry**: Retentativa com espera exponencial.
  - **Circuit Breaker**: Interromper chamadas se o serviço externo estiver fora do ar para evitar cascata de erros.
- **Resource Limits**: Sempre defina limites de CPU e Memória no seu arquivo de orquestração (Kubernetes/Docker Compose).

## 5. Security DevOps (DevSecOps)
- **Secrets Management**: Nunca suba `appsettings.json` com senhas. Use variáveis de ambiente, Azure Key Vault ou GitHub Secrets.
- **Dependency Scan**: Use ferramentas como `dotnet list package --vulnerable` no pipeline para detectar bibliotecas com falhas de segurança conhecidas.