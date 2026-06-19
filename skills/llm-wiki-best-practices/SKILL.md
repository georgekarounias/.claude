---
name: llm-wiki-best-practices
description: Skill for building and maintaining an LLM wiki with immutable raw sources, an LLM-owned interlinked markdown wiki, and schema-driven ingest, query, and lint workflows. Use this when scaffolding a git-backed or Obsidian-friendly knowledge base, ingesting new sources into durable pages, filing useful answers back into the wiki, or checking the wiki for contradictions, stale claims, duplicates, orphan pages, and missing cross-references.
---

# LLM Wiki Best Practices

An LLM wiki is a persistent knowledge system, not a one-shot retrieval index.
Instead of re-deriving knowledge from raw documents on every question, the agent
maintains an interlinked markdown wiki that compounds over time.

The human curates sources, asks questions, and reviews important decisions. The
LLM does the bookkeeping: summarization, indexing, cross-references, synthesis,
contradiction tracking, and ongoing maintenance.

## Core Model

An LLM wiki has three layers:

1. Raw sources: immutable inputs such as articles, papers, notes, transcripts, PDFs, images, or datasets.
2. The wiki: LLM-maintained markdown pages for summaries, entities, concepts, comparisons, timelines, reports, and higher-level synthesis.
3. The schema: the rules that govern directory layout, page types, naming, citations, ingest, query, and lint workflows.

The key distinction from basic RAG is persistence. The wiki is the compiled
knowledge layer that sits between the human and the raw sources.

## Starter Template Pack

Use the template pack in `./.claude/skills/llm-wiki-best-practices/templates/`
before inventing page shapes from scratch.

Available templates:

- `schema-template.md`
- `source-page.md`
- `entity-page.md`
- `concept-page.md`
- `query-page.md`
- `tension-page.md`
- `lint-report.md`

These files are the default contract for scaffolding and for introducing new
page types into a wiki.

## Default Structure

Prefer a plain markdown and git-first setup unless scale or the user explicitly
requires something heavier.

Start with a minimal structure like:

- `raw/`
- `raw/assets/` when local images or attachments matter
- `wiki/index.md`
- `wiki/log.md`
- `wiki/overview.md`
- `wiki/sources/`
- `wiki/entities/`
- `wiki/concepts/`
- `wiki/queries/`
- `wiki/reports/`
- `wiki/tensions/` when contradictions or competing claims should be first-class
- `wiki/SCHEMA.md`

Only add specialized areas such as `wiki/tensions/`, `wiki/timelines/`,
`wiki/people/`, `wiki/projects/`, or domain-specific folders when the content
actually needs them.

If a repo already has `CLAUDE.md`, `AGENTS.md`, or another governing instruction
file for the wiki, extend that instead of creating a competing contract.

## Stable Identity Convention

Do not rely on page titles alone for identity once the wiki becomes non-trivial.

- Source pages use `source_id`.
- Entity and concept pages use `canonical_id`.
- Query pages use `query_id`.
- Tension pages use `tension_id`.
- Reports use `report_id`.
- Use `aliases` when the same thing appears under more than one common name.

If a non-trivial claim is likely to be repeated, contradicted, or revised across
multiple pages, give it a stable inline marker such as `[claim:market-share-2026-q1]`.
This makes deduplication and contradiction tracking more reliable than raw text search alone.

## Operating Modes

### Scaffold

When a wiki does not exist yet:

1. Clarify the domain, source types, and expected workflow.
2. Create the directory structure and minimal starter files.
3. Write the schema so future sessions know how to ingest, query, file-back, and lint.
4. Seed `index.md`, `log.md`, and `overview.md` with structure, not filler.

The schema should define:

- directory layout
- page categories
- page templates
- citation and provenance rules
- ingest workflow
- query workflow
- lint workflow
- when to update an existing page versus create a new page
- how contradictions, stale claims, and open questions are represented

Use `schema-template.md` as the starting point unless the repo already has a
more specific schema contract.

### Ingest

When adding a source:

1. Read the source carefully.
2. Create or update a summary page under `wiki/sources/`.
3. Update existing entity, concept, and synthesis pages touched by the source.
4. Create a new page only when the source adds a durable new concept, entity, or recurring topic.
5. Update `overview.md` when the source materially changes the evolving synthesis.
6. Update `index.md`.
7. Append a structured entry to `log.md`.
8. If the source introduces an unresolved disagreement, create or update a page in `wiki/tensions/` instead of hiding the conflict in prose.

A single source often changes many pages. That is normal if the edits are
provenance-backed and precise.

### Query And File-Back

When answering a question:

