"""
Observatory pipeline orchestrator.

Runs: ingest -> dedup -> TF-IDF rank -> synthesize candidate cards ->
merge into accumulator blob -> render.

Design note: the cron does NOT invoke an LLM. We tried LLM-in-the-loop
adjudication (Gemini 2.5 Flash, then Flash-Lite) and burned through
free-tier daily quotas reliably enough that the cron couldn't be trusted
to complete on any given day. The Karpathy / arxiv-sanity-lite pattern
sidesteps the problem entirely: TF-IDF over title+abstract, cosine
similarity against the axes.yaml claim seeds, present the top-N as
candidates. No LLM, no network calls past ingest, no quota dependency.

The LLM adjudicator remains in adjudicate.py and can be invoked
manually for deep-evaluating specific items; it's just not on the
standing-monitor critical path.

Accumulator: candidates persist across runs in a single KV blob
(observatory:candidates_blob). Each run merges its new top-N into the
blob, dedupes by fingerprint, drops items older than MAX_BLOB_AGE_DAYS,
and trims to MAX_BLOB_TOTAL by relevance score. The page renders the
merged blob (with user-flagged "noise" items hidden), so a one-shot
backfill plus a weekly cron together produce a steady, curated digest.

Usage:
    python pipeline.py --local                       # SQLite dev mode
    python pipeline.py --production                  # Vercel KV
    python pipeline.py --backfill --production       # one-shot backfill
"""

import argparse
import json
import logging
import os
from datetime import datetime, timedelta, timezone

from ingest import IngestManager
from dedup import DedupStore
from embed import EmbeddingFilter
from render import ObservatoryRenderer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("observatory")

# Weekly run: how many new candidates the pipeline synthesizes per run.
CANDIDATE_TOP_N = 15

# Backfill run: how many candidates to keep from the full ~5-month window.
BACKFILL_TOP_N = 60

# Accumulator (persisted in KV across runs)
MAX_BLOB_TOTAL = 60        # total cards kept after merge + prune
MAX_BLOB_AGE_DAYS = 180    # drop items older than this from the blob

# Top this many items in the final blob get the "high" confidence label
# (shown in the renderer's "Clears the bar" section). The rest go to
# "flagged for review". Cosmetic prioritization only.
HIGH_CONFIDENCE_CUTOFF = 10

# Tier-1 (named-scholar) items must clear this TF-IDF score before
# being eligible for ranking. Many tracked scholars (Nussbaum, etc.)
# publish across non-AI fields; without a floor their literary work
# floods the candidate list. 0.02 ≈ p25 of observed distribution.
TIER1_RELEVANCE_FLOOR = 0.02


def run_pipeline(
    mode: str = "local",
    *,
    lookback_days: int = 8,
    top_n: int = CANDIDATE_TOP_N,
    skip_dedup: bool = False,
    label: str = "weekly",
):
    """
    Execute the pipeline.

    `lookback_days` and `top_n` are tuned per call-site:
      weekly:   8 days, top 15 new candidates
      backfill: 150 days, top 60 new candidates

    `skip_dedup=True` (used by backfill) ignores prior "seen" state so
    every item in the lookback window is scored fresh. Items still get
    marked seen at the end so the next weekly run doesn't re-process
    them.
    """
    logger.info(f"Starting observatory pipeline ({label}) in {mode} mode")
    start_time = datetime.now(timezone.utc)

    dedup = DedupStore(mode=mode)
    ingester = IngestManager(config_path="config/sources.yaml")
    relevance = EmbeddingFilter(axes_path="config/axes.yaml")
    renderer = ObservatoryRenderer(template_path="templates/observatory.html")

    # Step 1: Ingest
    logger.info(f"Step 1: Ingesting (lookback={lookback_days}d)")
    raw_items = ingester.fetch_all(lookback_days=lookback_days)
    logger.info(f"  Fetched {len(raw_items)} raw items")

    # Step 2: Dedup
    # Backfill skips the cross-run `seen` check but still collapses
    # intra-batch duplicates (multiple arXiv search feeds hitting the
    # same paper).
    if skip_dedup:
        new_items = DedupStore.dedup_within_batch(raw_items)
        logger.info(
            f"Step 2: {len(new_items)} items after intra-batch dedup "
            f"(backfill mode, cross-run dedup skipped)"
        )
    else:
        new_items = dedup.filter_new(raw_items)
        logger.info(
            f"Step 2: {len(new_items)} new items after dedup "
            f"({len(raw_items) - len(new_items)} seen before or duplicate in batch)"
        )

    # Step 3: Score with TF-IDF, apply tier-1 floor
    new_results: list[dict] = []
    if new_items:
        tier1_all = [it for it in new_items if it.get("tier") == 1]
        other_items = [it for it in new_items if it.get("tier") != 1]

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

        # Step 4: Synthesize new candidate result dicts (no LLM)
        pool = tier1_items + other_items
        candidates = EmbeddingFilter.top_k(pool, top_n)
        if candidates:
            logger.info(
                f"Step 4: Synthesizing {len(candidates)} new candidate cards "
                f"(score range "
                f"{candidates[-1].get('relevance_score', 0.0):.3f}-"
                f"{candidates[0].get('relevance_score', 0.0):.3f})"
            )
        new_results = _synthesize_candidate_results(candidates)
    else:
        logger.info("Step 3/4: No new items to score; will refresh page from existing blob")

    # Step 5: Merge into the candidates blob, prune, re-rank.
    # Anything already filed (in filed_blob) is excluded — it's no
    # longer pending.
    filed_blob = dedup.load_filed_blob()
    filed_fps = {c.get("fingerprint", "") for c in filed_blob if c.get("fingerprint")}

    existing_blob = dedup.load_candidates_blob()
    logger.info(
        f"Step 5: Loaded {len(existing_blob)} pending + {len(filed_blob)} filed "
        f"from KV"
    )
    new_results_unfiled = [
        r for r in new_results if r.get("fingerprint", "") not in filed_fps
    ]
    if len(new_results_unfiled) < len(new_results):
        logger.info(
            f"  Skipped {len(new_results) - len(new_results_unfiled)} new items "
            f"that are already filed"
        )

    merged_candidates = _merge_and_rerank(
        existing_blob, new_results_unfiled,
        max_total=MAX_BLOB_TOTAL,
        max_age_days=MAX_BLOB_AGE_DAYS,
    )
    # Defensive: drop anything filed that snuck in.
    merged_candidates = [c for c in merged_candidates if c.get("fingerprint", "") not in filed_fps]
    logger.info(f"  Candidates after merge: {len(merged_candidates)} items")
    dedup.save_candidates_blob(merged_candidates)

    # Step 6: Persist seen state and per-result records (latter is legacy)
    dedup.mark_seen(raw_items)
    if new_results:
        dedup.store_results(new_results)

    # Step 7: Render — passes both blobs so the renderer can split into
    # Pending / Integrated / Useful later / Noise tabs.
    logger.info(
        f"Step 7: Rendering ({len(merged_candidates)} pending, "
        f"{len(filed_blob)} filed)"
    )
    output_path = _output_path(mode)
    renderer.render(
        merged_candidates,
        output_path=output_path,
        filed=filed_blob,
    )

    if mode == "production":
        logger.info("Pushing rendered HTML to KV")
        with open(output_path) as f:
            html = f.read()
        dedup._kv_set("observatory:current", html)

    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    logger.info(f"Pipeline complete in {elapsed:.1f}s. Output: {output_path}")


