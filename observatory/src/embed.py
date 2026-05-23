"""
Local TF-IDF relevance filter.

Approach borrowed from Karpathy's arxiv-sanity-lite: TF-IDF vectors over
title+abstract, cosine similarity against seed-claim vectors built from
axes.yaml. No API calls, no rate limits, no daily quotas, no network
dependency — the whole thing runs in the GH Actions container in under
a second for ~200 items.

We tried the Gemini batchEmbedContents API first (text-embedding-004 then
gemini-embedding-001) but the free-tier daily quotas were too tight for
weekly use, and the cosine-sim floor of the large general embedding model
was too high to threshold against. TF-IDF over a research-abstract corpus
gives crisper separation because the seed claims and the items share a
specific vocabulary (labor, alignment, displacement, evaluation, etc.).

Threshold-based filter is still available but the pipeline uses top_k()
to bound LLM volume regardless of how many items the corpus contains.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("observatory.embed")

DEFAULT_THRESHOLD = 0.10   # TF-IDF cosine sims are much lower than dense embeds


class EmbeddingFilter:
    """
    Build a TF-IDF model from the claim seeds in axes.yaml plus any items
    we want to score, then rank items by their max cosine similarity to
    any single seed.

    Method names (score_items, filter, top_k) intentionally mirror the
    previous API-based EmbeddingFilter so the pipeline didn't have to change.
    """

    def __init__(
        self,
        api_key: str = "",       # kept for API parity; unused
        axes_path: str = "config/axes.yaml",
        cache_dir: str = "cache",  # unused but kept for API parity
        threshold: float = DEFAULT_THRESHOLD,
    ):
        self.axes_path = Path(axes_path)
        self.threshold = threshold
        self.seed_ids, self.seed_labels, self.seed_texts = self._load_seed_texts()
        # The vectorizer is fit per call to score_items() because we want
        # the IDF statistics to reflect the actual item corpus, not just
        # the seed set.
        self._vectorizer: TfidfVectorizer | None = None
        logger.info(f"Loaded {len(self.seed_ids)} claim seeds from {self.axes_path.name}")

    # --------------------------------------------------------------- seeds

    def _load_seed_texts(self) -> tuple[list[str], list[str], list[str]]:
        """Return (ids, labels, texts) drawn from axes.yaml."""
        data = yaml.safe_load(self.axes_path.read_text())
        ids: list[str] = []
        labels: list[str] = []
        texts: list[str] = []
        for axis_id, axis in data.get("axes", {}).items():
            thesis = (axis.get("core_thesis") or "").strip()
            title = (axis.get("title") or "").strip()
            ids.append(axis_id)
            labels.append(f"{axis_id}: {title}")
            texts.append(f"{title}. {thesis}")
            for c in axis.get("load_bearing_claims", []):
                claim_id = c.get("id", "")
                claim_text = (c.get("claim") or "").strip()
                vulnerability = (c.get("vulnerability") or "").strip()
                if not claim_id or not claim_text:
                    continue
                ids.append(claim_id)
                labels.append(f"{claim_id}: {claim_text[:80]}")
                combined = claim_text
                if vulnerability:
                    combined += f" {vulnerability}"
                texts.append(combined)
        return ids, labels, texts

    # --------------------------------------------------------------- scoring

    def score_items(self, items: list[dict]) -> list[dict]:
        """
        Annotate each item with relevance_score, relevance_claim, relevance_top.
        Returns the same list.
        """
        if not items:
            return items

        item_texts = [self._item_text(item) for item in items]
        # Fit on the combined corpus (seeds + items) so IDF reflects what
        # we're actually scoring against. unigrams + bigrams handles short
        # phrases like "task share" or "open weight".
        corpus = self.seed_texts + item_texts
        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            stop_words="english",
            sublinear_tf=True,
        )
        matrix = self._vectorizer.fit_transform(corpus)
        seed_matrix = matrix[: len(self.seed_texts)]
        item_matrix = matrix[len(self.seed_texts):]

        sims = cosine_similarity(item_matrix, seed_matrix)  # (n_items, n_seeds)

        for i, item in enumerate(items):
            row = sims[i]
            best_idx = int(np.argmax(row))
            item["relevance_score"] = float(row[best_idx])
            item["relevance_claim"] = self.seed_ids[best_idx]
            top_k_idx = np.argsort(-row)[:3]
            item["relevance_top"] = [
                (self.seed_ids[j], float(row[j])) for j in top_k_idx
            ]
        return items

    def filter(self, items: list[dict]) -> list[dict]:
        """Keep items whose top-claim similarity meets the threshold."""
        return [it for it in items if it.get("relevance_score", 0.0) >= self.threshold]

    def log_score_distribution(self, items: list[dict]) -> None:
        """One-line summary of the relevance-score distribution."""
        scores = [it.get("relevance_score") for it in items if it.get("relevance_score") is not None]
        if not scores:
            logger.info("Relevance score distribution: (no scored items)")
            return
        arr = np.asarray(scores, dtype=np.float32)
        q = np.quantile(arr, [0.0, 0.25, 0.5, 0.75, 0.9, 1.0])
        logger.info(
            f"Relevance score distribution over {len(arr)} items: "
            f"min={q[0]:.3f} p25={q[1]:.3f} p50={q[2]:.3f} "
            f"p75={q[3]:.3f} p90={q[4]:.3f} max={q[5]:.3f}"
        )

    @staticmethod
    def top_k(items: list[dict], k: int) -> list[dict]:
        """Return the k items with the highest relevance_score, sorted desc."""
        return sorted(items, key=lambda it: it.get("relevance_score", 0.0), reverse=True)[:k]

    @staticmethod
    def _item_text(item: dict) -> str:
        title = item.get("title", "")
        abstract = item.get("abstract", "")
        words = abstract.split()
        if len(words) > 400:
            abstract = " ".join(words[:400])
        return f"{title}. {abstract}".strip()
