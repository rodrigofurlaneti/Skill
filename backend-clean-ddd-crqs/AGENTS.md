# AGENTS.md — Backend DingFood

Guia de padrões do backend. Leia antes de criar ou alterar qualquer código em `backend/`.

Escrito para quem (pessoa ou agente) vai escrever código aqui. Descreve o que o projeto
**realmente faz hoje**, não um ideal. Quando houver divergência entre este documento e o código,
o código vence — e o documento deve ser corrigido.

---

## 1. Stack

| Item | Versão / escolha |
|---|---|
| Runtime | .NET 9 (`net9.0`), C# 13, `Nullable` e `ImplicitUsings` habilitados |
| Banco | MySQL 8.4 via **Pomelo.EntityFrameworkCore.MySql** (não o provider da Oracle) |
| Mediação | MediatR |
| Validação | FluentValidation + SharpGrip AutoValidation |
| Log | Serilog (console + arquivo) |
| Auth | JWT Bearer |
| Docs | Swashbuckle |
| Testes | xUnit + FluentAssertions + NSubstitute + NetArchTest |
| CI | GitHub Actions + SonarQube Cloud (análise via scanner no CI, **não** Automatic Analysis) |

---

## 2. Arquitetura

Clean Architecture em quatro projetos. A dependência aponta sempre para dentro:

```
DingFood.API  ──►  DingFood.Application  ──►  DingFood.Domain
      │                                            ▲
      └──────►  DingFood.Infrastructure  ──────────┘
```

Regras **verificadas por teste** em `test/DingFood.ArchTests/ArchitectureTests.cs`. Quebrar
qualquer uma delas derruba o CI:

- **Domain** não pode depender de Application, Infrastructure, API, MediatR, EF Core nem FluentValidation.
- **Application** não pode depender de Infrastructure, API nem EF Core.
- **Infrastructure** não pode depender de API.

Consequência prática: a Application é uma class library pura, **sem `Microsoft.AspNetCore.*`**.
Tudo que precisa de framework (hash de senha, JWT, Data Protection, HttpClient) entra como
interface na Application e implementação na Infrastructure.

### Onde cada coisa mora

```
src/DingFood.Domain/
  Constants/          FeatureCodes, LookupIds, validadores puros (CnpjValidator, CepValidator)
  Entities/           entidades e agregados
  Enums/
  Exceptions/         ConcurrencyException, TenantAccessException, DeliveryPricingException
  Primitives/         Entity, AggregateRoot, Result, Error, ValueObject, IDomainEvent
  Repositories/       APENAS interfaces (IXRepository), + IUnitOfWork

src/DingFood.Application/
  Abstractions/
    Messaging/        ICommand, IQuery, BaseCommandHandler, BaseQueryHandler
    Integrations/<Provedor>/   contrato do parceiro (interface + DTOs)
    Authentication|Security|Storage|Printing|Payments|Fiscal|Notifications|Tenancy/
  Features/<Área>/
    <Ação>/           Command/Query + Handler + Validator
    XResponse.cs      contrato de saída da área

src/DingFood.Infrastructure/
  Integrations/<Provedor>/     client HTTP + Settings + background services
  Persistence/
    AppDbContext.cs                    DbSets
    AppDbContext.Tenancy.cs            query filters por tenant
    AppDbContext.OperationalScopes.cs  classificação de escopo (ver §6)
    Configurations/XConfiguration.cs   IEntityTypeConfiguration
    Repositories/XRepository.cs        implementações
  Migrations/         migrations do EF Core
  Authentication|Security|Storage|Printing|Payments|Fiscal|Tenancy|Delivery|Time/
  DependencyInjection.cs               registro de TUDO da Infrastructure

src/DingFood.API/
  Controllers/        XController : ApiController
  Middleware/         ExceptionHandling, CompanyContext, WorkplaceContext
  Authorization/      FeatureAccessConvention, FeatureAuthorizationHandler
  Serialization/      UtcDateTimeConverter
  Program.cs
```

---

## 3. Convenções obrigatórias (checadas por ArchTests)

