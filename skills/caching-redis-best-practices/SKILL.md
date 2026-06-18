---
name: caching-redis-best-practices
description: Best practices for caching and in-memory data stores like Redis — caching patterns, invalidation, key and TTL design, stampede protection, serialization, eviction, resilience, and security. Use this whenever adding or reviewing caching, introducing Redis or a distributed cache, deciding what/when to cache, designing cache keys or expiry, or debugging stale data, cache stampedes, or memory issues. Trigger even when the user just says "cache this", "add Redis", or "speed this up with a cache" without mentioning best practices. Includes .NET (IDistributedCache / StackExchange.Redis / HybridCache) guidance.
---

# Caching & Redis Best Practices

A cache trades a little staleness for a lot of speed and reduced load. That trade-off is the whole game: the value of caching is performance, and the cost is that the cache can disagree with the source of truth. Almost every caching bug is really an *invalidation* or a *failure-handling* bug. Design for both from the start.

## Core principles

- **The cache is never the source of truth.** It is a disposable, reconstructable copy. Any cached entry must be safe to lose at any moment, and the system must work (just slower) when the cache is empty or down.
- **Cache to solve a measured problem.** Cache data that is read far more than it's written, expensive to compute or fetch, and tolerant of some staleness. Don't cache reflexively — caching adds a consistency problem you didn't have before.
- **Always set an expiry.** Every cached entry needs a TTL. A cache with no expiration is a memory leak and a source of permanently stale data.
- **Decide your staleness budget explicitly.** How wrong can this data be, for how long? The answer drives TTL, invalidation strategy, and write pattern. "Must be perfectly fresh" usually means "don't cache it."
- **Fail open.** If the cache is unavailable, fall back to the source of truth — never let a cache outage take down the app.

---

## Caching patterns — pick deliberately

- **Cache-aside (lazy loading)** — the default. The app checks the cache; on a miss it loads from the source, stores it with a TTL, and returns it. Simple and resilient (a cache miss/outage just hits the DB). Downside: first request after a miss is slow, and writes must invalidate.
  ```
  value = cache.Get(key)
  if (value is null) {
      value = db.Load(...)
      cache.Set(key, value, ttl)   // populate on miss
  }
  return value
  ```
- **Read-through** — the cache layer itself loads on miss (library/abstraction does the cache-aside for you). Cleaner call sites; same semantics.
- **Write-through** — write to cache and source together so the cache is always fresh. Costs write latency; good when reads must be consistent right after writes.
- **Write-behind (write-back)** — write to cache, flush to source asynchronously. Fast writes, but risks data loss and complexity; use only with care and durability guarantees.
- **Refresh-ahead** — proactively refresh popular entries before they expire to avoid latency spikes. Useful for hot keys.

For most CRUD apps: **cache-aside on read + explicit invalidation on write** is the right default.

## Invalidation & consistency (the hard part)

- **On write, update or invalidate the affected keys.** Decide between:
  - *Invalidate (delete) on write* — next read repopulates from source. Simple and usually safest; brief miss penalty.
  - *Update on write* — write the new value into the cache. Lower latency but races with concurrent writers; easy to leave the cache wrong if the DB write later fails.
- **Order matters.** Prefer writing the source of truth first, then invalidating the cache, and design for the small window where they disagree. Be aware of the classic race: a read repopulates a stale value between a DB update and the cache delete — mitigate with short TTLs and, for critical paths, patterns like delayed double-delete.
- **Don't rely on TTL alone for data that changes on user action.** TTL is a safety net (a ceiling on staleness), not a substitute for invalidating on writes.
- **Cache derived/aggregated data carefully** — when one source row feeds many cached aggregates, you need a clear map of what to invalidate.

## Key design

- **Use a consistent, namespaced key scheme:** `app:entity:id[:variant]`, e.g. `catalog:product:42`, `user:1001:permissions`. Namespacing prevents collisions and makes keys scannable and droppable by prefix.
- **Make keys deterministic and include everything that changes the value** — tenant id, locale, version, query parameters. A key that ignores a relevant input returns the wrong data to someone.
- **Version your keys** (`v2:product:42`) or your serialized payloads so a schema change doesn't return data the new code can't deserialize. Bumping a version prefix is also a clean bulk-invalidation.
- Keep keys reasonably short but readable; avoid unbounded key cardinality from high-variance inputs.

## TTL & expiration

- **Set a TTL on every entry.** Choose it from the staleness budget, not a habit.
- **Add jitter** to TTLs (e.g. base ± random seconds) so many keys created together don't all expire at the same instant and cause a synchronized stampede on the source.
- **Absolute vs sliding:** absolute expiry caps total staleness; sliding expiry keeps hot data alive but can keep stale data indefinitely if always accessed — combine sliding with an absolute cap.

## Stampede / thundering-herd protection

When a hot key expires, many concurrent requests can all miss and hammer the source at once.

