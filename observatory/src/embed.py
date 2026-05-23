"""
Embedding-based relevance filter.

Replaces the previous regex-prefilter + LLM-triage steps. For each ingested
item we embed `title + abstract` with gemini-embedding-001 (free on Gemini's
free tier, 1500 req/day, 5 RPM), then compute cosine similarity against a
pre-computed seed matrix built from the 20 load-bearing claims in
axes.yaml. Items keep a `relevance_score` plus the top-3 nearest claim IDs
as a hint for adjudication.

Why this shape:
- Embeddings are essentially free for our volume (~40 items/week).
- One vector match catches "workforce displacement" ≈ "labor automation"
  in a way a regex keyword list cannot.
- We drop two whole modules (prefilter.py, triage.py + their prompts)
  and the per-item LLM call that was eating our RPM budget.

Pattern follows what arxiv-sanity-lite / Semantic Scholar / personalized
arXiv-feed projects already use: cheap embedding gate first, expensive
reasoning later.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import time
from pathlib import Path
from typing import Optional

import numpy as np
import requests
import yaml

logger = logging.getLogger("observatory.embed")

EMBED_MODEL = "models/gemini-embedding-001"
EMBED_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/{model}:batchEmbedContents"
)
EMBED_BATCH_SIZE = 100         # gemini-embedding-001 batchEmbedContents cap
MAX_RETRIES = 4

# Default cosine-similarity threshold below which items are dropped.
# Calibrated low to stay generous; tune up later by inspecting passing items.
DEFAULT_THRESHOLD = 0.55


class EmbeddingFilter:
    """
    Loads claim seed text from axes.yaml, caches their embeddings to disk,
    and scores ingested items by maximum cosine similarity against the seed
    matrix.
    """

    def __init__(
        self,
        api_key: str,
        axes_path: str = "config/axes.yaml",
        cache_dir: str = "cache",
        threshold: float = DEFAULT_THRESHOLD,
    ):
        self.api_key = api_key
        self.axes_path = Path(axes_path)
        self.cache_dir = Path(cache_dir)
        self.threshold = threshold

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.seed_ids, self.seed_labels, self.seed_matrix = self._load_or_build_seeds()

    # ------------------------------------------------------------------ seeds

    def _seed_texts(self) -> tuple[list[str], list[str], list[str]]:
        """Return (ids, labels, texts) drawn from axes.yaml."""
        data = yaml.safe_load(self.axes_path.read_text())
        ids: list[str] = []
        labels: list[str] = []
        texts: list[str] = []
        for axis_id, axis in data.get("axes", {}).items():
            thesis = (axis.get("core_thesis") or "").strip()
            title = (axis.get("title") or "").strip()
            # Axis-level seed: title + thesis.
            ids.append(axis_id)
            labels.append(f"{axis_id}: {title}")
            texts.append(f"{title}. {thesis}")
            # Per-claim seeds: claim text + vulnerability so the embedding
            # also matches counter-evidence, not just supporting work.
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
                    combined += f" Counter-evidence relevant: {vulnerability}"
                texts.append(combined)
        return ids, labels, texts

    def _seeds_cache_key(self, texts: list[str]) -> str:
        """Fingerprint the seed text so cache invalidates when axes.yaml changes."""
        h = hashlib.sha256()
        h.update(EMBED_MODEL.encode())
        for t in texts:
            h.update(b"\x1f")
            h.update(t.encode())
        return h.hexdigest()[:16]

    def _load_or_build_seeds(self) -> tuple[list[str], list[str], np.ndarray]:
        ids, labels, texts = self._seed_texts()
        key = self._seeds_cache_key(texts)
        npy_path = self.cache_dir / f"seed_embeddings_{key}.npy"
        meta_path = self.cache_dir / f"seed_embeddings_{key}.json"

        if npy_path.exists() and meta_path.exists():
            try:
                matrix = np.load(npy_path)
                meta = json.loads(meta_path.read_text())
                if meta.get("ids") == ids and matrix.shape[0] == len(ids):
                    logger.info(f"Loaded {len(ids)} cached seed embeddings from {npy_path.name}")
                    return ids, labels, matrix
            except Exception as e:
                logger.warning(f"Seed cache load failed; recomputing: {e}")

        logger.info(f"Computing seed embeddings for {len(texts)} claims")
        vectors = self._embed_texts(texts, task_type="SEMANTIC_SIMILARITY")
        matrix = _normalize(np.asarray(vectors, dtype=np.float32))
        np.save(npy_path, matrix)
        meta_path.write_text(json.dumps({"ids": ids, "labels": labels}, indent=2))
        return ids, labels, matrix

    # ------------------------------------------------------------------ scoring

    def score_items(self, items: list[dict]) -> list[dict]:
        """
        Embed each item's title+abstract and annotate it in-place with:
        - relevance_score (float, max cosine similarity to any seed)
        - relevance_claim (str, id of best-matching seed)
        - relevance_top (list[tuple[id, score]], top-3 matches)
        Returns the same list.
        """
        if not items:
            return items

        texts = [self._item_text(item) for item in items]
        vectors = self._embed_texts(texts, task_type="SEMANTIC_SIMILARITY")
        if not vectors:
            return items
        item_matrix = _normalize(np.asarray(vectors, dtype=np.float32))

        # (n_items, n_seeds) — both sides are already L2-normalized so this
        # is the cosine similarity matrix directly.
        sims = item_matrix @ self.seed_matrix.T

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
        kept = [it for it in items if it.get("relevance_score", 0.0) >= self.threshold]
        return kept

    @staticmethod
    def _item_text(item: dict) -> str:
        title = item.get("title", "")
        abstract = item.get("abstract", "")
        # Keep it short — embedder is 2048 tokens but most signal is in first
        # ~200 words of the abstract anyway, and we want to stay well under.
        words = abstract.split()
        if len(words) > 400:
            abstract = " ".join(words[:400])
        return f"{title}\n\n{abstract}".strip()

    # ------------------------------------------------------------------ HTTP

    def _embed_texts(self, texts: list[str], task_type: str) -> list[list[float]]:
        """Embed a list of texts with batched calls. Returns list of vectors."""
        vectors: list[list[float]] = []
        for start in range(0, len(texts), EMBED_BATCH_SIZE):
            chunk = texts[start:start + EMBED_BATCH_SIZE]
            chunk_vectors = self._embed_chunk(chunk, task_type=task_type)
            vectors.extend(chunk_vectors)
        return vectors

    def _embed_chunk(self, chunk: list[str], task_type: str) -> list[list[float]]:
        url = EMBED_ENDPOINT.format(model=EMBED_MODEL)
        body = {
            "requests": [
                {
                    "model": EMBED_MODEL,
                    "content": {"parts": [{"text": text or " "}]},
                    "taskType": task_type,
                }
                for text in chunk
            ]
        }
        delay = 4.0
        last_err: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = requests.post(
                    url, params={"key": self.api_key}, json=body, timeout=60,
                )
                if resp.status_code in (429, 500, 502, 503, 504):
                    retry_after = resp.headers.get("Retry-After")
                    try:
                        sleep_for = float(retry_after) + random.uniform(0, 2) if retry_after else delay + random.uniform(0, delay / 2)
                    except ValueError:
                        sleep_for = delay + random.uniform(0, delay / 2)
                    logger.warning(
                        f"Embed transient {resp.status_code} (attempt {attempt+1}/{MAX_RETRIES}); "
                        f"sleeping {sleep_for:.1f}s"
                    )
                    time.sleep(sleep_for)
                    delay = min(delay * 2, 60.0)
                    continue
                resp.raise_for_status()
                data = resp.json()
                return [r["values"] for r in data["embeddings"]]
            except requests.RequestException as e:
                last_err = e
                sleep_for = delay + random.uniform(0, delay / 2)
                logger.warning(
                    f"Embed request error (attempt {attempt+1}/{MAX_RETRIES}): {e}; "
                    f"sleeping {sleep_for:.1f}s"
                )
                time.sleep(sleep_for)
                delay = min(delay * 2, 60.0)
        raise last_err or RuntimeError("Embedding exhausted retries")


def _normalize(matrix: np.ndarray) -> np.ndarray:
    """L2-normalize rows so a dot product equals cosine similarity."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms
