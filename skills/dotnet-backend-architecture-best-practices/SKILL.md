---
name: dotnet-backend-architecture-best-practices
description: Backend architecture guidance for .NET APIs, application services, domain boundaries, EF Core data access, jobs, integrations, DTO boundaries, and secure composition roots. Use this whenever designing or reviewing backend structure, choosing where logic belongs, defining layers or modules, shaping API/application boundaries, or preventing architecture drift in .NET systems.
---

# Building .NET Backend Systems

We're building .NET backend systems that follow specific architecture principles focused on
clarity, maintainability, reliability, security, and long-term evolution.

These principles define the expected architecture outcomes.

## Architecture Boundaries

- **PREFER** dependencies that point toward business logic
- **DO NOT** allow the Domain layer to depend on:
  - ASP.NET Core
  - Entity Framework Core
  - SQL or database providers
  - AI provider SDKs
  - Storage SDKs
  - Messaging SDKs
  - HTTP clients
- **PREFER** application-owned abstractions for infrastructure dependencies
- Keep Infrastructure implementations outside the Domain and Application layers
- Treat API and Worker projects as composition roots
- **AVOID** circular dependencies between modules
- **DO NOT** allow one business module to update another module's data directly

## Domain-Driven Design

- **PREFER** organizing the system around business capabilities
- Use a consistent ubiquitous language across:
  - Code
  - Requirements
  - Tests
  - Events
  - Logs
  - Documentation
- **PREFER** explicit bounded contexts for independent business areas
- **PREFER** aggregates, entities, value objects, policies, and domain services where business rules exist
- Keep business invariants inside the Domain model
- **DO NOT** place core business rules in controllers, repositories, or mapping code
- **AVOID** applying complex DDD patterns to simple CRUD functionality without clear value

## Aggregates & Domain State

- **PREFER** small aggregates with clear consistency boundaries
- Change aggregate state only through the aggregate root
- Reference other aggregates by identifier instead of object navigation
- Create repositories for aggregate roots, not for every database table
- **PREFER** one aggregate change per transaction
- Use domain events or application orchestration for cross-aggregate workflows
- **AVOID** large aggregates with unbounded collections
- **DO NOT** expose setters that bypass domain rules

## Controllers

- Keep controllers small and transport-focused
- Controllers should:
  - Accept and validate HTTP input
  - Call an application service or handler
  - Perform transport-specific authorization when required
  - Map application results to HTTP responses
  - Return the correct HTTP status code
- **DO NOT** access `DbContext` from controllers
- **DO NOT** execute SQL from controllers
- **DO NOT** place business rules in controllers
- **DO NOT** call AI, storage, or messaging providers directly
- **DO NOT** manage transactions or background threads in controllers

## Application Services

- **PREFER** application services that represent one clear use case
- Application services should:
  - Load aggregates
  - Check permissions
  - Invoke domain behavior
  - Call repositories
  - Schedule background jobs
  - Use external-service abstractions
  - Commit a Unit of Work
  - Return application results
- Keep orchestration in the Application layer
- Keep business decisions in the Domain layer
- **DO NOT** depend on HTTP-specific types
- **DO NOT** return persistence entities
- **DO NOT** expose provider SDK types

## Repositories

- **PREFER** repositories that use domain language
- Define repository interfaces in the Domain or Application layer
- Keep repository implementations in Infrastructure
- Use repositories for aggregate persistence
- Use query services or read models for complex reads
- **DO NOT** expose unrestricted `IQueryable` outside Infrastructure
- **DO NOT** commit changes inside repository methods
- **AVOID** generic repositories unless they provide clear business value
- **AVOID** repositories for child entities that do not have an independent lifecycle

## Unit of Work & Transactions

- Use an explicit Unit of Work for each application use case
- Scope the Unit of Work to one bounded context
- Commit aggregate changes and outbox records atomically
- Keep transactions short
- **DO NOT** keep a transaction open while:
  - Calling an AI provider
  - Uploading or downloading files
  - Generating embeddings
  - Querying a vector store
  - Calling external APIs
  - Waiting for messages
  - Streaming SSE responses
