"""
Observatory pipeline orchestrator.

Runs: ingest -> dedup -> TF-IDF rank -> synthesize candidate cards -> render.

Design note: the cron does NOT invoke an LLM. We tried LLM-in-the-loop
adjudication (Gemini 2.5 Flash, then Flash-Lite) and burned through
free-tier daily quotas reliably enough that the cron couldn't be trusted
to complete on any given day. The Karpathy / arxiv-sanity-lite pattern
sidesteps the problem entirely: TF-IDF over title+abstract, cosine
similarity against the axes.yaml claim seeds, present the top-N as
candidates. No LLM, no network calls past ingest, no quota dependency.

The LLM adjudicator remains in adjudicate.py and can be invoked
manually via --adjudicate for deep-evaluating specific items; it's just
not on the standing-monitor critical path.

Usage:
    python pipeline.py --local          # Local dev with SQLite
    python pipeline.py --production     # Production with Vercel KV
    python pipeline.py --backfill       # One-time backfill sweep
"""

import argparse
import json
import logging
import os
from datetime import datetime, timezone

from ingest import IngestManager
from dedup import DedupStore
from embed import EmbeddingFilter
from adjudicate import Adjudicator
from render import ObservatoryRenderer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("observatory")

# How many candidate cards to render per run. Top-N by TF-IDF score
# across all (tier-floored) items. The first HIGH_CONFIDENCE_CUTOFF
# of those are shown in the "clears" section, the rest in "flagged
# for review" — a soft prioritization, not an LLM verdict.
CANDIDATE_TOP_N = 15
HIGH_CONFIDENCE_CUTOFF = 5

# Tier-1 (named-scholar) items must clear this TF-IDF score before
# being eligible for ranking. Many tracked scholars (Nussbaum, etc.)
# publish across non-AI fields; without a floor their literary work
# floods the candidate list. 0.02 ≈ p25 of observed distribution.
TIER1_RELEVANCE_FLOOR = 0.02


def run_pipeline(mode: str = "local"):
    """Execute the full pipeline."""
    logger.info(f"Starting observatory pipeline in {mode} mode")
    start_time = datetime.now(timezone.utc)

    # GEMINI_API_KEY is no longer required for the cron path — left in
    # the environment so the manual --adjudicate mode (which does call
    # Gemini) still works without code changes.
    dedup = DedupStore(mode=mode)
    ingester = IngestManager(config_path="config/sources.yaml")
    relevance = EmbeddingFilter(axes_path="config/axes.yaml")
    renderer = ObservatoryRenderer(template_path="templates/observatory.html")

    # Step 1: Ingest
    # 8-day lookback covers the weekly cron cadence with a day of slack
    # for rescheduled runs and feed-publication lag.
    logger.info("Step 1: Ingesting from all sources")
    raw_items = ingester.fetch_all(lookback_days=8)
    logger.info(f"  Fetched {len(raw_items)} raw items")

    # Step 2: Dedup
    logger.info("Step 2: Deduplication")
    new_items = dedup.filter_new(raw_items)
    logger.info(f"  {len(new_items)} new items after dedup ({len(raw_items) - len(new_items)} seen before)")

    if not new_items:
        logger.info("No new items. Regenerating page with existing data.")
        existing = dedup.get_recent_results(days=30)
        renderer.render(existing, output_path=_output_path(mode))
        return

    # Step 3: Score all items with TF-IDF, apply tier-1 floor.
    tier1_all = [item for item in new_items if item.get("tier") == 1]
    other_items = [item for item in new_items if item.get("tier") != 1]

    logger.info(f"Step 3: TF-IDF relevance filter on {len(new_items)} items")
    relevance.score_items(other_items)
    relevance.score_items(tier1_all)
    relevance.log_score_distribution(other_items + tier1_all)

    tier1_items = [
        it for it in tier1_all
        if it.get("relevance_score", 0.0) >= TIER1_RELEVANCE_FLOOR
    ]
    tier1_dropped = len(tier1_all) - len(tier1_items)
    if tier1_dropped:
        logger.info(
            f"  Dropped {tier1_dropped} of {len(tier1_all)} tier-1 items "
            f"below relevance floor {TIER1_RELEVANCE_FLOOR}"
        )

    # Step 4: Pick top-N candidates by score and synthesize result dicts.
    # No LLM call here — the cron is intentionally LLM-free. See the
    # module docstring for the rationale.
    pool = tier1_items + other_items
    candidates = EmbeddingFilter.top_k(pool, CANDIDATE_TOP_N)
    if candidates:
        top_score = candidates[0].get("relevance_score", 0.0)
        bottom_score = candidates[-1].get("relevance_score", 0.0)
        logger.info(
            f"Step 4: Synthesizing {len(candidates)} candidate cards "
            f"(score range {bottom_score:.3f}-{top_score:.3f})"
        )
    else:
        logger.info("Step 4: No candidates after relevance filter")
    results = _synthesize_candidate_results(candidates)

    high = [r for r in results if r.get("confidence") == "high"]
    flagged = [r for r in results if r.get("confidence") == "medium"]
    logger.info(f"  {len(high)} top picks, {len(flagged)} flagged for review")

    # Step 5: Store results + mark items seen
    # We still keep the per-result records in KV so a future
    # accumulator/archive view can read them; for the current page we
    # just render this run's `results` directly because the existing
    # KV KEYS-pattern scan in _kv_get_recent_results doesn't reliably
    # return matches against Vercel KV.
    logger.info("Step 5: Storing results")
    dedup.mark_seen(raw_items)
    dedup.store_results(results)

    # Step 6: Render
    logger.info("Step 6: Rendering observatory page")
    output_path = _output_path(mode)
    renderer.render(results, output_path=output_path)

    # In production, push rendered HTML to KV for the serve function
    if mode == "production":
        logger.info("Pushing rendered HTML to KV")
        with open(output_path) as f:
            html = f.read()
        dedup._kv_set("observatory:current", html)

    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    logger.info(f"Pipeline complete in {elapsed:.1f}s. Output: {output_path}")


