---
name: dotnet-webapi-security-best-practices
description: Security conventions and best practices for building and reviewing ASP.NET Core (.NET / C#) Web APIs. Use this whenever writing, generating, reviewing, or refactoring backend API code that touches authentication, authorization, input handling, data exposure, secrets, CORS, transport security, rate limiting, or error handling — even when the user just says "add an endpoint", "secure this API", or "review this controller" without explicitly mentioning security. Organized around the OWASP API Security Top 10 with concrete ASP.NET Core patterns.
---

# ASP.NET Core Web API Security

Security for HTTP APIs is mostly about three questions on every request: _Who is calling? Are they allowed to do this specific thing? Can I trust this input?_ Get those wrong and nothing else matters. Apply these rules whenever building or reviewing API code, and treat any deviation as something to justify, not assume.

## Guiding principles

- **Never trust input or the client.** Anything from the request — body, query, headers, route, JWT claims you didn't validate — is attacker-controlled until proven otherwise.
- **Secure by default; fail closed.** Deny access unless explicitly granted. A missing `[Authorize]` should not be the only thing standing between an attacker and your data.
- **Defense in depth.** No single control is enough. Auth + authorization + validation + least privilege together.
- **Least privilege everywhere** — for users, for tokens (scopes), for DB accounts, for service identities.
- **Don't roll your own crypto or auth.** Use the platform: ASP.NET Core Identity, the Data Protection APIs, established JWT/OAuth libraries. Hand-rolled token schemes and password hashing are where breaches come from.

---

## 1. Authentication — prove who is calling

- Use a vetted scheme: JWT bearer tokens (OAuth2/OpenID Connect) for APIs, or ASP.NET Core Identity for user management. Don't invent a token format.
- **Validate every part of incoming JWTs.** Set `TokenValidationParameters` explicitly — issuer, audience, lifetime, and signing key must all be validated. Never set `ValidateIssuer`/`ValidateAudience`/`ValidateIssuerSigningKey` to `false` to "make it work."

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = config["Auth:Issuer"],
            ValidAudience = config["Auth:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(config["Auth:SigningKey"]!)),
            ClockSkew = TimeSpan.FromSeconds(30) // tighten the default 5-min skew
        };
    });
```

- Reject the `alg: none` JWT and never accept the algorithm from the token header — pin the expected algorithm.
- Hash passwords with a strong, salted KDF via Identity's `PasswordHasher` (don't use MD5/SHA-1/unsalted SHA-256). Never store or log plaintext passwords.
- Keep access tokens short-lived; use refresh tokens with rotation and server-side revocation. Provide a real logout/revocation path.
- Enforce strong authentication on sensitive flows (MFA where appropriate); throttle and lock out brute-force attempts on login.

## 2. Authorization — prove they're allowed to do THIS

This is the most commonly broken control. Authentication ≠ authorization.

- **Always check object-level ownership (prevents BOLA/IDOR).** A logged-in user passing `GET /orders/123` must be verified as the owner of order 123. Don't assume the ID in the route belongs to the caller.

```csharp
var order = await _repo.GetByIdAsync(id);
if (order is null) return NotFound();
if (order.OwnerId != User.GetUserId()) return Forbid(); // never return the data
```

- Use **policy-based / resource-based authorization** rather than scattering role-string checks. Centralize rules in `IAuthorizationHandler` / policies so they're testable and consistent.
- Apply `[Authorize]` at the controller/endpoint level and use `[AllowAnonymous]` deliberately and rarely. Consider a global `RequireAuthenticatedUser` fallback policy so new endpoints are protected by default.
- Enforce **function-level authorization** — admin endpoints must check admin privileges server-side, not rely on the UI hiding a button.
- Don't trust claims you didn't issue/validate; map roles/permissions from a trusted source, not from client-supplied fields.

## 3. Input validation & injection

- **Validate and constrain all input.** Use model validation (data annotations / FluentValidation), validate `ModelState`, and reject anything outside expected ranges, lengths, and formats. Validate on the server even if the client also validates.
- **Prevent SQL injection** by using parameterized queries or EF Core LINQ. Never concatenate user input into SQL. If you must use raw SQL, use parameters (`FromSqlInterpolated`, `SqlParameter`) — never string interpolation into `FromSqlRaw`.
- **Prevent mass assignment / over-posting.** Bind to explicit request DTOs containing only the fields a client may set — never bind directly to EF entities. An attacker should not be able to set `IsAdmin` or `OwnerId` by adding it to the JSON body.
- Guard against path traversal in any file/path handling (canonicalize and whitelist).
- Beware injection in other interpreters too: command execution, LDAP, and unsafe deserialization. Avoid `BinaryFormatter` entirely.

## 4. Data exposure — return only what's needed

- **Return DTOs, never EF entities.** Entities leak navigation properties, internal fields, and shape changes. Map to response models that expose exactly the intended fields (prevents excessive data exposure).
- Don't rely on the client to filter sensitive fields — do it server-side.
- Strip secrets, password hashes, internal IDs, and PII from responses and logs.
- Apply property-level authorization: a field a normal user shouldn't see must not be serialized for them.

## 5. Transport security

- **Enforce HTTPS** (`app.UseHttpsRedirection()`) and enable **HSTS** in production (`app.UseHsts()`).
- Require modern TLS; disable old protocol versions at the host/proxy.
- Mark auth cookies (if used) `Secure`, `HttpOnly`, and `SameSite` appropriately.
- Never send tokens or credentials over plaintext HTTP or in URLs/query strings (they end up in logs and history).

## 6. Secrets management

- **No secrets in source code or committed config.** No connection strings, signing keys, or API keys in `appsettings.json` checked into git.
- Use User Secrets in development and a secret store (Azure Key Vault, AWS Secrets Manager, environment variables injected by the platform) in production.
- Rotate secrets and signing keys; support key rollover without downtime.
- Scan the repo and CI for accidentally committed secrets.

## 7. CORS

- Configure an **explicit allow-list of origins**. Never combine `AllowAnyOrigin()` with `AllowCredentials()` — that's an invalid, dangerous combination.

```csharp
builder.Services.AddCors(o => o.AddPolicy("app", p => p
    .WithOrigins("https://app.example.com")
    .AllowCredentials()
    .WithMethods("GET", "POST", "PUT", "DELETE")
    .WithHeaders("Authorization", "Content-Type")));
