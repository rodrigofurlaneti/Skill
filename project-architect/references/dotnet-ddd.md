# .NET DDD + Clean Architecture Reference

This reference contains all the code patterns and templates for generating a production-grade .NET backend following DDD, Clean Architecture, SOLID, and Repository Pattern.

## Table of Contents

1. [Domain Layer](#domain-layer)
2. [Application Layer](#application-layer)
3. [Infrastructure Layer](#infrastructure-layer)
4. [API Layer](#api-layer)
5. [Configuration](#configuration)
6. [Testing Patterns](#testing-patterns)

---

## Domain Layer

The domain layer is the heart of the application. It contains entities, value objects, domain events, enumerations, and repository interfaces. It has ZERO external dependencies — no NuGet packages except basic .NET abstractions.

### Entity Base Class

Every entity inherits from this base. It provides identity, audit fields, and domain event support.

```csharp
namespace {Name}.Domain.Common;

public abstract class Entity
{
    private readonly List<IDomainEvent> _domainEvents = new();

    public Guid Id { get; protected set; }
    public DateTime CreatedAt { get; protected set; }
    public DateTime? UpdatedAt { get; protected set; }

    public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    protected Entity()
    {
        Id = Guid.NewGuid();
        CreatedAt = DateTime.UtcNow;
    }

    public void AddDomainEvent(IDomainEvent domainEvent) => _domainEvents.Add(domainEvent);
    public void RemoveDomainEvent(IDomainEvent domainEvent) => _domainEvents.Remove(domainEvent);
    public void ClearDomainEvents() => _domainEvents.Clear();

    protected void SetUpdated() => UpdatedAt = DateTime.UtcNow;
}
```

### Domain Events Interface

```csharp
namespace {Name}.Domain.Common;

public interface IDomainEvent : MediatR.INotification
{
    DateTime OccurredOn { get; }
}

public abstract record BaseDomainEvent : IDomainEvent
{
    public DateTime OccurredOn { get; } = DateTime.UtcNow;
}
```

### Rich Entity Example (NOT Anemic)

Entities must contain business logic. The entity controls its own state transitions and validates its own invariants. External code cannot set properties directly — it must call behavior methods.

```csharp
namespace {Name}.Domain.Entities;

public class TaskItem : Entity
{
    public string Title { get; private set; } = null!;
    public string? Description { get; private set; }
    public TaskStatus Status { get; private set; }
    public Priority Priority { get; private set; }
    public DateTime? DueDate { get; private set; }
    public DateTime? CompletedAt { get; private set; }
    public Guid ProjectId { get; private set; }
    public Guid? AssigneeId { get; private set; }

    private TaskItem() { } // EF Core constructor

    // Factory method — the ONLY way to create a TaskItem
    public static TaskItem Create(
        string title,
        Guid projectId,
        Priority priority = Priority.Medium,
        string? description = null,
        DateTime? dueDate = null)
    {
        if (string.IsNullOrWhiteSpace(title))
            throw new DomainException("Task title cannot be empty.");

        if (dueDate.HasValue && dueDate.Value < DateTime.UtcNow.Date)
            throw new DomainException("Due date cannot be in the past.");

        var task = new TaskItem
        {
            Title = title.Trim(),
            Description = description?.Trim(),
            ProjectId = projectId,
            Priority = priority,
            Status = TaskStatus.Pending,
            DueDate = dueDate
        };

        task.AddDomainEvent(new TaskCreatedEvent(task.Id, projectId));
        return task;
    }

    // Behavior methods — business logic lives HERE
    public void Complete()
    {
        if (Status == TaskStatus.Completed)
            throw new DomainException("Task is already completed.");

        Status = TaskStatus.Completed;
        CompletedAt = DateTime.UtcNow;
        SetUpdated();
        AddDomainEvent(new TaskCompletedEvent(Id, ProjectId));
    }

    public void AssignTo(Guid userId)
    {
        AssigneeId = userId;
        SetUpdated();
    }

    public void UpdatePriority(Priority newPriority)
    {
        if (Status == TaskStatus.Completed)
            throw new DomainException("Cannot change priority of completed task.");

        Priority = newPriority;
        SetUpdated();
    }

    public void UpdateDetails(string title, string? description, DateTime? dueDate)
    {
        if (string.IsNullOrWhiteSpace(title))
            throw new DomainException("Task title cannot be empty.");

        Title = title.Trim();
        Description = description?.Trim();
        DueDate = dueDate;
        SetUpdated();
    }

    public bool IsOverdue => DueDate.HasValue
        && DueDate.Value < DateTime.UtcNow
        && Status != TaskStatus.Completed;
}
```

### Value Objects

Value Objects represent concepts that are defined by their attributes, not by identity. They are immutable and self-validating.

```csharp
namespace {Name}.Domain.ValueObjects;

public sealed record Email
{
    public string Value { get; }

    private Email(string value) => Value = value;

    public static Email Create(string email)
    {
        if (string.IsNullOrWhiteSpace(email))
            throw new DomainException("Email cannot be empty.");

        email = email.Trim().ToLowerInvariant();

        if (!email.Contains('@') || !email.Contains('.'))
            throw new DomainException($"'{email}' is not a valid email address.");

        return new Email(email);
    }

    // Allows implicit conversion: string email = myEmailVO;
    public static implicit operator string(Email email) => email.Value;

    public override string ToString() => Value;
}
```

### Domain Exceptions

```csharp
namespace {Name}.Domain.Common;

public class DomainException : Exception
{
    public DomainException(string message) : base(message) { }
}

public class NotFoundException : Exception
{
    public NotFoundException(string entity, object key)
        : base($"Entity \"{entity}\" ({key}) was not found.") { }
}
```

### Enumerations (Smart Enum Pattern)

```csharp
namespace {Name}.Domain.Enumerations;

public enum TaskStatus
{
    Pending,
    InProgress,
    InReview,
    Completed,
    Cancelled
}

public enum Priority
{
    Low,
    Medium,
    High,
    Critical
}

public enum MemberRole
{
    Member,
    Admin,
    Owner
}
```

### Repository Interfaces (in Domain)

Repository interfaces live in the Domain layer. Implementations live in Infrastructure. This is the Dependency Inversion Principle in action.

```csharp
namespace {Name}.Domain.Interfaces;

public interface IRepository<T> where T : Entity
{
    Task<T?> GetByIdAsync(Guid id, CancellationToken ct = default);
    Task<List<T>> GetAllAsync(CancellationToken ct = default);
    Task AddAsync(T entity, CancellationToken ct = default);
    void Update(T entity);
    void Remove(T entity);
}

public interface ITaskRepository : IRepository<TaskItem>
{
    Task<List<TaskItem>> GetByProjectAsync(Guid projectId, CancellationToken ct = default);
    Task<(List<TaskItem> Items, int TotalCount)> GetByProjectPagedAsync(
        Guid projectId, int page, int pageSize, CancellationToken ct = default);
    Task<List<TaskItem>> GetOverdueAsync(CancellationToken ct = default);
}

public interface IProjectRepository : IRepository<Project>
{
    Task<List<Project>> GetByCompanyAsync(Guid companyId, CancellationToken ct = default);
    Task<(List<Project> Items, int TotalCount)> GetByCompanyPagedAsync(
        Guid companyId, int page, int pageSize, CancellationToken ct = default);
}

public interface IUnitOfWork
{
    Task<int> SaveChangesAsync(CancellationToken ct = default);
}
```

---

## Application Layer

The application layer contains use cases (commands/queries), validators, DTOs, interfaces for external services, and pipeline behaviors. It references only the Domain layer.

### NuGet Packages

```xml
<ItemGroup>
    <PackageReference Include="MediatR" Version="12.*" />
    <PackageReference Include="FluentValidation" Version="11.*" />
    <PackageReference Include="FluentValidation.DependencyInjectionExtensions" Version="11.*" />
</ItemGroup>
```

### Result Pattern

Instead of throwing exceptions for expected business failures, use a Result type. This makes error handling explicit.

```csharp
namespace {Name}.Application.Common.Models;

public class Result
{
    public bool IsSuccess { get; }
    public string? Error { get; }
    public ResultType Type { get; }

    protected Result(bool isSuccess, string? error, ResultType type)
    {
        IsSuccess = isSuccess;
        Error = error;
        Type = type;
    }

    public static Result Success() => new(true, null, ResultType.Ok);
    public static Result Failure(string error) => new(false, error, ResultType.Failure);
    public static Result NotFound(string error) => new(false, error, ResultType.NotFound);
    public static Result Forbidden(string error) => new(false, error, ResultType.Forbidden);
    public static Result ValidationError(string error) => new(false, error, ResultType.Validation);
}

public class Result<T> : Result
{
    public T? Value { get; }

    private Result(T? value, bool isSuccess, string? error, ResultType type)
        : base(isSuccess, error, type) => Value = value;

    public static Result<T> Success(T value) => new(value, true, null, ResultType.Ok);
    public new static Result<T> Failure(string error) => new(default, false, error, ResultType.Failure);
    public new static Result<T> NotFound(string error) => new(default, false, error, ResultType.NotFound);
    public new static Result<T> Forbidden(string error) => new(default, false, error, ResultType.Forbidden);
    public new static Result<T> ValidationError(string error) => new(default, false, error, ResultType.Validation);
}

public enum ResultType
{
    Ok,
    Failure,
    NotFound,
    Forbidden,
    Validation
}

public record PaginatedResult<T>(
    List<T> Items,
    int TotalCount,
    int PageNumber,
    int PageSize)
{
    public int TotalPages => (TotalCount + PageSize - 1) / PageSize;
    public bool HasPreviousPage => PageNumber > 1;
    public bool HasNextPage => PageNumber < TotalPages;
}
```

### CQRS — Commands

Commands change state. They return `Result` or `Result<T>`.

```csharp
namespace {Name}.Application.Features.Tasks.Commands;

// Command definition
public record CreateTaskCommand(
    string Title,
    string? Description,
    Guid ProjectId,
    string Priority,
    DateTime? DueDate) : IRequest<Result<Guid>>;

// Validator — ALWAYS validate commands
public class CreateTaskCommandValidator : AbstractValidator<CreateTaskCommand>
{
    public CreateTaskCommandValidator()
    {
        RuleFor(x => x.Title)
            .NotEmpty().WithMessage("Title is required.")
            .MaximumLength(200).WithMessage("Title must not exceed 200 characters.");

        RuleFor(x => x.ProjectId)
            .NotEmpty().WithMessage("Project is required.");

        RuleFor(x => x.Priority)
            .Must(p => Enum.TryParse<Priority>(p, true, out _))
            .WithMessage("Invalid priority value.");

        RuleFor(x => x.DueDate)
            .GreaterThan(DateTime.UtcNow.Date)
            .When(x => x.DueDate.HasValue)
            .WithMessage("Due date must be in the future.");
    }
}

// Handler
public class CreateTaskCommandHandler : IRequestHandler<CreateTaskCommand, Result<Guid>>
{
    private readonly ITaskRepository _taskRepo;
    private readonly IProjectRepository _projectRepo;
    private readonly IUnitOfWork _uow;
    private readonly ICurrentUserService _currentUser;

    public CreateTaskCommandHandler(
        ITaskRepository taskRepo,
        IProjectRepository projectRepo,
        IUnitOfWork uow,
        ICurrentUserService currentUser)
    {
        _taskRepo = taskRepo;
        _projectRepo = projectRepo;
        _uow = uow;
        _currentUser = currentUser;
    }

    public async Task<Result<Guid>> Handle(
        CreateTaskCommand request, CancellationToken ct)
    {
        var project = await _projectRepo.GetByIdAsync(request.ProjectId, ct);
        if (project is null)
            return Result<Guid>.NotFound("Project not found.");

        var priority = Enum.Parse<Priority>(request.Priority, true);

        var task = TaskItem.Create(
            InputSanitizer.Sanitize(request.Title),
            request.ProjectId,
            priority,
            InputSanitizer.SanitizeNullable(request.Description),
            request.DueDate);

        await _taskRepo.AddAsync(task, ct);
        await _uow.SaveChangesAsync(ct);

        return Result<Guid>.Success(task.Id);
    }
}
```

### CQRS — Queries

Queries read state. They return DTOs, never domain entities.

```csharp
namespace {Name}.Application.Features.Tasks.Queries;

// DTO
public record TaskDto(
    Guid Id,
    string Title,
    string? Description,
    string Status,
    string Priority,
    DateTime? DueDate,
    DateTime? CompletedAt,
    Guid ProjectId,
    Guid? AssigneeId,
    bool IsOverdue,
    DateTime CreatedAt);

// Query with pagination
public record GetProjectTasksQuery(
    Guid ProjectId,
    int PageNumber = 1,
    int PageSize = 20) : IRequest<Result<PaginatedResult<TaskDto>>>;

// Handler
public class GetProjectTasksQueryHandler
    : IRequestHandler<GetProjectTasksQuery, Result<PaginatedResult<TaskDto>>>
{
    private readonly ITaskRepository _taskRepo;

    public GetProjectTasksQueryHandler(ITaskRepository taskRepo)
        => _taskRepo = taskRepo;

    public async Task<Result<PaginatedResult<TaskDto>>> Handle(
        GetProjectTasksQuery request, CancellationToken ct)
    {
        var (items, total) = await _taskRepo.GetByProjectPagedAsync(
            request.ProjectId, request.PageNumber, request.PageSize, ct);

        var dtos = items.Select(t => new TaskDto(
            t.Id, t.Title, t.Description,
            t.Status.ToString(), t.Priority.ToString(),
            t.DueDate, t.CompletedAt, t.ProjectId,
            t.AssigneeId, t.IsOverdue, t.CreatedAt))
            .ToList();

        return Result<PaginatedResult<TaskDto>>.Success(
            new PaginatedResult<TaskDto>(dtos, total, request.PageNumber, request.PageSize));
    }
}
```

### Pipeline Behaviors

Pipeline behaviors intercept every MediatR request. They run in order: Validation → Logging → Performance.

```csharp
namespace {Name}.Application.Common.Behaviors;

// Validation — runs FluentValidation automatically for every command
public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly IEnumerable<IValidator<TRequest>> _validators;

    public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators)
        => _validators = validators;

    public async Task<TResponse> Handle(
        TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
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
    }
}

// Logging — logs request start/end with user context
public class LoggingBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly ILogger<LoggingBehavior<TRequest, TResponse>> _logger;
    private readonly ICurrentUserService _currentUser;

    public LoggingBehavior(
        ILogger<LoggingBehavior<TRequest, TResponse>> logger,
        ICurrentUserService currentUser)
    {
        _logger = logger;
        _currentUser = currentUser;
    }

    public async Task<TResponse> Handle(
        TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
        var requestName = typeof(TRequest).Name;
        var userId = _currentUser.UserId;

        _logger.LogInformation(
            "[START] {RequestName} | UserId: {UserId}",
            requestName, userId);

        var response = await next();

        _logger.LogInformation(
            "[END] {RequestName} | UserId: {UserId}",
            requestName, userId);

        return response;
    }
}

// Performance — warns when requests take too long
public class PerformanceBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly ILogger<PerformanceBehavior<TRequest, TResponse>> _logger;
    private readonly Stopwatch _timer = new();

    /// <summary>
    /// Threshold in milliseconds. Requests exceeding this are logged as warnings.
    /// Consider moving to IOptions{PerformanceSettings} for per-environment tuning.
    /// </summary>
    private const int ThresholdMs = 500;

    public PerformanceBehavior(ILogger<PerformanceBehavior<TRequest, TResponse>> logger)
        => _logger = logger;

    public async Task<TResponse> Handle(
        TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
        _timer.Start();
        var response = await next();
        _timer.Stop();

        if (_timer.ElapsedMilliseconds > ThresholdMs)
        {
            _logger.LogWarning(
                "[PERF] {RequestName} took {Elapsed}ms (threshold: {Threshold}ms)",
                typeof(TRequest).Name, _timer.ElapsedMilliseconds, ThresholdMs);
        }

        return response;
    }
}
```

### Application Service Interfaces

```csharp
namespace {Name}.Application.Common.Interfaces;

public interface ICurrentUserService
{
    Guid? UserId { get; }
    Guid? CompanyId { get; }
    string? Email { get; }
    string? Role { get; }
    bool IsAuthenticated { get; }
}

public interface ITokenService
{
    string GenerateToken(Guid userId, string email, string role, Guid? companyId);
    (Guid userId, string email)? ValidateToken(string token);
}

public interface IPasswordHasher
{
    string Hash(string password);
    bool Verify(string password, string hash);
}

public interface IDateTimeService
{
    DateTime UtcNow { get; }
}
```

### Application DI Registration

```csharp
namespace {Name}.Application;

public static class ApplicationServiceRegistration
{
    public static IServiceCollection AddApplicationServices(this IServiceCollection services)
    {
        services.AddMediatR(cfg =>
            cfg.RegisterServicesFromAssembly(typeof(ApplicationServiceRegistration).Assembly));

        services.AddValidatorsFromAssembly(typeof(ApplicationServiceRegistration).Assembly);

        services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
        services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
        services.AddTransient(typeof(IPipelineBehavior<,>), typeof(PerformanceBehavior<,>));

        return services;
    }
}
```

### Input Sanitizer

```csharp
namespace {Name}.Application.Common.Helpers;

public static class InputSanitizer
{
    public static string Sanitize(string? input) =>
        string.IsNullOrWhiteSpace(input)
            ? string.Empty
            : System.Net.WebUtility.HtmlEncode(input.Trim());

    public static string? SanitizeNullable(string? input) =>
        input is null ? null : Sanitize(input);
}
```

---

## Infrastructure Layer

The infrastructure layer implements all external concerns: database access, file storage, email, caching, etc. It references the Domain and Application layers.

### NuGet Packages

```xml
<ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="9.*" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="9.*" />
    <!-- OR for PostgreSQL: -->
    <!-- <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="9.*" /> -->
    <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="9.*" />
</ItemGroup>
```

### DbContext

```csharp
namespace {Name}.Infrastructure.Persistence;

public class AppDbContext : DbContext, IUnitOfWork
{
    private readonly IMediator _mediator;

    public AppDbContext(DbContextOptions<AppDbContext> options, IMediator mediator)
        : base(options) => _mediator = mediator;

    public DbSet<TaskItem> Tasks => Set<TaskItem>();
    public DbSet<Project> Projects => Set<Project>();
    // Add more DbSets per entity...

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(
            typeof(AppDbContext).Assembly);
        base.OnModelCreating(modelBuilder);
    }

    public override async Task<int> SaveChangesAsync(CancellationToken ct = default)
    {
        // Dispatch domain events before saving
        var entities = ChangeTracker.Entries<Entity>()
            .Where(e => e.Entity.DomainEvents.Any())
            .Select(e => e.Entity)
            .ToList();

        var domainEvents = entities.SelectMany(e => e.DomainEvents).ToList();
        entities.ForEach(e => e.ClearDomainEvents());

        foreach (var domainEvent in domainEvents)
            await _mediator.Publish(domainEvent, ct);

        return await base.SaveChangesAsync(ct);
    }
}
```

### Generic Repository Implementation

```csharp
namespace {Name}.Infrastructure.Persistence.Repositories;

public class Repository<T> : IRepository<T> where T : Entity
{
    protected readonly AppDbContext _context;
    protected readonly DbSet<T> _dbSet;

    public Repository(AppDbContext context)
    {
        _context = context;
        _dbSet = context.Set<T>();
    }

    public async Task<T?> GetByIdAsync(Guid id, CancellationToken ct = default)
        => await _dbSet.FindAsync(new object[] { id }, ct);

    public async Task<List<T>> GetAllAsync(CancellationToken ct = default)
        => await _dbSet.ToListAsync(ct);

    public async Task AddAsync(T entity, CancellationToken ct = default)
        => await _dbSet.AddAsync(entity, ct);

    public void Update(T entity) => _dbSet.Update(entity);

    public void Remove(T entity) => _dbSet.Remove(entity);
}
```

### Infrastructure DI Registration

```csharp
namespace {Name}.Infrastructure;

public static class InfrastructureServiceRegistration
{
    public static IServiceCollection AddInfrastructureServices(
        this IServiceCollection services, IConfiguration configuration)
    {
        services.AddDbContext<AppDbContext>(options =>
            options.UseSqlServer(
                configuration.GetConnectionString("DefaultConnection"),
                b => b.MigrationsAssembly(typeof(AppDbContext).Assembly.FullName)));

        services.AddScoped<IUnitOfWork>(sp => sp.GetRequiredService<AppDbContext>());
        services.AddScoped(typeof(IRepository<>), typeof(Repository<>));
        services.AddScoped<ITaskRepository, TaskRepository>();
        services.AddScoped<IProjectRepository, ProjectRepository>();

        return services;
    }
}
```

---

## API Layer

The API layer is the entry point. It configures DI, middleware, and exposes HTTP endpoints.

### Base ApiController

All controllers inherit from this base. It provides a standard way to convert Result → HTTP response.

```csharp
namespace {Name}.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public abstract class ApiController : ControllerBase
{
    protected IMediator Mediator =>
        HttpContext.RequestServices.GetRequiredService<IMediator>();

    protected IActionResult Problem(Result result)
    {
        if (result.IsSuccess)
            return Ok();

        var statusCode = result.Type switch
        {
            ResultType.NotFound => StatusCodes.Status404NotFound,
            ResultType.Forbidden => StatusCodes.Status403Forbidden,
            ResultType.Validation => StatusCodes.Status422UnprocessableEntity,
            _ => StatusCodes.Status500InternalServerError
        };

        return Problem(
            statusCode: statusCode,
            title: result.Error);
    }

    protected IActionResult Problem<T>(Result<T> result)
    {
        if (result.IsSuccess)
            return Ok(result.Value);

        return Problem((Result)result);
    }
}
```

### Controller Example

```csharp
namespace {Name}.API.Controllers;

public class TasksController : ApiController
{
    [HttpPost]
    public async Task<IActionResult> Create(
        [FromBody] CreateTaskCommand command, CancellationToken ct)
    {
        var result = await Mediator.Send(command, ct);
        return result.IsSuccess
            ? CreatedAtAction(nameof(GetById), new { id = result.Value }, result.Value)
            : Problem(result);
    }

    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetById(Guid id, CancellationToken ct)
    {
        var result = await Mediator.Send(new GetTaskByIdQuery(id), ct);
        return Problem(result);
    }

    [HttpGet("project/{projectId:guid}")]
    public async Task<IActionResult> GetByProject(
        Guid projectId,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20,
        CancellationToken ct = default)
    {
        var result = await Mediator.Send(
            new GetProjectTasksQuery(projectId, page, pageSize), ct);
        return Problem(result);
    }
}
```

### Global Exception Middleware

```csharp
namespace {Name}.API.Middleware;

public class GlobalExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<GlobalExceptionMiddleware> _logger;
    private readonly IHostEnvironment _env;

    public GlobalExceptionMiddleware(
        RequestDelegate next,
        ILogger<GlobalExceptionMiddleware> logger,
        IHostEnvironment env)
    {
        _next = next;
        _logger = logger;
        _env = env;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (OperationCanceledException) when (context.RequestAborted.IsCancellationRequested)
        {
            _logger.LogInformation("Request was cancelled by the client.");
            context.Response.StatusCode = 499; // Client Closed Request
        }
        catch (ValidationException ex)
        {
            _logger.LogWarning(ex, "Validation error occurred.");
            context.Response.StatusCode = StatusCodes.Status422UnprocessableEntity;
            await context.Response.WriteAsJsonAsync(new ProblemDetails
            {
                Status = 422,
                Title = "Validation Error",
                Detail = string.Join("; ", ex.Errors.Select(e => e.ErrorMessage)),
                Instance = context.Request.Path
            });
        }
        catch (DomainException ex)
        {
            _logger.LogWarning(ex, "Domain error: {Message}", ex.Message);
            context.Response.StatusCode = StatusCodes.Status400BadRequest;
            await context.Response.WriteAsJsonAsync(new ProblemDetails
            {
                Status = 400,
                Title = "Business Rule Violation",
                Detail = ex.Message,
                Instance = context.Request.Path
            });
        }
        catch (NotFoundException ex)
        {
            context.Response.StatusCode = StatusCodes.Status404NotFound;
            await context.Response.WriteAsJsonAsync(new ProblemDetails
            {
                Status = 404,
                Title = "Not Found",
                Detail = ex.Message,
                Instance = context.Request.Path
            });
        }
        catch (Exception ex)
        {
            var traceId = Activity.Current?.Id ?? context.TraceIdentifier;
            _logger.LogError(ex, "Unhandled exception. TraceId: {TraceId}", traceId);

            context.Response.StatusCode = StatusCodes.Status500InternalServerError;

            // SECURITY: Never expose stack traces in production
            await context.Response.WriteAsJsonAsync(new ProblemDetails
            {
                Status = 500,
                Title = "Internal Server Error",
                Detail = _env.IsDevelopment()
                    ? ex.ToString()
                    : $"An unexpected error occurred. TraceId: {traceId}",
                Instance = context.Request.Path
            });
        }
    }
}
```

### Program.cs

```csharp
var builder = WebApplication.CreateBuilder(args);

// Layer registrations (Clean Architecture DI)
builder.Services.AddApplicationServices();
builder.Services.AddInfrastructureServices(builder.Configuration);

// API services
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// JWT Authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!))
        };
    });

// CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins(builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>()!)
            .AllowAnyMethod()
            .AllowAnyHeader()
            .AllowCredentials();
    });
});

// Current User Service
builder.Services.AddHttpContextAccessor();
builder.Services.AddScoped<ICurrentUserService, CurrentUserService>();

var app = builder.Build();

// Middleware pipeline (ORDER MATTERS)
app.UseMiddleware<GlobalExceptionMiddleware>();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

---

## Testing Patterns

### Domain Tests

```csharp
public class TaskItemTests
{
    [Fact]
    public void Create_WithValidData_ShouldCreateTask()
    {
        var task = TaskItem.Create("Test Task", Guid.NewGuid());
        Assert.Equal("Test Task", task.Title);
        Assert.Equal(TaskStatus.Pending, task.Status);
        Assert.Single(task.DomainEvents); // TaskCreatedEvent
    }

    [Fact]
    public void Create_WithEmptyTitle_ShouldThrowDomainException()
    {
        Assert.Throws<DomainException>(() =>
            TaskItem.Create("", Guid.NewGuid()));
    }

    [Fact]
    public void Complete_AlreadyCompleted_ShouldThrowDomainException()
    {
        var task = TaskItem.Create("Test", Guid.NewGuid());
        task.Complete();
        Assert.Throws<DomainException>(() => task.Complete());
    }
}
```

### Application Tests (with Mocked Repositories)

```csharp
public class CreateTaskCommandHandlerTests
{
    private readonly Mock<ITaskRepository> _taskRepoMock = new();
    private readonly Mock<IProjectRepository> _projectRepoMock = new();
    private readonly Mock<IUnitOfWork> _uowMock = new();
    private readonly Mock<ICurrentUserService> _currentUserMock = new();

    [Fact]
    public async Task Handle_ValidCommand_ShouldReturnSuccess()
    {
        var projectId = Guid.NewGuid();
        _projectRepoMock.Setup(x => x.GetByIdAsync(projectId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(Project.Create("Test Project", projectId));

        var handler = new CreateTaskCommandHandler(
            _taskRepoMock.Object, _projectRepoMock.Object,
            _uowMock.Object, _currentUserMock.Object);

        var command = new CreateTaskCommand("New Task", null, projectId, "Medium", null);
        var result = await handler.Handle(command, CancellationToken.None);

        Assert.True(result.IsSuccess);
        _taskRepoMock.Verify(x => x.AddAsync(It.IsAny<TaskItem>(), It.IsAny<CancellationToken>()), Times.Once);
        _uowMock.Verify(x => x.SaveChangesAsync(It.IsAny<CancellationToken>()), Times.Once);
    }
}
```
