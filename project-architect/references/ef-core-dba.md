# Entity Framework Core & SQL Server Best Practices — Senior DBA Guide

Este guia estabelece os padrões obrigatórios para mapeamento, performance, segurança e manutenção do acesso a dados em projetos .NET com EF Core.

## 1. Mapeamento e Esquema

### 1.1. Tabelas e Schemas
- **Nomes de Tabela**: Sempre definir explicitamente com `ToTable("Nome", "schema")`.
- **Schema padrão**: Use `dbo` para entidades de negócio e `auth` para entidades de autenticação.
- **Naming Convention**: Tabelas no plural (`Tasks`, `Projects`), colunas no singular (`Name`, `Status`).

### 1.2. Tipos de Dados (Strict Typing)
- **Strings**: Nunca deixar strings sem tamanho definido. Use `.HasMaxLength(n)`. Jamais aceite `nvarchar(max)` sem justificativa explícita.
- **Decimais**: Para valores financeiros, use `.HasColumnType("decimal(18,2)")`. Para quantidades, `.HasColumnType("decimal(10,4)")`.
- **Datas**: Use `DateTime` com `datetime2(7)` no SQL Server. Sempre armazene em UTC.
- **GUIDs**: Use `uniqueidentifier` no SQL Server. Considere `newsequentialid()` para PKs clusterizadas.
- **Booleans**: Mapeie explicitamente para evitar ambiguidade: `.HasColumnType("bit")`.

### 1.3. Fluent API (Obrigatório)
O mapeamento DEVE ser feito via `IEntityTypeConfiguration<T>` em arquivos separados. Data Annotations são proibidas para mapeamento de banco.

```csharp
public class TaskConfiguration : IEntityTypeConfiguration<TaskItem>
{
    public void Configure(EntityTypeBuilder<TaskItem> builder)
    {
        builder.ToTable("Tasks", "dbo");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.Title)
            .HasMaxLength(200)
            .IsRequired();

        builder.Property(x => x.Description)
            .HasMaxLength(2000);

        builder.Property(x => x.Status)
            .HasConversion<string>()
            .HasMaxLength(20);

        builder.Property(x => x.Priority)
            .HasConversion<string>()
            .HasMaxLength(20);

        builder.Property(x => x.RowVersion)
            .IsRowVersion();
    }
}
```

### 1.4. Concorrência Otimista (RowVersion)
- Entidades críticas devem implementar `RowVersion` para evitar conflitos de escrita.
- Use `builder.Property(x => x.RowVersion).IsRowVersion()` no mapeamento.
- No handler, capture `DbUpdateConcurrencyException` e retorne `Result.Failure("Conflito de concorrência")`.

## 2. Indexação

### 2.1. Regras de Indexação
- **Foreign Keys**: Todo campo de chave estrangeira DEVE ter um índice. O EF Core não cria automaticamente.
- **TenantId**: Em sistemas multi-tenant, o `TenantId` deve fazer parte de índices compostos.
- **Nomes**: Padronizar como `IX_TableName_ColumnName`.
- **Índices Compostos**: Para queries frequentes, crie índices compostos na ordem do filtro.

```csharp
// Índice simples em FK
builder.HasIndex(x => x.ProjectId)
    .HasDatabaseName("IX_Tasks_ProjectId");

// Índice composto para multi-tenant
builder.HasIndex(x => new { x.TenantId, x.ProjectId })
    .HasDatabaseName("IX_Tasks_TenantId_ProjectId");

// Índice com Include para Covering Index
builder.HasIndex(x => x.Status)
    .HasDatabaseName("IX_Tasks_Status")
    .IncludeProperties(x => new { x.Title, x.Priority });
```

### 2.2. Índices Únicos
- Use para campos que devem ser únicos dentro de um contexto (ex: email por tenant).
- `builder.HasIndex(x => new { x.TenantId, x.Email }).IsUnique()`.

## 3. Performance de Consulta

### 3.1. AsNoTracking (Obrigatório para Leitura)
- **Todas** as queries de leitura (Queries no CQRS) DEVEM usar `.AsNoTracking()`.
- Queries de escrita (dentro de Commands) podem usar tracking normal.

