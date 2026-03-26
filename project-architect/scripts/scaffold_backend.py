#!/usr/bin/env python3
"""
Scaffold Generator for .NET Clean Architecture Backend
Generates a complete DDD solution structure with all layers.

Usage:
    python scaffold_backend.py --name MyApp --output ./output --db sqlserver
"""

import argparse
import os
from pathlib import Path

def create_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Created: {path}")

def scaffold(name: str, output: str, db: str = "sqlserver", entities: list[str] = None):
    if entities is None:
        entities = ["Task", "Project"]

    base = Path(output) / name
    src = base / "src"
    tests = base / "tests"

    print(f"\n🏗️  Scaffolding {name} Backend (Clean Architecture + DDD)")
    print(f"   Database: {db}")
    print(f"   Entities: {', '.join(entities)}")
    print(f"   Output: {base}\n")

    # ========== Solution File ==========
    create_file(str(base / f"{name}.sln"), generate_sln(name))
    create_file(str(base / ".gitignore"), generate_gitignore())

    # ========== Domain Layer ==========
    domain = src / f"{name}.Domain"
    create_file(str(domain / f"{name}.Domain.csproj"), generate_domain_csproj())
    create_file(str(domain / "Common" / "Entity.cs"), generate_entity_base(name))
    create_file(str(domain / "Common" / "IDomainEvent.cs"), generate_domain_event_interface(name))
    create_file(str(domain / "Common" / "DomainException.cs"), generate_domain_exceptions(name))
    create_file(str(domain / "Interfaces" / "IRepository.cs"), generate_repository_interfaces(name, entities))
    create_file(str(domain / "Interfaces" / "IUnitOfWork.cs"), generate_unit_of_work(name))

    for entity in entities:
        create_file(str(domain / "Entities" / f"{entity}.cs"), generate_entity_placeholder(name, entity))

    # ========== Application Layer ==========
    app = src / f"{name}.Application"
    create_file(str(app / f"{name}.Application.csproj"), generate_application_csproj(name))
    create_file(str(app / "ApplicationServiceRegistration.cs"), generate_app_registration(name))
    create_file(str(app / "Common" / "Models" / "Result.cs"), generate_result_pattern(name))
    create_file(str(app / "Common" / "Behaviors" / "ValidationBehavior.cs"), generate_validation_behavior(name))
    create_file(str(app / "Common" / "Behaviors" / "LoggingBehavior.cs"), generate_logging_behavior(name))
    create_file(str(app / "Common" / "Behaviors" / "PerformanceBehavior.cs"), generate_performance_behavior(name))
    create_file(str(app / "Common" / "Interfaces" / "ICurrentUserService.cs"), generate_current_user_interface(name))
    create_file(str(app / "Common" / "Helpers" / "InputSanitizer.cs"), generate_input_sanitizer(name))

    for entity in entities:
        create_file(str(app / "Features" / f"{entity}s" / "Commands" / f"Create{entity}Command.cs"),
                    generate_create_command(name, entity))
        create_file(str(app / "Features" / f"{entity}s" / "Queries" / f"Get{entity}sQuery.cs"),
                    generate_get_query(name, entity))

    # ========== Infrastructure Layer ==========
    infra = src / f"{name}.Infrastructure"
    create_file(str(infra / f"{name}.Infrastructure.csproj"), generate_infrastructure_csproj(name, db))
    create_file(str(infra / "InfrastructureServiceRegistration.cs"), generate_infra_registration(name, db))
    create_file(str(infra / "Persistence" / "AppDbContext.cs"), generate_dbcontext(name, entities))
    create_file(str(infra / "Persistence" / "Repositories" / "Repository.cs"), generate_generic_repository(name))

    # ========== API Layer ==========
    api = src / f"{name}.API"
    create_file(str(api / f"{name}.API.csproj"), generate_api_csproj(name))
    create_file(str(api / "Program.cs"), generate_program_cs(name))
    create_file(str(api / "Controllers" / "ApiController.cs"), generate_api_controller_base(name))
    create_file(str(api / "Middleware" / "GlobalExceptionMiddleware.cs"), generate_exception_middleware(name))
    create_file(str(api / "Services" / "CurrentUserService.cs"), generate_current_user_service(name))
    create_file(str(api / "appsettings.json"), generate_appsettings(name, db))
    create_file(str(api / "appsettings.Development.json"), generate_appsettings_dev())

    for entity in entities:
        create_file(str(api / "Controllers" / f"{entity}sController.cs"),
                    generate_controller(name, entity))

    # ========== Test Projects ==========
    create_file(str(tests / f"{name}.Domain.Tests" / f"{name}.Domain.Tests.csproj"), generate_test_csproj(name, "Domain"))
    create_file(str(tests / f"{name}.Application.Tests" / f"{name}.Application.Tests.csproj"), generate_test_csproj(name, "Application"))

    print(f"\n✅ Backend scaffold complete!")
    print(f"   Next steps:")
    print(f"   1. cd {base}")
    print(f"   2. dotnet restore")
    print(f"   3. dotnet build")
    print(f"   4. Add your entity properties and business logic")
    print(f"   5. dotnet ef migrations add InitialCreate -p src/{name}.Infrastructure -s src/{name}.API")