| Tipo | Regra |
|---|---|
| `*CommandHandler` | `internal sealed`, na Application |
| `*QueryHandler` | `internal sealed`, na Application |
| `*Repository` (impl.) | `internal sealed`, em `DingFood.Infrastructure.Persistence.Repositories` |
| `I*Repository` (interface) | em `DingFood.Domain.Repositories` |
| `*Configuration` | `internal sealed`, em `DingFood.Infrastructure.Persistence.Configurations` |
| `*Response` | `sealed` |
| `*Validator` | herda `AbstractValidator<T>` |
| `*Command` / `*Query` | dentro de `DingFood.Application.Features` |
| Classes em `Domain.Entities` | `sealed` |
| Agregados | herdam `AggregateRoot` |
| Entidades filhas | herdam `Entity`, **não** `AggregateRoot` |

Agregado = raiz de consistência com repositório próprio (Company, Branch, AppUser, CustomerOrder,
Sale, CashSession, StockItem, Purchase). Entidade filha = só existe dentro do agregado e é
carregada por ele (OrderItem, SalePayment, CashMovement, StockMovement, PurchaseItem).

---

## 4. Result, não exceção

O fluxo de negócio usa `Result` / `Result<T>` (`Domain/Primitives`). Exceção é para falha
excepcional, não para regra de negócio.

```csharp
public static Result<Supplier> Create(long companyId, string legalName, ...)
{
    if (string.IsNullOrWhiteSpace(legalName))
        return Result.Failure<Supplier>(new Error("Supplier.EmptyLegalName", "LegalName is required."));

    return Result.Success(new Supplier(companyId, legalName, ...));
}
```

### O `Error.Code` define o HTTP status

`ApiController.HandleFailure` mapeia **por sufixo**:

| Sufixo do Code | HTTP |
|---|---|
| `.Forbidden` | 403 |
| `.NotFound` | 404 |
| `.AlreadyExists` | 409 |
| `.Duplicate` | 409 |
| qualquer outro | **400** |

Então `Cnpj.NotFound` vira 404 automaticamente, mas `Cnpja.RateLimited` vira 400 — não existe
mapeamento para 429 hoje. Nomeie o Code pensando no status que você quer, ou adicione o sufixo
novo em `HandleFailure` (afeta ~60 controllers, avalie antes).

Padrão de nome: `<Contexto>.<Motivo>` em PascalCase — `Supplier.EmptyLegalName`, `Cep.NotFound`,
`Tenant.Forbidden`.

---

## 5. Entidades

```csharp
public sealed class Supplier : AggregateRoot
{
    public long CompanyId { get; private set; }
    public string LegalName { get; private set; } = null!;
    public DateTime CreatedAt { get; private set; }
    public DateTime? UpdatedAt { get; private set; }
    public bool IsActive { get; private set; }

    private Supplier() : base(0) { }                    // EF
    private Supplier(long companyId, ...) : base(0) { } // fábrica

    public static Result<Supplier> Create(...) { ... }
    public void Deactivate() { IsActive = false; UpdatedAt = DateTime.Now; }
}
```

- Setters **privados**. Estado muda por método de domínio, nunca por atribuição externa.
- Ctor privado sem parâmetros para o EF; ctor privado com parâmetros para a fábrica.
- `base(0)` — o `Id` é gerado pelo banco (`ValueGeneratedOnAdd`).
- Colunas de auditoria `CreatedAt` / `UpdatedAt?` / `IsActive` na maioria das entidades.
- Exclusão é **lógica** (`IsActive = false`), não física.
- Quando o construtor teria mais de ~10 parâmetros, use um `record` de snapshot no mesmo arquivo
  (ver `CnpjQuerySnapshot`, `CepQuerySnapshot`) e passe-o para `Create`/`Refresh`.

⚠️ O projeto usa `DateTime.Now` (hora local) nas entidades, não `DateTime.UtcNow`. Existe um
`UtcDateTimeConverter` na serialização da API. Mantenha a consistência com o que já existe; não
misture os dois numa mesma entidade.

---

## 6. Multi-tenancy — leia antes de criar qualquer entidade

O isolamento por empresa é automático e **obrigatório por construção**.
`AppDbContext.OperationalScopes.cs` classifica toda entidade do modelo em uma de quatro
categorias e, se sobrar alguma, lança no `OnModelCreating`:

```
InvalidOperationException: Entities without ownership: <NomeDaEntidade>
```

Esse erro trava `dotnet ef migrations add` e a subida da API. As quatro categorias:

1. **Escopada por tenant** — tem `CompanyId` e/ou `BranchId` e/ou `BrandId`. Ganha query filter
   automático. É o caso normal.
