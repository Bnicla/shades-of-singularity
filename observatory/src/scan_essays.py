"""
Scan the published essays + scenarios for existing citations and seed
observatory:filed_blob with one card per unique URL, signal='integrated'.

Run via:
    python src/scan_essays.py --local        # local SQLite/JSON
    python src/scan_essays.py --production   # writes to Vercel KV

Or via the GitHub Actions workflow with `mode=scan-essays`.

Design
------
- Walks ../content/essays/*.md and ../content/scenarios/*.md (relative
  to observatory/, which is the cwd in the workflow).
- Pulls every markdown `[anchor](url)` pair plus footnote definitions
  `[^N]: ... [anchor](url) ...`.
- Skips internal links, anchor-only links, and image links.
- Canonicalizes URLs (arXiv via observatory.src.ingest._canonical_url)
  so /abs/1234v1 and /pdf/1234v2.pdf collapse to the same fingerprint.
- Builds one card per unique fingerprint; if the same URL is cited from
  multiple files, the integration_note lists all of them.
- Scores each card with the existing TF-IDF EmbeddingFilter so cards
  inherit the same primary_claim assignment as cron-produced cards
  (keeps everything consistent across the page).
- Merges into the existing filed_blob. User-flagged signals win — if
  you've explicitly marked a citation 'noise', the scan won't overwrite
  it back to 'integrated'.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import yaml

from dedup import DedupStore
from embed import EmbeddingFilter
from ingest import _canonical_url

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("observatory.scan_essays")


# Match markdown link `[anchor](url)`. Anchor can be nested-bracket-free
# (no ] inside), URL stops at first ) — good enough for the citation
# styles in our content.
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")

# Image links (![alt](url)) — skip
_IMG_RE = re.compile(r"!\[")


_DATE_PATH_RE = re.compile(r"^\d{4}(?:[-_]\d{1,2}){0,2}$|^\d{4}/\d{1,2}(?:/\d{1,2})?$")
_PURE_NUM_RE = re.compile(r"^\d+$")
_FILLER_SEGMENTS = {
    "index.html", "index", "default", "post", "article", "articles",
    "papers", "story", "stories", "research", "blog", "news", "view",
    "core", "abs", "pdf", "en", "page", "p",
}
_ACRONYMS = {
    "ai", "ml", "us", "uk", "eu", "un", "nato", "agi", "llm", "gpt",
    "wsj", "nyt", "fbi", "cia", "cdc", "imf", "oecd", "gdp", "rsp",
    "ipcc", "ngo", "ftc", "doj", "doe",
}


def _title_from_url(url: str) -> Optional[str]:
    """Derive a readable title from the most informative URL path segment.

    Used as a fallback when the markdown anchor text is just a bare
    source name (e.g., 4 cards titled "Fortune" because the author
    wrote `[Fortune](url)` four times).
    """
    if not url or url.startswith("arxiv:"):
        return None
    try:
        from urllib.parse import unquote
        path = unquote(urlparse(url).path)
    except Exception:
        return None
    segments = [s for s in path.split("/") if s]
    informative = []
    for s in segments:
        sl = s.lower()
        if sl in _FILLER_SEGMENTS:
            continue
        if _DATE_PATH_RE.match(s):
            continue
        if _PURE_NUM_RE.match(s):
            continue
        if sl.endswith(".html") or sl.endswith(".pdf") or sl.endswith(".htm"):
            s = s.rsplit(".", 1)[0]
        informative.append(s)
    if not informative:
        return None
    # The last (often most specific) informative segment usually beats
    # the longest one — paths like /journals/foo/article/bar prefer "bar".
    best = informative[-1]
    # Some hosts prepend short IDs (e.g. "w12345-paper-title"); strip them.
    best = re.sub(r"^[a-z]?\d{3,}[-_]", "", best, flags=re.IGNORECASE)
    title = re.sub(r"[-_]+", " ", best).strip()
    title = re.sub(r"\s+", " ", title)
    if not title:
        return None
    # Title case while preserving common acronyms
    out = []
    for w in title.split():
        if w.lower() in _ACRONYMS:
            out.append(w.upper())
        else:
            out.append(w[0].upper() + w[1:] if w else w)
    return " ".join(out)


def _disambiguate_titles(cards: list[dict]) -> int:
    """Where N cards share the same title, replace each with its URL-
    derived title so they show up as visually distinct sources.

    The fingerprints don't change; only the displayed title does.
    Returns the count of cards whose title was rewritten.
    """
    from collections import defaultdict
    groups: dict[str, list[dict]] = defaultdict(list)
    for c in cards:
        t = (c.get("item", {}).get("title") or "").strip().lower()
        if t:
            groups[t].append(c)
    rewrites = 0
    for title, group in groups.items():
        if len(group) <= 1:
            continue
        for c in group:
            url = c.get("item", {}).get("url", "")
            derived = _title_from_url(url)
            if derived and len(derived.split()) >= 2:
                c["item"]["title"] = derived
                rewrites += 1
    if rewrites:
        logger.info(f"Disambiguated {rewrites} colliding card titles via URL-derived titles")
    return rewrites


def _clean_title(s: str) -> str:
    """Strip surrounding quotes/emphasis and trailing punctuation from
    anchor text so cards have presentable titles."""
    s = (s or "").strip()
    # Iterate: surrounding quotes/emphasis chars, then trailing punct
    changed = True
    while changed and s:
        changed = False
        # Surrounding matched markers
        for left, right in [('"', '"'), ("'", "'"), ("*", "*"), ("_", "_"),
                            ("“", "”"), ("‘", "’")]:
            if len(s) > 1 and s.startswith(left) and s.endswith(right):
                s = s[len(left):-len(right)].strip()
                changed = True
        # Lone leading quote
        for q in ("“", "‘", '"', "'"):
            if s.startswith(q):
                s = s[len(q):].lstrip()
                changed = True
        # Lone trailing quote
        for q in ("”", "’", '"', "'"):
            if s.endswith(q):
                s = s[:-len(q)].rstrip()
                changed = True
        # Trailing punctuation
        while s and s[-1] in ",;:.":
            s = s[:-1].rstrip()
            changed = True
    return s


def _is_skippable(url: str) -> bool:
    """Filter out non-citation URLs."""
    if not url:
        return True
    if url.startswith("#"):
        return True
    parsed = urlparse(url)
    if parsed.netloc.endswith("shadesofsingularity.com"):
        return True
    # Strip query/fragment-only diffs in checks
    if not parsed.scheme.startswith("http"):
        return True
    return False


def _source_label(url: str) -> str:
    """Human-readable source name derived from the URL host."""
    if url.startswith("arxiv:"):
        return "arXiv"
    host = urlparse(url).netloc.lower()
    if not host:
        return "web"
    host = host.removeprefix("www.")
    # Friendly names for common citation hosts
    mapping = {
        "arxiv.org": "arXiv",
        "export.arxiv.org": "arXiv",
        "nber.org": "NBER",
        "www.nber.org": "NBER",
        "imf.org": "IMF",
        "brookings.edu": "Brookings",
        "anthropic.com": "Anthropic",
        "openai.com": "OpenAI",
        "deepmind.google": "DeepMind",
        "ai.meta.com": "Meta AI",
        "cset.georgetown.edu": "CSET",
        "rand.org": "RAND",
        "ainowinstitute.org": "AI Now",
        "science.org": "Science",
        "nature.com": "Nature",
        "academic.oup.com": "OUP",
        "foreignaffairs.com": "Foreign Affairs",
        "hbr.org": "HBR",
        "technologyreview.com": "MIT Tech Review",
        "economist.com": "The Economist",
        "ft.com": "FT",
        "nytimes.com": "NYT",
        "wsj.com": "WSJ",
        "github.com": "GitHub",
        "world.org": "World",
        "artificialintelligenceact.eu": "EU AI Act",
    }
    if host in mapping:
        return mapping[host]
    # Pull a tidy "domain" name for unknown hosts
    parts = host.split(".")
    if len(parts) >= 2:
        return parts[-2].capitalize()
    return host


def _citation_quality(url: str) -> str:
    if url.startswith("arxiv:") or "arxiv.org" in url:
        return "working_paper"
    host = urlparse(url).netloc.lower()
    if any(h in host for h in ("nber.org", "imf.org", "brookings.edu", "cset.georgetown", "rand.org", "ainowinstitute")):
        return "policy_report"
    if any(h in host for h in ("science.org", "nature.com", "academic.oup.com", "frontiersin.org", "pnas")):
        return "peer_reviewed"
    if any(h in host for h in ("anthropic.com", "openai.com", "deepmind", "meta.com", "google", "microsoft")):
        return "blog_post"
    return "news"


# Map essay file number → axis id used in axes.yaml (and in our card
# primary_claim schema)
_ESSAY_AXIS = {
    1: "essay_1_labor",
    2: "essay_2_truth",
    3: "essay_3_power",
    4: "essay_4_human",
    5: "essay_5_inheritance",
    6: "essay_6_governance",
}


def _parse_frontmatter(text: str) -> dict:
    """Parse leading YAML frontmatter; return {} if absent."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return {}