- **Coalesce regeneration** so only one caller recomputes while others wait or briefly serve stale (single-flight / per-key lock).
- **Use early/probabilistic recomputation** or refresh-ahead for very hot keys so the value is refreshed before it expires.
- **TTL jitter** (above) spreads expirations out.
- Cache *negative results* (a "not found") briefly to stop repeated misses for non-existent keys from pounding the source.

## Serialization

- Pick a compact, well-supported format (JSON for debuggability; a binary format like MessagePack/protobuf for size/speed on hot paths).
- **Version the payload** so old cached blobs don't break new code; on a deserialization failure, treat it as a miss and repopulate rather than throwing.
- Don't cache live object graphs with behavior — cache plain data (DTOs).

## Redis-specific guidance

- **Choose the right data structure**, don't stuff everything into strings: hashes for objects/fields you update individually, sets for membership, sorted sets for ranking/leaderboards and time-ordered data, lists for queues. The structure determines which operations are cheap.
- **Use atomic operations and server-side logic** for correctness: `INCR`/`DECR`, `SETNX`, `SET key val EX n NX`, and Lua scripts for multi-step atomic updates. Don't read-modify-write across round trips when an atomic command exists.
- **Avoid big keys and hot keys.** A single huge value or one key taking all the traffic becomes a latency and failover problem. Split big collections; shard or replicate hot reads.
- **Never run `KEYS` in production** — it blocks the server. Use `SCAN` for iteration.
- **Use pipelining/batching** to cut round trips; use `MGET`/`MSET` for bulk access.
- **Set `maxmemory` and an eviction policy** that matches usage — typically `allkeys-lru`/`allkeys-lfu` for a pure cache so Redis evicts cold data under pressure instead of erroring. Use `volatile-*` policies only if some keys must never be evicted.
- **Distributed locks:** Redis locks (e.g. the Redlock approach) are useful but have well-known correctness caveats under failover/clock issues — don't use them as the sole guarantee for critical mutual exclusion; prefer the database for hard correctness.

## Resilience & failure handling

- **Wrap cache calls so a cache failure degrades to the source**, not an exception that bubbles up to the user.
- Set **short timeouts** on cache operations — a slow cache shouldn't be slower than just hitting the DB.
- Consider a **circuit breaker** so repeated cache failures temporarily bypass the cache instead of adding latency to every request.
- Plan for **cold-start / cache-flush** load: after a restart or mass eviction, the source gets a surge. Warm critical keys or rely on stampede protection.

## Security

- **Require authentication and use TLS**; never expose Redis on a public interface. Keep it on a private network/VPC with restricted access.
- **Be careful caching sensitive data.** Don't cache secrets; cache PII only with justification, encryption where appropriate, and correct expiry — a shared cache can leak data across tenants/users if keys aren't properly scoped.
- Scope keys by tenant/user so one user can never read another's cached data.

## .NET specifics

- Prefer the abstractions: **`IDistributedCache`** (backed by `StackExchange.Redis` via `AddStackExchangeRedisCache`) for simple distributed caching, and **`HybridCache`** (.NET 9+) when you want combined in-process + distributed caching with built-in stampede protection and tag-based invalidation.
- Reuse a single `ConnectionMultiplexer` (it's expensive and thread-safe) rather than creating connections per call.
- Keep `IMemoryCache` (in-process) for per-instance, ultra-hot data, but remember it isn't shared across instances — use the distributed cache for anything that must be consistent across servers.

---

## Review checklist

1. Is this data actually a good cache candidate (read-heavy, costly, staleness-tolerant)?
2. Does every entry have a TTL, with jitter where mass-expiry is a risk?
3. Are writes invalidating/updating the right keys (not relying on TTL alone)?
4. Is the key scheme namespaced, deterministic, and inclusive of every input that changes the value (tenant, locale, version)?
5. Is there stampede protection for hot keys (coalescing / jitter / negative caching)?
6. Does the app fall back to the source when the cache is down (fail open, short timeouts)?
7. Is the right Redis structure used, with no `KEYS` in prod and no giant/hot keys?
8. Is `maxmemory` + an eviction policy configured?
9. Is the cache secured (auth, TLS, private network) and free of unscoped sensitive data?
10. Is the serialized payload versioned so schema changes don't break reads?

## Anti-patterns to reject

- Treating the cache as the source of truth, or crashing when it's unavailable.
- Cached entries with no TTL.
- Relying only on TTL for data that changes on user writes (no invalidation).
- Keys that omit a relevant input (tenant/locale/params), returning the wrong data.
- `KEYS *` in production; giant values; one hot key taking all traffic.
- No stampede protection on hot keys; all TTLs expiring at the same instant.
- Caching secrets, or caching PII without scoping/justification.
- Exposing Redis without auth/TLS on a reachable network.
- Creating a new Redis connection per request instead of reusing the multiplexer.

When in doubt, ask whether the system still behaves correctly if the cache returns nothing, returns stale data, or is entirely down — and design so the answer is always "yes, just slower."
