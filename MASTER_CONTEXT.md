# MASTER CONTEXT — Legal RAG (Offline, Local) — Phase A: everything except the LLM

> Give this whole file to the coding agent as the project brief. Follow it literally. When something is ambiguous, pick the simplest option that satisfies the acceptance criteria and note the choice in `DECISIONS.md`.

---

## 1. Project in one paragraph

A local-first, privacy-preserving RAG system that helps lawyers work through large legal documents (contracts, agreements, policies, statutes). It ingests PDF / DOCX / TXT files, recovers their legal structure (Act → Chapter → Section → Sub-section → Clause), indexes every clause with hierarchy-aware metadata, and answers questions by hybrid retrieval (BM25 + dense vectors, fused with RRF) that returns clauses **with their full parent chain and cross-references** and exact citations (document, section path, clause, page/line). Everything runs on one laptop, offline.

**Phase A (this file) builds every block in the architecture diagram EXCEPT the Local Inference Layer and the Verification Layer.** The LLM and the claim-validation gate are deferred, but the code must leave clean hooks so they plug in later without refactoring (see section 12).

## 2. Hard constraints

- **Offline only.** No network calls at runtime. No cloud APIs. Models are downloaded once, then loaded from local paths.
- **Hardware:** AMD Ryzen 5 5500U, 16 GB RAM, **no GPU**. CPU-only everything. Keep peak RAM under ~4 GB for Phase A.
- **Python 3.11.** Single repo, runnable with `pip install -r requirements.txt` and `streamlit run app/main.py`.
- **Deterministic and testable.** No LLM in the pipeline. Same input gives the same tree, the same index, and the same retrieval results.
- Every stored clause must be traceable back to its source: document, page (if available), paragraph/line range.

## 3. Tech stack (final — do not substitute)

| Concern | Choice |
|---|---|
| PDF parsing | PyMuPDF (`pymupdf`) — gives text, font size, bold flags, bbox, page number |
| DOCX parsing | `python-docx` — paragraph styles, numbering, runs |
| TXT | plain read, same heading heuristics |
| OCR (scanned PDFs) | **P2 / optional**: `pytesseract` stub only; detect "no text layer" and warn clearly |
| Embeddings | BGE-small-en-v1.5 via **FastEmbed (ONNX, CPU)** |
| Vector store | **LanceDB** (replaces FAISS) — embedded, on-disk, no server |
| Keyword index | `rank_bm25` (BM25Okapi), persisted with pickle/JSON |
| Metadata + audit store | SQLite (`sqlite3`) |
| Clause tree store | JSON file per document |
| Config | YAML (`config/settings.yaml`) loaded with pydantic models |
| UI | Streamlit, runs on localhost |
| Tests | pytest |
| Models | pydantic v2 dataclasses for all data structures |

## 4. Architecture → modules map (build every block below)

| Diagram block | Module | Priority |
|---|---|---|
| Legal Documents input (PDF/DOCX/TXT) | `src/ingest/loader.py` | P0 |
| System Configuration | `config/settings.yaml`, `src/config.py` | P0 |
| Document Parser (text extraction, layout, heading/numbering detection) | `src/parsing/pdf_parser.py`, `docx_parser.py`, `txt_parser.py`, `heading_detect.py` | P0 |
| OCR (if scanned) | `src/parsing/ocr.py` (stub + warning) | P2 |
| Hierarchy Builder (tree + cross-ref detection) | `src/hierarchy/builder.py`, `xref.py` | P0 |
| Metadata Encoder | `src/hierarchy/metadata.py` | P0 |
| Clause Embeddings | `src/indexing/embedder.py` | P0 |
| Hybrid Index: dense (LanceDB) + sparse (BM25) | `src/indexing/vector_store.py`, `bm25_index.py` | P0 |
| Parent Summary Index | `src/indexing/summary_index.py` | P1 |
| Local Data Stores | `src/storage/` (tree json, lancedb, sqlite, files) | P0 |
| Hybrid Retrieval Engine (BM25 + semantic + RRF) | `src/retrieval/hybrid.py`, `fusion.py` | P0 |
| Context Assembler (top-K + parent chain + xrefs) | `src/retrieval/context_assembler.py` | P0 |
| Context to LLM (structured prompt builder — **no model call**) | `src/retrieval/prompt_builder.py` | P1 |
| Web Application (local) + User Experience | `app/main.py`, `app/pages/*` | P0 |
| Audit & Logs | `src/audit/logger.py` | P1 |
| Naive-chunking baseline (for evaluation) | `src/baseline/naive_chunker.py` | P0 |
| Evaluation harness | `eval/run_eval.py`, `eval/questions.jsonl` | P0 |
| **Local 4-bit LLM, Draft Answer + Source Claims** | `src/llm/` — **interface + NullBackend only** | Deferred |
| **Citation / Claim Validation Gate** | `src/verify/` — **empty package with docstring** | Deferred |