- **PREFER** multiple short transactions for long-running workflows
- **DO NOT** use a global Unit of Work across unrelated bounded contexts

## DTOs & Mapping

- Use separate types for:
  - API requests
  - API responses
  - Commands
  - Queries
  - Application results
  - Internal DTOs
  - Domain entities
  - Value objects
  - Read models
  - Persistence records
  - Integration events
  - Provider models
- **DO NOT** return Domain entities directly from API endpoints
- **DO NOT** expose persistence records outside Infrastructure
- **DO NOT** reuse one class across multiple layers only to reduce mapping code
- **PREFER** dedicated mappers for important boundaries
- Keep mapping code free of business rules
- Use domain constructors, factories, or methods when creating aggregates
- Use mapping libraries only for mechanical mappings
- Test non-trivial mappings

## Long-Running Jobs

- Execute long-running work in a Worker or durable job processor
- Persist a job before returning from the API
- **PREFER** returning `202 Accepted` when work continues asynchronously
- Persist job state and progress
- Support cancellation
- Make job handlers idempotent
- Distinguish transient failures from permanent failures
- Use retry limits and dead-letter handling
- Use leases or equivalent ownership when multiple workers are possible
- **DO NOT** depend on the lifetime of an HTTP request
- **DO NOT** use an in-memory queue as the only source of truth

## Server-Sent Events

- Treat SSE as a delivery channel, not as job state
- Persist progress events before publishing them
- Use stable sequence numbers
- Support client reconnection
- **PREFER** supporting `Last-Event-ID`
- Replay missed events from durable storage
- Authorize access to the requested job or resource
- Close the stream after a terminal event
- Use live pub/sub only as an optimization
- **DO NOT** depend on a live SSE connection for correctness

## Authentication & Authorization

- Treat authentication and authorization as separate concerns
- Require authentication unless an endpoint is explicitly public
- **PREFER** policy-based permissions
- Use resource-based authorization for jobs, documents, conversations, and knowledge bases
- Derive `UserId` and `TenantId` from trusted authentication context
- Enforce tenant isolation in every relevant data-access path
- **DO NOT** accept ownership or tenant identity from the client
- **DO NOT** rely only on frontend permission checks

## AI & External Providers

- Hide AI, embedding, vector, storage, OCR, email, and messaging providers behind interfaces
- Keep provider implementations in Infrastructure
- Translate provider models through anti-corruption adapters
- Translate provider failures into application-level failures
- **PREFER** configurable provider selection
- Record model, provider, prompt version, token usage, and cost where relevant
- **DO NOT** expose provider SDK types to the Domain or Application layers
- **DO NOT** store provider credentials in source-controlled configuration

## RAG & Document Management

- Apply tenant and permission filters during retrieval
- **DO NOT** retrieve unauthorized chunks and filter them afterward
- Treat retrieved document content as untrusted input
- Validate file type, size, and content before processing
- **PREFER** immutable document versions
- Record chunking, embedding, and index versions
- Include source references in grounded responses
- Keep binary storage separate from document metadata
- **DO NOT** use technical job state as the only business document state

## Configuration

- Use strongly typed options
- Validate mandatory configuration during startup
- Document configuration precedence
- Keep secrets in an approved secret store
- Use dedicated providers for tenant-specific configuration
- Use typed feature names
- Define which settings:
  - Require restart
  - Support dynamic reload
  - Support tenant overrides
  - Support job-specific overrides
- Record effective configuration versions for reproducible long-running jobs
- **DO NOT** inject raw `IConfiguration` throughout business code
- **DO NOT** allow every setting to be overridden at every scope

## Code Quality, Nullability & Static Analysis

- Enable nullable reference types in all new projects
- Treat nullable annotations as part of the public contract
- Use `?` only when `null` is a valid value
- Resolve nullable warnings instead of suppressing them broadly
- **AVOID** the null-forgiving operator (`!`)
  - Use it only when an invariant is known and documented