# ==================== GENERATORS ====================

def generate_sln(name):
    return f"""Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
# Generated by project-architect skill
"""

def generate_gitignore():
    return """bin/
obj/
.vs/
*.user
*.suo
appsettings.*.local.json
"""

def generate_domain_csproj():
    return """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="MediatR.Contracts" Version="2.*" />
  </ItemGroup>
</Project>"""

def generate_entity_base(name):
    return f"""namespace {name}.Domain.Common;

public abstract class Entity
{{
    private readonly List<IDomainEvent> _domainEvents = new();

    public Guid Id {{ get; protected set; }}
    public DateTime CreatedAt {{ get; protected set; }}
    public DateTime? UpdatedAt {{ get; protected set; }}

    public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    protected Entity()
    {{
        Id = Guid.NewGuid();
        CreatedAt = DateTime.UtcNow;
    }}

    public void AddDomainEvent(IDomainEvent domainEvent) => _domainEvents.Add(domainEvent);
    public void RemoveDomainEvent(IDomainEvent domainEvent) => _domainEvents.Remove(domainEvent);
    public void ClearDomainEvents() => _domainEvents.Clear();

    protected void SetUpdated() => UpdatedAt = DateTime.UtcNow;
}}"""

def generate_domain_event_interface(name):
    return f"""namespace {name}.Domain.Common;

public interface IDomainEvent : MediatR.INotification
{{
    DateTime OccurredOn {{ get; }}
}}

public abstract record BaseDomainEvent : IDomainEvent
{{
    public DateTime OccurredOn {{ get; }} = DateTime.UtcNow;
}}"""

def generate_domain_exceptions(name):
    return f"""namespace {name}.Domain.Common;

public class DomainException : Exception
{{
    public DomainException(string message) : base(message) {{ }}
}}

public class NotFoundException : Exception
{{
    public NotFoundException(string entity, object key)
        : base($"Entity \\"{{entity}}\\" ({{key}}) was not found.") {{ }}
}}"""

def generate_repository_interfaces(name, entities):
    interfaces = f"""using {name}.Domain.Common;

namespace {name}.Domain.Interfaces;

public interface IRepository<T> where T : Entity
{{
    Task<T?> GetByIdAsync(Guid id, CancellationToken ct = default);
    Task<List<T>> GetAllAsync(CancellationToken ct = default);
    Task AddAsync(T entity, CancellationToken ct = default);
    void Update(T entity);
    void Remove(T entity);
}}
"""
    for entity in entities:
        interfaces += f"""
public interface I{entity}Repository : IRepository<Entities.{entity}>
{{
    Task<(List<Entities.{entity}> Items, int TotalCount)> GetPagedAsync(
        int page, int pageSize, CancellationToken ct = default);
}}
"""
    return interfaces

def generate_unit_of_work(name):
    return f"""namespace {name}.Domain.Interfaces;

public interface IUnitOfWork
{{
    Task<int> SaveChangesAsync(CancellationToken ct = default);
}}"""

def generate_entity_placeholder(name, entity):
    return f"""using {name}.Domain.Common;

namespace {name}.Domain.Entities;

public class {entity} : Entity
{{
    public string Name {{ get; private set; }} = null!;
    // TODO: Add your properties here

    private {entity}() {{ }} // EF Core

    public static {entity} Create(string name)
    {{
        if (string.IsNullOrWhiteSpace(name))
            throw new DomainException("{entity} name cannot be empty.");

        return new {entity}
        {{
            Name = name.Trim()
        }};
    }}

    public void UpdateName(string name)
    {{
        if (string.IsNullOrWhiteSpace(name))
            throw new DomainException("{entity} name cannot be empty.");

        Name = name.Trim();
        SetUpdated();
    }}
}}"""

