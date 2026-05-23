"""
Feedback calibration tool.

Run quarterly to analyze accumulated feedback signals and generate
recommendations for tuning the adjudication prompt.

Usage:
    python calibrate.py --local     # Read from local SQLite
    python calibrate.py --production  # Read from Vercel KV
"""

import argparse
import json
import logging
from collections import Counter

from dedup import DedupStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("observatory.calibrate")


def calibrate(mode: str = "local"):
    """Analyze feedback and produce calibration report."""
    store = DedupStore(mode=mode)
    feedback = store.get_feedback_log()

    if not feedback:
        print("No feedback accumulated yet. Mark items on the observatory page first.")
        return

    # Count signals
    signals = Counter(f["signal"] for f in feedback)
    total = len(feedback)

    print(f"\n{'='*60}")
    print(f"Observatory Calibration Report")
    print(f"{'='*60}")
    print(f"\nTotal feedback entries: {total}")
    print(f"  Integrated:   {signals.get('integrated', 0)} ({_pct(signals.get('integrated', 0), total)})")
    print(f"  Useful later: {signals.get('useful_later', 0)} ({_pct(signals.get('useful_later', 0), total)})")
    print(f"  Noise:        {signals.get('noise', 0)} ({_pct(signals.get('noise', 0), total)})")

    noise_rate = signals.get("noise", 0) / total if total > 0 else 0
    integrated_rate = signals.get("integrated", 0) / total if total > 0 else 0

    print(f"\n--- Diagnosis ---")

    if noise_rate > 0.4:
        print("\nHIGH NOISE RATE (>{:.0%}): The adjudication prompt is too generous.".format(noise_rate))
        print("Recommendations:")
        print("  1. Review noise-marked items for common patterns")
        print("  2. Add exclusion criteria to the adjudication prompt")
        print("  3. Consider raising the citation_quality threshold")
        print("  4. Check if specific axes are producing disproportionate noise")

    elif noise_rate < 0.1 and integrated_rate < 0.2:
        print("\nLOW INTEGRATION RATE with low noise: The bar may be appropriate")
        print("but the source list may need expansion, or the pipeline is")
        print("missing relevant material before it reaches adjudication.")
        print("Recommendations:")
        print("  1. Review triage drops for false negatives")
        print("  2. Consider adding new sources or scholars")

    elif integrated_rate > 0.3:
        print("\nHIGH INTEGRATION RATE (>{:.0%}): The system is working well.".format(integrated_rate))
        print("Consider whether the bar could be tightened slightly to")
        print("reduce review burden without missing material.")

    else:
        print("\nCalibration looks reasonable. No major adjustments needed.")

    # Per-axis breakdown (requires joining feedback with results)
    print(f"\n--- Axis-level detail ---")
    print("(Requires joining feedback fingerprints with stored results)")
    print("Run a manual review of the results database to identify which")
    print("axes produce the most noise and which produce the most integrations.")

    # Specific prompt tuning suggestions
    print(f"\n--- Prompt tuning checklist ---")
    print("  [ ] Review noise items: are they topically adjacent but argumentatively inert?")
    print("  [ ] Check if any claim IDs are never cited (may indicate the claim")
    print("      description doesn't match how authors actually write about the topic)")
    print("  [ ] Look for items that should have been flagged on multiple axes")
    print("      but were only tagged on one")
    print("  [ ] Verify that 'extends' relationship isn't being used as a catch-all")
    print("      for items that are merely topically related")
    print()


def _pct(n: int, total: int) -> str:
    return f"{n/total*100:.1f}%" if total > 0 else "0%"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Observatory calibration")
    parser.add_argument("--local", action="store_true", default=True)
    parser.add_argument("--production", action="store_true")
    args = parser.parse_args()
    mode = "production" if args.production else "local"
    calibrate(mode)
