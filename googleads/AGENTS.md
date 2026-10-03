# AGENTS.md — PropertyRegistration

## Escopo e leitura obrigatória

Este documento consolida os ajustes da integração Google Ads e da experiência de campanhas realizados em **03/10/2026**. Descreve o estado implementado no repositório; não comprova publicação em produção nem funcionamento contra uma conta real.

- Antes de alterar backend, leia [backend/AGENTS.md](backend/AGENTS.md).
- Antes de alterar frontend, leia [frontend/AGENTS.md](frontend/AGENTS.md).
- Para operação e publicação, consulte [deploy/README.md](deploy/README.md).
- Preserve alterações existentes do usuário. Não faça commit, push ou implantação sem autorização no pedido.
- Em divergências entre este documento e o código, investigue e atualize a documentação. Não implemente comportamento apenas para corresponder a um registro desatualizado.
- As regras específicas abaixo aplicam-se ao módulo de campanhas, não a funcionalidades sem relação com ele.

## Organização do painel administrativo

Rota: `/backoffice/campanhas`. A sessão é de administrador, separada da sessão do cliente.

| Aba | Conteúdo | Parâmetro `aba` |
| --- | --- | --- |
| Google Ads | Conta, credencial JSON, salvar e testar conexão | `google` |
| Conversões do site | Configuração automática, gestão das ações e tags manuais | `conversoes` |
| Criar campanha | Formulário, validação, revisão e criação pausada; gerador de links | `criar` |
| Gerenciar campanhas | Consulta e alteração de recursos existentes no Google | `gerenciar` |
| Resultados | Relatório interno de cadastros, análises, assinantes e receita | `resultados` |

- A aba padrão é Google Ads; valores desconhecidos também usam essa aba.
- Mantenha formulários montados ao alternar abas para preservar os dados digitados durante a navegação. Isso não significa persistência do rascunho após recarregar a página.
- Preserve os atributos `tablist`, `tab`, `tabpanel`, `aria-selected`, os vínculos entre abas e painéis e a navegação por setas, Home e End.
- Preserve a seleção na URL e o funcionamento de voltar/avançar do navegador.
- Tags manuais ficam em uma seção expansível de Conversões. Links para outros canais ficam em uma seção expansível de Criar campanha.
- Resultados internos por UTM não são uma lista de campanhas ativas, nem um relatório de impressões/cliques sincronizado com o Google Ads.

## Conexão e proteção das credenciais

- Configuração com ID Google Ads de 10 dígitos, ID opcional da conta administradora e JSON de conta de serviço de até 16 KB.
- O servidor testa o acesso antes de substituir uma configuração funcional. O fluxo de configuração exige conta em BRL.
- Nunca retornar a chave privada ao frontend nem gravá-la em logs, storage do navegador, documentação ou testes.
- A credencial é protegida com ASP.NET Data Protection. Em produção, `GoogleAds:DiretorioChaves` precisa apontar para armazenamento persistente; perder essas chaves impede a leitura das credenciais salvas.
- Endpoints de autenticação e API são fixos; não seguir `token_uri` fornecido no upload.
- Ao trocar a conta, as conversões Google nas tags precisam ser desvinculadas para evitar atribuição à conta anterior.
- A interface deve manter os três inputs com a mesma altura e largura. Use estilos limitados a `.ads-connection-grid`, com rótulos, inputs e dicas em linhas alinhadas; preserve o empilhamento no celular e os temas claro/escuro.

## Criação de campanha de pesquisa

