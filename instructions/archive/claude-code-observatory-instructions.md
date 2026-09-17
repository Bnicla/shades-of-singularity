# Observatory Integration — Claude Code Master Instructions

## Context

Observatory is an automated research monitoring pipeline for the Shades of Singularity essay collection. It runs as two Vercel serverless functions completely decoupled from the Astro site. The pipeline scans ~40 academic feeds, lab blogs, and policy outlets daily, filters items through a two-stage LLM evaluation (cheap triage then expensive adjudication against specific essay claims), renders a static HTML digest, and stores it in Vercel KV. A rewrite rule proxies `/observatory` to the serve function so the page lives on-domain without touching Astro.

All source files are in the `observatory/` tarball. This document tells you exactly what to do with them.

## Prerequisites (manual, done by Boris before you start)

1. Vercel KV store created in the Vercel dashboard (Storage > KV) and linked to the shadesofsingularity project. This auto-populates `KV_REST_API_URL` and `KV_REST_API_TOKEN` as environment variables.
2. `ANTHROPIC_API_KEY` set in Vercel dashboard under Settings > Environment Variables.
3. The `observatory/` tarball extracted somewhere accessible.

Confirm with Boris that these three prerequisites are done before proceeding.

---

## Step 1: Place observatory files in the project

Create an `observatory/` directory at the project root (sibling to `src/`, `content/`, `public/`).

Copy into it:
```
observatory/
├── config/
│   ├── sources.yaml
│   └── axes.yaml
├── src/
│   ├── pipeline.py
│   ├── ingest.py
│   ├── dedup.py
│   ├── triage.py
│   ├── adjudicate.py
│   ├── render.py
│   ├── prompts.py
│   └── calibrate.py
└── requirements.txt
```

Do NOT place these inside the Astro `src/` directory. `observatory/` is a top-level directory.

## Step 2: Place API functions

Create an `api/` directory at the project root if it does not already exist.

Copy into it:
```
api/
├── observatory-run.py
└── observatory-serve.py
```

These are Vercel serverless functions. Vercel auto-detects Python files in `api/`.

## Step 3: Fix import paths in API functions

The API functions import from `observatory/src/`. The `sys.path.insert` line in `observatory-run.py` needs to resolve correctly from Vercel's execution context.

In `api/observatory-run.py`, find:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "observatory", "src"))
```

Verify this resolves to the correct path. If the project root is the working directory at runtime, this should work. If not, adjust to:
```python
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "observatory", "src"))
```

Also add a config path fix in `observatory-run.py`. The pipeline loads `config/sources.yaml` with a relative path. Add before the `run_pipeline` call:
```python
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "observatory"))
```

## Step 4: Place requirements.txt

Vercel Python functions need dependencies declared. Check if a `requirements.txt` already exists at the project root.

- If NO existing `requirements.txt`: copy `observatory/requirements.txt` to the project root.
- If YES existing `requirements.txt`: merge the following dependencies into it (skip duplicates):
  ```
  anthropic>=0.40.0
  feedparser>=6.0.0
  requests>=2.31.0
  python-dateutil>=2.8.0
  pyyaml>=6.0
  jinja2>=3.1.0
  ```

## Step 5: Modify vercel.json

Open `vercel.json` in the project root. If it does not exist, create it.

Add the following, merging with any existing configuration. Do NOT overwrite existing crons or rewrites.

Add to `crons` array (create if absent):
```json
{
  "path": "/api/observatory-run",
  "schedule": "0 10 * * *"
}
```

Add to `rewrites` array (create if absent):
```json
{
  "source": "/observatory",
  "destination": "/api/observatory-serve"
}
```

The final `vercel.json` should look something like (preserving any existing entries):
```json
{
  "crons": [
    {
      "path": "/api/observatory-run",
      "schedule": "0 10 * * *"
    }
  ],
  "rewrites": [
    {
      "source": "/observatory",
      "destination": "/api/observatory-serve"
    }
  ]
}
```

## Step 6: Verify nothing bleeds into Astro

Run these checks:

1. `observatory/` is NOT referenced in `astro.config.mjs`
2. `observatory/` is NOT referenced in `src/content.config.ts`
3. No Astro component imports anything from `observatory/`
4. The nav component does NOT include `/observatory`
5. If a `sitemap` integration exists, `/observatory` is excluded
6. `public/robots.txt` does NOT reference `/observatory` (the page handles its own noindex via meta tag)

## Step 7: Test the Astro build

Run:
```bash
npm run build
```

The Astro build should complete without errors. The `observatory/` directory should be invisible to Astro — it has no `.astro`, `.md`, or `.ts` files that Astro would try to process.

## Step 8: Deploy

```bash
npx vercel --prod
```

## Step 9: Verify deployment

After deploy:

1. Visit `shadesofsingularity.com/observatory` — should show the fallback page ("The research monitor is initializing. The first scan has not yet run.")
2. The cron will run automatically at 10:00 UTC (6:00 AM ET) the next day
3. To trigger the first run manually: visit `shadesofsingularity.com/api/observatory-run` in a browser (only works if `CRON_SECRET` is not set; if it is, the manual trigger requires the Bearer token)

After the first pipeline run, `/observatory` should display the rendered digest with any items that cleared the bar.

---

## What NOT to do

- Do NOT add observatory to any Astro content collection
- Do NOT add observatory to site navigation
- Do NOT add observatory to sitemap
- Do NOT import observatory Python modules into any Astro/JS/TS files
- Do NOT modify any existing Astro pages, components, layouts, or styles
- Do NOT create a `templates/` directory or Jinja2 template file — the renderer has an inline fallback that generates the HTML directly

## Troubleshooting

If the Astro build fails after adding `observatory/`:
- Check that no `.md` files exist inside `observatory/` that Astro might try to collect (the README.md and INTEGRATION.md should be fine since they're not in a content collection path, but if Astro complains, add them to `.gitignore` or remove them)

If `/observatory` returns 404:
- Check that the rewrite rule is in `vercel.json`
- Check that `api/observatory-serve.py` exists and is a valid Python file
- Check Vercel function logs in the dashboard

If `/api/observatory-run` returns 500:
- Check Vercel function logs for the specific error
- Most likely: missing environment variables (`ANTHROPIC_API_KEY`, `KV_REST_API_URL`, `KV_REST_API_TOKEN`)
- Or: import path issue (Step 3 not correctly resolved)