- Enable the recommended .NET analyzers
- Maintain a shared `.editorconfig`
- **PREFER** enforcing agreed style and quality rules during builds
- Treat selected warnings as errors in CI
- Centralize shared compiler and analyzer settings in `Directory.Build.props`
- Keep suppressions narrow and documented
- **DO NOT** disable analyzers globally to avoid fixing warnings
- **DO NOT** use broad `#pragma warning disable` directives

## Naming

- Use names that reveal both business meaning and architectural role
- **PREFER**:

  ```text
  CreateDocumentCommand
  GetDocumentQuery
  CreateDocumentResult
  DocumentDetailsDto
  DocumentResponseMapper
  IJobRepository
  IDocumentManagementUnitOfWork
  JobExecutionOptions
  DocumentVersionValidated
  DocumentVersionReadyIntegrationEvent
  OpenAiChatAdapter
  JobRecord
  ```

- **AVOID** vague names such as:

  ```text
  Manager
  Helper
  Utility
  CommonService
  Data
  Info
  Item
  Object
  Processor
  GeneralHandler
  ```

- Name asynchronous methods with the `Async` suffix
- Name boolean members so they read naturally (`IsCompleted`, `CanRetry`, `HasPermission`)
- Use past tense for events
- Use business terms instead of database-oriented names

## SOLID & Reusability

- Keep every class focused on one responsibility
- **PREFER** composition over inheritance
- **PREFER** small, consumer-focused interfaces
- Depend on abstractions at business boundaries
- Add extension points where behavior is expected to vary
- **AVOID** creating an interface only because a class exists
- **AVOID** deep inheritance hierarchies
- Extract shared code only when the shared behavior has the same meaning and reason to change
- **AVOID** large `Common`, `Helpers`, or `Utilities` modules
- Write code for humans first and frameworks second

## Dependency Injection & Service Lifetimes

- Choose service lifetimes deliberately:
  - Use scoped services for request- or job-scoped state
  - Use transient services for lightweight stateless behavior
  - Use singleton services only when they are thread-safe and application-wide
- **DO NOT** inject a scoped service into a singleton
- **DO NOT** resolve scoped services from the root service provider
- Create an explicit scope for each background-job execution
- Let the dependency-injection container dispose services it creates
- Dispose objects manually only when the application creates and owns them
- **DO NOT** dispose injected dependencies
- **DO NOT** use the service-locator pattern
- **DO NOT** pass `IServiceProvider` into business services to resolve arbitrary dependencies
- **DO NOT** call `BuildServiceProvider()` during service registration
- **AVOID** registering disposable transient services that may be resolved from the root scope
- **PREFER** typed factories when runtime creation or selection is required
- Validate the dependency graph during startup where supported

## Async/Await & Cancellation

- Use `async` and `await` for I/O-bound operations
- Name asynchronous methods with the `Async` suffix
- Return `Task` or `Task<T>` from asynchronous methods
- Use `ValueTask` only when measurements show a clear benefit
- Accept `CancellationToken` as the final parameter of asynchronous public methods
- Pass the same `CancellationToken` through every cancellable operation
- Respect cancellation in:
  - API requests
  - Database calls
  - HTTP calls
  - Background jobs
  - File operations
  - AI and vector-provider calls
  - Async streams
- Use `OperationCanceledException` to represent cancellation
- **DO NOT** convert cancellation into a generic failure
- **DO NOT** catch `OperationCanceledException` unless cancellation-specific handling is required
- **DO NOT** use `.Result`, `.Wait()`, or `.GetAwaiter().GetResult()` in application code
- **DO NOT** use `async void`
  - Exception: event handlers that require a `void` signature
- **DO NOT** wrap naturally asynchronous I/O in `Task.Run()`
- Use `Task.Run()` only for deliberate CPU-bound work that must be moved from the current thread
- Keep asynchronous methods asynchronous through the complete call chain
- **AVOID** mixing synchronous and asynchronous versions of the same operation
- Use `Task.WhenAll()` only when operations:
  - Are independent
  - May safely run concurrently
  - Do not share a non-thread-safe dependency
  - Respect provider and system concurrency limits
