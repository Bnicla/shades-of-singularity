"""
Inject a single URL into the observatory by hand.

Use when a piece of content the standing monitor would have missed
deserves to be on the page — e.g., a one-off document that doesn't
sit on any of our RSS sources. Adds a card to either the
candidates_blob (signal=pending) or the filed_blob (any other signal),
fingerprint-canonicalized so a future cron pulling the same URL via
a feed won't create a duplicate.

Usage:
    python inject_card.py \\
        --production \\
        --url   "https://www.vaticannews.va/en/pope/news/2026-05/..." \\
        --title "Magnifica Humanitas: Pope Leo XIV's AI encyclical" \\
        --signal pending \\
        --summary "First major papal text on AI..." \\
        --source "Vatican News"
"""

import argparse
import logging
import sys
from datetime import datetime, timezone

from dedup import DedupStore
from embed import EmbeddingFilter
from ingest import _canonical_url

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("observatory.inject_card")


VALID_SIGNALS = {"pending", "integrated", "useful_later", "noise"}


def build_card(
    *,
    url: str,
    title: str,
    signal: str,
    summary: str = "",
    source: str = "",
    relevance: EmbeddingFilter,
    now_iso: str,
) -> dict:
    fp = _canonical_url(url)

    # Score against the claim seeds so the chip lights up the right axis
    item = {"fingerprint": fp, "title": title, "abstract": summary or title}
    relevance.score_items([item])
    claim = item.get("relevance_claim", "")
    score = item.get("relevance_score", 0.0)
    top = item.get("relevance_top") or []

    card = {
        "fingerprint": fp,
        "clears_bar": True,
        "confidence": "high",
        "primary_claim": claim,
        "secondary_claims": [cid for cid, _ in top[1:]],
        "relationship": None,
        "summary": summary or title,
        "citation_quality": "policy_report",
        "named_scholar_match": False,
        "integration_note": "",
        "source_of_truth": "manual_inject",
        "item": {
            "title": title,
            "source": source or "Manual",
            "authors": [],
            "date": now_iso[:10],
            "url": url,
            "tier": 2,
            "relevance_score": score,
            "relevance_claim": claim,
        },
    }
    if signal != "pending":
        card["signal"] = signal
        card["filed_at"] = now_iso
    return card


def main():
    parser = argparse.ArgumentParser(description="Inject a URL into the observatory")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--production", action="store_true")
    parser.add_argument("--url", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--signal", choices=sorted(VALID_SIGNALS), default="pending")
    parser.add_argument("--summary", default="")
    parser.add_argument("--source", default="")
    args = parser.parse_args()

    mode = "production" if args.production else "local"
    dedup = DedupStore(mode=mode)
    relevance = EmbeddingFilter(axes_path="config/axes.yaml")
    now_iso = datetime.now(timezone.utc).isoformat()

    card = build_card(
        url=args.url, title=args.title, signal=args.signal,
        summary=args.summary, source=args.source,
        relevance=relevance, now_iso=now_iso,
    )

    target = "filed" if args.signal != "pending" else "candidates"
    if target == "candidates":
        blob = dedup.load_candidates_blob()
    else:
        blob = dedup.load_filed_blob()

    fp = card["fingerprint"]
    existing_idx = next((i for i, c in enumerate(blob) if c.get("fingerprint") == fp), None)
    if existing_idx is not None:
        logger.warning(
            f"Card with fingerprint {fp} already exists in {target}_blob; "
            f"updating in place."
        )
        # Preserve user signal if present
        if "signal" in blob[existing_idx] and args.signal == "pending":
            logger.info(f"  Existing signal '{blob[existing_idx]['signal']}' preserved")
            return
        blob[existing_idx] = card
    else:
        blob.append(card)

    if target == "candidates":
        dedup.save_candidates_blob(blob)
    else:
        dedup.save_filed_blob(blob)

    logger.info(
        f"Injected card: title='{args.title[:60]}', signal={args.signal}, "
        f"primary_claim={card['primary_claim']}, score={card['item']['relevance_score']:.3f}, "
        f"fp={fp[:60]}"
    )


if __name__ == "__main__":
    main()
