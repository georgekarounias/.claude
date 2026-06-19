---
name: clean-csharp-dotnet
description: C# and .NET coding conventions for services, handlers, domain logic, APIs, async code, dependency injection, nullability, error handling, logging, and testing. Use this whenever writing or reviewing C# files, refactoring backend logic, fixing analyzer warnings, improving async correctness, or removing unsafe patterns in .NET code.
---

# Clean C# and .NET

We use **C# and .NET to express business intent clearly and safely**, not to create unnecessary abstractions.
Code should be correct, readable, testable, secure, and maintainable.

## Code Quality Philosophy

- **PRIORITIZE** correctness, clarity, security, reliability, and maintainability
- Prefer simple, explicit code over clever or overly abstract solutions
- Preserve existing behavior unless a behavioral change is explicitly requested
- Follow the project's target framework, C# version, architecture, and conventions
- Distinguish required fixes from optional style improvements

## Naming & Style

- Use `PascalCase` for types, methods, properties, events, and public members
- Use `camelCase` for parameters and local variables
- Use `_camelCase` for private instance fields
- Prefix interfaces with `I`
- Use meaningful names that communicate intent
- **AVOID** unnecessary abbreviations and type prefixes
- Use braces for control-flow statements
- Prefer file-scoped namespaces when appropriate
- Follow the repository's `.editorconfig`

## Types & Object Design

- Prefer small, cohesive types with one clear responsibility
- Prefer composition over inheritance
- Seal classes that are not designed for inheritance
- Keep implementation details private
- Expose the smallest practical public API
- Prefer immutable state where practical
- Use `record` types for value-oriented data when value equality is appropriate
- Use classes for objects with identity, lifecycle, or mutable behavior
- Use structs only for small, immutable, value-like data
- **AVOID** mutable public fields
- **AVOID** abstractions without a concrete need

## Nullability & Validation

- Enable nullable reference types
- Use non-nullable types for required values
- Use nullable types only when absence is a valid state
- Resolve nullable warnings instead of hiding them
- **DO NOT** use the null-forgiving operator (`!`) unless correctness is guaranteed
- Validate public method and constructor arguments
- Prefer `ArgumentNullException.ThrowIfNull` for required reference arguments
- Use guard clauses to reject invalid input early
- Keep objects valid after construction
- Do not use `null` as an undocumented sentinel value

## Variables & Expressions

- Use `var` when the type is obvious from the right-hand side
- Use explicit types when they improve clarity
- Prefer pattern matching and switch expressions when they simplify control flow
- Prefer expression-bodied members only when they remain easy to read
- Extract complex conditions into clearly named variables or methods
- **AVOID** clever expressions that combine unrelated operations

## Methods & APIs

- Keep methods focused on one operation
- Prefer clear method names over explanatory comments
- Keep parameter lists small and cohesive
- Prefer return values over `ref` and `out` parameters
- Use `Try...` methods when failure is expected
- Do not expose mutable collections directly
- Return the least powerful collection abstraction that satisfies the contract
- Avoid returning `null` collections; return an empty collection when appropriate
- Keep public API behavior predictable

## Asynchronous Code

- Use asynchronous APIs for I/O-bound operations
- Use the `Async` suffix for asynchronous methods
- Keep asynchronous operations asynchronous throughout the call chain
- **DO NOT** block asynchronous code with `.Result`, `.Wait()`, or `.GetAwaiter().GetResult()`
- **AVOID** `async void` except for event handlers
- Pass `CancellationToken` through cancellable operations
- Place `CancellationToken` last in public method signatures
- Respect cancellation promptly
- **AVOID** `Task.Run` for naturally asynchronous I/O
- Use `Task.WhenAll` for independent operations that can safely run concurrently
- Do not create unbounded concurrency
- Use `ValueTask` only when measurement demonstrates a benefit

## Dependency Injection & Configuration

- Prefer constructor injection for required dependencies
- Keep constructors simple and free of I/O or business logic
- **AVOID** the service locator pattern
- **AVOID** resolving services directly from `IServiceProvider` in application code
- Choose service lifetimes deliberately
- Do not inject scoped services into singleton services
- Keep dependency lists focused
- Use strongly typed options for related configuration
- Validate configuration during startup
- Use `IHttpClientFactory` or an intentionally managed long-lived `HttpClient`

## Exception Handling

