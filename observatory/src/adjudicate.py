"""
Adjudicator: Gemini 2.5 Flash evaluation of whether an item bears on
a specific load-bearing claim in the essay collection.

This is the precision pass. Each item gets a full-text analysis
against the claim inventory defined in prompts.py.
"""

import json
import logging
import time
from typing import Optional

import requests

from prompts import ADJUDICATION_SYSTEM, ADJUDICATION_USER

logger = logging.getLogger("observatory.adjudicate")

# Cost control
MAX_ADJUDICATE_BATCH = 50
RATE_LIMIT_DELAY = 1.0  # seconds between API calls

# Gemini REST endpoint template
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class Adjudicator:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
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
                # Merge item metadata into result for rendering
                result["item"] = {
                    "title": item.get("title", ""),
                    "source": item.get("source", ""),
                    "authors": item.get("authors", []),
                    "date": item.get("date", ""),
                    "url": item.get("url", ""),
                    "tier": item.get("tier", 0),
                    "named_scholar": item.get("named_scholar"),
                }
                result["fingerprint"] = item.get("fingerprint", "")
                results.append(result)

            # Rate limiting
            if i < len(items) - 1:
                time.sleep(RATE_LIMIT_DELAY)

        return results

    def _adjudicate_single(self, item: dict, _retry: bool = False) -> Optional[dict]:
        """Run adjudication on a single item."""
        # Use full text if available, fall back to abstract
        text = item.get("text", "") or item.get("abstract", "")

        # Truncate very long texts to manage token costs
        words = text.split()
        if len(words) > 3000:
            text = " ".join(words[:3000]) + "\n\n[... truncated for evaluation ...]"

        user_prompt = ADJUDICATION_USER.format(
            title=item.get("title", ""),
            source=item.get("source", ""),
            authors=", ".join(item.get("authors", [])),
            date=item.get("date", ""),
            url=item.get("url", ""),
            text=text
        )

        body = {
            "systemInstruction": {"parts": [{"text": ADJUDICATION_SYSTEM}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 800,
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
                timeout=60,
            )

            # Rate-limit handling: one retry after 60s
            if resp.status_code == 429:
                if not _retry:
                    logger.warning("Adjudication rate-limited. Waiting 60s before retry.")
                    time.sleep(60)
                    return self._adjudicate_single(item, _retry=True)
                else:
                    raise RuntimeError("Adjudication rate-limit retry exhausted")

            resp.raise_for_status()
            data = resp.json()
            response_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

            # responseMimeType=application/json should return clean JSON,
            # but defensively strip code fences
            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1] if "\n" in response_text else response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

            result = json.loads(response_text)

            # Validate required fields
            required = ["clears_bar", "confidence", "primary_claim", "relationship", "summary"]
            for field in required:
                if field not in result:
                    result[field] = None

            return result

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.warning(f"Failed to parse adjudication for '{item.get('title', '')}': {e}")
            return {
                "clears_bar": False,
                "confidence": "low",
                "primary_claim": None,
                "secondary_claims": [],
                "relationship": None,
                "summary": f"Parse error during adjudication: {e}",
                "citation_quality": "unknown",
                "named_scholar_match": item.get("tier") == 1,
                "integration_note": None
            }
        except Exception as e:
            logger.error(f"Adjudication API error for '{item.get('title', '')}': {e}")
            return {
                "clears_bar": False,
                "confidence": "low",
                "primary_claim": None,
                "secondary_claims": [],
                "relationship": None,
                "summary": f"API error: {e}",
                "citation_quality": "unknown",
                "named_scholar_match": item.get("tier") == 1,
                "integration_note": None
            }