def run_backfill(mode: str = "local"):
    """One-time backfill sweep for the last 2-3 months."""
    logger.info("Starting backfill sweep")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set")

    ingester = IngestManager(config_path="config/sources.yaml")
    adjudicator = Adjudicator(api_key=api_key)
    renderer = ObservatoryRenderer(template_path="templates/observatory.html")

    # Fetch with extended lookback
    logger.info("Fetching with 90-day lookback")
    raw_items = ingester.fetch_all(lookback_days=90)
    logger.info(f"  Fetched {len(raw_items)} items from last 90 days")

    # No dedup for backfill; evaluate everything
    logger.info(f"Adjudicating all {len(raw_items)} items (backfill mode)")
    results = adjudicator.evaluate(raw_items)

    clears = [r for r in results if r["clears_bar"]]
    logger.info(f"  {len(clears)} items clear the bar")

    # Render backfill report
    renderer.render(
        results,
        output_path=_output_path(mode, suffix="_backfill"),
        title="Observatory Backfill: January - May 2026"
    )
    logger.info("Backfill complete")


def _synthesize_candidate_results(items: list[dict]) -> list[dict]:
    """
    Turn TF-IDF scored items into result dicts that match the schema the
    renderer expects from LLM adjudication. We populate fields from the
    relevance signals instead of from an LLM verdict.

    The first HIGH_CONFIDENCE_CUTOFF items by score are flagged
    confidence='high' so they land in the renderer's "clears" section;
    the rest get 'medium' and land in "flagged for review". That's
    purely cosmetic prioritization — there is no LLM verdict here.
    """
    ranked = sorted(
        items, key=lambda it: it.get("relevance_score", 0.0), reverse=True
    )
    results = []
    for rank, item in enumerate(ranked):
        abstract = item.get("abstract", "")
        summary = abstract[:280] + ("…" if len(abstract) > 280 else "")
        tier = item.get("tier", 0)
        citation_quality = {
            1: "working_paper",
            2: "policy_report",
            3: "blog_post",
        }.get(tier, "blog_post")

        top_matches = item.get("relevance_top") or []
        secondary = [cid for cid, _ in top_matches[1:]]
        score = item.get("relevance_score", 0.0)
        claim = item.get("relevance_claim", "")

        results.append({
            "clears_bar": True,
            "confidence": "high" if rank < HIGH_CONFIDENCE_CUTOFF else "medium",
            "primary_claim": claim,
            "secondary_claims": secondary,
            "relationship": None,
            "summary": summary,
            "citation_quality": citation_quality,
            "named_scholar_match": tier == 1,
            "integration_note": (
                f"TF-IDF candidate — surfaced because its abstract has the "
                f"closest vocabulary overlap with claim {claim} "
                f"(similarity {score:.3f}). Not yet adjudicated against the "
                f"essay claims."
            ),
            "item": {
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "authors": item.get("authors", []),
                "date": item.get("date", ""),
                "url": item.get("url", ""),
                "tier": tier,
                "named_scholar": item.get("named_scholar"),
                "relevance_score": score,
                "relevance_claim": claim,
            },
            "fingerprint": item.get("fingerprint", ""),
        })
    return results


def _output_path(mode: str, suffix: str = "") -> str:
    if mode == "local":
        os.makedirs("output", exist_ok=True)
        return f"output/observatory{suffix}.html"
    else:
        # Vercel serverless functions can only write to /tmp.
        # The rendered HTML is written here, then read back and pushed to KV.
        return f"/tmp/observatory{suffix}.html"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Observatory pipeline")
    parser.add_argument("--local", action="store_true", help="Run locally with SQLite")
    parser.add_argument("--production", action="store_true", help="Run with Vercel KV")
    parser.add_argument("--backfill", action="store_true", help="One-time backfill sweep")
    args = parser.parse_args()

    mode = "production" if args.production else "local"

    if args.backfill:
        run_backfill(mode)
    else:
        run_pipeline(mode)