def generate_application_csproj(name):
    return f"""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="MediatR" Version="12.*" />
    <PackageReference Include="FluentValidation" Version="11.*" />
    <PackageReference Include="FluentValidation.DependencyInjectionExtensions" Version="11.*" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\\{name}.Domain\\{name}.Domain.csproj" />
  </ItemGroup>
</Project>"""

def generate_app_registration(name):
    return f"""using FluentValidation;
using MediatR;
using {name}.Application.Common.Behaviors;
using Microsoft.Extensions.DependencyInjection;

namespace {name}.Application;

public static class ApplicationServiceRegistration
{{
    public static IServiceCollection AddApplicationServices(this IServiceCollection services)
    {{
        services.AddMediatR(cfg =>
            cfg.RegisterServicesFromAssembly(typeof(ApplicationServiceRegistration).Assembly));

        services.AddValidatorsFromAssembly(typeof(ApplicationServiceRegistration).Assembly);

        services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
        services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
        services.AddTransient(typeof(IPipelineBehavior<,>), typeof(PerformanceBehavior<,>));

        return services;
    }}
}}"""

def generate_result_pattern(name):
    return f"""namespace {name}.Application.Common.Models;

public class Result
{{
    public bool IsSuccess {{ get; }}
    public string? Error {{ get; }}
    public ResultType Type {{ get; }}

    protected Result(bool isSuccess, string? error, ResultType type)
    {{
        IsSuccess = isSuccess;
        Error = error;
        Type = type;
    }}

    public static Result Success() => new(true, null, ResultType.Ok);
    public static Result Failure(string error) => new(false, error, ResultType.Failure);
    public static Result NotFound(string error) => new(false, error, ResultType.NotFound);
    public static Result Forbidden(string error) => new(false, error, ResultType.Forbidden);
    public static Result ValidationError(string error) => new(false, error, ResultType.Validation);
}}

public class Result<T> : Result
{{
    public T? Value {{ get; }}

    private Result(T? value, bool isSuccess, string? error, ResultType type)
        : base(isSuccess, error, type) => Value = value;

    public static Result<T> Success(T value) => new(value, true, null, ResultType.Ok);
    public new static Result<T> Failure(string error) => new(default, false, error, ResultType.Failure);
    public new static Result<T> NotFound(string error) => new(default, false, error, ResultType.NotFound);
    public new static Result<T> Forbidden(string error) => new(default, false, error, ResultType.Forbidden);
    public new static Result<T> ValidationError(string error) => new(default, false, error, ResultType.Validation);
}}

public enum ResultType
{{
    Ok,
    Failure,
    NotFound,
    Forbidden,
    Validation
}}

public record PaginatedResult<T>(
    List<T> Items,
    int TotalCount,
    int PageNumber,
    int PageSize)
{{
    public int TotalPages => (TotalCount + PageSize - 1) / PageSize;
    public bool HasPreviousPage => PageNumber > 1;
    public bool HasNextPage => PageNumber < TotalPages;
}}"""

def generate_validation_behavior(name):
    return f"""using FluentValidation;
using MediatR;

namespace {name}.Application.Common.Behaviors;

public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{{
    private readonly IEnumerable<IValidator<TRequest>> _validators;

    public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators)
        => _validators = validators;

    public async Task<TResponse> Handle(
        TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {{
        if (!_validators.Any()) return await next();

        var context = new ValidationContext<TRequest>(request);
        var failures = (await Task.WhenAll(
            _validators.Select(v => v.ValidateAsync(context, ct))))
            .SelectMany(r => r.Errors)
            .Where(f => f != null)
            .ToList();

        if (failures.Count > 0)
            throw new ValidationException(failures);

        return await next();
    }}
}}"""

