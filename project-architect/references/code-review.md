# Code Review Guidelines — Tech Lead Agent

## 1. Backend (.NET)
- **Dependency Injection**: Verifique se as dependências são via interface no construtor.
- **Async/Await**: Certifique-se de que `CancellationToken` está sendo passado até o final da cadeia.
- **Exceptions**: O código usa o `Result Pattern` para erros de negócio ou joga exceptions caras?
- **Mapping**: DTOs estão sendo usados para retornar dados da API? Jamais retorne Entidades.

## 2. Database (DBA)
- **Queries**: Algum `.ToList()` foi chamado antes do `.Where()`? (Memória vs Banco).
- **Concurrency**: Entidades críticas possuem tratamento de `RowVersion`?
- **Multi-tenancy**: O filtro global de TenantId está configurado na nova entidade?

## 3. Frontend (React)
- **Props**: Estão devidamente tipadas com TypeScript?
- **Effects**: Os `useEffect` possuem arrays de dependência corretos?
- **Components**: O componente é pequeno o suficiente ou deve ser quebrado?