```

- Don't reflect the request `Origin` back unconditionally. Be as narrow as the app allows.

## 8. Rate limiting & resource consumption

- Apply rate limiting (the built-in `AddRateLimiter` middleware) to protect against brute force, scraping, and DoS — especially on auth, search, and expensive endpoints.
- Cap request body size, pagination page sizes, and query complexity. Reject unbounded `take`/`limit` values.
- Set sensible timeouts and guard against unbounded loops triggered by input.

## 9. Error handling

- **Never leak stack traces, exception messages, or internal details to clients.** Use the developer exception page only in Development; in production return sanitized `ProblemDetails`.
- Return generic auth failures — don't reveal whether a username exists ("invalid username or password", not "no such user").
- Log the full error server-side with a correlation id; return only that id to the client.

## 10. Logging, monitoring & misconfiguration

- Log security-relevant events: auth successes/failures, authorization denials, privilege changes. Include correlation ids.
- **Never log secrets, tokens, passwords, or full PII.** Scrub sensitive fields before logging.
- Add security response headers (e.g. `X-Content-Type-Options: nosniff`, a restrictive `Content-Security-Policy` where the API serves content, `Referrer-Policy`). Remove headers that leak stack info (`Server`, `X-Powered-By`).
- Disable Swagger/OpenAPI and verbose diagnostics in production unless intentionally protected.
- **Anti-forgery (CSRF):** required for cookie/session-based auth with state-changing requests; use ASP.NET Core anti-forgery tokens. Pure bearer-token APIs are generally not CSRF-susceptible, but never accept credentials from cookies _and_ bearer interchangeably without thinking it through.

## 11. Dependencies & supply chain

- Keep NuGet packages and the .NET runtime patched; track advisories.
- Run vulnerability scanning (`dotnet list package --vulnerable`, Dependabot, or equivalent) in CI and fail on known-critical issues.
- Pin/lock versions and review transitive dependencies for high-risk packages.

---

## Review checklist (use when reviewing API code)

1. Is the endpoint authenticated, and is `[AllowAnonymous]` intentional?
2. Is there an **object-level ownership check** for every resource accessed by id?
3. Does it bind to a request DTO (not an entity), preventing over-posting?
4. Is all input validated and are queries parameterized?
5. Does the response use a DTO that excludes sensitive/internal fields?
6. Are secrets pulled from config/secret store, never hard-coded?
7. Is CORS scoped to known origins (no `AllowAnyOrigin` + credentials)?
8. Are errors sanitized (no stack traces / detail leakage)?
9. Are auth events logged without logging secrets/PII?
10. Is the endpoint rate-limited / size-capped if expensive or auth-related?

---

## Anti-patterns to reject

- Disabling JWT validation flags or accepting `alg: none`.
- Trusting an id from the route/body as proof of ownership (BOLA/IDOR).
- Binding requests directly to EF entities (mass assignment).
- Building SQL by string concatenation / interpolation into `FromSqlRaw`.
- Returning EF entities or full exception details to clients.
- `AllowAnyOrigin()` together with credentials.
- Secrets in `appsettings.json` or source control.
- Rolling custom token/crypto/password-hashing schemes.
- Relying on the frontend to hide privileged actions instead of enforcing authorization server-side.

When code would require any of these to function, restructure it — add the ownership check, introduce a DTO, inject the secret — rather than shipping the insecure shortcut.
