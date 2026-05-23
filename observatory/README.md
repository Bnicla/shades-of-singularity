# Observatory

A private monitoring pipeline for the *Shades of Singularity* essay collection.
Watches academic feeds, lab blogs, and policy outlets daily, filters for material
that would justify integration into one of the six essays or thirty shades, and
renders a self-updating digest page at a hidden URL on the site.

## Architecture

```
                  ┌─────────────┐
                  │  Cron (daily)│
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │   Ingest    │  RSS/Atom feeds, API polling
                  │  (sources)  │  ~40 feeds across 3 tiers
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │   Dedup     │  Fingerprint check against KV store
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │   Triage    │  Haiku-class: does it touch an axis?
                  │  (cheap)    │  Generous filter, drops obvious noise
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │ Adjudicate  │  Sonnet-class: which claim does it
                  │ (expensive) │  bear on? What's the relationship?
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │   Render    │  Static HTML digest, styled to match
                  │             │  shadesofsingularity.com aesthetic
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │   Serve     │  Vercel KV + serverless function
                  │             │  at /observatory
                  └─────────────┘
```

## Source tiers

| Tier | Description | Triage? | Examples |
|------|-------------|---------|----------|
| 1 | Named scholars — new output from specific researchers | No (auto-adjudicate) | Acemoglu, Hooker, Allen, Hadfield, Pettit |
| 2 | Institutional feeds — high-volume, needs filtering | Yes | arXiv, NBER, IMF, Brookings, lab blogs |
| 3 | Editorial — rigorous enough to cite | Yes | Science, Nature, Foreign Affairs, HBR |

## Setup

### Prerequisites

- Python 3.11+
- Anthropic API key
- Vercel account (already configured for shadesofsingularity.com)
- Vercel KV store (for dedup state and rendered HTML cache)

### Environment variables

```bash
ANTHROPIC_API_KEY=sk-ant-...        # For triage + adjudication LLM calls
KV_REST_API_URL=...                 # Vercel KV endpoint
KV_REST_API_TOKEN=...               # Vercel KV auth token
```

### Local development

```bash
cd observatory
pip install -r requirements.txt

# Run pipeline locally (uses SQLite instead of KV)
python src/pipeline.py --local

# Preview the rendered HTML
open output/observatory.html
```

### Deployment to Vercel

Two components to deploy:

1. **The pipeline** runs as a Vercel Cron Function (daily at 6 AM ET).
   Add to your site's `vercel.json`:

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

2. **The serve function** reads the latest rendered HTML from KV and returns it.

   Both serverless functions live in `api/` in your Astro project root.

### Integration with the Astro site

The observatory is intentionally decoupled from Astro's build.
No content collection, no Astro component, no nav link.
It's a raw serverless function that serves pre-rendered HTML.

To integrate:
1. Copy `api/observatory-run.py` and `api/observatory-serve.py` to your project's `api/` directory
2. Copy `src/` and `config/` to a location accessible by the serverless functions
3. Add the cron and rewrite rules to `vercel.json`
4. Set environment variables in Vercel dashboard
5. Deploy with `npx vercel --prod`

The `/observatory` URL will not appear in navigation, sitemap, or robots.txt.

## Feedback loop

The observatory page includes discreet feedback controls on each card.
Marking items as "integrated," "useful later," or "noise" stores signals
in KV that are used to refine the adjudication prompt over time.

Run `python src/calibrate.py` quarterly to review accumulated feedback
and generate prompt refinement suggestions.

## File structure

```
observatory/
├── README.md
├── requirements.txt
├── config/
│   ├── sources.yaml          # Feed URLs and scholar lists
│   └── axes.yaml             # Essay axes with load-bearing claims
├── src/
│   ├── pipeline.py           # Main orchestrator
│   ├── ingest.py             # Feed fetching and parsing
│   ├── dedup.py              # Fingerprinting and state management
│   ├── triage.py             # Cheap LLM pass (axis detection)
│   ├── adjudicate.py         # Expensive LLM pass (claim-level analysis)
│   ├── render.py             # HTML generation
│   ├── prompts.py            # All LLM prompts
│   └── calibrate.py          # Feedback analysis and prompt tuning
├── templates/
│   └── observatory.html      # Jinja2 template for the digest page
├── api/
│   ├── observatory-run.py    # Vercel cron function (pipeline trigger)
│   └── observatory-serve.py  # Vercel serverless function (page serving)
└── output/                   # Local dev output (gitignored)
```
