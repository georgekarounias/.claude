---
name: database-schema-design
description: Best practices for designing relational database schemas — tables, keys, relationships, data types, constraints, indexes, and naming. Use this whenever modeling new data, adding or reshaping tables/columns, choosing keys or relationships, picking data types, or reviewing a schema or EF Core entity model. Trigger even when the user just says "model this", "design the tables", "add an entity", or "what columns should this have", without explicitly mentioning schema design. Focused on relational design (SQL Server / PostgreSQL) and how it maps to EF Core.
---

# Database Schema Design Best Practices

A schema is the longest-lived part of an application — code gets rewritten, data and its shape persist for years. Good schema design pushes correctness into the database itself (keys, constraints, types) so bad data can't exist, and models the domain clearly enough that queries are natural. Get the shape right up front; reshaping a populated production schema later is the expensive path (see the EF migrations skill).

## Core principles

- **Let the database enforce integrity, not just the app.** Foreign keys, unique constraints, check constraints, and NOT NULL are guarantees that hold no matter what code (or which app, or a stray script) writes to the table. Application-only validation eventually gets bypassed.
- **Normalize first; denormalize deliberately.** Start from a normalized design (each fact in one place) and only introduce redundancy for a measured performance reason — documenting the trade-off, because duplicated data must be kept consistent.
- **Model the domain, not the screen.** Tables represent entities and relationships, not the shape of a particular UI or API response. Shape data for queries at read time (DTOs/views), not by distorting the schema.
- **Every column should be NOT NULL unless null carries real meaning.** "Unknown/optional" is a meaningful null; a NULL used as a placeholder for "0" or "" is a design smell.
- **Choose the most specific correct type.** The type is your first line of validation — it constrains what can ever be stored.

---

## Keys

- **Give every table a primary key.** No exceptions for "real" tables.
- **Prefer a surrogate key** (an auto-generated `int`/`bigint` identity, or a GUID) over natural keys for most entities — natural keys (email, SSN, code) tend to change and that change cascades everywhere. Keep the natural key too, enforced with a **unique constraint**.
- **Pick the key type intentionally:**
  - `int`/`bigint` identity — compact, fast, clustering-friendly, sequential. Default choice. Use `bigint` when you might exceed ~2.1B rows.
  - `GUID`/`uniqueidentifier` — good when ids must be generated client-side or be unguessable/mergeable across systems, but random GUIDs fragment clustered indexes and are wider. If you need GUIDs in SQL Server, prefer sequential GUIDs to reduce fragmentation.
- Don't expose sequential surrogate keys in public URLs if enumeration is a concern — use a separate opaque/public id.
- For **join (many-to-many) tables**, use a composite primary key of the two foreign keys (plus a unique constraint covering any business rule), rather than an extra surrogate unless the relationship itself carries data.

## Relationships & referential integrity

- **Always define foreign keys** for relationships. They prevent orphaned rows and document the model.
- **Choose cascade behavior deliberately.** Cascade delete is convenient but dangerous — a delete can silently wipe large subtrees. Prefer `Restrict`/`NoAction` for important data and delete explicitly in code, reserving cascade for true owned/child data (e.g. order → order lines).
- Make the **cardinality explicit**: one-to-many via an FK on the "many" side; many-to-many via a join table; one-to-one via a shared/unique FK (and question whether it should just be columns on the same table).
- Avoid polymorphic/"generic" foreign keys (one nullable FK column that points at different tables depending on a type column) — they can't be enforced by a real FK. Use separate FK columns or table-per-type instead.

## Data types

- **Money:** use `decimal` with explicit precision/scale (e.g. `decimal(19,4)`). Never `float`/`double` for money — binary floating point can't represent currency exactly.
- **Date/time:** store points in time as UTC. Use `datetimeoffset` (SQL Server) / `timestamptz` (PostgreSQL) when timezone matters; `date` for dates without time. Avoid storing local time without an offset.
- **Text:** use Unicode types (`nvarchar` in SQL Server) for human text; size columns to a sensible bound rather than defaulting everything to `max`. Reserve `nvarchar(max)`/`text` for genuinely large content.
- **Booleans:** a real `bit`/`boolean`, not a `char(1)` 'Y'/'N' or an int.
- **Enums / fixed sets:** store as a small int or a short code, and back it with either a CHECK constraint or a lookup table (below). Avoid free-text status columns.
- **Don't store structured data as a delimited string** (CSV in a column). If it's a list, it's a related table. Reserve JSON columns for genuinely schemaless/sparse data, knowing you lose relational integrity and easy querying on it.

## Constraints — encode the rules

