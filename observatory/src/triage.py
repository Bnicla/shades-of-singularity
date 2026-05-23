"""
Triage filter: cheap Gemini Flash pass to determine if an item
plausibly touches one of the six essay axes.

Generous filter. False positives are acceptable; false negatives are not.
"""

import json
import logging
import time
from typing import Optional

import requests

from prompts import TRIAGE_SYSTEM, TRIAGE_USER

logger = logging.getLogger("observatory.triage")

# Cost control: maximum items to triage per run
MAX_TRIAGE_BATCH = 200

# Gemini REST endpoint template
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class TriageFilter:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model

    def filter(self, items: list[dict]) -> list[dict]:
        """Filter items, returning those that pass triage."""
        if len(items) > MAX_TRIAGE_BATCH:
            logger.warning(
                f"Triage batch size {len(items)} exceeds limit {MAX_TRIAGE_BATCH}. "
                f"Processing first {MAX_TRIAGE_BATCH} only."
            )
            items = items[:MAX_TRIAGE_BATCH]

        passed = []
        for item in items:
            result = self._triage_single(item)
            if result and result.get("pass"):
                item["triage_axes"] = result.get("candidate_axes", [])
                item["triage_confidence"] = result.get("confidence", "low")
                passed.append(item)

        return passed

    def _triage_single(self, item: dict) -> Optional[dict]:
        """Run triage on a single item."""
        user_prompt = TRIAGE_USER.format(
            title=item.get("title", ""),
            source=item.get("source", ""),
            date=item.get("date", ""),
            abstract=item.get("abstract", "")[:1000]  # Limit input size
        )

        body = {
            "systemInstruction": {"parts": [{"text": TRIAGE_SYSTEM}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 300,
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }

        url = GEMINI_ENDPOINT.format(model=self.model)
        try:
            resp = requests.post(
                url,
                params={"key": self.api_key},
                json=body,
                timeout=30,
            )

            # Single retry on rate-limit
            if resp.status_code == 429:
                logger.warning("Triage rate-limited. Waiting 30s before retry.")
                time.sleep(30)
                resp = requests.post(
                    url,
                    params={"key": self.api_key},
                    json=body,
                    timeout=30,
                )

            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

            # responseMimeType=application/json should return clean JSON,
            # but defensively strip fences just in case
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

            return json.loads(text)

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.warning(f"Failed to parse triage response for '{item.get('title', '')}': {e}")
            # On parse failure, pass the item through (generous filter)
            return {"pass": True, "candidate_axes": ["UNKNOWN"], "confidence": "low"}
        except Exception as e:
            logger.error(f"Triage API error for '{item.get('title', '')}': {e}")
            # On API error, pass the item through
            return {"pass": True, "candidate_axes": ["UNKNOWN"], "confidence": "low"}