def generate_logging_behavior(name):
    return f"""using MediatR;
using Microsoft.Extensions.Logging;
using {name}.Application.Common.Interfaces;

namespace {name}.Application.Common.Behaviors;

public class LoggingBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{{
    private readonly ILogger<LoggingBehavior<TRequest, TResponse>> _logger;
    private readonly ICurrentUserService _currentUser;

    public LoggingBehavior(
        ILogger<LoggingBehavior<TRequest, TResponse>> logger,
        ICurrentUserService currentUser)
    {{
        _logger = logger;
        _currentUser = currentUser;
    }}

    public async Task<TResponse> Handle(
        TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {{
        var requestName = typeof(TRequest).Name;
        _logger.LogInformation("[START] {{RequestName}} | UserId: {{UserId}}",
            requestName, _currentUser.UserId);

        var response = await next();

        _logger.LogInformation("[END] {{RequestName}} | UserId: {{UserId}}",
            requestName, _currentUser.UserId);

        return response;
    }}
}}"""

def generate_performance_behavior(name):
    return f"""using System.Diagnostics;
using MediatR;
using Microsoft.Extensions.Logging;

namespace {name}.Application.Common.Behaviors;

public class PerformanceBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{{
    private readonly ILogger<PerformanceBehavior<TRequest, TResponse>> _logger;
    private readonly Stopwatch _timer = new();
    private const int ThresholdMs = 500;

    public PerformanceBehavior(ILogger<PerformanceBehavior<TRequest, TResponse>> logger)
        => _logger = logger;

    public async Task<TResponse> Handle(
        TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {{
        _timer.Start();
        var response = await next();
        _timer.Stop();

        if (_timer.ElapsedMilliseconds > ThresholdMs)
        {{
            _logger.LogWarning("[PERF] {{RequestName}} took {{Elapsed}}ms",
                typeof(TRequest).Name, _timer.ElapsedMilliseconds);
        }}

        return response;
    }}
}}"""

def generate_current_user_interface(name):
    return f"""namespace {name}.Application.Common.Interfaces;

public interface ICurrentUserService
{{
    Guid? UserId {{ get; }}
    Guid? CompanyId {{ get; }}
    string? Email {{ get; }}
    string? Role {{ get; }}
    bool IsAuthenticated {{ get; }}
}}

public interface ITokenService
{{
    string GenerateToken(Guid userId, string email, string role, Guid? companyId);
}}

public interface IPasswordHasher
{{
    string Hash(string password);
    bool Verify(string password, string hash);
}}"""

def generate_input_sanitizer(name):
    return f"""namespace {name}.Application.Common.Helpers;

public static class InputSanitizer
{{
    public static string Sanitize(string? input) =>
        string.IsNullOrWhiteSpace(input)
            ? string.Empty
            : System.Net.WebUtility.HtmlEncode(input.Trim());

    public static string? SanitizeNullable(string? input) =>
        input is null ? null : Sanitize(input);
}}"""

def generate_create_command(name, entity):
    return f"""using MediatR;
using {name}.Application.Common.Models;
using {name}.Application.Common.Helpers;
using {name}.Domain.Interfaces;
using {name}.Domain.Entities;
using FluentValidation;

namespace {name}.Application.Features.{entity}s.Commands;

public record Create{entity}Command(string Name) : IRequest<Result<Guid>>;

public class Create{entity}CommandValidator : AbstractValidator<Create{entity}Command>
{{
    public Create{entity}CommandValidator()
    {{
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Name is required.")
            .MaximumLength(200).WithMessage("Name must not exceed 200 characters.");
    }}
}}

public class Create{entity}CommandHandler : IRequestHandler<Create{entity}Command, Result<Guid>>
{{
    private readonly I{entity}Repository _repo;
    private readonly IUnitOfWork _uow;

    public Create{entity}CommandHandler(I{entity}Repository repo, IUnitOfWork uow)
    {{
        _repo = repo;
        _uow = uow;
    }}

    public async Task<Result<Guid>> Handle(Create{entity}Command request, CancellationToken ct)
    {{
        var entity = {entity}.Create(InputSanitizer.Sanitize(request.Name));
        await _repo.AddAsync(entity, ct);
        await _uow.SaveChangesAsync(ct);
        return Result<Guid>.Success(entity.Id);
    }}
}}"""

