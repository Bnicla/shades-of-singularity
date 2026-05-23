"""
Adjudicator: Gemini 2.5 Flash-Lite evaluation of whether an item bears
on a specific load-bearing claim in the essay collection.

This is the precision pass. Each item gets a full-text analysis against
the claim inventory in prompts.py. The pipeline upstream caps the number
of items reaching us via top-K embedding rank, so volume is bounded.

We deliberately pick Flash-Lite over Flash for free-tier headroom:
- Flash:      10 RPM,  500 RPD
- Flash-Lite: 15 RPM, 1000 RPD
Quality is acceptable for our structured-JSON prompt; the embedding
similarity is doing the topic-relevance work already.

Two model-specific gotchas worth calling out:
- Gemini 2.5 spends "thinking" tokens against maxOutputTokens by default.
  We disable thinking via thinkingConfig so the budget all goes to JSON.
- The response includes ~10 fields; even with thinking off it's ~300-400
  tokens. We set a generous cap to avoid mid-string truncation.
"""

import json
import logging
import random
import time
from typing import Optional

import requests

from prompts import ADJUDICATION_SYSTEM, ADJUDICATION_USER

logger = logging.getLogger("observatory.adjudicate")

MAX_ADJUDICATE_BATCH = 50          # hard cap on items per pipeline run
RATE_LIMIT_DELAY = 6.5             # baseline seconds between calls (~9 RPM)
MAX_RETRIES = 5
MAX_OUTPUT_TOKENS = 1200           # response JSON is ~300-400 tokens; cushion

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class Adjudicator:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite"):
        self.api_key = api_key
        self.model = model

    def evaluate(self, items: list[dict]) -> list[dict]:
        """Evaluate items against the claim inventory."""
        if len(items) > MAX_ADJUDICATE_BATCH:
            logger.warning(
                f"Adjudication batch size {len(items)} exceeds limit {MAX_ADJUDICATE_BATCH}. "
                f"Processing first {MAX_ADJUDICATE_BATCH} only."
            )
            items = items[:MAX_ADJUDICATE_BATCH]

        results = []
        for i, item in enumerate(items):
            logger.info(f"  Adjudicating {i+1}/{len(items)}: {item.get('title', '')[:60]}...")
            result = self._adjudicate_single(item)
            if result:
                result["item"] = {
                    "title": item.get("title", ""),
                    "source": item.get("source", ""),
                    "authors": item.get("authors", []),
                    "date": item.get("date", ""),
                    "url": item.get("url", ""),
                    "tier": item.get("tier", 0),
                    "named_scholar": item.get("named_scholar"),
                    "relevance_score": item.get("relevance_score"),
                    "relevance_claim": item.get("relevance_claim"),
                }
                result["fingerprint"] = item.get("fingerprint", "")
                results.append(result)

            if i < len(items) - 1:
                time.sleep(RATE_LIMIT_DELAY)

        return results

    def _adjudicate_single(self, item: dict) -> Optional[dict]:
        """Run adjudication on a single item."""
        text = item.get("text", "") or item.get("abstract", "")
        words = text.split()
        if len(words) > 3000:
            text = " ".join(words[:3000]) + "\n\n[... truncated for evaluation ...]"

        # Build the embedding-relevance hint from the top-3 claim matches
        # the embedder produced, if any. This is a steering signal only —
        # the adjudication prompt is explicit that the LLM may override it.
        top = item.get("relevance_top") or []
        if top:
            relevance_hint = "\n".join(
                f"  - {cid} (cosine={score:.2f})" for cid, score in top
            )
        else:
            relevance_hint = "  (no embedding hint available)"

        user_prompt = ADJUDICATION_USER.format(
            title=item.get("title", ""),
            source=item.get("source", ""),
            authors=", ".join(item.get("authors", [])),
            date=item.get("date", ""),
            url=item.get("url", ""),
            relevance_hint=relevance_hint,
            text=text,
        )

        body = {
            "systemInstruction": {"parts": [{"text": ADJUDICATION_SYSTEM}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "maxOutputTokens": MAX_OUTPUT_TOKENS,
                "temperature": 0.2,
                "responseMimeType": "application/json",
                # Disable Gemini 2.5 thinking so the response budget goes to
                # JSON, not internal reasoning we don't read.
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }
        url = GEMINI_ENDPOINT.format(model=self.model)

        try:
            response_text = self._call_with_backoff(url, body)
        except Exception as e:
            logger.error(f"Adjudication API error for '{item.get('title', '')}': {e}")
            return self._parse_failure(item, f"API error: {e}")

        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1] if "\n" in response_text else response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse adjudication for '{item.get('title', '')}': {e}")
            return self._parse_failure(item, f"Parse error: {e}")

        required = ["clears_bar", "confidence", "primary_claim", "relationship", "summary"]
        for field in required:
            if field not in result:
                result[field] = None
        return result

    def _call_with_backoff(self, url: str, body: dict) -> str:
        """POST with exponential backoff on 429 and transient 5xx."""
        delay = 8.0
        last_err: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = requests.post(
                    url, params={"key": self.api_key}, json=body, timeout=90,
                )
                if resp.status_code in (429, 500, 502, 503, 504):
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after:
                        try:
                            sleep_for = float(retry_after) + random.uniform(0, 2)
                        except ValueError:
                            sleep_for = delay + random.uniform(0, delay / 2)
                    else:
                        sleep_for = delay + random.uniform(0, delay / 2)
                    logger.warning(
                        f"Adjudication transient {resp.status_code} (attempt {attempt+1}/{MAX_RETRIES}); "
                        f"sleeping {sleep_for:.1f}s"
                    )
                    time.sleep(sleep_for)
                    delay = min(delay * 2, 90.0)
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except requests.RequestException as e:
                last_err = e
                sleep_for = delay + random.uniform(0, delay / 2)
                logger.warning(
                    f"Adjudication request error (attempt {attempt+1}/{MAX_RETRIES}): {e}; "
                    f"sleeping {sleep_for:.1f}s"
                )
                time.sleep(sleep_for)
                delay = min(delay * 2, 90.0)
        raise last_err or RuntimeError("Adjudication exhausted retries")

    def _parse_failure(self, item: dict, msg: str) -> dict:
        """Build a placeholder result so a broken item doesn't drop silently."""
        return {
            "clears_bar": False,
            "confidence": "low",
            "primary_claim": None,
            "secondary_claims": [],
            "relationship": None,
            "summary": msg,
            "citation_quality": "unknown",
            "named_scholar_match": item.get("tier") == 1,
            "integration_note": None,
        }