2. **Herdada** — sem coluna de tenant, mas com FK única para uma entidade já classificada.
   Herda o escopo do pai. Relações ambíguas precisam de entrada em `AggregateParents`.
3. **`IdentityTables`** — identidade e organização (AppUser, Company, Brand, BusinessGroup...).
4. **`SystemTables`** — tabela de referência global, igual para todos os tenants.

Se a sua entidade é global de propósito (tabela de domínio público, lookup compartilhado),
adicione o nome dela em `SystemTables`:

```csharp
internal static readonly HashSet<string> SystemTables = new(StringComparer.Ordinal)
{
    "AppFeature", "Permission", "UnitOfMeasure", ..., "CnpjQuery", "CepQuery"
};
```

O comentário no código é explícito: *"a new table cannot silently become a global operational
table"*. A declaração manual é intencional — não contorne criando uma FK artificial.

### TenantRequestBehavior

Pipeline behavior do MediatR que roda em **todo** request. Se há tenant autenticado:

- request com propriedade `CompanyId` diferente da empresa da sessão → `TenantAccessException` → **403**;
- request com propriedade terminada em `BranchId` → valida que a filial pertence à empresa e está ativa.

Features públicas (`PublicOrdering`, `Storefront`, `Checkout`, `Auth.CustomerLogin`) passam pelo
`IPublicWorkplaceScope`, que amarra o escopo por `BranchId`, `Token` ou `CustomerOrderId`.

Ou seja: **não escreva checagem manual de tenant no handler.** Basta nomear a propriedade
`CompanyId` ou `...BranchId` no command/query.

---

## 7. Receita: criar uma feature nova

Exemplo para uma área `Foo` com listagem e criação.

**1. Domain**

```
Domain/Entities/Foo.cs                 sealed, AggregateRoot, Create -> Result<Foo>
Domain/Repositories/IFooRepository.cs  GetByIdAsync, GetByIdForUpdateAsync,
                                       GetByCompanyAsync, AddAsync
```

Se a entidade não tiver `CompanyId`/`BranchId`/FK para agregado classificado → §6.

**2. Application**

```
Features/Foo/FooResponse.cs                        sealed record
Features/Foo/Create/CreateFooCommand.cs            sealed record : ICommand<long>
Features/Foo/Create/CreateFooCommandHandler.cs     internal sealed : BaseCommandHandler<,>
Features/Foo/Create/CreateFooCommandValidator.cs   AbstractValidator<CreateFooCommand>
Features/Foo/GetByCompany/GetFoosByCompanyQuery.cs        : IQuery<IReadOnlyCollection<FooResponse>>
Features/Foo/GetByCompany/GetFoosByCompanyQueryHandler.cs internal sealed : BaseQueryHandler<,>
```

Handler de comando:

```csharp
internal sealed class CreateFooCommandHandler(
    IFooRepository fooRepository,
    ILogTrackerRepository logRepository,
    IUnitOfWork unitOfWork)
    : BaseCommandHandler<CreateFooCommand, long>(logRepository, unitOfWork)
{
    public override async Task<Result<long>> Handle(CreateFooCommand request, CancellationToken ct)
    {
        return await ExecuteWithLogAsync(
            nameof(CreateFooCommandHandler), nameof(Handle), null,
            async (userIdBox) =>
            {
                var foo = Foo.Create(request.CompanyId, request.Name);
                if (foo.IsFailure) return Result.Failure<long>(foo.Error);

                await fooRepository.AddAsync(foo.Value, ct);
                await unitOfWork.CommitAsync(ct);

                return Result.Success(foo.Value.Id);
            });
    }
}
```

`ExecuteWithLogAsync` grava um `LogTracker` (classe, método, sucesso, tempo, erro, IP) na mesma
unidade de trabalho. **Não remova e não torne fire-and-forget** — o código tem comentário
explicando que isso já causou `NullReferenceException` em `ChangeDetector.DetectChanges` por
uso do `DbContext` fora do escopo da requisição.

Construtor primário é o padrão no código novo; construtor explícito também existe e é aceito.

**3. Infrastructure**

```
Persistence/Configurations/FooConfiguration.cs  internal sealed
Persistence/Repositories/FooRepository.cs       internal sealed
```

E registrar em `Infrastructure/DependencyInjection.cs`:

```csharp
services.AddScoped<IFooRepository, FooRepository>();
```

**4. API**