P0 = must work for the demo. P1 = build if P0 is done. P2 = stub or skip.

## 5. Repository layout

```
legal-rag/
├── MASTER_CONTEXT.md
├── DECISIONS.md
├── README.md
├── requirements.txt
├── config/settings.yaml
├── data/
│   ├── raw/                 # uploaded source documents
│   ├── trees/               # <doc_id>.json clause trees
│   ├── lancedb/             # vector tables
│   ├── bm25/                # persisted BM25 indexes
│   └── meta.sqlite          # documents, audit_log
├── src/
│   ├── config.py
│   ├── models.py            # pydantic: Document, ClauseNode, Hit, ContextBundle
│   ├── ingest/loader.py
│   ├── parsing/ ...
│   ├── hierarchy/ ...
│   ├── indexing/ ...
│   ├── retrieval/ ...
│   ├── baseline/naive_chunker.py
│   ├── audit/logger.py
│   ├── llm/                 # base.py (LLMBackend), null_backend.py
│   ├── verify/              # placeholder
│   └── storage/ ...
├── app/
│   ├── main.py
│   └── pages/ (1_Ingest, 2_Ask, 3_Inspect, 4_Benchmark, 5_Audit)
├── eval/ (questions.jsonl, run_eval.py, results/)
├── scripts/ (ingest_cli.py, ask_cli.py)
└── tests/
```

## 6. Data models (`src/models.py`)

**ClauseNode** (one per structural unit; this is the unit of embedding and citation)

```
node_id        str   stable: f"{doc_id}:{index_path}"  e.g. "nda01:2.3.1"
doc_id         str
doc_title      str
node_type      enum  {root, part, chapter, article, section, subsection, clause, subclause, schedule, paragraph, flat}
level          int   0 = root
label          str   as written: "2.3", "(a)", "Section 138", "Article IV"
heading        str|None   heading text if the unit has one
text           str   the unit's OWN text (not children's)
parent_id      str|None
children_ids   list[str]
path           list[str]   e.g. ["Chapter XVII","Section 138","(b)"]  -> used for citations
order          int   global reading order within the doc
page_start     int|None   (None for DOCX/TXT where pages are unknown)
page_end       int|None
line_start     int   paragraph/line index in the source (always available)
line_end       int
xrefs_raw      list[str]   raw reference strings found in text, e.g. "Section 5(2)"
xrefs_resolved list[str]   node_ids that the references resolved to (may be empty)
version        str   ingest version / file hash prefix
token_count    int
```

**Hit**: `node_id, score, source ("bm25"|"dense"|"fused"), rank`.

**ContextBundle**: `query, mode, hits[], items[]` where each item = `{clause, parent_chain[], xref_clauses[], citation_str}` plus `total_tokens`.

## 7. Parsing and hierarchy (the riskiest part — time-box to 2 days)

### 7.1 Text extraction
- **PDF:** use PyMuPDF `page.get_text("dict")`. Keep for every line: text, font size, bold flag, page number, y-position. Drop repeated headers/footers (a line that repeats on >50% of pages at the same y-position) and bare page numbers.
- **DOCX:** iterate paragraphs; keep style name (`Heading 1..n`), bold-run ratio, and any list numbering text. Pages are unknown, so set `page_* = None`.
- **TXT:** one paragraph per non-empty block.
- If a PDF has almost no extractable text, log a warning "likely scanned; OCR not enabled in Phase A" and skip that file cleanly.
- Produce a normalized list of `Line(text, page, line_idx, font_size, is_bold, style)`.

### 7.2 Heading / numbering detection (`heading_detect.py`)
Rule-based, ordered pattern table. Each pattern maps to a depth rank. Suggested patterns (case-insensitive, anchored at line start):