def generate_get_query(name, entity):
    return f"""using MediatR;
using {name}.Application.Common.Models;
using {name}.Domain.Interfaces;

namespace {name}.Application.Features.{entity}s.Queries;

public record {entity}Dto(Guid Id, string Name, DateTime CreatedAt);

public record Get{entity}sQuery(int PageNumber = 1, int PageSize = 20)
    : IRequest<Result<PaginatedResult<{entity}Dto>>>;

public class Get{entity}sQueryHandler
    : IRequestHandler<Get{entity}sQuery, Result<PaginatedResult<{entity}Dto>>>
{{
    private readonly I{entity}Repository _repo;

    public Get{entity}sQueryHandler(I{entity}Repository repo) => _repo = repo;

    public async Task<Result<PaginatedResult<{entity}Dto>>> Handle(
        Get{entity}sQuery request, CancellationToken ct)
    {{
        var (items, total) = await _repo.GetPagedAsync(
            request.PageNumber, request.PageSize, ct);

        var dtos = items.Select(e => new {entity}Dto(e.Id, e.Name, e.CreatedAt)).ToList();

        return Result<PaginatedResult<{entity}Dto>>.Success(
            new PaginatedResult<{entity}Dto>(dtos, total, request.PageNumber, request.PageSize));
    }}
}}"""

def generate_infrastructure_csproj(name, db):
    db_pkg = "Microsoft.EntityFrameworkCore.SqlServer" if db == "sqlserver" else "Npgsql.EntityFrameworkCore.PostgreSQL"
    return f"""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="9.*" />
    <PackageReference Include="{db_pkg}" Version="9.*" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="9.*" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\\{name}.Domain\\{name}.Domain.csproj" />
    <ProjectReference Include="..\\{name}.Application\\{name}.Application.csproj" />
  </ItemGroup>
</Project>"""

def generate_infra_registration(name, db):
    use_method = "UseSqlServer" if db == "sqlserver" else "UseNpgsql"
    return f"""using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using {name}.Domain.Interfaces;
using {name}.Infrastructure.Persistence;
using {name}.Infrastructure.Persistence.Repositories;

namespace {name}.Infrastructure;

public static class InfrastructureServiceRegistration
{{
    public static IServiceCollection AddInfrastructureServices(
        this IServiceCollection services, IConfiguration configuration)
    {{
        services.AddDbContext<AppDbContext>(options =>
            options.{use_method}(
                configuration.GetConnectionString("DefaultConnection"),
                b => b.MigrationsAssembly(typeof(AppDbContext).Assembly.FullName)));

        services.AddScoped<IUnitOfWork>(sp => sp.GetRequiredService<AppDbContext>());
        services.AddScoped(typeof(IRepository<>), typeof(Repository<>));

        return services;
    }}
}}"""

def generate_dbcontext(name, entities):
    dbsets = "\n".join([f"    public DbSet<{e}> {e}s => Set<{e}>();" for e in entities])
    return f"""using MediatR;
using Microsoft.EntityFrameworkCore;
using {name}.Domain.Common;
using {name}.Domain.Entities;
using {name}.Domain.Interfaces;

namespace {name}.Infrastructure.Persistence;

public class AppDbContext : DbContext, IUnitOfWork
{{
    private readonly IMediator _mediator;

    public AppDbContext(DbContextOptions<AppDbContext> options, IMediator mediator)
        : base(options) => _mediator = mediator;

{dbsets}

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {{
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
        base.OnModelCreating(modelBuilder);
    }}

    public override async Task<int> SaveChangesAsync(CancellationToken ct = default)
    {{
        var entities = ChangeTracker.Entries<Entity>()
            .Where(e => e.Entity.DomainEvents.Any())
            .Select(e => e.Entity)
            .ToList();

        var domainEvents = entities.SelectMany(e => e.DomainEvents).ToList();
        entities.ForEach(e => e.ClearDomainEvents());

        foreach (var domainEvent in domainEvents)
            await _mediator.Publish(domainEvent, ct);

        return await base.SaveChangesAsync(ct);
    }}
}}"""

def generate_generic_repository(name):
    return f"""using Microsoft.EntityFrameworkCore;
using {name}.Domain.Common;
using {name}.Domain.Interfaces;

namespace {name}.Infrastructure.Persistence.Repositories;

public class Repository<T> : IRepository<T> where T : Entity
{{
    protected readonly AppDbContext _context;
    protected readonly DbSet<T> _dbSet;

    public Repository(AppDbContext context)
    {{
        _context = context;
        _dbSet = context.Set<T>();
    }}

    public async Task<T?> GetByIdAsync(Guid id, CancellationToken ct = default)
        => await _dbSet.FindAsync(new object[] {{ id }}, ct);

    public async Task<List<T>> GetAllAsync(CancellationToken ct = default)
        => await _dbSet.ToListAsync(ct);

    public async Task AddAsync(T entity, CancellationToken ct = default)
        => await _dbSet.AddAsync(entity, ct);

    public void Update(T entity) => _dbSet.Update(entity);

    public void Remove(T entity) => _dbSet.Remove(entity);
}}"""