def run_backfill(mode: str = "local"):
    """One-shot historical sweep: 150-day lookback, top 60 candidates.

    Wipes the candidates blob first. By definition a backfill is a
    "redo from scratch" — without wiping, items written by prior runs
    (potentially with stale fingerprints, e.g. before arXiv URL
    canonicalization) would carry forward as duplicates of the new
    sweep's entries.
    """
    dedup = DedupStore(mode=mode)
    logger.info("Backfill: wiping observatory:candidates_blob before re-sweep")
    dedup.save_candidates_blob([])
    run_pipeline(
        mode,
        lookback_days=150,
        top_n=BACKFILL_TOP_N,
        skip_dedup=True,
        label="backfill",
    )


def _merge_and_rerank(
    existing: list[dict],
    new: list[dict],
    *,
    max_total: int,
    max_age_days: int,
) -> list[dict]:
    """
    Merge new candidate results into the existing blob.

    - Dedupe by fingerprint (new entries overwrite existing).
    - Drop items whose item.date is older than max_age_days.
    - Sort by item.relevance_score (desc).
    - Cap to max_total.
    - Reassign confidence based on final rank (top HIGH_CONFIDENCE_CUTOFF
      get "high", rest "medium").
    """
    by_fp: dict[str, dict] = {}
    for c in existing:
        fp = c.get("fingerprint", "")
        if fp:
            by_fp[fp] = c
    for c in new:
        fp = c.get("fingerprint", "")
        if fp:
            by_fp[fp] = c

    cutoff_iso = (
        datetime.now(timezone.utc) - timedelta(days=max_age_days)
    ).isoformat()

    def _date_ok(card: dict) -> bool:
        d = (card.get("item") or {}).get("date") or ""
        # Missing date = keep (some sources don't expose pub date)
        return (not d) or (d >= cutoff_iso[:10]) or (d >= cutoff_iso)

    pruned = [c for c in by_fp.values() if _date_ok(c)]
    pruned.sort(
        key=lambda c: (c.get("item") or {}).get("relevance_score", 0.0),
        reverse=True,
    )
    pruned = pruned[:max_total]

    for rank, card in enumerate(pruned):
        card["confidence"] = "high" if rank < HIGH_CONFIDENCE_CUTOFF else "medium"

    return pruned


def _synthesize_candidate_results(items: list[dict]) -> list[dict]:
    """
    Turn TF-IDF scored items into result dicts that match the schema the
    renderer expects from LLM adjudication. Confidence is set to
    "medium" here; _merge_and_rerank reassigns based on the final
    global rank in the merged blob.
    """
    results = []
    for item in items:
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
            "confidence": "medium",
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
