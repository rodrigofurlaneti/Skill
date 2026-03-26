# Security & Identity Guidelines — Security Officer Agent

Este guia estabelece os padrões de autenticação, autorização e proteção de dados (OWASP Top 10).

## 1. Autenticação (JWT + Identity)
- **Token Strategy**: Use JWT com `RS256` (assinatura assimétrica) ou `HS256` com chaves de no mínimo 32 caracteres.
- **Expiration**: Access Tokens curtos (15-60 min) + Refresh Tokens seguros armazenados em `HttpOnly Cookies`.
- **Claims**: Mantenha o payload do JWT leve. Use apenas `sub`, `email`, `role` e `TenantId`.

## 2. Autorização (RBAC & ABAC)
- **Role-Based (RBAC)**: Use `[Authorize(Roles = "Admin")]` para permissões fixas.
- **Policy-Based**: Use Políticas para lógicas complexas (ex: "Apenas o dono do registro ou um Admin pode deletar").
- **Multi-tenant Isolation**: Toda query deve ser filtrada pelo `TenantId` do usuário logado (validado no JWT).

## 3. Proteção contra Ataques (OWASP)
- **Injeção**: Use sempre EF Core (Parametrized Queries) para evitar SQL Injection.
- **XSS**: Sanitização obrigatória de todos os inputs de texto que serão renderizados no Front (use `InputSanitizer.cs`).
- **Sensitive Data**: Nunca armazene senhas em texto plano. Use `BCrypt` ou `Argon2` com Salt.
- **Logging**: Jamais logue dados sensíveis (Senhas, CVV, Tokens) nos logs estruturados.

## 4. Comunicação Segura
- **HTTPS**: Obrigatório em todos os ambientes.
- **CORS**: Política de "Least Privilege". Apenas domínios conhecidos podem acessar a API.
- **Headers**: Implemente `HSTS`, `X-Content-Type-Options` e `Content-Security-Policy`.