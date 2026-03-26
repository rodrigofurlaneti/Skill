# Entity Framework Core & SQL Server Best Practices

## 1. Mapeamento e Esquema
- **Nomes de Tabela**: Sempre definir explicitamente com `ToTable("Nome", "schema")`.
- **Strings**: Nunca deixar strings sem tamanho definido. Use `.HasMaxLength(n)`.
- **Decimais**: Para valores financeiros, use `.HasColumnType("decimal(18,2)")`.
- **Concorrência**: Implementar `builder.Property(x => x.RowVersion).IsRowVersion()` para evitar conflitos de escrita.

## 2. Indexação
- **FKs**: Todo campo de chave estrangeira deve ter um índice.
- **TenantId**: Em sistemas Multi-tenant, o `TenantId` deve fazer parte de índices compostos para otimizar o filtro global.
- **Nomes**: Padronizar nomes de índices como `IX_TableName_ColumnName`.

## 3. Performance de Consulta
- **Split Queries**: Usar `.AsSplitQuery()` quando houver mais de 2 `Include()` complexos.
- **Projeções**: Preferir `Select(x => new Dto { ... })` em vez de retornar a entidade completa se apenas alguns campos forem necessários.

## 4. Otimização de Queries
- **Consultas de Lista**: Sempre usar Projeções (DTOs) para evitar o carregamento de colunas desnecessárias no SELECT.
- **CancellationToken**: Propagar o token em todas as chamadas assíncronas ao banco (`ToListAsync(ct)`).