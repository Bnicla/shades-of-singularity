"""
Deduplication and result storage.

Local mode: SQLite database in output/observatory.db
Production mode: Vercel KV store
"""

import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional

logger = logging.getLogger("observatory.dedup")


class DedupStore:
    def __init__(self, mode: str = "local"):
        self.mode = mode
        if mode == "local":
            self._init_sqlite()
        else:
            self._init_kv()

    # ---- SQLite (local dev) ----

    def _init_sqlite(self):
        os.makedirs("output", exist_ok=True)
        self.db = sqlite3.connect("output/observatory.db")
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS seen (
                fingerprint TEXT PRIMARY KEY,
                first_seen TEXT NOT NULL,
                source TEXT
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint TEXT NOT NULL,
                date_evaluated TEXT NOT NULL,
                item_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                feedback TEXT DEFAULT NULL
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint TEXT NOT NULL,
                signal TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        self.db.commit()

    # ---- Vercel KV (production) ----

    def _init_kv(self):
        self.kv_url = os.environ.get("KV_REST_API_URL")
        self.kv_token = os.environ.get("KV_REST_API_TOKEN")
        if not self.kv_url or not self.kv_token:
            raise EnvironmentError("KV_REST_API_URL and KV_REST_API_TOKEN required in production mode")

        import requests
        self.kv_session = requests.Session()
        self.kv_session.headers.update({
            "Authorization": f"Bearer {self.kv_token}"
        })

    # ---- Public interface ----

    def filter_new(self, items: list[dict]) -> list[dict]:
        """Return only items not previously seen.

        Also dedups within the batch — the five arXiv search-query feeds
        can return the same paper, and they have the same canonical
        fingerprint after ingest.py normalization, so we keep only the
        first occurrence.
        """
        new = []
        seen_in_batch: set[str] = set()
        for item in items:
            fp = item.get("fingerprint", "")
            if not fp or fp in seen_in_batch:
                continue
            if not self._has_seen(fp):
                new.append(item)
                seen_in_batch.add(fp)
        return new

    @staticmethod
    def dedup_within_batch(items: list[dict]) -> list[dict]:
        """First-occurrence dedup by fingerprint, no `seen` table check.

        Used by backfill (skip_dedup=True) so the historical sweep
        still collapses duplicates across feeds.
        """
        out: list[dict] = []
        seen: set[str] = set()
        for item in items:
            fp = item.get("fingerprint", "")
            if not fp or fp in seen:
                continue
            seen.add(fp)
            out.append(item)
        return out

    def mark_seen(self, items: list[dict]):
        """Record items as seen so they won't be processed again."""
        now = datetime.now(timezone.utc).isoformat()
        for item in items:
            fp = item.get("fingerprint", "")
            if fp:
                self._set_seen(fp, now, item.get("source", ""))

    def store_results(self, results: list[dict]):
        """Store adjudication results."""
        now = datetime.now(timezone.utc).isoformat()
        for result in results:
            self._store_result(result, now)

    def get_recent_results(self, days: int = 30) -> list[dict]:
        """Retrieve results from the last N days for rendering."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        if self.mode == "local":
            cursor = self.db.execute(
                "SELECT result_json FROM results WHERE date_evaluated > ? ORDER BY date_evaluated DESC",
                (cutoff,)
            )
            return [json.loads(row[0]) for row in cursor.fetchall()]
        else:
            return self._kv_get_recent_results(cutoff)

    def load_candidates_blob(self) -> list[dict]:
        """Load the merged candidates JSON blob. Returns [] if absent."""
        if self.mode == "local":
            path = "output/candidates_blob.json"
            if os.path.exists(path):
                try:
                    with open(path) as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"candidates blob load failed: {e}")
            return []
        else:
            resp = self.kv_session.get(f"{self.kv_url}/get/observatory:candidates_blob")
            if resp.status_code != 200:
                return []
            data = resp.json().get("result")
            if not data:
                return []
            try:
                return json.loads(data)
            except Exception as e:
                logger.warning(f"candidates blob parse failed: {e}")
                return []

    def save_candidates_blob(self, candidates: list[dict]) -> None:
        """Persist the merged candidates list to the KV blob (or local JSON)."""
        payload = json.dumps(candidates)
        if self.mode == "local":
            os.makedirs("output", exist_ok=True)
            with open("output/candidates_blob.json", "w") as f:
                f.write(payload)
        else:
            self._kv_set("observatory:candidates_blob", payload)

    def load_filed_blob(self) -> list[dict]:
        """Load filed cards. Each entry is a card dict with a `signal`
        field ('integrated' | 'useful_later' | 'noise') stamped in.
        Filed cards don't age out — they're the user's curated history.
        """
        if self.mode == "local":
            path = "output/filed_blob.json"
            if os.path.exists(path):
                try:
                    with open(path) as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"filed blob load failed: {e}")
            return []
        else:
            resp = self.kv_session.get(f"{self.kv_url}/get/observatory:filed_blob")
            if resp.status_code != 200:
                return []
            data = resp.json().get("result")
            if not data:
                return []
            try:
                blob = json.loads(data)
                return blob if isinstance(blob, list) else []
            except Exception as e:
                logger.warning(f"filed blob parse failed: {e}")
                return []

    def save_filed_blob(self, filed: list[dict]) -> None:
        """Persist the filed cards list."""
        payload = json.dumps(filed)
        if self.mode == "local":
            os.makedirs("output", exist_ok=True)
            with open("output/filed_blob.json", "w") as f:
                f.write(payload)
        else:
            self._kv_set("observatory:filed_blob", payload)

    def load_feedback_map(self) -> dict:
        """Return {fingerprint: signal} derived from filed_blob.

        Kept for callers that just need a quick "has this fp been
        filed?" lookup without loading the whole card list.
        """
        out: dict = {}
        for card in self.load_filed_blob():
            fp = card.get("fingerprint", "")
            signal = card.get("signal")
            if fp and signal:
                out[fp] = signal
        return out

    def store_feedback(self, fingerprint: str, signal: str):
        """Store user feedback on a result (integrated / useful_later / noise)."""
        now = datetime.now(timezone.utc).isoformat()

        if self.mode == "local":
            self.db.execute(
                "INSERT INTO feedback (fingerprint, signal, timestamp) VALUES (?, ?, ?)",
                (fingerprint, signal, now)
            )
            self.db.commit()
        else:
            key = f"feedback:{fingerprint}"
            self._kv_set(key, json.dumps({"signal": signal, "timestamp": now}))

    def get_feedback_log(self) -> list[dict]:
        """Retrieve all feedback for calibration."""
        if self.mode == "local":
            cursor = self.db.execute(
                "SELECT fingerprint, signal, timestamp FROM feedback ORDER BY timestamp DESC"
            )
            return [
                {"fingerprint": r[0], "signal": r[1], "timestamp": r[2]}
                for r in cursor.fetchall()
            ]
        else:
            return self._kv_get_feedback_log()

    # ---- Internal: SQLite ----

    def _has_seen(self, fingerprint: str) -> bool:
        if self.mode == "local":
            cursor = self.db.execute(
                "SELECT 1 FROM seen WHERE fingerprint = ?", (fingerprint,)
            )
            return cursor.fetchone() is not None
        else:
            return self._kv_exists(f"seen:{fingerprint}")

    def _set_seen(self, fingerprint: str, timestamp: str, source: str):
        if self.mode == "local":
            self.db.execute(
                "INSERT OR IGNORE INTO seen (fingerprint, first_seen, source) VALUES (?, ?, ?)",
                (fingerprint, timestamp, source)
            )
            self.db.commit()
        else:
            self._kv_set(
                f"seen:{fingerprint}",
                json.dumps({"first_seen": timestamp, "source": source}),
                ex=90 * 86400  # TTL: 90 days
            )

    def _store_result(self, result: dict, timestamp: str):
        if self.mode == "local":
            self.db.execute(
                "INSERT INTO results (fingerprint, date_evaluated, item_json, result_json) VALUES (?, ?, ?, ?)",
                (
                    result.get("fingerprint", ""),
                    timestamp,
                    json.dumps(result.get("item", {})),
                    json.dumps(result)
                )
            )
            self.db.commit()
        else:
            key = f"result:{timestamp}:{result.get('fingerprint', '')}"
            self._kv_set(key, json.dumps(result), ex=180 * 86400)  # 180 day TTL

    # ---- Internal: Vercel KV ----

    def _kv_set(self, key: str, value: str, ex: Optional[int] = None):
        url = f"{self.kv_url}/set/{key}"
        params = {}
        if ex:
            params["ex"] = ex
        self.kv_session.post(url, params=params, data=value)

    def _kv_exists(self, key: str) -> bool:
        resp = self.kv_session.get(f"{self.kv_url}/exists/{key}")
        return resp.json().get("result", 0) > 0

    def _kv_get_recent_results(self, cutoff: str) -> list[dict]:
        # Vercel KV doesn't support range queries natively.
        # Use a sorted set or maintain a results index key.
        # Simplified: store a daily index key listing that day's result keys.
        # For MVP, scan recent keys.
        resp = self.kv_session.get(f"{self.kv_url}/keys/result:*")
        keys = resp.json().get("result", [])

        results = []
        for key in keys:
            if key > f"result:{cutoff}":
                resp = self.kv_session.get(f"{self.kv_url}/get/{key}")
                data = resp.json().get("result")
                if data:
                    results.append(json.loads(data))

        return sorted(results, key=lambda r: r.get("date", ""), reverse=True)

    def _kv_get_feedback_log(self) -> list[dict]:
        resp = self.kv_session.get(f"{self.kv_url}/keys/feedback:*")
        keys = resp.json().get("result", [])

        feedback = []
        for key in keys:
            resp = self.kv_session.get(f"{self.kv_url}/get/{key}")
            data = resp.json().get("result")
            if data:
                entry = json.loads(data)
                entry["fingerprint"] = key.replace("feedback:", "")
                feedback.append(entry)

        return feedback