```csharp
// ✅ Correto — Query de leitura
var tasks = await _context.Tasks
    .AsNoTracking()
    .Where(t => t.ProjectId == projectId)
    .Select(t => new TaskDto(t.Id, t.Title, t.Status.ToString()))
    .ToListAsync(ct);

// ❌ Errado — Leitura sem AsNoTracking (desperdiça memória)
var tasks = await _context.Tasks
    .Where(t => t.ProjectId == projectId)
    .ToListAsync(ct);
```

### 3.2. Split Queries
- Usar `.AsSplitQuery()` quando houver mais de 2 `Include()` complexos para evitar cartesian explosion.

```csharp
var project = await _context.Projects
    .AsNoTracking()
    .Include(p => p.Tasks)
    .Include(p => p.Members)
    .Include(p => p.Categories)
    .AsSplitQuery()
    .FirstOrDefaultAsync(p => p.Id == projectId, ct);
```

### 3.3. Projeções (Select)
- Preferir `Select(x => new Dto { ... })` em vez de retornar a entidade completa.
- Projeções reduzem o SELECT do SQL para apenas as colunas necessárias.
- Isso economiza bandwidth, memória e elimina a necessidade de `AsNoTracking`.

### 3.4. Paginação
- Sempre use `Skip/Take` no banco, nunca carregue toda a lista para paginar em memória.
- Retorne `totalCount` separadamente para o frontend calcular as páginas.

```csharp
var query = _context.Tasks
    .AsNoTracking()
    .Where(t => t.ProjectId == projectId);

var totalCount = await query.CountAsync(ct);
var items = await query
    .OrderByDescending(t => t.CreatedAt)
    .Skip((page - 1) * pageSize)
    .Take(pageSize)
    .Select(t => new TaskDto(...))
    .ToListAsync(ct);
```

## 4. Multi-Tenancy (Filtros Globais)

### 4.1. HasQueryFilter
- Use `.HasQueryFilter()` para garantir isolamento de dados entre tenants.
- O filtro é aplicado automaticamente em TODAS as queries, inclusive `Include`.

```csharp
public class TaskConfiguration : IEntityTypeConfiguration<TaskItem>
{
    private readonly ITenantProvider _tenantProvider;

    public TaskConfiguration(ITenantProvider tenantProvider)
        => _tenantProvider = tenantProvider;

    public void Configure(EntityTypeBuilder<TaskItem> builder)
    {
        builder.HasQueryFilter(x => x.TenantId == _tenantProvider.TenantId);
    }
}
```

### 4.2. Bypass do Filtro (Apenas para Admin)
- Use `.IgnoreQueryFilters()` apenas em operações administrativas cross-tenant.
- Sempre valide a Role do usuário antes de ignorar filtros.

## 5. Otimização de Queries

### 5.1. CancellationToken
- Propagar o token em todas as chamadas assíncronas ao banco: `ToListAsync(ct)`, `FirstOrDefaultAsync(p => ..., ct)`, `SaveChangesAsync(ct)`.

### 5.2. Bulk Operations
- Para inserções em massa (>100 registros), considere `EFCore.BulkExtensions` ou `ExecuteUpdate/ExecuteDelete` do EF Core 7+.

### 5.3. Compiled Queries
- Para queries executadas com alta frequência, use `EF.CompileAsyncQuery` para evitar overhead de tradução.

```csharp
private static readonly Func<AppDbContext, Guid, CancellationToken, Task<TaskItem?>> GetByIdQuery =
    EF.CompileAsyncQuery((AppDbContext ctx, Guid id, CancellationToken ct) =>
        ctx.Tasks.FirstOrDefault(t => t.Id == id));
```

## 6. Migrations

### 6.1. Boas Práticas
- Nomeie migrations de forma descritiva: `AddTenantIdToTasks`, `CreateProjectsTable`.
- Nunca edite uma migration já aplicada em produção.
- Use `Data Seeding` apenas para dados de referência (enums, roles default).
- Em produção, aplique migrations via pipeline CI/CD, nunca pelo `EnsureCreated()`.
