# Code Review Guidelines — Tech Lead Agent

Este guia define os critérios obrigatórios de revisão de código para garantir qualidade, consistência e aderência aos padrões arquiteturais do projeto.

## 1. Backend (.NET) — Clean Architecture

### 1.1. Dependency Injection
- Verifique se todas as dependências são injetadas via interface no construtor.
- Nunca use `new` para criar serviços dentro de handlers ou controllers.
- Registre dependências com o escopo correto: `Scoped` para repositórios, `Transient` para behaviors, `Singleton` apenas para stateless.

### 1.2. Async/Await
- Certifique-se de que `CancellationToken` está sendo passado até o final da cadeia.
- Nunca use `.Result` ou `.Wait()` — isso causa deadlocks.
- Métodos async devem ter sufixo `Async` apenas em interfaces públicas (dentro de handlers, o nome do método é `Handle`).

### 1.3. Result Pattern
- O código usa o `Result Pattern` para erros de negócio? Jamais lance exceptions para erros esperados.
- Verifique se `Result.Failure`, `Result.NotFound` e `Result.ValidationError` estão sendo usados corretamente.
- Exceptions devem ser reservadas para erros inesperados (falha de conexão, timeout).

### 1.4. Mapping & DTOs
- DTOs estão sendo usados para retornar dados da API? Jamais retorne Entidades diretamente.
- Projeções (`.Select()`) são preferíveis a `AutoMapper` para queries simples.
- Verifique se não há propriedades sensíveis (senha, token) sendo expostas nos DTOs.

### 1.5. Segurança no Código
- Inputs de texto estão sendo sanitizados com `InputSanitizer`?
- Endpoints possuem `[Authorize]` ou `[AllowAnonymous]` explícito?
- Dados sensíveis nunca são logados (senhas, tokens, CVVs).

## 2. Database (DBA Review)

### 2.1. Queries
- Algum `.ToList()` foi chamado antes do `.Where()`? Isso carrega toda a tabela na memória.
- Existe `N+1 Problem`? (ex: loop com chamadas ao banco dentro). Use `Include` ou projeções.
- Queries de leitura usam `.AsNoTracking()`?

### 2.2. Concorrência
- Entidades críticas possuem tratamento de `RowVersion`?
- `DbUpdateConcurrencyException` está sendo tratado nos handlers relevantes?

### 2.3. Mapeamento
- Todas as strings possuem `HasMaxLength()`?
- Decimais financeiros usam `decimal(18,2)`?
- O mapeamento está em `IEntityTypeConfiguration<T>` separado (não no DbContext)?

### 2.4. Multi-tenancy
- O filtro global de `TenantId` está configurado para a nova entidade?
- Se o filtro foi ignorado com `IgnoreQueryFilters()`, há validação de Role?
- Índices compostos incluem `TenantId` como primeiro campo?

### 2.5. Performance
- Paginação está no banco (`Skip/Take`) ou em memória?
- Queries com mais de 2 `Include` usam `.AsSplitQuery()`?
- Campos usados em `WHERE` e `ORDER BY` possuem índices?

## 3. Frontend (React + TypeScript)

### 3.1. Type Safety
- Existem tipos `any` no código? Zero `any` é a meta.
- Props estão devidamente tipadas com interfaces explícitas?
- Tipos de API response estão definidos em `src/types/`?

### 3.2. React Patterns
- Os `useEffect` possuem arrays de dependência corretos? Sem dependências faltantes ou desnecessárias.
- Callbacks passados para componentes filhos usam `useCallback`?
- Listas grandes usam `useMemo` para cálculos derivados?
- Componentes possuem `key` correta em iterações (nunca use index como key para listas dinâmicas)?

### 3.3. Componentização
- O componente é pequeno o suficiente ou deve ser quebrado?
- Lógica de negócio está separada da apresentação (custom hooks vs componentes)?
- Componentes UI reutilizáveis estão em `components/ui/`, não duplicados em features.

### 3.4. Estado
- Estado global (Zustand) é usado apenas para dados que precisam persistir entre páginas?
- Estado de servidor (queries) usa React Query, não Zustand?
- Formulários usam estado local (`useState`), não estado global?

### 3.5. Acessibilidade
- Botões com ícone possuem `aria-label`?
- Formulários possuem `label` associado via `htmlFor`?
- Contraste de texto atende o mínimo 4.5:1?
- Navegação por teclado funciona (Tab, Enter, Escape)?

## 4. Tratamento de Erros

### 4.1. Backend
- Não use `try-catch` para controle de fluxo. Use `Result.Failure()`.
- Errors inesperados devem ser capturados pelo middleware global (`UseExceptionHandler`).
- Logs de erro incluem contexto estruturado: `UserId`, `RequestName`, `CorrelationId`.

### 4.2. Frontend
- Erros de API são exibidos ao usuário com mensagens claras (não stack traces)?
- Existe `ErrorBoundary` para erros de rendering?
- Mutations possuem `onError` com feedback visual (toast)?

## 5. Checklist de PR (Obrigatório)

Antes de aprovar qualquer PR, verifique:

- [ ] **DDD**: A lógica de negócio está na Entidade/Value Object (não no Service)?
- [ ] **Clean Arch**: As dependências apontam para dentro? (Domain não conhece Infra/API).
- [ ] **Performance**: Consultas de leitura usam `.AsNoTracking()`?
- [ ] **Resiliência**: `CancellationToken` foi propagado em todos os métodos async?
- [ ] **Contrato**: Foi usado `Result Pattern` em vez de Exceptions para erros de negócio?
- [ ] **DB**: O mapeamento Fluent API foi atualizado (se necessário)?
- [ ] **Segurança**: Inputs sanitizados, endpoints protegidos, dados sensíveis não logados?
- [ ] **Tipos**: Zero `any` no frontend, DTOs no backend?
- [ ] **Testes**: Unit tests incluídos para a regra de negócio?
- [ ] **ArchTests**: Testes de arquitetura passaram localmente (`dotnet test`)?