1. Read `index.md` first.
2. Read the smallest relevant set of pages.
3. Answer from the wiki with clear page-level citations or source references when possible.
4. If the result is durable, useful synthesis, file it to `wiki/queries/YYYY-MM-DD-<slug>.md` instead of leaving it only in chat history.
5. Update `index.md` and `log.md` when that new synthesis becomes part of the durable knowledge base.

### Lint And Repair

Periodically check the wiki for:

- contradictions or superseded claims
- duplicate or near-duplicate pages
- orphan pages with no meaningful inbound links
- missing cross-references
- concepts frequently mentioned but lacking their own page
- stale summaries that no longer match newer sources
- empty or low-value pages
- obvious content gaps that should trigger more sourcing or follow-up questions

Auto-fix low-risk structural issues. For ambiguous semantic conflicts, record
the tension or produce a review report instead of silently overwriting content.

## Canonical Page Requirements

At minimum, durable pages should follow the template pack:

- Source pages summarize one source, track provenance, and list the key entities, concepts, tensions, and claims drawn from that source.
- Entity pages summarize one durable entity, list its key facts and relationships, and point back to relevant sources.
- Concept pages summarize one durable concept, its core definition, key claims, related concepts, and tensions.
- Query pages capture valuable answers that should compound in the knowledge base.
- Tension pages hold unresolved contradictions or competing interpretations explicitly.

If you deviate from the template, do it deliberately and document why in the schema.

## Lint Contract

A lint pass is not complete until it writes a durable report to
`wiki/reports/lint-YYYY-MM-DD.md` using the lint-report template.

Every lint pass should check at least the following:

1. Required core files exist: `wiki/index.md`, `wiki/log.md`, and `wiki/overview.md`.
2. Pages listed in `index.md` resolve to real files.
3. Wikilinks are not obviously broken.
4. There are no duplicate page titles, `canonical_id` values, or `source_id` values for the same concept.
5. Durable pages include the expected `page_type` and stable ID fields.
6. Source pages contain usable provenance.
7. Entity, concept, and overview pages do not present durable unsupported claims as fact unless clearly labeled as synthesis, hypothesis, contradiction, or open question.
8. Orphan pages are listed explicitly.
9. Open tensions or superseded claims are listed explicitly.
10. Stale pages that no longer reflect newer sources are flagged for review.

The lint report should include:

- a summary count of what was scanned and what was flagged
- auto-fixes applied
- issues requiring human review
- missing pages or content gaps
- suggested next sources or questions

## Provenance And Reliability

- Treat raw sources as immutable.
- Do not rewrite or delete raw sources.
- Do not present unsupported claims as settled fact.
- Every durable claim should trace back to one or more sources or be clearly labeled as synthesis, hypothesis, contradiction, or open question.
- Before writing a claim, grep for the existing claim, title, alias, wikilink, or citation.
- Prefer updating or superseding an existing claim over duplicating it with slightly different wording.
- Prefer updating canonical pages over scattering the same fact across multiple pages.
- Preserve historical provenance when the current understanding changes.
- Prefer append-only updates for logs and history sections.
- Avoid broad rewrites when a targeted edit will do.
- Do not invent precision the sources do not support.

## Indexing And Navigation

- `index.md` should be content-oriented: grouped links with one-line summaries and optional lightweight metadata.
- `log.md` should be chronological and append-only.
- Prefer consistent log headings like `## [YYYY-MM-DD] ingest | Source Title` so the file stays greppable.
- `overview.md` should be the evolving synthesis of the wiki, not a dump of raw notes.
- Each durable page should make it easy to see what it is, why it matters, what it links to, and what supports it.
- Use frontmatter only when it clearly helps navigation or tooling; do not overdesign metadata.
- `wiki/tensions/` is the preferred home for unresolved contradictions that matter beyond one page.

## Concurrency And Maintenance

If multiple agents or sessions may write to the wiki:

- prefer one writer per target file or section where possible
- prefer append-only logs and history trails
- deduplicate semantically before writing
- do not assume a clean git merge means the wiki is semantically correct

Transport-level merge safety and semantic deduplication are different problems.

## Tooling Guidance

- Prefer plain markdown, folders, and git first.
- Use Obsidian-friendly conventions when the user is browsing the wiki there.
- Avoid adding vector stores, web apps, schedulers, or background services unless the user asks for them or the wiki has clearly outgrown the simpler model.
- At moderate scale, `index.md` plus ordinary grep/search is often enough.
- Introduce heavier retrieval tooling only when the need is concrete.

## What Good Looks Like

A good LLM wiki:

- compounds with every source and every useful question
- makes relationships and contradictions visible
- stays navigable by humans in ordinary markdown tools
- is easy for future agents to maintain because the schema is explicit
- preserves provenance and avoids silent drift
- remains lightweight unless scale justifies more infrastructure
