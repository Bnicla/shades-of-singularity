"""
Observatory pipeline orchestrator.

Runs: ingest -> dedup -> embedding relevance filter -> adjudicate -> render.

The relevance step uses text-embedding-004 (free on Gemini free tier) to
cosine-match each item against the 20 load-bearing claims in axes.yaml.
That replaces what used to be a regex prefilter + an LLM-triage step,
and it cuts the number of items that reach the expensive Gemini 2.5
Flash adjudicator to the handful that are semantically on-topic.

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


def run_pipeline(mode: str = "local"):
    """Execute the full pipeline."""
    logger.info(f"Starting observatory pipeline in {mode} mode")
    start_time = datetime.now(timezone.utc)

    # Initialize components
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set")

    dedup = DedupStore(mode=mode)
    ingester = IngestManager(config_path="config/sources.yaml")
    relevance = EmbeddingFilter(api_key=api_key, axes_path="config/axes.yaml")
    adjudicator = Adjudicator(api_key=api_key)
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

    # Step 3: Relevance filter (embeddings).
    # Tier 1 (named-scholar) items bypass the filter — their output is
    # auto-adjudicated regardless of topic. Everything else is embedded with
    # text-embedding-004 and dropped if its top-claim cosine similarity is
    # below the threshold.
    tier1_items = [item for item in new_items if item.get("tier") == 1]
    other_items = [item for item in new_items if item.get("tier") != 1]

    logger.info(f"Step 3: Embedding relevance filter on {len(other_items)} non-tier-1 items")
    relevance.score_items(other_items)
    # Also score tier 1 so we can pass the top-claim hint into adjudicate,
    # but never drop them.
    relevance.score_items(tier1_items)

    kept_other = relevance.filter(other_items)
    logger.info(
        f"  {len(kept_other)} of {len(other_items)} items cleared the "
        f"{relevance.threshold:.2f} similarity threshold "
        f"(+ {len(tier1_items)} tier-1 bypassing)"
    )

    to_adjudicate = tier1_items + kept_other

    # Step 4: Adjudicate
    logger.info(f"Step 4: Adjudication ({len(to_adjudicate)} items)")
    results = adjudicator.evaluate(to_adjudicate)

    high_confidence = [r for r in results if r["confidence"] == "high"]
    medium_confidence = [r for r in results if r["confidence"] == "medium"]
    dropped = [r for r in results if r["confidence"] == "low" or not r["clears_bar"]]

    logger.info(f"  High confidence (auto-file): {len(high_confidence)}")
    logger.info(f"  Medium confidence (flagged): {len(medium_confidence)}")
    logger.info(f"  Dropped: {len(dropped)}")

    # Step 5: Store results
    logger.info("Step 5: Storing results")
    dedup.mark_seen(raw_items)
    dedup.store_results(results)

    # Step 6: Render
    logger.info("Step 6: Rendering observatory page")
    all_recent = dedup.get_recent_results(days=30)
    output_path = _output_path(mode)
    renderer.render(all_recent, output_path=output_path)

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