1. Keyword headings: `^(PART|CHAPTER|ARTICLE|SCHEDULE|ANNEXURE|APPENDIX)\s+[IVXLC\d]+` and `^SECTION\s+\d+[A-Z]?`
2. Decimal numbering: `^\d+\.\s+[A-Z]` (depth 1), `^\d+\.\d+\.?\s` (depth 2), `^\d+\.\d+\.\d+\.?\s` (depth 3), and so on
3. Bare section numbers common in Indian statutes: `^\d+[A-Z]?\.\s` followed by a short bold/title-cased heading
4. Lettered sub-clauses: `^\(([a-z])\)\s` and roman numerals `^\(([ivxlc]+)\)\s`, `^\(\d+\)\s`
5. Provisos / explanations: lines starting `Provided that`, `Explanation`, `Illustration`, `Exception` attach to the preceding unit as part of its text, or as a child of type `paragraph`

Boost heading confidence with: font size larger than body median, bold, ALL CAPS, short line (< 12 words), no ending period. A line is a heading if the numbering pattern matches OR (style/font signals are strong AND the line is short).

**Depth assignment:** do not hardcode one global depth table. Learn the order in which numbering styles first appear inside the document (a stack-based approach): when a new style appears below the current one, push; when a previously seen style appears, pop back to its level. This handles documents that mix `1.` / `(a)` / `(i)` differently from statutes.

### 7.3 Hierarchy builder (`builder.py`)
- Build the tree with a stack. Every non-heading line is appended to the `text` of the current deepest open node.
- Create a root node per document (`node_type=root`, `heading=doc title`).
- **Fallback:** if fewer than 3 headings are detected in the whole document, mark the document `structure="flat"`, split by paragraph, create `flat` nodes under the root, and show a visible "flat document" badge in the UI. Never crash.
- Each node gets `path`, `parent_id`, `children_ids`, `page_start/end`, `line_start/end`, `token_count`.
- Save the tree as `data/trees/<doc_id>.json` and its rows in SQLite.

### 7.4 Cross-reference detection (`xref.py`)
- Regexes for: `Section 5`, `Section 5(2)(a)`, `clause 4.2`, `Article III`, `paragraph (c) above`, `Schedule 2`, `sub-section (3)`.
- Store raw strings in `xrefs_raw`.
- Resolve within the same document by matching the label/path against existing nodes; store matches in `xrefs_resolved`. Unresolved refs stay in `xrefs_raw` only (do not guess).

### 7.5 Metadata encoder (`metadata.py`)
Fill/validate every ClauseNode field (page, line range, clause ID, parent ID, doc ID, version = first 8 chars of file SHA-256). Provide `citation_str(node)` that produces, for example:
`NDA_Acme.pdf › Article 4 › 4.2 › (b), p.7, lines 112-118`
(omit page if `None`, show "para" numbers instead).

## 8. Indexing (`src/indexing/`)

### 8.1 Embedding unit
- **One clause node = one retrieval unit.** Do not split a clause mid-way in the stored text.
- Text sent to the embedder: `"{path joined with ' > '}: {heading}. {text}"` (contextual prefix improves legal retrieval).
- BGE-small's limit is ~512 tokens. If a node is longer, embed it as several windows but **store all windows under the same `node_id`** and aggregate by max score at query time. Never produce a separate citable unit for a window.
- For query embedding use BGE's query instruction prefix: `"Represent this sentence for searching relevant passages: "`.
- Batch the embeddings (batch size 32), show a progress bar, cache by text hash so re-ingesting is fast.

### 8.2 LanceDB tables (`data/lancedb/`)
- `clauses`: `node_id, doc_id, vector (384), text, path_str, level, node_type, page_start, line_start, version`
- `summaries`: same shape for parent summary vectors (see 8.4)
- `naive_chunks`: `chunk_id, doc_id, vector, text, page_start, char_start, char_end` (baseline only)
- Use a flat/exact search by default (corpus is small); add an IVF/HNSW index only if the table exceeds ~50k rows.
- Support delete-by-`doc_id` and re-ingest of a changed document (version bump).

### 8.3 BM25 (`bm25_index.py`)
- Tokenize: lowercase, strip punctuation, keep numbers and section labels as tokens (e.g. "138"), drop a short stopword list but keep legal modals (`shall`, `may`, `must`, `not`).
- Build over the same `path_str + heading + text` string used for embeddings.
- Persist per-corpus; rebuild on ingest. Keep a `node_id` list aligned with the BM25 doc order.