- **DO NOT** run concurrent EF Core operations on the same `DbContext`
- Limit concurrency for bulk or fan-out operations
- **AVOID** creating an unbounded number of tasks
- Use `Parallel.ForEachAsync()` or bounded channels only when concurrency is intentional and controlled
- Use `IAsyncEnumerable<T>` for streaming data that can be produced incrementally
- Propagate cancellation with `[EnumeratorCancellation]` in async iterators
- Dispose asynchronous resources with `await using`
- **PREFER** `ConfigureAwait(false)` in reusable libraries that do not require a synchronization context
- In ASP.NET Core application code, `ConfigureAwait(false)` is optional and should not be added inconsistently
- Let exceptions propagate to the layer responsible for handling them
- Preserve the original stack trace by using `throw;`, not `throw exception;`
- **DO NOT** start fire-and-forget tasks from request code
- Schedule background work through the durable job infrastructure

## Exceptions & API Error Handling

- Use centralized exception-handling middleware
- Return consistent `ProblemDetails` responses for API failures
- Map known failures to explicit HTTP status codes
- Include a stable application error code where clients need programmatic handling
- Include correlation or trace identifiers in error responses
- **DO NOT** expose stack traces, SQL details, internal paths, or provider secrets
- Show detailed exception information only in approved development environments
- Use standard exception types when they accurately describe the failure
- Create custom exceptions only when callers need a distinct failure meaning
- **AVOID** exceptions for expected high-frequency control flow
- **PREFER** `Try...` methods or result types for routinely expected failures
- Let unexpected exceptions reach the centralized handler
- Preserve stack traces with `throw;`
- **DO NOT** use `throw exception;`
- **AVOID** catch blocks that only log and rethrow when centralized logging already exists

## Outbound HTTP & Resilience

- Manage HTTP connection lifetimes using:
  - `IHttpClientFactory`, or
  - A deliberately configured long-lived `HttpClient`
- **DO NOT** create and dispose a new unmanaged `HttpClient` for every request
- Define explicit timeouts for outbound operations
- Propagate cancellation tokens to outbound calls
- Apply retries only to transient failures
- Retry non-idempotent operations only when an idempotency strategy exists
- **DO NOT** retry every status code or exception
- Use circuit breakers to prevent repeated calls to an unhealthy dependency
- Use hedging only for safe operations and when duplicate requests are acceptable
- **AVOID** stacking multiple retry layers across libraries, proxies, and application code
- Bound total execution time across timeout, retry, and circuit-breaker policies
- Record dependency name, duration, outcome, and retry count
- **DO NOT** log authorization headers, tokens, or sensitive request bodies

## Data Access & Entity Framework Core

- Keep `DbContext` short-lived and scoped to one request, command, or job execution
- **DO NOT** share a `DbContext` between threads or concurrent operations
- Project queries directly to DTOs or read models when full aggregates are not required
- Select only the columns needed by the use case
- Use bounded result sets
- Enforce maximum page sizes
- **PREFER** keyset pagination for large sequential result sets
- Use offset pagination only when random page access is required and the cost is acceptable
- **PREFER** no-tracking queries for read-only entity results
- Choose tracking explicitly when updates are expected
- **AVOID** implicit lazy loading
- Prevent N+1 queries through projection, explicit loading, or deliberate eager loading
- Review large `Include` graphs for Cartesian explosion
- Consider split queries when one large joined query produces excessive duplication
- Keep filtering, ordering, and pagination in the database
- Inspect generated SQL for important queries
- Verify indexes and execution plans for critical paths
- Use optimistic concurrency tokens for data that can be edited concurrently
- Handle concurrency conflicts explicitly
- Return a conflict response or apply a documented retry/merge strategy
- **DO NOT** automatically retry business-level concurrency conflicts without re-evaluating current state

