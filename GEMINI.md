# FizzBuzz: The Inquisition — Repository Architecture & Agent Directives

## 🏛️ Project Overview
**FizzBuzz: The Inquisition** (`https://fizzbuzz.adamoutler.com/`) is a live 17-agent Byzantine zero-trust courtroom web application (`web/`) and standalone CLI (`byzantine_fizzbuzz.py`) that adjudicates whether integers are `Fizz`, `Buzz`, `FizzBuzz`, or raw digits without ever using modulo (`%`) or division (`/`).

### Module Manifest
- `byzantine_fizzbuzz.py` — Standalone zero-dependency CLI implementation.
- `web/app/main.py` — FastAPI server, WebSocket broadcast endpoint (`/ws`), REST endpoints (`/api/health`, `/api/status`, `/api/history`, `/api/archives`, `/api/docket/{case_id}`, `/api/queue`), and PWA routes (`/manifest.json`, `/sw.js`, `/favicon.ico`).
- `web/app/config.py` — Environment-driven `AppConfig` (`OLLAMA_SERVER`, `OLLAMA_MODEL`, `RECESS_SECONDS=30`, `DATABASE_PATH=/data/dockets.db`, `AMAZON_ASSOCIATE_TAG=adamoutler-20`).
- `web/app/engine/primitives.py` — Zero-modulo, zero-division Peano string arithmetic (`recursive_digital_root_trace`, `inspect_terminal_glyph`, `verify_fizz_claim`, `verify_buzz_claim`).
- `web/app/engine/structured_schemas.py` — Pydantic schemas subclassing `StrictStructuredModel` for Ollama GBNF grammar enforcement across all 17 agents.
- `web/app/engine/streaming_parser.py` — `StreamingSpeechExtractor` (streams only the `"speech"` JSON field value to the UI) and `parse_structured_output` (3-tier resilient JSON/regex parser).
- `web/app/engine/async_engine.py` — 9-phase `AsyncByzantineEngine` orchestrating Bailiff Bar, Court Historian, Judge Baz, multi-round closed-door Fizz/Buzz caucuses, floor petitions, Forensic Auditor, Antitrust Regulator, ratification pleas, remand circuits, and victory addresses.
- `web/app/engine/scheduler.py` — 1-deep priority queue + Statutory Calendar sequence scheduler (`DocketScheduler`).
- `web/app/database/models.py` — `DocketLedger` (`aiosqlite` persistent SQLite storage in `/data/dockets.db`).
- `web/app/static/` — Single-page courtroom UI (`index.html`, `styles.css`, `app.js`, `sw.js`, `manifest.json`, and `icons/`).
- `web/scripts/generate_assets.py` — Generates SVG/PNG PWA icons and the 1200x630 Open Graph banner (`og-image.png`).

---

## 🛡️ Core Architectural & Behavioral Invariants

### 1. Zero Modulo (`%`) & Zero Division (`/`)
- The AST prohibition test (`tests/test_primitives.py::test_ast_prohibitions`) inspects the Python AST of the engine. Never use `%`, `/`, `//`, `divmod`, `math`, `decimal`, or `operator.mod`.

### 2. Ollama Structured Outputs (`StrictStructuredModel`)
- **Property Ordering (`speech` first, `action` last):** Every agent response schema in `web/app/engine/structured_schemas.py` MUST declare `speech: str` as its **first** field and `action: Literal[...]` as its **last** field. This guarantees `StreamingSpeechExtractor` streams natural courtroom testimony immediately and stops the LLM as soon as the final `action` enum is chosen.
- **All Fields Required & No Redundant Booleans:** `StrictStructuredModel.model_json_schema()` forces every exported property into `"required"` in declaration order. Do NOT add redundant boolean/float fields alongside `action` in agent schemas, as small models (`gemma4:e2b`) can produce contradictory boolean vs. enum combinations.

### 3. Stare Decisis Ledger & Court Historian Accuracy
- **Order of Inquisition Sorting:** Both `get_recent_dockets()` (Historical Precedents sidebar) and `get_all_dockets()` (`The Archives` modal) MUST sort by **Order of Inquisition** (`id DESC, adjudicated_at DESC` or `id ASC, adjudicated_at ASC`), NEVER by `CAST(payload AS INTEGER)`. User-queued numbers (e.g. `420`) must appear at the exact point in the timeline where their inquisition occurred.
- **Never Overwrite Prior Dockets:** When a number is adjudicated more than once, `async_engine.py` appends `-R2`, `-R3`, etc. (`BZ-2026-0001-R2`) rather than overwriting the earlier `case_id` row.
- **Statutory Calendar Resumption:** On startup (`main.py` lifespan), always call `await ledger.get_highest_calendar_seq()` and `scheduler.resume_from_calendar_seq(highest_cal)` so container restarts resume at the next sequential integer instead of resetting to `1`.
- **Historian Prompt Context:** Feed the Court Historian strictly: (1) total records in the archive, (2) number of prior precedents for the current payload (`get_payload_precedents`), and (3) the last ruling on that specific payload.

### 4. Desktop Layout & UI Invariants
- **Single Sidebar Scrollbar:** On desktop (`> 900px`), `.sidebar-panel` must keep `overflow: hidden` with `flex-shrink: 0` on `.queue-card` and `.amazon-ad-card`, while `.ledger-card` (`flex: 1 1 auto; min-height: 175px; max-height: 520px;`) and `.ledger-list` (`flex: 1 1 auto; overflow-y: auto;`) scale dynamically to fit the screen without causing a second outer scrollbar on the right panel.