### 8.4 Parent Summary Index (P1)
No LLM is available, so summaries are **extractive**: for each `section`/`chapter`/`article`/`root` node, summary = heading + the first two sentences of its own text + the headings of its children. Embed these into the `summaries` table. Retrieval use: if a summary hits strongly, boost or expand to its children (feature flag `retrieval.use_summary_boost`). Document in `DECISIONS.md` that summaries are extractive until the LLM exists.

## 9. Retrieval (`src/retrieval/`)

1. **Keyword search:** BM25 top `n_bm25` (default 20).
2. **Semantic search:** LanceDB top `n_dense` (default 20), aggregate windows by `node_id`.
3. **Fusion (`fusion.py`):** Reciprocal Rank Fusion, `score = Σ 1/(k + rank)`, `k = 60`. Also implement weighted-sum fusion behind a config flag so both can be compared in the benchmark.
4. Return the top `K` fused hits (default 5).
5. **Mode switch:** `mode = "hierarchical"` (clauses table) or `"naive"` (naive_chunks table). The same retrieval code path serves both so the comparison is fair.
6. Optional filters: restrict to a `doc_id` or a set of documents.

### Context Assembler (`context_assembler.py`)
For each top-K hit build an item containing:
- the clause text,
- its **full parent chain** (root → … → parent, each with label, heading, and the first ~60 words of parent text),
- up to 2 resolved cross-referenced clauses (one hop, truncated to ~120 words each),
- a `citation_str`.

Enforce a total token budget (`context.max_tokens`, default 3000): drop lowest-ranked items or truncate parent/xref text first, never the clause text of the top-ranked hit. De-duplicate parents shared by several hits (show the chain once, reference by id).

### Prompt builder (`prompt_builder.py`) — builds, does not send
Render a structured prompt string from a `ContextBundle`: instructions, numbered context blocks each tagged with `[CITE: node_id | citation_str]`, the user question, and the required answer format (answer with inline `[node_id]` citations; say "not found in the provided clauses" when unsupported). Return the string and show it in the UI under **"Prompt that would be sent to the LLM"**. This proves the pipeline is ready for the LLM and costs nothing.

## 10. Application (`app/`, Streamlit, runs on localhost)

Pages:
1. **Ingest:** upload one or more PDF/DOCX/TXT; show a progress bar through parse → hierarchy → embed → index; show a summary (nodes found, depth, structure type, pages, time taken, warnings such as "flat document" or "scanned").
2. **Ask:** question box; radio toggle **Hierarchical / Naive**; document filter; top-K slider. Output: ranked retrieved clauses with scores (BM25 rank, dense rank, fused rank), citation strings, parent chain breadcrumb, cross-referenced clauses, and an expander with the assembled prompt. Since the LLM is off, show a clear banner: "Generation disabled in Phase A — showing retrieval and citations only".
3. **Inspect:** collapsible tree view of any ingested document; clicking a node shows its text, metadata, xrefs, and page/line source. Provide an "open original" action that shows the page text (PDF page render via PyMuPDF `get_pixmap` if easy, otherwise page text).
4. **Benchmark:** run the evaluation set and show the naive vs hierarchical table and chart.
5. **Audit:** table view of the audit log with filters.

UX rules: no spinner without a message, no unhandled exceptions shown to the user, every error has a human-readable message.

## 11. Audit & logs (`src/audit/logger.py`)

SQLite table `audit_log(id, ts, event_type, payload_json)` with event types: `ingest_started`, `ingest_finished`, `ingest_warning`, `query`, `retrieval_result`, `benchmark_run`, `error`. For `query` events store the question, mode, filters, returned `node_id`s with scores, and latency in ms. Also write a rolling text log under `data/logs/`. Everything stays on disk locally.

## 12. Hooks for the deferred layers (build the seams now)

- `src/llm/base.py`: `class LLMBackend(Protocol): def generate(self, prompt: str, **kw) -> str`.
- `src/llm/null_backend.py`: returns a fixed notice string; this is the default.
- Config key `llm.backend: "null"` (later `"ollama"` with model `qwen2.5:3b`; not implemented now).
- `src/verify/__init__.py`: docstring describing the future gate (claim → source clause entailment check) and the expected input format: a list of `{claim_text, cited_node_id}`.
- The `ContextBundle` and the `[CITE: node_id | ...]` tags are the contract the future LLM and verifier will rely on. Do not change their shape casually.