## API Contracts, Payloads & Performance

- Generate an OpenAPI document for HTTP APIs
- Validate the OpenAPI contract during build or CI where practical
- Keep public request and response contracts backward compatible
- Version breaking API changes deliberately
- Expose interactive API documentation only in approved environments
- Protect production API documentation when it must remain available
- Define maximum limits for:
  - Request bodies
  - File uploads
  - Page sizes
  - Collection sizes
  - Generated responses
- Reject oversized requests before fully buffering them
- Stream large request and response bodies when possible
- **AVOID** loading large payloads completely into memory
- **AVOID** large temporary allocations on hot paths
- Optimize only after measuring with profiling or production telemetry
- Use rate limiting based on endpoint cost, user, client, or tenant
- Return `429 Too Many Requests` when a rate limit is exceeded
- Include retry guidance when appropriate
- Load-test rate-limit and payload-limit policies
- Use asynchronous I/O throughout request processing
- **DO NOT** perform long-running CPU work on request threads

## Web Security Hardening

- Enforce HTTPS outside local development
- Use HSTS in production where appropriate
- Configure forwarded headers correctly when running behind trusted proxies
- Define explicit CORS policies
- Allow only required origins, methods, and headers
- **DO NOT** use permissive CORS with credentials
- Protect state-changing cookie-authenticated endpoints against CSRF
- Do not treat CORS as an authorization mechanism
- Use ASP.NET Core Data Protection for application-protected data
- Persist and protect Data Protection keys in multi-instance deployments
- Share the correct key ring and application name only between trusted instances
- Rotate secrets and signing keys through an approved process
- Secure administrative, diagnostic, health, and documentation endpoints
- Apply secure cookie settings when cookies are used:
  - `HttpOnly`
  - `Secure`
  - Appropriate `SameSite`
- Validate redirect and return URLs
- **DO NOT** trust proxy headers from untrusted networks

## Date, Time, Properties & Resource Lifetime

- Use `TimeProvider` instead of reading the system clock directly in business code
- Store timestamps with an explicit UTC or offset contract
- **PREFER** `DateTimeOffset` for timestamps that represent an instant
- Treat a time-zone identifier separately from a UTC offset
- Convert to local display time only at system boundaries
- **DO NOT** use `DateTime.Now` in Domain or Application logic
- Keep property getters simple, synchronous, and inexpensive
- Use methods for:
  - Expensive work
  - Asynchronous work
  - Operations with meaningful side effects
  - Operations expected to fail
- Dispose resources deterministically when the code owns them
- Use `using` and `await using` where appropriate
- Implement `IDisposable` or `IAsyncDisposable` only when the type owns disposable resources
- Make disposal safe when called more than once
- **AVOID** finalizers unless directly owning unmanaged resources

## Caching & Response Compression

- Cache only when data lifetime and invalidation rules are understood
- Define:
  - Cache key
  - Scope
  - Expiration
  - Invalidation strategy
  - Maximum size
- Use distributed caching when multiple instances must share cached state
- Prevent cache keys from mixing tenants or users
- **DO NOT** cache sensitive personalized responses without explicit isolation
- Use output caching only for safe responses
- Vary cached responses by every value that changes the result
- Verify middleware ordering when authentication and output caching are combined
- Enable response compression for suitable text-based responses
- **DO NOT** expect compression to improve already compressed formats
- Measure compression CPU cost and response-size benefit
- **AVOID** caching errors unless the failure behavior is deliberate

## Health Checks & Deployment Probes

- Define separate probes for:
  - Startup
  - Readiness
  - Liveness
- Use startup checks for required initialization
- Use readiness checks to decide whether the instance can receive traffic
- Use liveness checks only to determine whether the process should be restarted
- **DO NOT** make liveness depend on every external service
- Mark the instance unready while it is draining or unable to serve requests safely
- Keep health-check execution bounded by timeouts
- Return only the information required by the orchestrator
- Protect detailed diagnostic health endpoints
- Test probe behavior during dependency failures and deployments

