## TonyStark Vault Schema

This vault follows a three-layer workflow inspired by Karpathy's persistent wiki pattern.

### Layers
- Raw sources: immutable conversation exports and local source references under `10 Sources/`. Full conversations extracted to `10 Sources/raw/conversations/`.
- Wiki: agent-maintained notes under `20 Sessions/`, `30 Topics/`, `40 Tools/`, `50 Syntheses/`, and `60 Knowledge/`.
- Schema: this file plus `AGENTS.md` and `90 System/` define conventions and update rules.

### Core Rules
- Never edit original chat exports in place.
- Prefer updating existing notes over creating duplicate notes.
- Every imported session should become one canonical session note.
- Session notes should link to tool notes and synthesis notes with wikilinks.
- If a source is partial or metadata-only, mark that limitation explicitly instead of fabricating content.

### Folder Conventions
- `10 Sources/`: inventories, source pointers, and manual drop zones. `raw/conversations/` holds full extracted conversations.
- `20 Sessions/`: one note per valuable conversation session (≥3 turns). Low-value sessions (<3 turns) are deleted during knowledge compilation.
- `30 Topics/`: depth topic pages, LLM-synthesized from knowledge pages (not keyword counts).
- `40 Tools/`: one note per AI tool or interface.
- `50 Syntheses/`: cross-topic synthesis pages (technical debt, data flow, agent capability).
- `60 Knowledge/`: compiled entity knowledge pages — Concepts/, Decisions/, Solutions/. Each page has: 核心问题 / 关键结论 / 操作要点 / 踩过的坑 / 待解决问题, with source_session backlinks.
- `90 System/`: templates, bases, and operational docs.

### Knowledge Compilation Workflow
1. `scripts/extract_full_conversations.py` — extract full conversations (untruncated) from jsonl to `10 Sources/raw/conversations/`.
2. `scripts/compile_all.py` — LLM-compile each conversation into a `60 Knowledge/` page.
3. `scripts/write_topics.py` — synthesize knowledge pages into `30 Topics/` depth pages.
4. `scripts/write_syntheses.py` — cross-topic synthesis into `50 Syntheses/`.
5. `gbrain import` — index everything for semantic search and synthesis queries.

### Ingest Workflow
1. Discover new sources from local tool histories or manual exports.
2. Record raw source paths in `10 Sources/Source Inventory.md`.
3. Create or update one session note per conversation.
4. Update tool notes with counts, paths, and caveats.
5. Refresh synthesis notes and Bases views.

### Note Style
- Use Obsidian frontmatter.
- Use wikilinks for internal links.
- Keep summaries factual and source-backed.
- Add caveats when transcripts are incomplete.