- Modelo inicial: Brasil, presença na região, português, Pesquisa Google, CPC manual, palavras em correspondência de frase, orçamento diário médio de R$ 20 e CPC máximo de R$ 2.
- Orçamento diário médio não é um teto rígido de cobrança diária. Preserve a explicação ao administrador.
- O formulário começa com **9 títulos, 4 descrições e 10 palavras negativas**, todos editáveis.
- Os textos exatos ficam em `frontend/src/features/backoffice/GoogleAdsPainel.tsx`; mantenha uma única fonte para as sugestões.
- As sugestões combinam análise/leitura de matrículas, registros, averbações, ônus, envio de PDF, parecer online e planos. Não prometa segurança jurídica garantida nem funcionalidades que o produto não tenha.
- Negativas iniciais tratam de matrículas escolares/universitárias, creche, Enem, curso de corretor, empregos e concurso de cartório. Não acrescente negativas indiscriminadamente: podem excluir buscas relevantes. Não excluir automaticamente termos como grátis, pois a ferramenta pode oferecer análise gratuita.
- Mais conteúdo não garante mais procura. Os dois termos positivos iniciais podem ter baixo volume; não apresentar sugestões como resultado de pesquisa de volume no Planejador.
- Mantenha contadores de linhas e do tamanho da maior linha, campos ampliados e instrução de uma opção por linha.
- Títulos: 3 a 15, até 30 caracteres cada. Descrições: 2 a 4, até 90 caracteres cada. Não somar sugestões acima desses limites.
- Palavras e negativas: até 30 por lista e 80 caracteres por item; backend também limita a 10 palavras por item e recusa aspas/colchetes. Linhas repetidas são rejeitadas.
- Validar/revisar não cria recursos. Uma edição após a revisão exige nova validação.
- A criação sempre envia a campanha como `PAUSED`, com orçamento, grupo, anúncio responsivo e critérios na mesma mutação, `partialFailure=false`.
- Preserve a reserva durável por `OperacaoId`, conta e hash do pedido. Em timeout ou resultado incerto, não repetir automaticamente a criação com outro identificador.
- `sessionStorage` mantém somente o identificador da operação pendente, não a credencial. O registro no servidor protege contra duplicidade entre instâncias.
- O backend acrescenta UTM no `finalUrlSuffix` (origem, mídia, campanha, anúncio e palavra). Não é necessário gerar um link manual para esse fluxo.
- O gerador manual continua útil para outros canais e anúncios criados fora da integração.

## Gestão de recursos existentes

- Consulta campanhas de pesquisa da conta salva, inclusive as criadas fora da ferramenta, e percorre as páginas da resposta do Google.
- Campanha: editar nome e orçamento não compartilhado; ativar, pausar e remover.
- Grupo: editar nome e CPC quando a estratégia é `MANUAL_CPC`; ativar, pausar e remover.
- Anúncio responsivo: editar destino, títulos e descrições; ativar, pausar e remover. Preserve fixações dos títulos mantidos, sem reenviar metadados somente de leitura.
- Palavras: adicionar em frase, exata ou ampla; pausar, ativar e remover. Texto/correspondência são trocados adicionando a nova palavra e removendo a antiga.
- Negativas de campanha: adicionar e remover.
- Renomear campanha preserva o sufixo UTM original; não modificar silenciosamente o histórico de atribuição.
- Orçamento compartilhado não deve ser editado por esse painel, pois afeta outras campanhas.
- A conta enviada deve coincidir com a configuração salva; valide o formato do recurso e resolva-o no Google antes de modificar. Não confiar em recursos arbitrários enviados pelo navegador.
- Alterações de gestão fazem `validateOnly` antes do envio e usam `partialFailure=false`. Máscaras de atualização REST usam lowerCamelCase; consultas GAQL usam snake_case.
- Escritas não têm retry automático. Após erro ou resultado incerto, exigir atualização e conferência do estado antes de repetir.
- Confirmar alterações, remoções e ativações. Na ativação, explicar os possíveis gastos e, para campanha, mostrar o orçamento diário médio.
- Remoção não apaga o histórico; não oferecer reativação de campanhas, anúncios e palavras removidos.
- Exibir os diagnósticos retornados, traduzindo os principais avisos. Não confundir status ENABLED com anúncio aprovado, qualificado ou efetivamente em veiculação.

## Conversões e medição do site

- Configuração automática cria ou reutiliza `PropertyRegistration - Cadastro` (SIGNUP, secundária) e `PropertyRegistration - Assinatura paga` (SUBSCRIBE_PAID, principal), do tipo WEBPAGE.
- Salva os códigos de conversão nas tags do site e preserva Analytics e Meta. O frontend deriva o ID AW das conversões; não exige redigitar esse ID no campo Google tag.
- A gestão permite editar principal/secundária, contagem, janela de clique e valor padrão das ações WEBPAGE. Preserva nome, categoria, moeda e comportamento de valor.
- Remoção de uma conversão ainda vinculada às tags do site é bloqueada. O administrador deve desvincular o código primeiro.
- Se a ação existente divergir das categorias/prioridades exigidas pelo assistente automático, explicar o conflito; não sobrescrever sua configuração silenciosamente.
- Carregar rastreamento somente após consentimento de cookies. O backoffice não deve ser rastreado.
- A medição atual é pelo navegador. Para assinatura, o cliente precisa estar na tela quando o pagamento for confirmado. Envio de conversões pelo servidor/Data Manager não está implementado.
- Status cadastral ou criação bem-sucedida da ação não comprovam recebimento de eventos. A verificação real depende de Tag Assistant e eventos do site.
- Não apresentar conversões otimizadas como configuradas: esse recurso não está implementado.

