"""
Vercel Serverless Function: file / reclassify / unfile observatory cards.

POST /api/observatory-feedback
Body: { "fingerprint": str, "signal": "integrated"|"useful_later"|"noise"|"pending" }

State model
-----------
There are two KV blobs:
  - observatory:candidates_blob — pending cards from the pipeline
  - observatory:filed_blob       — cards the user has decided on; each
                                   carries a `signal` field

Transitions
-----------
- "file"      : signal in {integrated, useful_later, noise}, card is
                currently in candidates_blob → move to filed_blob, stamp
                signal + timestamp, remove from candidates.
- "reclassify": signal in {integrated, useful_later, noise}, card is
                already in filed_blob → update its signal in place.
- "unfile"    : signal == "pending", card is in filed_blob → move back
                to candidates_blob, drop the signal.

Single-blob design (one JSON dict/list per blob) is intentional —
Vercel KV's KEYS pattern endpoint doesn't return matches reliably,
so we don't store per-fingerprint keys.

Environment variables required:
  KV_REST_API_URL
  KV_REST_API_TOKEN
"""

import json
import logging
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("observatory.feedback")

FILE_SIGNALS = {"integrated", "useful_later", "noise"}
ALL_SIGNALS = FILE_SIGNALS | {"pending"}  # "pending" means "send back to candidates"

CANDIDATES_KEY = "observatory:candidates_blob"
FILED_KEY = "observatory:filed_blob"


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw.decode("utf-8") or "{}")
        except Exception as e:
            return self._json(400, {"error": f"bad request body: {e}"})

        fingerprint = (body.get("fingerprint") or "").strip()
        signal = (body.get("signal") or "").strip()

        if not fingerprint:
            return self._json(400, {"error": "fingerprint required"})
        if signal not in ALL_SIGNALS:
            return self._json(400, {"error": f"signal must be one of {sorted(ALL_SIGNALS)}"})

        kv_url = os.environ.get("KV_REST_API_URL")
        kv_token = os.environ.get("KV_REST_API_TOKEN")
        if not kv_url or not kv_token:
            logger.error("KV credentials not configured")
            return self._json(500, {"error": "KV not configured"})

        auth = {"Authorization": f"Bearer {kv_token}"}

        try:
            candidates = self._load_list(kv_url, auth, CANDIDATES_KEY)
            filed = self._load_list(kv_url, auth, FILED_KEY)

            now = datetime.now(timezone.utc).isoformat()
            action = ""

            # Look the card up in both blobs.
            cand_idx = next(
                (i for i, c in enumerate(candidates) if c.get("fingerprint") == fingerprint),
                None,
            )
            filed_idx = next(
                (i for i, c in enumerate(filed) if c.get("fingerprint") == fingerprint),
                None,
            )

            if signal == "pending":
                # Unfile: move filed → candidates.
                if filed_idx is None:
                    return self._json(404, {"error": "card not in filed_blob"})
                card = filed.pop(filed_idx)
                card.pop("signal", None)
                card.pop("filed_at", None)
                # Avoid duplicates if it's somehow already pending.
                if cand_idx is None:
                    candidates.append(card)
                action = "unfile"
            else:
                # File (or reclassify if already filed).
                if filed_idx is not None:
                    filed[filed_idx]["signal"] = signal
                    filed[filed_idx]["filed_at"] = now
                    action = "reclassify"
                elif cand_idx is not None:
                    card = candidates.pop(cand_idx)
                    card["signal"] = signal
                    card["filed_at"] = now
                    filed.append(card)
                    action = "file"
                else:
                    return self._json(
                        404,
                        {"error": "card not found in candidates or filed"},
                    )

            self._save_list(kv_url, auth, CANDIDATES_KEY, candidates)
            self._save_list(kv_url, auth, FILED_KEY, filed)

        except requests.RequestException as e:
            logger.error(f"KV request failed: {e}")
            return self._json(502, {"error": "KV request failed"})

        return self._json(200, {
            "ok": True,
            "action": action,
            "fingerprint": fingerprint,
            "signal": signal,
        })

    # --------------------------------------------------------- helpers

    @staticmethod
    def _load_list(kv_url: str, auth: dict, key: str) -> list:
        resp = requests.get(f"{kv_url}/get/{key}", headers=auth, timeout=8)
        if resp.status_code != 200:
            return []
        data = resp.json().get("result")
        if not data:
            return []
        try:
            parsed = json.loads(data)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []

    @staticmethod
    def _save_list(kv_url: str, auth: dict, key: str, payload: list) -> None:
        put = requests.post(
            f"{kv_url}/set/{key}",
            headers=auth,
            data=json.dumps(payload),
            timeout=8,
        )
        if put.status_code >= 400:
            raise requests.RequestException(
                f"KV set {key} failed: {put.status_code} {put.text[:200]}"
            )

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        logger.info(format % args)