- **UNIQUE** for natural keys and any "no duplicates" rule (email, slug, (tenant_id, code)).
- **CHECK** for value rules the type can't express (`Quantity >= 0`, `EndDate >= StartDate`, status in a known set).
- **DEFAULT** for sensible defaults (timestamps, flags) so inserts don't depend on the app remembering.
- **NOT NULL** aggressively — see core principles.

These constraints are documentation that can't go stale and protection that can't be bypassed.

## Lookup vs. CHECK for categorical data

- Use a **lookup table** (with an FK) when the set of values changes over time, needs extra attributes (display name, sort order, active flag), or is referenced/joined often.
- Use a **CHECK constraint** (or an app/DB enum) when the set is small, stable, and code-defined (e.g. order status). Keep the database value stable even if the display label changes.

## Indexing

- The primary key gets an index automatically (clustered by default in SQL Server). Choose the clustered key to be narrow, increasing, and unique — surrogate identity keys are ideal.
- **Index your foreign keys.** They're not auto-indexed and are constantly used in joins and cascade checks.
- Add indexes to support real query patterns (frequent `WHERE`/`JOIN`/`ORDER BY` columns). For composite indexes, **order columns by selectivity and how queries filter** (equality columns first, then range).
- Use **covering indexes** (`INCLUDE` columns) for hot read paths to avoid key lookups.
- **Don't over-index.** Every index slows writes and costs storage. Index for measured query needs, not "just in case." Review and remove unused indexes.
- Enforce uniqueness with a unique index/constraint rather than app checks (which race).

## Naming conventions

- Be **consistent** above all. Pick singular or plural table names and stick to it (EF Core convention pluralizes `DbSet` names; many teams keep tables singular — choose one).
- Use clear, consistent casing (snake_case is conventional in PostgreSQL; PascalCase common with SQL Server + EF). Configure EF mapping to match the DB convention.
- Name keys/constraints predictably: `PK_Orders`, `FK_Orders_Customers_CustomerId`, `IX_Orders_CustomerId`, `UQ_Users_Email`. Predictable names make migrations and errors readable.
- Avoid reserved words and ambiguous abbreviations. A column named `Status` should make clear *whose* status by its table context.

## Common columns & patterns

- **Audit columns:** `CreatedAtUtc`, `CreatedBy`, `UpdatedAtUtc`, `UpdatedBy` where you need history of who/when. Set via defaults or app interceptors consistently.
- **Optimistic concurrency:** add a `rowversion`/`xmin` concurrency token so concurrent updates don't silently overwrite each other; EF Core maps these to concurrency checks.
- **Soft delete:** an `IsDeleted`/`DeletedAtUtc` flag plus a global query filter, *if* you need recoverability or audit — but understand the cost (every query must filter it, unique constraints must account for it). Don't add it reflexively.
- **Multi-tenancy:** if tenant isolation matters, put `TenantId` on tenant-owned tables and include it in unique constraints and indexes from day one — retrofitting it is painful.

---

## Review checklist

1. Does every table have a primary key, and is the clustered/PK choice narrow and increasing?
2. Are all relationships backed by real foreign keys, with deliberate cascade behavior?
3. Are foreign key columns indexed?
4. Is every column NOT NULL unless null has real meaning?
5. Are natural keys / "no duplicates" rules enforced by unique constraints?
6. Are types the most specific correct ones (decimal for money, UTC date/time, no stringly-typed status)?
7. Are domain rules encoded as CHECK/DEFAULT constraints, not just app code?
8. Is categorical data a lookup table or constrained set — not free text or magic strings?
9. Are indexes justified by real query patterns (and not redundant/unused)?
10. Are naming conventions consistent and constraint names predictable?

## Anti-patterns to reject

- Tables with no primary key.
- Relationships with no foreign key ("we enforce it in the app").
- `float`/`double` for money.
- Local time stored without an offset; mixing UTC and local.
- Status/category as free-text with no constraint.
- Storing lists/CSV/delimited values in a single column instead of a related table.
- EAV ("entity-attribute-value") god tables and untyped key/value bags as a default modeling approach.
- Polymorphic FKs (one nullable column pointing at multiple tables) with no real referential integrity.
- Wide everything-`nvarchar(max)` columns and reflexive nullable columns.
- Over-indexing every column "to be safe," or never indexing foreign keys.
- Cascade-delete everywhere without considering what it can wipe.

When the data doesn't fit a clean relational shape, model the relationship explicitly (a new table, a lookup, a proper FK) rather than reaching for a delimited string, a generic key/value table, or an unconstrained column.
