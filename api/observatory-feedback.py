"""
Vercel Serverless Function: receive observatory feedback.

POST /api/observatory-feedback
Body: { "fingerprint": str, "signal": "integrated"|"useful_later"|"noise" }

Persists feedback in a single Vercel KV blob keyed `observatory:feedback_blob`,
shaped as { fingerprint -> { signal, timestamp } }. The pipeline reads this
blob during render to hide 'noise' items and badge 'integrated' / 'useful_later'.

Single-blob design is intentional — Vercel KV's KEYS pattern endpoint doesn't
return matches reliably, so we don't store per-fingerprint keys.

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

VALID_SIGNALS = {"integrated", "useful_later", "noise"}
BLOB_KEY = "observatory:feedback_blob"


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
        if signal not in VALID_SIGNALS:
            return self._json(400, {"error": f"signal must be one of {sorted(VALID_SIGNALS)}"})

        kv_url = os.environ.get("KV_REST_API_URL")
        kv_token = os.environ.get("KV_REST_API_TOKEN")
        if not kv_url or not kv_token:
            logger.error("KV credentials not configured")
            return self._json(500, {"error": "KV not configured"})

        auth = {"Authorization": f"Bearer {kv_token}"}

        # Read-modify-write the single feedback blob. Not concurrency-safe
        # but feedback is human-paced (clicks per second, not per ms).
        try:
            resp = requests.get(f"{kv_url}/get/{BLOB_KEY}", headers=auth, timeout=8)
            blob: dict = {}
            if resp.status_code == 200:
                data = resp.json().get("result")
                if data:
                    try:
                        parsed = json.loads(data)
                        if isinstance(parsed, dict):
                            blob = parsed
                    except Exception as e:
                        logger.warning(f"feedback blob unparseable, overwriting: {e}")

            blob[fingerprint] = {
                "signal": signal,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            payload = json.dumps(blob)

            put = requests.post(
                f"{kv_url}/set/{BLOB_KEY}",
                headers=auth,
                data=payload,
                timeout=8,
            )
            if put.status_code >= 400:
                logger.error(f"KV set failed: {put.status_code} {put.text[:200]}")
                return self._json(502, {"error": "could not persist feedback"})

        except requests.RequestException as e:
            logger.error(f"KV request failed: {e}")
            return self._json(502, {"error": "KV request failed"})

        return self._json(200, {"ok": True, "fingerprint": fingerprint, "signal": signal})

    def do_OPTIONS(self):
        # CORS preflight (same-origin in practice, but defensive)
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