```csharp
public sealed class FoosController(
    IMediator mediator,
    ILogTrackerRepository logRepository,
    IUnitOfWork unitOfWork) : ApiController(mediator)
{
    [HttpGet("company/{companyId:long}")]
    public Task<IActionResult> GetByCompany(long companyId, CancellationToken ct) =>
        ExecuteWithLogAsync(logRepository, unitOfWork, nameof(FoosController), nameof(GetByCompany), async () =>
        {
            var result = await Mediator.Send(new GetFoosByCompanyQuery(companyId), ct);
            return result.IsFailure ? HandleFailure(result) : Ok(result.Value);
        });

    [Authorize(Roles = ManagerRoles)]
    [HttpPost]
    public Task<IActionResult> Create([FromBody] CreateFooCommand command, CancellationToken ct) =>
        ExecuteWithLogAsync(logRepository, unitOfWork, nameof(FoosController), nameof(Create), async () =>
        {
            var result = await Mediator.Send(command, ct);
            return result.IsFailure ? HandleFailure(result) : Ok(result.Value);
        });
}
```

- A rota base vem de `[Route("api/[controller]")]` no `ApiController`. Não repita.
- `ManagerRoles` é const do `ApiController` (`"Administrador"`).

**5. Migration** — §9.

---

## 8. Persistência

### Configuration

```csharp
internal sealed class FooConfiguration : IEntityTypeConfiguration<Foo>
{
    public void Configure(EntityTypeBuilder<Foo> builder)
    {
        builder.ToTable("foo");                                  // minúsculo, sem separador
        builder.HasKey(x => x.Id);
        builder.Property(x => x.Id).ValueGeneratedOnAdd();

        builder.Property(x => x.Name).HasColumnType("varchar(200)").IsRequired();
        builder.Property(x => x.CreatedAt).HasColumnType("datetime(6)").IsRequired();
        builder.Property(x => x.UpdatedAt).HasColumnType("datetime(6)");
        builder.Property(x => x.IsActive).HasColumnType("bit").IsRequired();

        builder.HasIndex(x => x.CompanyId).HasDatabaseName("IX_Foo_CompanyId");

        builder.HasOne<Company>().WithMany().HasForeignKey(x => x.CompanyId)
            .HasConstraintName("FK_Foo_Company").OnDelete(DeleteBehavior.Restrict);
    }
}
```

Convenções de banco:

| Item | Padrão |
|---|---|
| Tabela | minúsculo, sem underscore: `cnpjquery`, `ifoodintegrationsetting` |
| Data/hora | `datetime(6)` |
| Data pura | `date` (mapeia `DateOnly?`) |
| Booleano | `bit` |
| Monetário | `decimal(18,2)` |
| Texto curto | `varchar(n)` / `nvarchar(n)` |
| Texto longo / JSON | `longtext` |
| Documento fixo | `char(14)` CNPJ, `char(8)` CEP, `char(2)` UF |
| Índice | `IX_<Entidade>_<Coluna>` |
| Índice único | `UX_<Entidade>_<Coluna>` |
| FK | `FK_<Entidade>_<Destino>`, `DeleteBehavior.Restrict` |

`ApplyConfigurationsFromAssembly` descobre as configurations sozinho — não há registro manual.
Mas o **DbSet** precisa ser declarado em `AppDbContext.cs`.

MySQL não tem índice único filtrado. Regras do tipo "uma configuração ativa por empresa" são
garantidas por upsert no handler, não por constraint (ver `IfoodIntegrationSettingConfiguration`).

### Repository

```csharp
internal sealed class FooRepository(AppDbContext context) : IFooRepository
{
    public async Task<Foo?> GetByIdAsync(long id, CancellationToken ct = default)
        => await context.Foos.AsNoTracking().FirstOrDefaultAsync(x => x.Id == id, ct);

    public async Task<Foo?> GetByIdForUpdateAsync(long id, CancellationToken ct = default)
        => await context.Foos.FirstOrDefaultAsync(x => x.Id == id, ct);

    public async Task AddAsync(Foo entity, CancellationToken ct = default)
        => await context.Foos.AddAsync(entity, ct);
}
```

- Leitura → `AsNoTracking()`. Escrita → método `...ForUpdateAsync` **com** tracking.
- O repositório **nunca** chama `SaveChanges`. Quem commita é o handler, via `IUnitOfWork`.
- `IgnoreQueryFilters()` só em background service / job sem tenant (ver `IfoodIntegrationSettingRepository`).
- `AppDbContext` implementa `IUnitOfWork`; `CommitAsync` traduz `DbUpdateException` em `ConcurrencyException`.