def generate_api_csproj(name):
    return f"""<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="9.*" />
    <PackageReference Include="Swashbuckle.AspNetCore" Version="7.*" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\\{name}.Application\\{name}.Application.csproj" />
    <ProjectReference Include="..\\{name}.Infrastructure\\{name}.Infrastructure.csproj" />
  </ItemGroup>
</Project>"""

def generate_program_cs(name):
    return f"""using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using {name}.Application;
using {name}.Application.Common.Interfaces;
using {name}.Infrastructure;
using {name}.API.Middleware;
using {name}.API.Services;

var builder = WebApplication.CreateBuilder(args);

// Clean Architecture DI
builder.Services.AddApplicationServices();
builder.Services.AddInfrastructureServices(builder.Configuration);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// JWT Authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {{
        options.TokenValidationParameters = new TokenValidationParameters
        {{
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!))
        }};
    }});

// CORS
builder.Services.AddCors(options =>
{{
    options.AddDefaultPolicy(policy =>
    {{
        policy.WithOrigins(builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>()!)
            .AllowAnyMethod()
            .AllowAnyHeader()
            .AllowCredentials();
    }});
}});

builder.Services.AddHttpContextAccessor();
builder.Services.AddScoped<ICurrentUserService, CurrentUserService>();

var app = builder.Build();

app.UseMiddleware<GlobalExceptionMiddleware>();

if (app.Environment.IsDevelopment())
{{
    app.UseSwagger();
    app.UseSwaggerUI();
}}

app.UseHttpsRedirection();
app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();"""

def generate_api_controller_base(name):
    return f"""using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using {name}.Application.Common.Models;

namespace {name}.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public abstract class ApiController : ControllerBase
{{
    protected IMediator Mediator =>
        HttpContext.RequestServices.GetRequiredService<IMediator>();

    protected IActionResult Problem(Result result)
    {{
        if (result.IsSuccess) return Ok();

        var statusCode = result.Type switch
        {{
            ResultType.NotFound => StatusCodes.Status404NotFound,
            ResultType.Forbidden => StatusCodes.Status403Forbidden,
            ResultType.Validation => StatusCodes.Status422UnprocessableEntity,
            _ => StatusCodes.Status500InternalServerError
        }};

        return Problem(statusCode: statusCode, title: result.Error);
    }}

    protected IActionResult Problem<T>(Result<T> result)
    {{
        if (result.IsSuccess) return Ok(result.Value);
        return Problem((Result)result);
    }}
}}"""

def generate_exception_middleware(name):
    return f"""using System.Diagnostics;
using FluentValidation;
using {name}.Domain.Common;

namespace {name}.API.Middleware;

public class GlobalExceptionMiddleware
{{
    private readonly RequestDelegate _next;
    private readonly ILogger<GlobalExceptionMiddleware> _logger;
    private readonly IHostEnvironment _env;

    public GlobalExceptionMiddleware(
        RequestDelegate next,
        ILogger<GlobalExceptionMiddleware> logger,
        IHostEnvironment env)
    {{
        _next = next;
        _logger = logger;
        _env = env;
    }}

    public async Task InvokeAsync(HttpContext context)
    {{
        try
        {{
            await _next(context);
        }}
        catch (OperationCanceledException) when (context.RequestAborted.IsCancellationRequested)
        {{
            _logger.LogInformation("Request cancelled by client.");
            context.Response.StatusCode = 499;
        }}
        catch (ValidationException ex)
        {{
            context.Response.StatusCode = StatusCodes.Status422UnprocessableEntity;
            await context.Response.WriteAsJsonAsync(new
            {{
                status = 422,
                title = "Validation Error",
                detail = string.Join("; ", ex.Errors.Select(e => e.ErrorMessage))
            }});
        }}
        catch (DomainException ex)
        {{
            context.Response.StatusCode = StatusCodes.Status400BadRequest;
            await context.Response.WriteAsJsonAsync(new
            {{
                status = 400,
                title = "Business Rule Violation",
                detail = ex.Message
            }});
        }}
        catch (NotFoundException ex)
        {{
            context.Response.StatusCode = StatusCodes.Status404NotFound;
            await context.Response.WriteAsJsonAsync(new
            {{
                status = 404,
                title = "Not Found",
                detail = ex.Message
            }});
        }}
        catch (Exception ex)
        {{
            var traceId = Activity.Current?.Id ?? context.TraceIdentifier;
            _logger.LogError(ex, "Unhandled exception. TraceId: {{TraceId}}", traceId);

            context.Response.StatusCode = StatusCodes.Status500InternalServerError;
            await context.Response.WriteAsJsonAsync(new
            {{
                status = 500,
                title = "Internal Server Error",
                detail = _env.IsDevelopment() ? ex.ToString() : $"TraceId: {{traceId}}"
            }});
        }}
    }}
}}"""