## Arquivos e contratos principais

| Área | Arquivos |
| --- | --- |
| Página, abas e relatórios internos | `frontend/src/features/backoffice/MarketingPage.tsx` |
| Conexão, assistente e sugestões | `frontend/src/features/backoffice/GoogleAdsPainel.tsx` |
| Gestão de recursos | `frontend/src/features/backoffice/GoogleAdsGestao.tsx` |
| Contratos, hooks e validação frontend | `googleAdsApi.ts`, `googleAdsHooks.ts`, `googleAdsSchema.ts` na mesma pasta |
| Rastreamento e atribuição | `frontend/src/lib/rastreio.ts`, `frontend/src/lib/origem.ts` |
| Contratos e handlers backend | `backend/src/PropertyRegistration.Application/Marketing/GoogleAds.cs`, `GoogleAdsGestao.cs` |
| Integração backend | `backend/src/PropertyRegistration.Infrastructure/Marketing/GoogleAdsAdministracao.cs`, `GoogleAdsCampanhas.cs`, `GoogleAdsGestao.cs`, `GoogleAdsHttp.cs` |
| Endpoints administrativos | `backend/src/PropertyRegistration.WebApi/Controllers/GoogleAdsController.cs` |
| Persistência inicial | `sql/16_google_ads.sql`; tabelas `BackofficeConfiguracaoGoogleAds` e `BackofficeOperacaoGoogleAds` |

Base da API: `/api/v1/backoffice/integracoes/google-ads`, sempre com política Backoffice.

- `GET` / `PUT` na base: consultar metadados / salvar configuração.
- `POST /teste`: testar acesso.
- `POST /conversoes`: configurar as duas ações do site.
- `POST /campanhas?validar=true|false`: validar ou criar pausada.
- `GET /gestao?tipo=campanhas|conversoes`: consultar recursos.
- `GET /gestao?tipo=detalhes&campanha=ID_NUMERICO`: consultar grupos, anúncios e palavras.
- `PUT /gestao`: alterar recurso com conta, tipo, ação e campos pertinentes.

As melhorias de abas, sugestões e gestão não acrescentaram tabelas além da estrutura inicial da integração.

## Limites do escopo entregue

A ferramenta não reproduz todo o Google Ads. Performance Max, outras redes, segmentação geográfica avançada, estratégias automáticas de lance, extensões/recursos, faturamento, edição de orçamento compartilhado e conversões otimizadas continuam fora do painel. Preserve essa informação na interface e na documentação; não simule suporte inexistente.

## Validação para próximas alterações

- Testes não devem operar contas Google reais nem ler credenciais de produção. Use respostas simuladas, inclusive para falhas, recusas e timeouts.
- Backend: `GoogleAdsTests.cs`, `GoogleAdsGestaoTests.cs` e `GoogleAdsE2ETests.cs` verificam criação, gestão, proteção de credenciais, autorização e conta/recurso.
- Frontend: `googleAds.spec.ts`, `googleAdsGestao.spec.ts` e `backoffice.spec.ts` verificam fluxos, preservação entre abas e confirmações; Playwright roda em desktop e celular.
- Para mudanças de lógica, execute build/lint/tipos e suítes pertinentes conforme os AGENTS de backend/frontend. Confira visualmente alterações de layout nos temas e tamanhos afetados.
- No fechamento de 03/10/2026, a gestão passou por 456 testes backend, 60 unitários frontend e 96 de navegador (4 capturas opcionais ignoradas). O ajuste posterior de sugestões/alinhamento passou por build, lint e 4 testes Google Ads de navegador. São registros históricos, não substituem validação de alterações futuras.
- Testes simulados não validam aprovação de anúncios, volume de buscas, entrega real de conversões nem disponibilidade de todos os recursos da API na conta conectada.

Referências para futuras verificações: [anúncios responsivos](https://support.google.com/google-ads/answer/7684791), [edição de anúncios](https://developers.google.com/google-ads/api/docs/ads/mutate-ads), [representação JSON REST](https://developers.google.com/google-ads/api/rest/design/json-mappings).
