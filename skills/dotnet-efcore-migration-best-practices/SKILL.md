---
name: dotnet-efcore-migration-best-practices
description: Best practices for creating, reviewing, and applying Entity Framework Core migrations safely. Use this whenever a change touches entity models, the DbContext, or the database schema — adding/removing/renaming columns or tables, changing types or nullability, adding indexes or constraints, generating or editing a migration, or planning how to deploy a schema change. Trigger even when the user just says "add a column", "change the model", or "create a migration" without mentioning safety. Covers reversibility, avoiding data loss, zero-downtime deploys, and team workflow.
---

# EF Core Migration Best Practices

A migration is a versioned, ordered change to a production database that real user data lives in. The cost of a bad migration is not a failed build — it's data loss or downtime. So the bar is higher than for ordinary code: every migration must be **reviewed, reversible, and safe to run against populated tables**.

## Core principles

- **Migrations are source code.** They are committed, code-reviewed, and never silently regenerated after they've shipped. Treat the generated file as something to read and verify, not blindly trust.
- **Never edit a migration that has already been applied anywhere** (shared dev, staging, prod). Once applied, it's history. To change it, add a _new_ migration. Editing applied migrations desyncs the model snapshot and other developers' databases.
- **Always read the generated `Up` and `Down` before committing.** The scaffolder is good, not infallible — it can turn a rename into a destructive drop+add, or generate a change that loses data.
- **Assume the table has data.** A change that's harmless on an empty dev table can fail or destroy data on a populated production table.
- **One logical change per migration**, with a descriptive name. Small, focused migrations are reviewable and easy to roll back.

---

## Creating a migration

- Generate against the correct project and startup project:
  ```bash
  dotnet ef migrations add AddOrderStatusColumn --project Data --startup-project Api
  ```
- **Name it for what it does**, in a consistent style: `AddOrderStatusColumn`, `MakeEmailRequired`, `CreateInvoicesTable`. The name shows up in history and in the `__EFMigrationsHistory` table.
- After scaffolding, **open the migration file and verify**:
  - `Up` does exactly the intended change — no surprise drops or recreations.
  - `Down` correctly reverses `Up` (see Reversibility).
  - Renames are emitted as `RenameColumn`/`RenameTable`, **not** as a drop followed by an add (drop+add discards the data in that column/table).
  - New indexes, foreign keys, and constraints are correct and named sensibly.
- Keep the model snapshot in sync — it's regenerated automatically; commit it alongside the migration.

## Reversibility — make `Down` real