def generate_current_user_service(name):
    return f"""using System.Security.Claims;
using {name}.Application.Common.Interfaces;

namespace {name}.API.Services;

public class CurrentUserService : ICurrentUserService
{{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public CurrentUserService(IHttpContextAccessor httpContextAccessor)
        => _httpContextAccessor = httpContextAccessor;

    private ClaimsPrincipal? User => _httpContextAccessor.HttpContext?.User;

    public Guid? UserId => Guid.TryParse(
        User?.FindFirstValue(ClaimTypes.NameIdentifier), out var id) ? id : null;

    public Guid? CompanyId => Guid.TryParse(
        User?.FindFirstValue("CompanyId"), out var id) ? id : null;

    public string? Email => User?.FindFirstValue(ClaimTypes.Email);
    public string? Role => User?.FindFirstValue(ClaimTypes.Role);
    public bool IsAuthenticated => User?.Identity?.IsAuthenticated ?? false;
}}"""

def generate_controller(name, entity):
    return f"""using Microsoft.AspNetCore.Mvc;
using {name}.Application.Features.{entity}s.Commands;
using {name}.Application.Features.{entity}s.Queries;

namespace {name}.API.Controllers;

public class {entity}sController : ApiController
{{
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] Create{entity}Command command, CancellationToken ct)
    {{
        var result = await Mediator.Send(command, ct);
        return result.IsSuccess
            ? CreatedAtAction(nameof(GetById), new {{ id = result.Value }}, result.Value)
            : Problem(result);
    }}

    [HttpGet("{{id:guid}}")]
    public async Task<IActionResult> GetById(Guid id, CancellationToken ct)
    {{
        // TODO: Implement GetByIdQuery
        return Ok();
    }}

    [HttpGet]
    public async Task<IActionResult> GetAll(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20,
        CancellationToken ct = default)
    {{
        var result = await Mediator.Send(new Get{entity}sQuery(page, pageSize), ct);
        return Problem(result);
    }}
}}"""

def generate_appsettings(name, db):
    conn = "Server=localhost;Database={0};Trusted_Connection=true;TrustServerCertificate=true;".format(name) if db == "sqlserver" else "Host=localhost;Database={0};Username=postgres;Password=postgres".format(name)
    return f"""{{
  "ConnectionStrings": {{
    "DefaultConnection": "{conn}"
  }},
  "Jwt": {{
    "Key": "YOUR-SECRET-KEY-CHANGE-THIS-IN-PRODUCTION-MINIMUM-32-CHARS",
    "Issuer": "{name}API",
    "Audience": "{name}Client",
    "ExpirationInHours": 24
  }},
  "Cors": {{
    "AllowedOrigins": ["http://localhost:5173", "http://localhost:3000"]
  }},
  "Logging": {{
    "LogLevel": {{
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }}
  }}
}}"""

def generate_appsettings_dev():
    return """{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft.AspNetCore": "Information"
    }
  }
}"""

def generate_test_csproj(name, layer):
    return f"""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.*" />
    <PackageReference Include="xunit" Version="2.*" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.*" />
    <PackageReference Include="Moq" Version="4.*" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\\..\\src\\{name}.{layer}\\{name}.{layer}.csproj" />
  </ItemGroup>
</Project>"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold .NET Clean Architecture Backend")
    parser.add_argument("--name", required=True, help="Project name (e.g., MyApp)")
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument("--db", default="sqlserver", choices=["sqlserver", "postgresql"], help="Database provider")
    parser.add_argument("--entities", nargs="+", default=["Task", "Project"], help="Entity names")
    args = parser.parse_args()

    scaffold(args.name, args.output, args.db, args.entities)
