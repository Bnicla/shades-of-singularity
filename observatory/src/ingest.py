"""
Feed ingestion: fetches and normalizes items from RSS/Atom feeds,
APIs, and web scraping targets.

Each item is normalized to:
{
    "fingerprint": str,      # URL or DOI, used for dedup
    "title": str,
    "source": str,           # Human-readable source name
    "authors": list[str],
    "date": str,             # ISO format
    "url": str,
    "abstract": str,         # First ~500 words or abstract
    "text": str,             # Full text if available, else abstract
    "tier": int,             # 1, 2, or 3
    "feed_category": str,    # e.g., "arxiv:cs.CY", "anthropic_blog"
}
"""

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import quote_plus

import feedparser
import requests
import yaml

logger = logging.getLogger("observatory.ingest")


class IngestManager:
    def __init__(self, config_path: str = "config/sources.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.session = requests.Session()
        ua = self.config.get("defaults", {}).get(
            "user_agent",
            "Observatory/1.0 (research-monitor)"
        )
        self.session.headers.update({"User-Agent": ua})
        self.timeout = self.config.get("defaults", {}).get("timeout_seconds", 30)
        self.max_items = self.config.get("defaults", {}).get("max_items_per_feed", 20)

    def fetch_all(self, lookback_days: int = 3) -> list[dict]:
        """Fetch items from all configured sources."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        items = []

        items.extend(self._fetch_scholar_feeds(cutoff))
        items.extend(self._fetch_institutional(cutoff))
        items.extend(self._fetch_editorial(cutoff))

        logger.info(f"Total items ingested: {len(items)}")
        return items

    def _fetch_scholar_feeds(self, cutoff: datetime) -> list[dict]:
        """Tier 1: Named scholar monitoring."""
        items = []
        scholars = self.config.get("tier_1_scholars", [])

        for scholar in scholars:
            name = scholar["name"]

            # arXiv author search
            if "arxiv_author" in scholar:
                try:
                    feed_items = self._fetch_arxiv_author(
                        scholar["arxiv_author"], name, cutoff
                    )
                    for item in feed_items:
                        item["tier"] = 1
                        item["named_scholar"] = name
                    items.extend(feed_items)
                except Exception as e:
                    logger.warning(f"Failed to fetch arXiv for {name}: {e}")

            # Google Scholar (via Semantic Scholar API as proxy)
            if "google_scholar_id" in scholar:
                try:
                    feed_items = self._fetch_semantic_scholar(
                        scholar["google_scholar_id"], name, cutoff
                    )
                    for item in feed_items:
                        item["tier"] = 1
                        item["named_scholar"] = name
                    items.extend(feed_items)
                except Exception as e:
                    logger.warning(f"Failed to fetch Semantic Scholar for {name}: {e}")

            # NBER author page
            if "nber_author" in scholar:
                try:
                    feed_items = self._fetch_nber_author(
                        scholar["nber_author"], name, cutoff
                    )
                    for item in feed_items:
                        item["tier"] = 1
                        item["named_scholar"] = name
                    items.extend(feed_items)
                except Exception as e:
                    logger.warning(f"Failed to fetch NBER for {name}: {e}")

        return items

    def _fetch_institutional(self, cutoff: datetime) -> list[dict]:
        """Tier 2: Institutional feeds."""
        items = []

        # arXiv search-query feeds (scoped to axis-relevant terms, not broad categories)
        arxiv_config = self.config.get("tier_2_institutional", {}).get("arxiv", {})
        for search in arxiv_config.get("searches", []):
            label = search.get("label", "untitled")
            try:
                query = quote_plus(search["query"])
                url = (
                    "https://export.arxiv.org/api/query"
                    f"?search_query={query}"
                    "&sortBy=submittedDate&sortOrder=descending"
                    f"&max_results={self.max_items}"
                )
                feed_items = self._parse_rss(url, f"arXiv: {label}", cutoff)
                for item in feed_items:
                    item["tier"] = 2
                    item["feed_category"] = f"arxiv:{label}"
                items.extend(feed_items)
            except Exception as e:
                logger.warning(f"Failed to fetch arXiv search '{label}': {e}")

        # Lab blogs
        for lab in self.config.get("tier_2_institutional", {}).get("lab_blogs", []):
            try:
                feed_items = self._parse_rss(
                    lab["feed_url"], lab["name"], cutoff
                )
                for item in feed_items:
                    item["tier"] = 2
                    item["feed_category"] = f"lab:{lab['name'].lower()}"
                items.extend(feed_items)
            except Exception as e:
                logger.warning(f"Failed to fetch {lab['name']} blog: {e}")

        # NBER
        nber = self.config.get("tier_2_institutional", {}).get("nber", {})
        if nber.get("feed_url"):
            try:
                feed_items = self._parse_rss(nber["feed_url"], "NBER", cutoff)
                for item in feed_items:
                    item["tier"] = 2
                    item["feed_category"] = "nber"
                items.extend(feed_items)
            except Exception as e:
                logger.warning(f"Failed to fetch NBER: {e}")

        # Brookings
        brookings = self.config.get("tier_2_institutional", {}).get("brookings", {})
        for feed in brookings.get("feeds", []):
            try:
                feed_items = self._parse_rss(
                    feed["url"], f"Brookings ({feed['label']})", cutoff
                )
                for item in feed_items:
                    item["tier"] = 2
                    item["feed_category"] = "brookings"
                items.extend(feed_items)
            except Exception as e:
                logger.warning(f"Failed to fetch Brookings {feed['label']}: {e}")

        # Policy institutes
        for inst in self.config.get("tier_2_institutional", {}).get("policy_institutes", []):
            if "feed_url" in inst:
                try:
                    feed_items = self._parse_rss(
                        inst["feed_url"], inst["name"], cutoff
                    )
                    for item in feed_items:
                        item["tier"] = 2
                        item["feed_category"] = f"policy:{inst['name'].lower()}"
                    items.extend(feed_items)
                except Exception as e:
                    logger.warning(f"Failed to fetch {inst['name']}: {e}")

        return items

    def _fetch_editorial(self, cutoff: datetime) -> list[dict]:
        """Tier 3: Editorial sources."""
        items = []

        # Journals
        for journal in self.config.get("tier_3_editorial", {}).get("journals", []):
            try:
                feed_items = self._parse_rss(
                    journal["feed_url"], journal["name"], cutoff
                )
                # Apply keyword filter for journals
                keywords = journal.get("filter_keywords", [])
                if keywords:
                    feed_items = [
                        item for item in feed_items
                        if any(
                            kw.lower() in (item.get("title", "") + " " + item.get("abstract", "")).lower()
                            for kw in keywords
                        )
                    ]
                for item in feed_items:
                    item["tier"] = 3
                    item["feed_category"] = f"journal:{journal['name'].lower()}"
                items.extend(feed_items)
            except Exception as e:
                logger.warning(f"Failed to fetch {journal['name']}: {e}")

        # Magazines
        for mag in self.config.get("tier_3_editorial", {}).get("magazines_and_reviews", []):
            if "feed_url" in mag:
                try:
                    feed_items = self._parse_rss(
                        mag["feed_url"], mag["name"], cutoff
                    )
                    keywords = mag.get("filter_keywords", [])
                    if keywords:
                        feed_items = [
                            item for item in feed_items
                            if any(
                                kw.lower() in (item.get("title", "") + " " + item.get("abstract", "")).lower()
                                for kw in keywords
                            )
                        ]
                    for item in feed_items:
                        item["tier"] = 3
                        item["feed_category"] = f"editorial:{mag['name'].lower()}"
                    items.extend(feed_items)
                except Exception as e:
                    logger.warning(f"Failed to fetch {mag['name']}: {e}")

        # Newsletters / blogs
        for blog in self.config.get("tier_3_editorial", {}).get("newsletters_and_blogs", []):
            url = blog.get("feed_url", blog.get("url"))
            if url:
                try:
                    feed_items = self._parse_rss(url, blog["name"], cutoff)
                    for item in feed_items:
                        item["tier"] = 3
                        item["feed_category"] = f"blog:{blog['name'].lower()}"
                    items.extend(feed_items)
                except Exception as e:
                    logger.warning(f"Failed to fetch {blog['name']}: {e}")

        return items

    # ---- Low-level fetchers ----

    def _parse_rss(self, url: str, source_name: str, cutoff: datetime) -> list[dict]:
        """Parse an RSS/Atom feed and return normalized items."""
        feed = feedparser.parse(url)
        items = []

        for entry in feed.entries[: self.max_items]:
            published = self._parse_date(entry)
            if published and published < cutoff:
                continue

            items.append({
                "fingerprint": self._fingerprint(entry),
                "title": entry.get("title", "").strip(),
                "source": source_name,
                "authors": self._extract_authors(entry),
                "date": published.isoformat() if published else "",
                "url": entry.get("link", ""),
                "abstract": self._extract_abstract(entry),
                "text": self._extract_abstract(entry),  # Full text fetched later if needed
            })

        return items

    def _fetch_arxiv_author(self, author_id: str, name: str, cutoff: datetime) -> list[dict]:
        """Fetch recent papers by a specific arXiv author."""
        url = f"https://export.arxiv.org/api/query?search_query=au:{author_id}&sortBy=submittedDate&sortOrder=descending&max_results=10"
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)

        items = []
        for entry in feed.entries:
            published = self._parse_date(entry)
            if published and published < cutoff:
                continue

            items.append({
                "fingerprint": entry.get("id", entry.get("link", "")),
                "title": entry.get("title", "").strip().replace("\n", " "),
                "source": f"arXiv (author: {name})",
                "authors": [a.get("name", "") for a in entry.get("authors", [])],
                "date": published.isoformat() if published else "",
                "url": entry.get("link", ""),
                "abstract": entry.get("summary", "").strip(),
                "text": entry.get("summary", "").strip(),
            })

        return items

    def _fetch_semantic_scholar(self, gs_id: str, name: str, cutoff: datetime) -> list[dict]:
        """
        Fetch recent papers via Semantic Scholar API.
        Note: Google Scholar IDs don't map directly; this uses name search
        as a fallback. Consider maintaining Semantic Scholar author IDs
        in the config for reliability.
        """
        # Semantic Scholar author search by name
        search_url = f"https://api.semanticscholar.org/graph/v1/author/search?query={name}&limit=1"
        try:
            resp = self.session.get(search_url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("data"):
                return []

            author_id = data["data"][0]["authorId"]
            papers_url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}/papers?fields=title,url,abstract,year,publicationDate,authors&limit=10&sort=publicationDate:desc"
            resp = self.session.get(papers_url, timeout=self.timeout)
            resp.raise_for_status()
            papers = resp.json().get("data", [])

            items = []
            for paper in papers:
                pub_date = paper.get("publicationDate")
                if pub_date:
                    try:
                        parsed = datetime.strptime(pub_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                        if parsed < cutoff:
                            continue
                    except ValueError:
                        pass

                items.append({
                    "fingerprint": paper.get("url", paper.get("paperId", "")),
                    "title": paper.get("title", ""),
                    "source": f"Semantic Scholar (author: {name})",
                    "authors": [a.get("name", "") for a in paper.get("authors", [])],
                    "date": pub_date or "",
                    "url": paper.get("url", ""),
                    "abstract": paper.get("abstract", "") or "",
                    "text": paper.get("abstract", "") or "",
                })
            return items

        except Exception as e:
            logger.warning(f"Semantic Scholar lookup failed for {name}: {e}")
            return []

    def _fetch_nber_author(self, author_slug: str, name: str, cutoff: datetime) -> list[dict]:
        """Fetch NBER working papers by author."""
        # NBER doesn't have a clean author API; use the feed and filter
        url = "https://www.nber.org/rss/new.xml"
        feed = feedparser.parse(url)
        items = []

        for entry in feed.entries[: self.max_items]:
            # Check if author name appears in the entry
            entry_text = (
                entry.get("title", "")
                + " "
                + entry.get("summary", "")
                + " "
                + str(entry.get("authors", ""))
            ).lower()

            if name.lower().split()[-1] not in entry_text:
                continue

            published = self._parse_date(entry)
            if published and published < cutoff:
                continue

            items.append({
                "fingerprint": self._fingerprint(entry),
                "title": entry.get("title", "").strip(),
                "source": f"NBER (author: {name})",
                "authors": self._extract_authors(entry),
                "date": published.isoformat() if published else "",
                "url": entry.get("link", ""),
                "abstract": entry.get("summary", "").strip(),
                "text": entry.get("summary", "").strip(),
            })

        return items

    # ---- Utilities ----

    def _fingerprint(self, entry) -> str:
        """Generate a stable fingerprint for deduplication."""
        url = entry.get("link", entry.get("id", ""))
        if url:
            return url
        # Fallback: hash of title
        title = entry.get("title", "")
        return hashlib.sha256(title.encode()).hexdigest()[:16]

    def _parse_date(self, entry) -> Optional[datetime]:
        """Extract and parse publication date from a feed entry."""
        for field in ("published_parsed", "updated_parsed"):
            parsed = entry.get(field)
            if parsed:
                try:
                    from time import mktime
                    return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
                except (ValueError, OverflowError):
                    pass

        for field in ("published", "updated"):
            date_str = entry.get(field)
            if date_str:
                try:
                    from dateutil.parser import parse as dateparse
                    return dateparse(date_str).replace(tzinfo=timezone.utc)
                except Exception:
                    pass

        return None

    def _extract_authors(self, entry) -> list[str]:
        """Extract author names from a feed entry."""
        authors = entry.get("authors", [])
        if authors:
            return [a.get("name", str(a)) for a in authors if a]

        author = entry.get("author")
        if author:
            return [author]

        return []

    def _extract_abstract(self, entry) -> str:
        """Extract abstract/summary, cleaning HTML."""
        summary = entry.get("summary", "")
        if not summary:
            content = entry.get("content", [])
            if content:
                summary = content[0].get("value", "")

        # Basic HTML stripping
        import re
        summary = re.sub(r"<[^>]+>", " ", summary)
        summary = re.sub(r"\s+", " ", summary).strip()

        # Truncate to ~500 words for triage
        words = summary.split()
        if len(words) > 500:
            summary = " ".join(words[:500]) + "..."

        return summary
