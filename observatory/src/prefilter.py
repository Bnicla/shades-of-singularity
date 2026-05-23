"""
Cheap heuristic pre-filter for ingested items.

The triage LLM call is the most expensive step per item. Most items pulled
from broad feeds (arXiv categories, journal RSS, magazine RSS) have no
chance of touching any of the six essay axes. Dropping them on a keyword
match before they hit the LLM cuts triage volume by ~80% on real runs.

Design: generous OR-match against axis-relevant terms. False positives are
fine — they just incur a triage cost. False negatives are bad — we lose
material. The list errs toward inclusion.

Tier 1 (named scholars) bypasses this filter entirely; their output is
auto-adjudicated regardless of topic.
"""

import re

# Word-boundary keyword groups, organized by axis. Order doesn't matter;
# this is a single OR-match. Stems use trailing patterns where useful
# (e.g. "regulat" matches regulate/regulation/regulatory).
_KEYWORDS = [
    # LABOR / ECONOMY
    "labor", "labour", "employment", "employ", "unemploy", "job", "jobs",
    "occupation", "workforce", "worker", "automation", "automate",
    "displace", "displacement", "productivity", "wage", "wages",
    "economy", "economic", "macroeconomic", "gdp", "inequality",
    "task share", "task-share", "deskilling", "reskilling", "gig",

    # TRUTH / INFORMATION
    "misinformation", "disinformation", "provenance", "watermark",
    "deepfake", "verification", "fact-check", "factcheck", "epistemic",
    "manipulation", "integrity", "synthetic media",

    # POWER / GOVERNANCE
    "governance", "regulat", "policy", "antitrust", "surveillance",
    "democracy", "democratic", "accountability", "monopoly", "platform",
    "concentration", "lock-in", "lockin", "capture", "oligopoly",
    "election", "political",

    # HUMAN / DEVELOPMENT
    "cognitive", "cognition", "scaffold", "metacognition", "expertise",
    "deskill", "atrophy", "skill", "education", "classroom", "student",
    "learning outcome", "pedagog",

    # INHERITANCE
    "child", "children", "adolescent", "intergenerational",
    "sensitive period", "neuroplastic", "parenting", "developmental",

    # SAFETY / ALIGNMENT / GOV-TECH
    "alignment", "safety", "frontier", "rsp", "evaluation", "eval",
    "red team", "red-team", "open-weight", "open weight", "proliferation",
    "agi", "transformative ai", "oversight", "license", "licensing",
    "liability", "ai act", "audit",
]

# Compile once. Word boundary on both sides for short tokens; substring
# match for stems (those without trailing space/hyphen). We treat every
# entry as a substring match against a lowercased haystack — this is the
# generous behavior we want.
_PATTERN = re.compile("|".join(re.escape(k) for k in _KEYWORDS), re.IGNORECASE)


def passes_prefilter(item: dict) -> bool:
    """Return True if the item's title or abstract contains any axis-relevant term."""
    haystack = (item.get("title", "") + " " + item.get("abstract", "")).lower()
    return bool(_PATTERN.search(haystack))