- Every migration should be reversible. Verify `Down` actually restores the prior state, not just structurally but for data where feasible.
- The scaffolder cannot recover dropped data on rollback — if `Up` drops a column, `Down` recreates an _empty_ one. Call this out and, for risky changes, preserve data explicitly (e.g. a temp column, or a kept-around column removed in a later migration once you're confident).
- For changes the scaffolder can't reverse, write the `Down` by hand rather than leaving it broken. A migration with a no-op or throwing `Down` is a migration you can't safely roll back.

## Avoiding data loss (the dangerous changes)

These are the operations to scrutinize hardest:

- **Adding a NOT NULL column to a populated table.** This fails unless you provide a default or backfill. Add it nullable, backfill existing rows, then tighten to NOT NULL in a later migration — or supply a `defaultValue`.
- **Renaming a column or table.** Confirm it's a true rename (`RenameColumn`) and not drop+add. If EF generated drop+add, replace it with the rename operation so data survives.
- **Changing a column type / narrowing it** (e.g. `nvarchar(200)` → `nvarchar(50)`, `string` → `int`). May truncate or fail on existing values. Add a custom data-migration/conversion step and validate existing data first.
- **Splitting or merging columns.** Don't drop the source column in the same migration that adds the target — copy data first, verify, then drop later.
- **Dropping columns/tables.** Irreversible data loss. Be certain nothing depends on them and consider a "deprecate first, drop later" gap.

When a change is destructive, prefer a **multi-step plan** over a single destructive migration, and write the data-movement step explicitly (raw SQL via `migrationBuilder.Sql(...)` or a separate data migration) rather than relying on the schema diff alone.

## Applying migrations safely

- **Do not blindly auto-apply migrations on app startup in production** (`db.Database.Migrate()` at boot). It races across multiple instances, runs with app-level permissions, and gives no review gate. Prefer a controlled deploy step.
- **Generate idempotent SQL scripts for production deploys** and have them reviewed/run by your pipeline:
  ```bash
  dotnet ef migrations script --idempotent --output migrate.sql --project Data --startup-project Api
  ```
  Idempotent scripts can be re-run safely and check the history table before applying each migration.
- For controlled environments, `dotnet ef database update` is fine in dev; for prod, prefer the reviewed SQL script or a migration bundle (`dotnet ef migrations bundle`).
- Run migrations with a database principal that has schema permissions — separate from the least-privileged account the running app uses.
- Always test the migration against a copy of production-like data (volume and shape) before shipping, and confirm the rollback path.

## Zero-downtime deploys (expand–contract)

When the app and database deploy together and you can't take downtime, make schema changes backward-compatible with the currently running code:

1. **Expand** — add the new column/table (nullable / additive); deploy. Old code ignores it, new code can use it.
2. **Migrate data & code** — backfill data; deploy app code that writes/reads the new shape.
3. **Contract** — once nothing uses the old shape, drop it in a later migration.

Avoid a single migration that renames or drops something the still-running previous version of the app depends on — that breaks requests during the rollout window.

## Team workflow

- **Migration merge conflicts:** if two branches each add a migration, the model snapshot will conflict. The usual fix is to remove the later migration (`dotnet ef migrations remove`), rebase/merge, and re-add it so ordering and the snapshot are correct. Don't hand-merge the snapshot blindly.
- Keep migrations in order; the `__EFMigrationsHistory` table tracks what's applied. Never reorder applied migrations.
- Review migrations in PRs like any other code — a second pair of eyes on `Up`/`Down` catches destructive diffs.

## Seeding & data

- Use `HasData` in `OnModelCreating` for small, static reference/lookup data — it's tracked by migrations and kept in sync.
- For large or environment-specific seeding, use a separate seeding routine or data migration, not `HasData`.
- For data transformations during a migration, use `migrationBuilder.Sql(...)` with parameter-safe SQL; keep it idempotent where possible.

## Performance on large tables

- Adding an index or a NOT NULL column on a very large table can lock it and take time — plan for it (off-peak, online index where the DB supports it, batched backfills).
- Backfill large tables in batches rather than one giant `UPDATE`.
- Review the generated SQL for operations that rewrite the whole table.

---

## Review checklist

1. Did you read both `Up` and `Down`?
2. Does `Down` actually reverse `Up`?
3. Are renames emitted as renames, not drop+add?
4. Any NOT NULL column added to a populated table without a default/backfill?
5. Any type change that could truncate or fail on existing data?
6. Any drop that loses data — is it intended and safe?
7. Is destructive work split into expand → backfill → contract where needed?
8. Is the production apply path a reviewed (idempotent) script, not blind startup auto-migrate?
9. Has it been tested against production-like data, including rollback?
10. Is the model snapshot committed and the migration named clearly?

## Anti-patterns to reject

- Editing a migration that's already been applied somewhere.
- Auto-running `Migrate()` on app startup in production.
- Adding a NOT NULL column to a populated table with no default/backfill.
- Accepting a scaffolded drop+add where a rename was intended.
- Dropping a column/table in the same migration that should have copied its data first.
- A broken, no-op, or throwing `Down` method.
- Hand-merging the model snapshot to resolve a conflict.
- Shipping a schema change that breaks the currently-running app version mid-deploy.

When a change forces one of these, restructure it into a safe multi-step migration rather than shipping the destructive shortcut.