## 13. Evaluation (`eval/`)

- `questions.jsonl`: one object per line: `{"qid": "...", "doc_id": "...", "question": "...", "gold_node_ids": ["..."], "type": "lookup|definition|obligation|cross-ref"}`.
- Target: 3–4 documents of different kinds (a statute excerpt, a contract, a policy), 5–8 questions each, about 20 questions in total. I (the human) will write the questions and gold clauses; the harness only needs to read them.
- For the naive baseline, a hit counts as correct if the chunk's character span **overlaps** a gold clause's span.
- `run_eval.py` computes **Recall@1/3/5** and **MRR** for: naive+dense, naive+hybrid, hierarchical+dense, hierarchical+hybrid. Output a markdown table and a CSV to `eval/results/`, and render the table in the Benchmark page.
- Also report average retrieval latency and index build time per document (the "experimental setup" evidence).

## 14. Configuration (`config/settings.yaml`)

```yaml
paths: {data_dir: data, models_dir: models}
parsing: {min_headings_for_structure: 3, drop_repeating_headers: true}
embedding: {model: BAAI/bge-small-en-v1.5, batch_size: 32, max_tokens: 512}
retrieval: {n_bm25: 20, n_dense: 20, top_k: 5, fusion: rrf, rrf_k: 60, use_summary_boost: false}
context: {max_tokens: 3000, max_xrefs_per_hit: 2}
baseline: {chunk_tokens: 512, overlap: 64}
llm: {backend: "null"}
```

All thresholds come from here; no magic numbers in code.

## 15. Build order (follow strictly; commit after each step)

1. Skeleton, config, models, SQLite init, `requirements.txt`.
2. PDF + DOCX + TXT loaders producing normalized `Line` lists. Test on 3 real files.
3. Heading detection + hierarchy builder + saved tree JSON. Print the tree for each test file and eyeball it. **Stop and fix parsing quality before moving on.**
4. Metadata encoder, xref detection, `citation_str`.
5. Embedder + LanceDB `clauses` table + BM25 index.
6. Hybrid retrieval + RRF + CLI `ask_cli.py` returning hits.
7. Context assembler + prompt builder.
8. Naive baseline chunker + `naive_chunks` table + mode switch.
9. Streamlit Ingest / Ask / Inspect pages.
10. Evaluation harness + Benchmark page.
11. Audit logging + Audit page.
12. Summary index (P1), OCR stub warning (P2), README.

If time runs out, steps 1–9 plus 10 are the demo; 11–12 are optional.

## 16. Acceptance criteria (Phase A is "done" when all are true)

- Uploading a text-based PDF and a DOCX through the UI produces a navigable clause tree and an indexed corpus without errors.
- A flat (structure-less) document ingests with a visible "flat" badge and still supports retrieval.
- Asking a question returns top-5 clauses, each showing its parent chain, any resolved cross-references, and a correct citation string (document, path, page or paragraph/line range).
- The Hierarchical/Naive toggle works over the same documents and the Benchmark page shows Recall@k and MRR for both.
- The assembled prompt for any query is visible and contains `[CITE: ...]` tags for every context block.
- No network access is needed after the one-time model download (verify by disabling Wi-Fi).
- `pytest` passes: at least tests for heading detection, hierarchy building on a fixture document, xref resolution, RRF fusion, and context token budgeting.
- Re-ingesting the same file does not duplicate rows; ingesting a changed file bumps its version.

## 17. Coding rules for the agent

- Type hints everywhere; pydantic models for all cross-module data.
- Small pure functions for parsing rules so they are unit-testable; no global state.
- Log with the `logging` module; never `print` in library code.
- Fail soft on bad documents (warn, skip, continue); fail loud on config errors.
- Do not add dependencies beyond section 3 without recording the reason in `DECISIONS.md`.
- Do not implement the LLM, the verifier, or anything that calls the network.
- Keep the README short: install, ingest, ask, benchmark, known limitations (scanned PDFs need OCR; DOCX has no page numbers; extractive summaries; cross-references resolve only within one document).

## 18. Known limitations to state honestly in the demo

Scanned PDFs need OCR (Phase B). DOCX files have no reliable page numbers, so citations use paragraph numbers. Parent summaries are extractive until the LLM is added. Cross-references resolve only inside the same document. Generation and claim verification arrive in Major Project-II.
