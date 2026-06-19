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
- `wiki/SCHEMA.md`

Only add specialized areas such as `wiki/tensions/`, `wiki/timelines/`,
`wiki/people/`, `wiki/projects/`, or domain-specific folders when the content
actually needs them.

If a repo already has `CLAUDE.md`, `AGENTS.md`, or another governing instruction
file for the wiki, extend that instead of creating a competing contract.

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

### Ingest

When adding a source:

1. Read the source carefully.
2. Create or update a summary page under `wiki/sources/`.
3. Update existing entity, concept, and synthesis pages touched by the source.
4. Create a new page only when the source adds a durable new concept, entity, or recurring topic.
5. Update `overview.md` when the source materially changes the evolving synthesis.
6. Update `index.md`.
7. Append a structured entry to `log.md`.

A single source often changes many pages. That is normal if the edits are
provenance-backed and precise.

### Query And File-Back

When answering a question:

1. Read `index.md` first.
2. Read the smallest relevant set of pages.
3. Answer from the wiki with clear page-level citations or source references when possible.
4. If the result is durable, useful synthesis, file it back into the wiki instead of leaving it only in chat history.
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

## Provenance And Reliability

- Treat raw sources as immutable.
- Do not rewrite or delete raw sources.
- Do not present unsupported claims as settled fact.
- Every durable claim should trace back to one or more sources or be clearly labeled as synthesis, hypothesis, contradiction, or open question.
- Before writing a claim, grep for the existing claim, title, alias, wikilink, or citation.
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