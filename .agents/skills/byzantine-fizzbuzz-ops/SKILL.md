---
name: byzantine-fizzbuzz-ops
description: >-
  Build, test, deploy, and update the FizzBuzz: The Inquisition live web application
  (byzantine-fizzbuzz-live container on port 8095 / fizzbuzz.adamoutler.com), including
  pytest verification, Service Worker cache-busting, and Open Graph asset generation.
---

# FizzBuzz: The Inquisition — Operations & Deployment Runbook

Use this skill whenever modifying, testing, or deploying `active-projects/byzantine-fizzbuzz/web`.

## 1. Running the Unit & Integration Test Suite
Always run `pytest` from `web/` with `PYTHONPATH=.` using the local `.venv`:

```bash
cd /home/adamoutler/MeatloafBot/active-projects/byzantine-fizzbuzz/web
PYTHONPATH=. .venv/bin/pytest tests/ -v
```

All 27 tests (`test_ledger.py`, `test_observer_manager.py`, `test_primitives.py`, `test_pwa_metadata.py`, `test_sanitization.py`, `test_scheduler.py`, `test_structured_adjudication.py`, `test_structured_engine.py`) must pass before deployment.

## 2. Deploying to the Live Container (`byzantine-fizzbuzz-live`)
The live production container `byzantine-fizzbuzz-live` listens on `0.0.0.0:8095->8000` (proxied by `https://fizzbuzz.adamoutler.com/`) and mounts `./data:/data` (`/data/dockets.db`).

### A. Fast Code/Asset Sync (No Env Changes)
To deploy Python or static file updates without rebuilding the Docker image:

```bash
cd /home/adamoutler/MeatloafBot/active-projects/byzantine-fizzbuzz/web
docker cp app/. byzantine-fizzbuzz-live:/app/app/
docker restart byzantine-fizzbuzz-live
```
*(Note: For pure static file edits in `app/static/`, `docker cp` takes effect immediately without requiring `docker restart`.)*

### B. Container Recreation (When `docker-compose.yml` or Env Vars Change)
When modifying environment variables in `docker-compose.yml` (such as `RECESS_SECONDS=30` or `OLLAMA_MODEL`), recreate the container and sync `app/`:

```bash
cd /home/adamoutler/MeatloafBot/active-projects/byzantine-fizzbuzz/web
docker compose up -d --force-recreate
docker cp app/. byzantine-fizzbuzz-live:/app/app/
docker restart byzantine-fizzbuzz-live
```

### C. Post-Deploy Verification
Verify health, archive ordering, and active configuration:

```bash
curl -s http://localhost:8095/api/health
curl -s "http://localhost:8095/api/archives?order=desc" | head -c 400
```

## 3. PWA & Service Worker Cache-Busting
Whenever `app/static/styles.css`, `app/static/app.js`, or `app/static/sw.js` is modified:
1. Increment the `?v=YYYYMMDD-N` query string in `app/static/index.html` on `<link rel="stylesheet" href="/static/styles.css?v=...">`, `<script src="/static/app.js?v=...">`, and `navigator.serviceWorker.register('/sw.js?v=...')`.
2. Increment `CACHE_NAME` (`fizzbuzz-inquisition-vN`) and the `PRECACHE_ASSETS` URLs in `app/static/sw.js` to match.

## 4. Regenerating PWA Icons & Open Graph Banner (`og-image.png`)
To update the social preview graphic (`app/static/icons/og-image.png`) or PWA icons:
1. Edit `scripts/generate_assets.py`.
   - **Important:** Linux ImageMagick `convert` does not render color emoji glyphs (`🔴`, `⚖️`, `🔷`) inside SVG `<text>`. Always use native SVG vector shapes (`<circle>`, `<polygon>`, `<rect>`, `<path>`) for badges and icons.
   - Keep `og:site_name` (`Adam Outler`), `og:title` (`FizzBuzz: The Inquisition 🔴 LIVE`), `og:description`, and the graphic's internal text distinct so Discord and Telegram embeds do not repeat the same lines.
2. Run the generator script:
   ```bash
   python3 /home/adamoutler/MeatloafBot/active-projects/byzantine-fizzbuzz/web/scripts/generate_assets.py
   ```
3. Increment the `?v=liveN` query parameter on `og:image`, `og:image:secure_url`, and `twitter:image` in `app/static/index.html`.
   - Note: Telegram and Discord cache link previews by URL. Append a new query parameter when testing in chat (e.g. `https://fizzbuzz.adamoutler.com/?live`) or flush Telegram's cache via `@WebpageBot`.
