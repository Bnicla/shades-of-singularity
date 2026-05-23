# Observatory Integration Instructions for Claude Code

## Overview

These instructions integrate the Observatory research monitor into the
shadesofsingularity.com Vercel deployment. The observatory is FULLY DECOUPLED
from the Astro build. It runs as two Vercel serverless functions:

1. A cron function that executes the pipeline daily
2. A serve function that returns the rendered HTML page

A rewrite rule in vercel.json proxies `/observatory` to the serve function,
keeping the URL on-domain without touching Astro's content collections or nav.

## File placement

Copy the following into the project root:

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

Copy the API functions to the project's `api/` directory (create if it doesn't exist):

```
api/
├── observatory-run.py
└── observatory-serve.py
```

## vercel.json modifications

Add to the existing vercel.json (or create if absent). Merge with any
existing configuration; do NOT overwrite existing rules.

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

The cron runs at 10:00 UTC (6:00 AM ET) daily.
The rewrite makes the page accessible at shadesofsingularity.com/observatory.

## Environment variables

Set these in the Vercel dashboard under Settings > Environment Variables:

- `ANTHROPIC_API_KEY`: Anthropic API key for triage (Haiku) and adjudication (Sonnet) calls
- `KV_REST_API_URL`: Vercel KV store REST endpoint
- `KV_REST_API_TOKEN`: Vercel KV store auth token
- `CRON_SECRET` (optional): If set, the cron endpoint requires this as a Bearer token

## Vercel KV setup

Create a KV store in the Vercel dashboard (Storage > KV) and link it to
the project. The environment variables above will be auto-populated.

The pipeline uses KV for three purposes:
1. `seen:*` keys - deduplication (90-day TTL)
2. `result:*` keys - adjudication results (180-day TTL)
3. `observatory:current` - the latest rendered HTML page (no TTL)
4. `feedback:*` keys - user feedback signals (no TTL)

## What NOT to touch

- Do NOT add observatory to any Astro content collection
- Do NOT add observatory to site navigation
- Do NOT add observatory to sitemap or robots.txt
- Do NOT import observatory modules into Astro components
- The observatory page includes its own `<meta name="robots" content="noindex, nofollow">`

## Python runtime

Vercel's Python runtime handles the serverless functions in `api/`.
The `requirements.txt` in the observatory directory lists dependencies.
Vercel will install them automatically for the Python serverless functions.

Note: Vercel Python functions need a `requirements.txt` at the project root
or in the `api/` directory. If the project root already has a `requirements.txt`
for other purposes, merge the observatory dependencies into it. Otherwise,
copy `observatory/requirements.txt` to the project root.

## Verification

After deployment:

1. Visit `shadesofsingularity.com/observatory` - should show the fallback page
   ("The research monitor is initializing")
2. Manually trigger the cron by visiting `/api/observatory-run` (if CRON_SECRET
   is not set) or wait for the next scheduled run
3. After the pipeline runs, `/observatory` should show the rendered digest

## Feedback API (not yet built)

The observatory page includes feedback buttons (Integrated / Useful later / Noise)
with JavaScript `sendFeedback()` calls, but the feedback API endpoint doesn't
exist yet. To complete the feedback loop, add a third API function:

```
api/observatory-feedback.py
```

That accepts POST requests with `{fingerprint, signal}` and stores them in KV.
This is a future enhancement; the buttons will silently fail until it's built.

## Local development

To run the pipeline locally without Vercel:

```bash
cd observatory
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python src/pipeline.py --local
open output/observatory.html
```

This uses SQLite instead of Vercel KV and writes output to `observatory/output/`.