- Use exceptions for exceptional failures, not routine control flow
- Catch exceptions only when the code can recover, add context, translate them, or clean up
- Catch the most specific exception type possible
- **DO NOT** swallow exceptions
- **DO NOT** use empty `catch` blocks
- Preserve the original stack trace with `throw;`
- Do not catch `System.Exception` except at application boundaries
- Use standard exception types when they accurately describe the failure
- Do not expose sensitive information in exception messages
- Do not throw exceptions from `finally` blocks

## Resource Management

- Dispose resources deterministically with `using` or `await using`
- Implement `IDisposable` or `IAsyncDisposable` when a type owns disposable resources
- Do not dispose dependencies that the type does not own
- Make disposal safe to call more than once
- Prefer `SafeHandle` over custom finalizers
- Do not rely on garbage collection for timely cleanup

## Collections & LINQ

- Use collection types that communicate intended behavior
- Prefer generic collections
- Avoid repeated enumeration of `IEnumerable<T>`
- Materialize sequences intentionally
- Keep LINQ queries readable and free of hidden side effects
- Prefer loops when they express complex stateful logic more clearly
- Avoid unnecessary intermediate collections
- Use dictionaries or sets for repeated lookups when appropriate

## Performance

- Measure before optimizing
- Optimize demonstrated bottlenecks rather than assumed ones
- Prefer algorithmic improvements over micro-optimizations
- Avoid unnecessary allocations in measured hot paths
- Avoid repeated reflection when results can be cached safely
- Avoid unnecessary string concatenation in loops
- Use `Span<T>`, `Memory<T>`, or pooling only when justified by profiling
- Do not sacrifice correctness or maintainability for insignificant gains

## Security

- Treat all external input as untrusted
- Validate input at system boundaries
- Use parameterized database commands
- **DO NOT** construct SQL by concatenating untrusted values
- **DO NOT** hard-code credentials, tokens, keys, or secrets
- Do not log passwords, tokens, payment data, or sensitive values
- Use established .NET cryptographic APIs
- Enforce authorization on the server
- Apply least-privilege access
- Avoid insecure or obsolete serialization technologies
- Address security analyzer findings unless a documented assessment proves they are not applicable

## Logging & Diagnostics

- Use structured logging with named properties
- Log actionable context, not implementation noise
- Use log levels consistently
- Avoid logging the same exception at multiple layers
- Include correlation information across service boundaries
- Do not expose internal exception details to clients
- Keep logs free of secrets and unnecessary personal data

## Testing

- Test observable behavior, not private implementation details
- Keep tests isolated, deterministic, repeatable, and fast
- Use clear test names that describe the scenario and expected result
- Follow Arrange, Act, Assert when it improves readability
- Test one behavior per test
- Include success, failure, boundary, and cancellation scenarios
- Mock only boundaries or dependencies that are slow or nondeterministic
- Prefer real objects when they are inexpensive and deterministic
- Add integration tests for database, serialization, HTTP, dependency injection, and framework behavior
- Include a regression test when fixing a defect

## Comments & Documentation

- Write comments that explain intent, constraints, trade-offs, or non-obvious decisions
- **DO NOT** write comments that merely restate the code
- Keep XML documentation accurate for public APIs
- Document important nullability, ownership, threading, cancellation, and exception behavior
- Remove outdated and commented-out code
- Prefer clear code over excessive documentation

## Code Review Behavior

When reviewing code:

- Identify correctness, security, reliability, and data-integrity problems first
- Separate required fixes from optional improvements
- Explain the consequence of each issue
- Include the affected code location when available
- Provide a concrete correction or revised code example
- Avoid rewriting unrelated code
- State assumptions when project context is missing
- Do not claim an issue exists without evidence
- Mention missing tests for important changed behavior

Use these severity levels:

- **Critical** — security vulnerability, data loss, or severe production risk
- **High** — likely defect, deadlock, resource leak, or major reliability issue
- **Medium** — maintainability, design, performance, or testability concern
- **Low** — localized readability or consistency improvement

## General Principles

- Code should communicate intent
- Make invalid states difficult to represent
- Prefer explicit dependencies and predictable control flow
- Favor maintainability over cleverness
- Follow existing project conventions unless they create a concrete problem
- Apply patterns only when they solve an observed need
- Leave the code simpler, safer, and easier to test than before