---

## 9. Migrations

O projeto **usa EF Core Migrations**. A baseline é `20260914144158_InitialCreate`.

```powershell
cd backend

dotnet ef migrations add <Nome> `
  --project src\DingFood.Infrastructure `
  --startup-project src\DingFood.API `
  --output-dir Migrations

dotnet ef database update `
  --project src\DingFood.Infrastructure `
  --startup-project src\DingFood.API
```

Antes de aplicar, **leia o `Up()` gerado**. Ele deve conter só o que você mudou. `CreateTable`
de tabela que já existe, `DropColumn` ou `AlterColumn` inesperados significam que o
`AppDbContextModelSnapshot` divergiu do banco — pare e investigue.

Commite sempre os **três** arquivos: `<timestamp>_<Nome>.cs`, `.Designer.cs` e o
`AppDbContextModelSnapshot.cs` atualizado.

⚠️ `Program.cs` **não** chama `Database.Migrate()`. Todo deploy precisa do `database update`
manual (ou de um passo no pipeline).

⚠️ Existem scripts soltos em `Persistence/Migrations/*.sql` (`IfoodWebhook.sql`,
`BusinessGroups.sql`). São **legado anterior às migrations**, aplicados à mão, e nada no código
os executa. Não crie novos — use EF migrations.

---

## 10. Integrações com serviços externos

Padrão consolidado (iFood, Keeta, Asaas, CNPJá, ViaCEP):

```
Application/Abstractions/Integrations/<Provedor>/
    I<Provedor>Client.cs        contrato, devolve Result<T> — nunca lança por falha remota
    <Provedor>XResponse.cs      DTOs com [JsonPropertyName]
    I<Provedor>Options.cs       config que a Application precisa ler (ex.: TTL de cache)

Infrastructure/Integrations/<Provedor>/
    <Provedor>Settings.cs         POCO com SectionName, ligado por Configure<T>
    <Provedor>OptionsProvider.cs  adapta IOptions<Settings> para I<Provedor>Options
    <Provedor>Client.cs           HttpClient tipado
    <Provedor>...BackgroundService.cs
```

Registro:

```csharp
services.Configure<FooSettings>(configuration.GetSection(FooSettings.SectionName));
services.AddSingleton<IFooOptions, FooOptionsProvider>();
services.AddHttpClient<IFooClient, FooClient>(c => c.Timeout = TimeSpan.FromSeconds(15));
```

Regras:

- O client **traduz falha remota em `Result.Failure`**, com `Error.Code` no formato
  `<Provedor>.<Motivo>` (`Cnpja.RateLimited`, `ViaCep.Timeout`). Só deixa escapar exceção
  realmente inesperada.
- Segredo persistido passa por `ISecretProtector.Protect(purpose, value)`. O `purpose` é uma
  string fixa e versionada (`"DingFood.Integrations.Ifood.ClientSecret.v1"`) — trocá-la torna
  ilegíveis os segredos já salvos.
- Consulta a serviço externo com limite de uso deve ter **cache no banco**: entidade snapshot com
  `RawJson` (`longtext`) + `QueriedAt` + TTL configurável. Veja `CnpjQuery` e `CepQuery`.
  Guarde o corpo HTTP original, não o DTO reserializado — campos não mapeados se perdem.
- Se o serviço cair e houver snapshot antigo, devolva o antigo marcado (`StaleData = true`)
  em vez de falhar. Só propague o erro quando não houver nada em cache.

---

## 11. Autenticação, autorização e features

- JWT Bearer. A claim `companyId` alimenta `ICurrentTenantService`, que alimenta os query filters.
- Política `"AppUser"`: usuário autenticado que **não** é `Customer`.
- `[Authorize(Roles = ManagerRoles)]` no controller para ação de gestor.
- `FeatureAccessConvention` amarra controller → funcionalidade (`Orders` → `Salao,Preparo,Caixa`).
  Controller novo que pertença a uma tela existente deve entrar nesse dicionário; se não entrar,
  não recebe checagem de feature.
- Códigos de feature em `Domain/Constants/FeatureCodes.cs`.
- Endpoint público (pré-login, ex.: cadastro, storefront) **não** leva `[Authorize]` — mas
  lembre que ele fica exposto. Há rate limiter global de 200 req/min por IP e uma política
  `"auth"` de 10/min; use `[EnableRateLimiting("auth")]` em endpoint anônimo sensível.

---

## 12. Validação — cuidado com a pegadinha

`Program.cs` registra `AddFluentValidationAutoValidation()`. Isso valida automaticamente os
**modelos ligados pelo MVC** — ou seja, um command vindo de `[FromBody]` é validado antes do
handler rodar, e a resposta 400 sai sozinha.

**Não existe `ValidationBehavior` no pipeline do MediatR.** Então um command que o controller
**constrói à mão** a partir de parâmetros de rota não passa por validador nenhum:

```csharp
[HttpGet("{taxId}")]
public Task<IActionResult> GetByTaxId(string taxId, CancellationToken ct) =>
    ...Mediator.Send(new ConsultCnpjCommand(taxId), ct);   // validator NÃO roda
```

Nesses casos, **valide dentro do handler** e devolva `Result.Failure` (ver
`ConsultCnpjCommandHandler` e `ConsultCepCommandHandler`). Escreva o validator mesmo assim — ele
documenta a regra e passa a valer se o command virar `[FromBody]`.

---

## 13. Testes

```
test/DingFood.Tests/      unitários, espelhando a estrutura src/ (Domain, Application, Infrastructure, API)
test/DingFood.ArchTests/  regras de arquitetura (NetArchTest) — §3
test/DingFood.Specs/      BDD
test/DingFood.E2ETests/
```

Ferramentas: xUnit, FluentAssertions, NSubstitute, `Microsoft.EntityFrameworkCore.Sqlite` para
DbContext em memória.

```powershell
dotnet test test/DingFood.Tests --settings coverage.runsettings --collect:"XPlat Code Coverage"
dotnet test test/DingFood.ArchTests
```

Feature nova deve vir com teste de handler cobrindo sucesso e as falhas de negócio.

---

## 14. CI

`.github/workflows/ci.yml` — job `backend`: restore → sonar begin → build Release → 3 suítes de
teste → sonar end.

- `-warnaserror` foi **removido** de propósito: com o analisador do Sonar ativo no build, as
  issues em remediação viravam erro de compilação e travavam o CI antes dos testes. Não recoloque.
- A etapa do Sonar só roda se o secret `SONAR_TOKEN` existir (protege forks).
- A análise é **CI-based**. O *Automatic Analysis* do SonarQube Cloud precisa ficar **desligado**
  no projeto — com os dois ativos, o scanner aborta com
  `You are running CI analysis while Automatic Analysis is enabled`.

---

## 15. Armadilhas conhecidas

1. **`Entities without ownership`** ao rodar migration ou subir a API → falta classificar a
   entidade nova. §6.
2. **`HandleFailure` não mapeia 429** nem outros status. Sufixo desconhecido = 400. §4.
3. **Validator não roda em command montado na controller.** §12.
4. **Nomenclatura inconsistente de arquivo x classe**: existem arquivos `IFoodXxx.cs` cujas
   classes se chamam `IfoodXxx`. Ao criar código novo, siga o nome da **classe** que já existe
   na pasta; não renomeie em massa sem necessidade.
5. **`Program.cs` não aplica migrations.** §9.
6. **`appsettings.json` versionado contém connection string e segredos de exemplo.** Não adicione
   credencial real; use variável de ambiente / secret do ambiente.
7. **Não crie `.sql` novo em `Persistence/Migrations/`.** §9.
8. `BaseCommandHandler.ExecuteWithLogAsync` faz `await` na gravação do log de propósito. §7.

---

## 16. Antes de abrir PR

- [ ] `dotnet build DingFood.sln -c Release` sem erro
- [ ] `dotnet test test/DingFood.ArchTests` verde
- [ ] `dotnet test test/DingFood.Tests` verde
- [ ] Entidade nova classificada em `OperationalScopes` (ou com coluna de tenant / FK de agregado)
- [ ] `DbSet` declarado no `AppDbContext`
- [ ] Registro em `Infrastructure/DependencyInjection.cs`
- [ ] Migration gerada, `Up()` revisado, três arquivos commitados
- [ ] `Error.Code` com sufixo que produz o HTTP status pretendido
- [ ] Controller novo avaliado para entrada em `FeatureAccessConvention`
