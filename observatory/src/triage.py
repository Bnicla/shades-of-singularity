"""
Triage filter: cheap Gemini Flash pass to determine if an item
plausibly touches one of the six essay axes.

Generous filter. False positives are acceptable; false negatives are not.

Items are sent in batches (default 15 per call) to stay well under
Gemini's free-tier RPM limit while preserving daily-token headroom.
"""

import json
import logging
import random
import time
from typing import Optional

import requests

from prompts import TRIAGE_SYSTEM, TRIAGE_BATCH_USER

logger = logging.getLogger("observatory.triage")

MAX_TRIAGE_BATCH = 200      # hard cap on items per pipeline run
DEFAULT_CHUNK_SIZE = 15     # items per LLM call
MAX_RETRIES = 5             # per chunk, on 429 / 5xx

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class TriageFilter:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", chunk_size: int = DEFAULT_CHUNK_SIZE):
        self.api_key = api_key
        self.model = model
        self.chunk_size = chunk_size

    def filter(self, items: list[dict]) -> list[dict]:
        """Filter items, returning those that pass triage."""
        if len(items) > MAX_TRIAGE_BATCH:
            logger.warning(
                f"Triage batch size {len(items)} exceeds limit {MAX_TRIAGE_BATCH}. "
                f"Processing first {MAX_TRIAGE_BATCH} only."
            )
            items = items[:MAX_TRIAGE_BATCH]

        passed = []
        for start in range(0, len(items), self.chunk_size):
            chunk = items[start:start + self.chunk_size]
            decisions = self._triage_chunk(chunk)

            for item, decision in zip(chunk, decisions):
                if decision and decision.get("pass"):
                    item["triage_axes"] = decision.get("candidate_axes", [])
                    item["triage_confidence"] = decision.get("confidence", "low")
                    passed.append(item)

        return passed

    def _triage_chunk(self, chunk: list[dict]) -> list[Optional[dict]]:
        """Run triage on a chunk of items. Returns one decision per input item."""
        items_block = "\n\n".join(
            f"Item {i+1}:\n"
            f"Title: {item.get('title', '')}\n"
            f"Source: {item.get('source', '')}\n"
            f"Date: {item.get('date', '')}\n"
            f"Abstract: {item.get('abstract', '')[:800]}"
            for i, item in enumerate(chunk)
        )
        user_prompt = TRIAGE_BATCH_USER.format(items_block=items_block, n=len(chunk))

        body = {
            "systemInstruction": {"parts": [{"text": TRIAGE_SYSTEM}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                # ~80 tokens per item decision + slack for the array scaffolding
                "maxOutputTokens": 120 * len(chunk) + 200,
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }
        url = GEMINI_ENDPOINT.format(model=self.model)

        try:
            text = self._call_with_backoff(url, body)
        except Exception as e:
            logger.error(f"Triage chunk failed after retries ({len(chunk)} items): {e}")
            # Generous fallback: pass every item through with low confidence.
            return [{"pass": True, "candidate_axes": ["UNKNOWN"], "confidence": "low"}] * len(chunk)

        return self._parse_array_response(text, expected=len(chunk))

    def _call_with_backoff(self, url: str, body: dict) -> str:
        """POST with exponential backoff on 429 and transient 5xx."""
        delay = 4.0
        last_err: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = requests.post(
                    url, params={"key": self.api_key}, json=body, timeout=60,
                )
                if resp.status_code in (429, 500, 502, 503, 504):
                    sleep_for = delay + random.uniform(0, delay / 2)
                    logger.warning(
                        f"Triage transient {resp.status_code} (attempt {attempt+1}/{MAX_RETRIES}); "
                        f"sleeping {sleep_for:.1f}s"
                    )
                    time.sleep(sleep_for)
                    delay = min(delay * 2, 60.0)
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except requests.RequestException as e:
                last_err = e
                sleep_for = delay + random.uniform(0, delay / 2)
                logger.warning(
                    f"Triage request error (attempt {attempt+1}/{MAX_RETRIES}): {e}; "
                    f"sleeping {sleep_for:.1f}s"
                )
                time.sleep(sleep_for)
                delay = min(delay * 2, 60.0)
        raise last_err or RuntimeError("Triage exhausted retries")

    def _parse_array_response(self, text: str, expected: int) -> list[Optional[dict]]:
        """Parse the LLM's JSON array. Tolerates fenced output."""
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        try:
            arr = json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse triage batch JSON: {e}. Passing items through.")
            return [{"pass": True, "candidate_axes": ["UNKNOWN"], "confidence": "low"}] * expected

        if not isinstance(arr, list):
            logger.warning("Triage response was not a JSON array. Passing items through.")
            return [{"pass": True, "candidate_axes": ["UNKNOWN"], "confidence": "low"}] * expected

        # If the model returned fewer items than expected, pad with low-confidence passes.
        if len(arr) < expected:
            logger.warning(
                f"Triage returned {len(arr)} decisions for {expected} items. Padding."
            )
            arr = list(arr) + [
                {"pass": True, "candidate_axes": ["UNKNOWN"], "confidence": "low"}
            ] * (expected - len(arr))
        return arr[:expected]
