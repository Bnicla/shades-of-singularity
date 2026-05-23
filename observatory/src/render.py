"""
Observatory page renderer.

Generates a self-contained static HTML page styled to match
the shadesofsingularity.com aesthetic: cream background, amber accent,
Source Serif 4 body, Instrument Sans headings.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger("observatory.render")

# Claim ID to essay title mapping
CLAIM_ESSAYS = {
    "e1": "On the End of Work as We Know It",
    "e2": "On the Economics of Truth",
    "e3": "On the Automation of Power",
    "e4": "On the Hollowing of the Human",
    "e5": "On the Inheritance We Choose",
    "e6": "On the Choices That Remain",
}

CLAIM_AXES = {
    "e1": "Labor",
    "e2": "Truth",
    "e3": "Power",
    "e4": "Human",
    "e5": "Inheritance",
    "e6": "Governance",
}

CLAIM_DESCRIPTIONS = {
    "e1_c1": "Task-share framework vs. occupation-level predictions",
    "e1_c2": "Hulten's theorem constraining macro AI impact",
    "e1_c3": "Regressive distributional effects without intervention",
    "e1_c4": "Task-share gap between exposure and impact",
    "e2_c1": "Triple asymmetry framework",
    "e2_c2": "Epistemic infrastructure as distinct category",
    "e2_c3": "Provenance/watermarking necessary but insufficient",
    "e3_c1": "Power concentration through decision automation",
    "e3_c2": "Self-reinforcing feedback loops and lock-in",
    "e4_c1": "Developmental vs. substitutive scaffolding distinction",
    "e4_c2": "DKE caveat on capacity degradation self-assessment",
    "e4_c3": "Current AI deployment predominantly substitutive",
    "e5_c1": "Agenesis vs. atrophy distinction",
    "e5_c2": "Sensitive periods and irreversible deficits",
    "e6_c1": "3-to-7-year chokepoint window",
    "e6_c2": "Three erosion vectors closing the window",
    "e6_c3": "Four coalition-mobilizing grievances",
    "e6_c4": "Developmental foundation interventions most durable",
    "e6_c5": "RSP v3.0 meaningful but insufficient",
}

RELATIONSHIP_LABELS = {
    "strengthens": "Strengthens",
    "weakens": "Challenges",
    "extends": "Extends",
    "reframes": "Reframes",
}

RELATIONSHIP_COLORS = {
    "strengthens": "#2d6a4f",
    "weakens": "#c1121f",
    "extends": "#B8860B",
    "reframes": "#4a5568",
}


class ObservatoryRenderer:
    def __init__(self, template_path: str = "templates/observatory.html"):
        self.template_path = template_path

    def render(
        self,
        results: list[dict],
        output_path: str,
        title: Optional[str] = None
    ):
        """Render the observatory page from adjudication results."""
        now = datetime.now(timezone.utc)

        # Separate high-confidence (auto-filed) from medium (flagged)
        clears = [r for r in results if r.get("clears_bar") and r.get("confidence") == "high"]
        flagged = [r for r in results if r.get("clears_bar") and r.get("confidence") == "medium"]
        # Low confidence / doesn't clear: not rendered

        # Group by essay axis
        clears_by_axis = self._group_by_axis(clears)
        flagged_by_axis = self._group_by_axis(flagged)

        # Build archive (group by month)
        archive = self._build_archive(results)

        # Prepare template context
        context = {
            "title": title or "Observatory",
            "generated_at": now.strftime("%B %d, %Y at %H:%M UTC"),
            "generated_iso": now.isoformat(),
            "clears_by_axis": clears_by_axis,
            "flagged_by_axis": flagged_by_axis,
            "clears_count": len(clears),
            "flagged_count": len(flagged),
            "total_scanned": len(results),
            "archive": archive,
            "claim_essays": CLAIM_ESSAYS,
            "claim_axes": CLAIM_AXES,
            "claim_descriptions": CLAIM_DESCRIPTIONS,
            "relationship_labels": RELATIONSHIP_LABELS,
            "relationship_colors": RELATIONSHIP_COLORS,
        }

        # Render with Jinja2
        try:
            env = Environment(loader=FileSystemLoader("."))
            template = env.get_template(self.template_path)
            html = template.render(**context)
        except Exception:
            # Fallback: generate HTML directly if template not found
            html = self._render_inline(context)

        # Write output
        with open(output_path, "w") as f:
            f.write(html)

        logger.info(f"Rendered {output_path}: {len(clears)} clears, {len(flagged)} flagged")

    def _group_by_axis(self, results: list[dict]) -> dict:
        """Group results by their primary essay axis."""
        grouped = {}
        for result in results:
            claim = result.get("primary_claim", "")
            if claim:
                axis = claim.split("_")[0]  # e.g., "e1" from "e1_c2"
            else:
                axis = "unknown"

            axis_label = CLAIM_AXES.get(axis, "Other")
            if axis_label not in grouped:
                grouped[axis_label] = []
            grouped[axis_label].append(result)

        # Sort axes in essay order
        order = ["Labor", "Truth", "Power", "Human", "Inheritance", "Governance", "Other"]
        return {k: grouped[k] for k in order if k in grouped}

    def _build_archive(self, results: list[dict]) -> dict:
        """Group all results by month for the archive section."""
        archive = {}
        for result in results:
            date_str = result.get("item", {}).get("date", "")
            if date_str:
                try:
                    month = date_str[:7]  # "2026-05"
                    if month not in archive:
                        archive[month] = []
                    archive[month].append(result)
                except Exception:
                    pass

        # Sort months descending
        return dict(sorted(archive.items(), reverse=True))

    def _render_inline(self, ctx: dict) -> str:
        """Fallback renderer: generates HTML without Jinja2 template."""
        cards_html = ""

        # Clears section
        if ctx["clears_count"] > 0:
            cards_html += '<section class="section"><h2>Clears the bar</h2>'
            for axis, items in ctx["clears_by_axis"].items():
                cards_html += f'<h3 class="axis-header">{axis}</h3>'
                for r in items:
                    cards_html += self._render_card(r, ctx)
            cards_html += "</section>"

        # Flagged section
        if ctx["flagged_count"] > 0:
            cards_html += '<section class="section"><h2>Flagged for review</h2>'
            for axis, items in ctx["flagged_by_axis"].items():
                cards_html += f'<h3 class="axis-header">{axis}</h3>'
                for r in items:
                    cards_html += self._render_card(r, ctx)
            cards_html += "</section>"

        if ctx["clears_count"] == 0 and ctx["flagged_count"] == 0:
            cards_html = '<section class="section"><p class="empty">No items cleared the bar in this period.</p></section>'

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>{ctx['title']} | Shades of Singularity</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;1,8..60,400&family=Instrument+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root {{
    --bg: #FDFBF7;
    --text: #2c2c2c;
    --text-secondary: #6b6b6b;
    --accent: #B8860B;
    --accent-light: rgba(184, 134, 11, 0.08);
    --border: #e8e2d8;
    --card-bg: #ffffff;
    --strengthens: #2d6a4f;
    --weakens: #c1121f;
    --extends: #B8860B;
    --reframes: #4a5568;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    font-family: 'Source Serif 4', Georgia, serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    max-width: 780px;
    margin: 0 auto;
    padding: 3rem 1.5rem;
}}

header {{
    margin-bottom: 3rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}}

header h1 {{
    font-family: 'Instrument Sans', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: var(--text);
    margin-bottom: 0.3rem;
}}

header .subtitle {{
    font-size: 0.9rem;
    color: var(--text-secondary);
    font-style: italic;
}}

header .meta {{
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 0.8rem;
}}

.section {{
    margin-bottom: 2.5rem;
}}

.section h2 {{
    font-family: 'Instrument Sans', sans-serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--accent);
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}

.axis-header {{
    font-family: 'Instrument Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin: 1.5rem 0 0.8rem;
    padding-left: 0.5rem;
    border-left: 3px solid var(--accent);
}}

.card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}}

.card:hover {{
    border-color: var(--accent);
}}

.card-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 0.6rem;
}}

.card-title {{
    font-family: 'Instrument Sans', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    line-height: 1.4;
}}

.card-title a {{
    color: var(--text);
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: border-color 0.2s;
}}

.card-title a:hover {{
    border-bottom-color: var(--accent);
}}

.relationship-tag {{
    font-family: 'Instrument Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.15rem 0.5rem;
    border-radius: 2px;
    white-space: nowrap;
    color: white;
}}

.card-meta {{
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-bottom: 0.6rem;
}}

.card-claim {{
    font-size: 0.82rem;
    color: var(--accent);
    margin-bottom: 0.5rem;
    font-style: italic;
}}

.card-summary {{
    font-size: 0.88rem;
    line-height: 1.6;
    margin-bottom: 0.5rem;
}}

.card-integration {{
    font-size: 0.82rem;
    color: var(--text-secondary);
    padding: 0.5rem 0.8rem;
    background: var(--accent-light);
    border-radius: 3px;
    margin-top: 0.5rem;
}}

.card-feedback {{
    display: flex;
    gap: 0.5rem;
    margin-top: 0.8rem;
    padding-top: 0.6rem;
    border-top: 1px solid var(--border);
}}

.feedback-btn {{
    font-family: 'Instrument Sans', sans-serif;
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
    border: 1px solid var(--border);
    border-radius: 2px;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
}}

.feedback-btn:hover {{
    border-color: var(--accent);
    color: var(--accent);
}}

.empty {{
    font-style: italic;
    color: var(--text-secondary);
    padding: 2rem 0;
}}

.archive {{
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
}}

.archive h2 {{
    font-family: 'Instrument Sans', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}}

.archive-month {{
    margin-bottom: 1.5rem;
}}

.archive-month h3 {{
    font-family: 'Instrument Sans', sans-serif;
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 0.4rem;
}}

.archive-item {{
    font-size: 0.82rem;
    padding: 0.3rem 0;
    color: var(--text);
}}

.archive-item a {{
    color: var(--text);
    text-decoration: none;
    border-bottom: 1px dotted var(--border);
}}

.archive-item .archive-axis {{
    font-family: 'Instrument Sans', sans-serif;
    font-size: 0.7rem;
    color: var(--text-secondary);
}}

footer {{
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    font-size: 0.75rem;
    color: var(--text-secondary);
    text-align: center;
}}

@media (max-width: 600px) {{
    body {{ padding: 1.5rem 1rem; }}
    .card-header {{ flex-direction: column; gap: 0.4rem; }}
}}
</style>
</head>
<body>
<header>
    <h1>{ctx['title']}</h1>
    <div class="subtitle">Research monitor for the Shades of Singularity collection</div>
    <div class="meta">
        Last updated: {ctx['generated_at']}<br>
        {ctx['total_scanned']} items scanned | {ctx['clears_count']} clear the bar | {ctx['flagged_count']} flagged for review
    </div>
</header>

{cards_html}

<footer>
    Observatory | Shades of Singularity<br>
    Automated research monitor. Not linked from the public site.
</footer>
</body>
</html>"""

    def _render_card(self, result: dict, ctx: dict) -> str:
        item = result.get("item", {})
        claim_id = result.get("primary_claim", "")
        relationship = result.get("relationship", "")
        rel_label = RELATIONSHIP_LABELS.get(relationship, "")
        rel_color = RELATIONSHIP_COLORS.get(relationship, "#888")

        claim_desc = CLAIM_DESCRIPTIONS.get(claim_id, "")
        essay_key = claim_id.split("_")[0] if claim_id else ""
        essay_title = CLAIM_ESSAYS.get(essay_key, "")

        authors = ", ".join(item.get("authors", [])[:3])
        if len(item.get("authors", [])) > 3:
            authors += " et al."

        tag_html = ""
        if rel_label:
            tag_html = f'<span class="relationship-tag" style="background:{rel_color}">{rel_label}</span>'

        claim_html = ""
        if claim_desc:
            claim_html = f'<div class="card-claim">Bears on: {claim_desc} ({essay_title})</div>'

        integration_html = ""
        if result.get("integration_note"):
            integration_html = f'<div class="card-integration">{result["integration_note"]}</div>'

        source_badge = item.get("source", "")
        citation_quality = result.get("citation_quality", "")
        if citation_quality:
            source_badge += f" | {citation_quality.replace('_', ' ')}"

        fp = result.get("fingerprint", "").replace('"', "&quot;")

        return f"""
<div class="card" data-fingerprint="{fp}">
    <div class="card-header">
        <div class="card-title"><a href="{item.get('url', '#')}" target="_blank" rel="noopener">{item.get('title', 'Untitled')}</a></div>
        {tag_html}
    </div>
    <div class="card-meta">{authors} | {source_badge} | {item.get('date', '')[:10]}</div>
    {claim_html}
    <div class="card-summary">{result.get('summary', '')}</div>
    {integration_html}
    <div class="card-feedback">
        <button class="feedback-btn" onclick="sendFeedback('{fp}', 'integrated')">Integrated</button>
        <button class="feedback-btn" onclick="sendFeedback('{fp}', 'useful_later')">Useful later</button>
        <button class="feedback-btn" onclick="sendFeedback('{fp}', 'noise')">Noise</button>
    </div>
</div>"""