## Conditional Performance Optimizations

- Measure before introducing specialized performance code
- **PREFER** source-generated logging with `[LoggerMessage]` on proven high-volume paths
- **PREFER** `System.Text.Json` source generation when:
  - Native AOT or trimming requires it
  - Serialization is a measured hot path
  - Startup or memory reduction is important
- **AVOID** pooling, spans, custom serializers, or unsafe code without benchmarks
- Document the measurement that justifies a specialized optimization
- Keep optimized code behind clear abstractions and tests

## Cross-Cutting Concerns

- Centralize repeated infrastructure behavior using:
  - Middleware
  - Decorators
  - Pipeline behaviors
  - Filters
  - Interceptors
- Suitable concerns include:
  - Validation
  - Logging
  - Metrics
  - Authorization
  - Transactions
  - Idempotency
  - Caching
  - Retry policies
  - Audit logging
  - Correlation IDs
- **DO NOT** duplicate cross-cutting infrastructure logic across application services

## Observability

- Use structured logging
- Use OpenTelemetry-compatible traces and metrics where practical
- Record dependency calls as spans
- Keep metric cardinality bounded
- **DO NOT** use user IDs, document IDs, or request IDs as metric labels
- Propagate correlation IDs across API, Worker, database, and provider calls
- Include business and execution identifiers in logs and traces
- Measure:
  - Latency
  - Failures
  - Retries
  - Queue depth
  - Job duration
  - Provider usage
  - Token usage
- Add health checks for required dependencies
- **DO NOT** log secrets, tokens, document contents, or sensitive provider responses

## Testing

- Test Domain rules with unit tests
- Test Application orchestration with focused service tests
- Test Infrastructure with real dependencies where practical
- Test API contracts, authentication, authorization, and status codes
- Test Worker retries, cancellation, leases, and idempotency
- Test SSE replay and reconnection behavior
- Test nullable and analyzer rules in CI
- Test service-lifetime validation
- Test `ProblemDetails` mappings
- Test outbound timeout, retry, and circuit-breaker behavior
- Test EF Core concurrency conflicts and query limits
- Test rate limiting and oversized payload rejection
- Test OpenAPI generation and compatibility
- Test readiness, liveness, and startup probe behavior
- Add architecture tests that enforce dependency rules
- **PREFER** automated checks over review-only conventions

## Project Structure

- **DO NOT** require every project to use the same folder structure
- **PREFER** a structure that makes these boundaries visible:
  - Domain
  - Application
  - Infrastructure
  - API or Worker hosts
  - Contracts
  - Tests
- Larger systems should also make bounded contexts visible
- The structure may use:
  - Separate projects
  - Modules
  - Feature folders
  - Namespaces
  - A modular monolith
  - Multiple services
- The chosen structure must preserve dependency direction, ownership, and testability

## Architecture Exceptions

- Document exceptions using an Architecture Decision Record
- Every exception should include:
  - Context
  - Decision
  - Alternatives considered
  - Consequences
  - Affected projects
  - Review date
- **DO NOT** introduce undocumented exceptions
- **PREFER** temporary exceptions with a clear removal plan

## Contributing to This Document

- Add principles that apply to more than one project
- State the principle before implementation details
- Use clear **PREFER**, **AVOID**, and **DO NOT** language
- Explain rules only when needed to remove ambiguity
- Keep examples short
- Avoid prescribing one library unless it is a team standard
- Add rules to the most relevant existing section
- Create a new section only when no existing section fits
- Have changes to mandatory rules reviewed by a senior developer or architect

## General Principles

- Write code for humans first, compilers second
- Prefer explicitness over cleverness
- Keep business logic independent from infrastructure
- Optimize for readability and long-term maintenance
- Prefer clear boundaries over unnecessary abstraction
- Use complexity only when the business problem requires it
- If a design is difficult to explain, reconsider the boundary
- Prefer safe defaults and fail-fast configuration
- Make limits explicit
- Treat warnings, telemetry, and operational behavior as part of the architecture
