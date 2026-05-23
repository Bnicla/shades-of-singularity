"""
Vercel Serverless Function: serves the observatory page.

Reads the latest rendered HTML from Vercel KV and returns it.
Proxied via rewrite rule: /observatory -> /api/observatory-serve

The page is pre-rendered by the cron function and stored as a
single HTML string in KV under the key "observatory:current".

Environment variables required:
  KV_REST_API_URL
  KV_REST_API_TOKEN
"""

import json
import logging
import os
from http.server import BaseHTTPRequestHandler

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("observatory.serve")

# Fallback page shown when no rendered content exists yet
FALLBACK_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Observatory | Shades of Singularity</title>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400&family=Instrument+Sans:wght@600&display=swap" rel="stylesheet">
<style>
body {
    font-family: 'Source Serif 4', Georgia, serif;
    background: #FDFBF7;
    color: #2c2c2c;
    max-width: 600px;
    margin: 0 auto;
    padding: 4rem 1.5rem;
    text-align: center;
    line-height: 1.7;
}
h1 {
    font-family: 'Instrument Sans', sans-serif;
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: 1rem;
}
p { color: #6b6b6b; }
</style>
</head>
<body>
<h1>Observatory</h1>
<p>The research monitor is initializing. The first scan has not yet run.</p>
<p>Check back after 10 AM UTC.</p>
</body>
</html>"""


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            html = self._get_current_page()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "public, max-age=3600, s-maxage=3600")
            self.send_header("X-Robots-Tag", "noindex, nofollow")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        except Exception as e:
            logger.error(f"Serve failed: {e}", exc_info=True)
            self.send_response(200)  # Still 200; show fallback
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(FALLBACK_HTML.encode("utf-8"))

    def _get_current_page(self) -> str:
        kv_url = os.environ.get("KV_REST_API_URL")
        kv_token = os.environ.get("KV_REST_API_TOKEN")

        if not kv_url or not kv_token:
            logger.warning("KV credentials not configured")
            return FALLBACK_HTML

        resp = requests.get(
            f"{kv_url}/get/observatory:current",
            headers={"Authorization": f"Bearer {kv_token}"},
            timeout=5
        )

        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result")
            if result:
                return result

        return FALLBACK_HTML

    def log_message(self, format, *args):
        logger.info(format % args)