def _strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end < 0:
        return text
    return text[end + 4 :]


def _surrounding_snippet(body: str, link_start: int, link_end: int, max_chars: int = 280) -> str:
    """Pull a short context window around a citation for the card summary."""
    # Expand to sentence boundaries
    lo = max(0, link_start - max_chars // 2)
    hi = min(len(body), link_end + max_chars // 2)
    snippet = body[lo:hi]
    # Strip markdown link syntax inside the window for readability
    snippet = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", snippet)
    snippet = re.sub(r"\s+", " ", snippet).strip()
    if len(snippet) > max_chars:
        snippet = snippet[: max_chars - 1] + "…"
    return snippet


# ---------------------------------------------------------------- scanner


def scan_content_dir(root: Path) -> dict:
    """
    Walk content/essays and content/scenarios, return a dict keyed by
    canonical fingerprint with extracted citation metadata:

        fp -> {
            "fingerprint": str,
            "urls": set[str],          # raw URLs that canonicalized to this fp
            "anchors": list[str],      # all anchor texts seen
            "best_anchor": str,        # longest non-trivial anchor text
            "snippet": str,            # best surrounding sentence
            "sources": list[dict],     # [{file, type, number, title}]
        }
    """
    out: dict[str, dict] = {}

    for kind in ("essays", "scenarios", "short-essays"):
        d = root / "content" / kind
        if not d.is_dir():
            logger.warning(f"Missing content directory: {d}")
            continue

        files = sorted(d.glob("*.md"))
        logger.info(f"Scanning {len(files)} {kind} in {d}")

        for path in files:
            text = path.read_text(encoding="utf-8")
            fm = _parse_frontmatter(text)
            body = _strip_frontmatter(text)

            source_label = (fm.get("title") or path.stem).strip()
            # Normalize type: essays + short-essays both publish under
            # /essays/{slug} on the main site; scenarios → /shades/{slug}.
            if kind == "scenarios":
                kind_type = "shade"
            else:
                kind_type = "essay"
            source_meta = {
                "file": str(path.relative_to(root)),
                "type": kind_type,
                "number": fm.get("number"),
                "title": source_label,
                "slug": (fm.get("slug") or "").strip(),
            }

            for m in _MD_LINK_RE.finditer(body):
                # Skip image links: `![alt](url)` shows up as `!`+match,
                # check the char before the opening bracket.
                if m.start() > 0 and body[m.start() - 1] == "!":
                    continue
                anchor = _clean_title(m.group(1))
                url = m.group(2).strip()
                if _is_skippable(url):
                    continue

                fp = _canonical_url(url)
                entry = out.setdefault(
                    fp,
                    {
                        "fingerprint": fp,
                        "urls": set(),
                        "anchors": [],
                        "best_anchor": "",
                        "snippet": "",
                        "sources": [],
                    },
                )
                entry["urls"].add(url)
                entry["anchors"].append(anchor)
                if len(anchor) > len(entry["best_anchor"]) and len(anchor) < 200:
                    entry["best_anchor"] = anchor

                # Keep the longest snippet across all citations of this URL
                snippet = _surrounding_snippet(body, m.start(), m.end())
                if len(snippet) > len(entry["snippet"]):
                    entry["snippet"] = snippet

                # Dedup by (type, number): the long and short versions of
                # an essay both point at the same /essays/{slug} URL, and
                # the user only wants to see "Essay 1" once even if it's
                # cited from both files.
                src_key = (source_meta["type"], source_meta.get("number"))
                if not any(
                    (s["type"], s.get("number")) == src_key
                    for s in entry["sources"]
                ):
                    entry["sources"].append(source_meta)

    logger.info(f"Found {len(out)} unique citations")
    return out


def _build_cards(
    scan: dict,
    relevance: EmbeddingFilter,
    now_iso: str,
) -> list[dict]:
    """Turn scanner output into filed-blob card dicts (signal='integrated')."""
    # Run TF-IDF over the best_anchor + snippet, so cards get a sensible
    # primary_claim assignment consistent with the cron output.
    scoring_items = []
    for fp, entry in scan.items():
        title = entry["best_anchor"] or "Untitled"
        abstract = entry["snippet"]
        scoring_items.append({
            "fingerprint": fp,
            "title": title,
            "abstract": abstract,
        })
    relevance.score_items(scoring_items)
    score_by_fp = {it["fingerprint"]: it for it in scoring_items}

    cards: list[dict] = []
    for fp, entry in scan.items():
        title = (entry["best_anchor"] or "Untitled").strip()
        scored = score_by_fp.get(fp, {})
        claim = scored.get("relevance_claim", "")
        score = scored.get("relevance_score", 0.0)
        top = scored.get("relevance_top") or []

        # Pick a representative URL to link to (prefer the canonical
        # arXiv URL if available, otherwise the first raw URL seen).
        raw_urls = sorted(entry["urls"])
        if fp.startswith("arxiv:"):
            url = f"https://arxiv.org/abs/{fp[len('arxiv:'):]}"
        else:
            url = raw_urls[0] if raw_urls else ""

        # Build the integration_note from the source list (fallback if
        # the renderer doesn't know about integration_sources yet)
        source_blurb = ", ".join(
            f"{s['type'].capitalize()} {s.get('number', '?')}: {s['title']}"
            for s in entry["sources"]
        )

        cards.append({
            "fingerprint": fp,
            "signal": "integrated",
            "filed_at": now_iso,
            "clears_bar": True,
            "confidence": "high",
            "primary_claim": claim,
            "secondary_claims": [cid for cid, _ in top[1:]],
            "relationship": None,
            "summary": entry["snippet"] or title,
            "citation_quality": _citation_quality(url),
            "named_scholar_match": False,
            "integration_note": f"Cited in: {source_blurb}",
            "integration_sources": entry["sources"],   # structured list for chips
            "source_of_truth": "essay_scan",
            "item": {
                "title": title,
                "source": _source_label(url),
                "authors": [],
                "date": "",
                "url": url,
                "tier": 2,
                "relevance_score": score,
                "relevance_claim": claim,
            },
        })
    return cards


def merge_into_filed(existing: list[dict], scanned: list[dict]) -> list[dict]:
    """
    Merge scanned cards into the existing filed list.

    Rules:
    - Brand-new fingerprints get appended.
    - Existing fingerprints whose source_of_truth is 'essay_scan' get
      upgraded in place (so re-running the scan picks up schema changes
      like new integration_sources without losing user reclassifications).
      We preserve the original filed_at and signal in case the user
      moved it to 'noise' or 'useful_later'.
    - Existing fingerprints from any other origin (cron-discovered cards
      the user manually filed) are left untouched.
    """
    by_fp = {c.get("fingerprint", ""): c for c in existing if c.get("fingerprint")}
    added = 0
    upgraded = 0
    preserved = 0
    for card in scanned:
        fp = card.get("fingerprint", "")
        if not fp:
            continue
        if fp not in by_fp:
            by_fp[fp] = card
            added += 1
            continue

        ex = by_fp[fp]
        if ex.get("source_of_truth") == "essay_scan":
            # Upgrade in place; keep the user's signal + original filing
            # time if they exist on the old card.
            upgraded_card = dict(card)
            upgraded_card["signal"] = ex.get("signal", card.get("signal"))
            if ex.get("filed_at"):
                upgraded_card["filed_at"] = ex["filed_at"]
            by_fp[fp] = upgraded_card
            upgraded += 1
        else:
            preserved += 1

    logger.info(
        f"Merged: {added} new, {upgraded} upgraded in place, "
        f"{preserved} user-curated cards preserved"
    )
    return list(by_fp.values())


def run_scan(mode: str, root: Optional[Path] = None) -> int:
    root = root or Path(__file__).resolve().parents[2]
    logger.info(f"Essay scan starting (mode={mode}, root={root})")

    dedup = DedupStore(mode=mode)
    relevance = EmbeddingFilter(axes_path="config/axes.yaml")

    scan = scan_content_dir(root)
    if not scan:
        logger.warning("No citations found.")
        return 0

    now_iso = datetime.now(timezone.utc).isoformat()
    new_cards = _build_cards(scan, relevance, now_iso)
    _disambiguate_titles(new_cards)

    existing = dedup.load_filed_blob()
    merged = merge_into_filed(existing, new_cards)
    dedup.save_filed_blob(merged)

    logger.info(f"filed_blob now has {len(merged)} cards total")
    return len(new_cards)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan essays for citation references")
    parser.add_argument("--local", action="store_true", help="Local mode (writes to output/filed_blob.json)")
    parser.add_argument("--production", action="store_true", help="Production mode (writes to Vercel KV)")
    parser.add_argument("--root", type=Path, default=None, help="Repo root (default: derived from script location)")
    args = parser.parse_args()
    mode = "production" if args.production else "local"
    n = run_scan(mode, root=args.root)
    print(f"Scanned, produced {n} citation cards.")
