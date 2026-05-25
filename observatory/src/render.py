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
        title: Optional[str] = None,
        feedback: Optional[dict] = None,
        filed: Optional[list] = None,
    ):
        """Render the observatory page.

        `results` is the pending-tab content (cards from candidates_blob).
        `filed` is the user-filed content (cards from filed_blob, each with
        a `signal` field). Cards split into 4 tabs: Pending / Integrated /
        Useful later / Noise.

        `feedback` is kept for backward compatibility and ignored if
        `filed` is provided.
        """
        now = datetime.now(timezone.utc)
        filed = filed or []
        # Backward-compat shim: synthesize feedback map from filed for
        # any caller still passing it.
        feedback = feedback or {
            c.get("fingerprint", ""): c.get("signal")
            for c in filed
            if c.get("fingerprint") and c.get("signal")
        }

        # Pending = results passed in (already excludes filed at pipeline).
        # Sub-split into "clears" (top) and "flagged" (rest) for visual
        # priority inside the Pending tab.
        clears = [r for r in results if r.get("clears_bar") and r.get("confidence") == "high"]
        flagged = [r for r in results if r.get("clears_bar") and r.get("confidence") == "medium"]

        # Filed buckets
        integrated = [c for c in filed if c.get("signal") == "integrated"]
        useful_later = [c for c in filed if c.get("signal") == "useful_later"]
        noise = [c for c in filed if c.get("signal") == "noise"]

        # Group pending by essay axis (unchanged)
        clears_by_axis = self._group_by_axis(clears)
        flagged_by_axis = self._group_by_axis(flagged)

        archive = self._build_archive(results)

        context = {
            "title": title or "Observatory",
            "generated_at": now.strftime("%B %d, %Y at %H:%M UTC"),
            "generated_iso": now.isoformat(),
            "clears_by_axis": clears_by_axis,
            "flagged_by_axis": flagged_by_axis,
            "clears_count": len(clears),
            "flagged_count": len(flagged),
            "pending_count": len(clears) + len(flagged),
            "integrated_cards": integrated,
            "useful_later_cards": useful_later,
            "noise_cards": noise,
            "integrated_count": len(integrated),
            "useful_later_count": len(useful_later),
            "noise_count": len(noise),
            "total_scanned": len(results) + len(filed),
            "feedback": feedback,
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
        # --- Pending panel ---
        pending_html = ""
        if ctx["clears_count"] > 0:
            pending_html += '<section class="section"><h2>Clears the bar</h2>'
            for axis, items in ctx["clears_by_axis"].items():
                pending_html += f'<h3 class="axis-header">{axis}</h3>'
                for r in items:
                    pending_html += self._render_card(r, ctx)
            pending_html += "</section>"
        if ctx["flagged_count"] > 0:
            pending_html += '<section class="section"><h2>Flagged for review</h2>'
            for axis, items in ctx["flagged_by_axis"].items():
                pending_html += f'<h3 class="axis-header">{axis}</h3>'
                for r in items:
                    pending_html += self._render_card(r, ctx)
            pending_html += "</section>"
        if ctx["clears_count"] == 0 and ctx["flagged_count"] == 0:
            pending_html = '<section class="section"><p class="empty">Nothing pending right now. Filed items live in the other tabs.</p></section>'

        # --- Filed panels (Integrated / Useful later / Noise) ---
        def _render_filed_list(cards: list, empty_msg: str) -> str:
            if not cards:
                return f'<section class="section"><p class="empty">{empty_msg}</p></section>'
            # Sort newest-filed first if filed_at exists, else by score
            sorted_cards = sorted(
                cards,
                key=lambda c: c.get("filed_at") or c.get("item", {}).get("date", ""),
                reverse=True,
            )
            html = '<section class="section">'
            for c in sorted_cards:
                html += self._render_card(c, ctx)
            html += "</section>"
            return html

        integrated_html = _render_filed_list(
            ctx["integrated_cards"],
            "Nothing here yet. Click ‘Integrated’ on a pending card to file it here.",
        )
        useful_later_html = _render_filed_list(
            ctx["useful_later_cards"],
            "Nothing here yet. ‘Useful later’ flags items to revisit without committing to integration.",
        )
        noise_html = _render_filed_list(
            ctx["noise_cards"],
            "Nothing here yet. Items you mark ‘Noise’ land here so you can audit your own filtering.",
        )

        # Tabs nav
        tabs_html = f"""
<nav class="tabs" role="tablist">
  <button class="tab" data-tab="pending"      role="tab" aria-selected="true">Pending <span class="tab-count">{ctx['pending_count']}</span></button>
  <button class="tab" data-tab="integrated"   role="tab" aria-selected="false">Integrated <span class="tab-count">{ctx['integrated_count']}</span></button>
  <button class="tab" data-tab="useful_later" role="tab" aria-selected="false">Useful later <span class="tab-count">{ctx['useful_later_count']}</span></button>
  <button class="tab" data-tab="noise"        role="tab" aria-selected="false">Noise <span class="tab-count">{ctx['noise_count']}</span></button>
</nav>
<div class="search-bar">
  <input type="search" id="card-search" placeholder="Filter cards in the current tab by title, source, or claim…" autocomplete="off">
</div>
"""

        panels_html = f"""
<section class="tab-panel" data-panel="pending">{pending_html}</section>
<section class="tab-panel" data-panel="integrated" hidden>{integrated_html}</section>
<section class="tab-panel" data-panel="useful_later" hidden>{useful_later_html}</section>
<section class="tab-panel" data-panel="noise" hidden>{noise_html}</section>
"""

        cards_html = tabs_html + panels_html

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>{ctx['title']} | Shades of Singularity</title>
<script>
// Match main-site behavior: read stored preference (else system), set
// data-theme on <html> BEFORE first paint so the page doesn't flash.
(function() {{
    var stored = localStorage.getItem('theme');
    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.setAttribute('data-theme', stored || (prefersDark ? 'dark' : 'light'));
}})();
</script>
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

[data-theme="dark"] {{
    --bg: #1A1814;
    --text: #E8E0D4;
    --text-secondary: #A09888;
    --accent: #D4A942;
    --accent-light: rgba(212, 169, 66, 0.13);
    --border: #3A352E;
    --card-bg: #252118;
    --strengthens: #57b896;
    --weakens: #ef5060;
    --extends: #D4A942;
    --reframes: #8b9bbf;
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

.header-top {{
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
}}

.dark-mode-toggle {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background: none;
    border: none;
    cursor: pointer;
    flex-shrink: 0;
    transition: background-color 0.15s ease;
}}

.dark-mode-toggle:hover {{
    background-color: var(--accent-light);
}}

.dark-mode-toggle svg {{
    width: 1.125rem;
    height: 1.125rem;
    stroke: var(--text-secondary);
    fill: none;
    stroke-width: 1.5;
    stroke-linecap: round;
    stroke-linejoin: round;
}}

.dark-mode-toggle .icon-sun {{ display: none; }}
.dark-mode-toggle .icon-moon {{ display: block; }}
[data-theme="dark"] .dark-mode-toggle .icon-sun {{ display: block; }}
[data-theme="dark"] .dark-mode-toggle .icon-moon {{ display: none; }}

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

.feedback-btn.actioned {{
    opacity: 0.4;
    cursor: default;
    pointer-events: none;
}}

.feedback-status {{
    font-family: 'Instrument Sans', sans-serif;
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
    color: var(--accent);
    align-self: center;
}}

.feedback-status[data-signal="noise"] {{
    color: var(--text-secondary);
    opacity: 0.6;
}}

/* Indicate which signal a filed card currently carries */
.feedback-btn.active {{
    border-color: var(--accent);
    color: var(--accent);
    background: var(--accent-light);
    font-weight: 600;
}}

/* Tabs */
.tabs {{
    display: flex;
    gap: 0.25rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}}

.tab {{
    font-family: 'Instrument Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.6rem 1rem;
    margin-bottom: -1px;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-secondary);
    cursor: pointer;
    white-space: nowrap;
    transition: color 0.15s, border-color 0.15s;
}}

.tab:hover {{
    color: var(--text);
}}

.tab[aria-selected="true"] {{
    color: var(--text);
    border-bottom-color: var(--accent);
}}

.tab-count {{
    display: inline-block;
    margin-left: 0.4rem;
    padding: 0.05rem 0.45rem;
    background: var(--accent-light);
    color: var(--accent);
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
}}

.tab[aria-selected="true"] .tab-count {{
    background: var(--accent);
    color: var(--bg);
}}

.tab-panel[hidden] {{ display: none; }}

/* Search box */
.search-bar {{
    margin-bottom: 2rem;
}}

#card-search {{
    width: 100%;
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.92rem;
    padding: 0.6rem 0.9rem;
    background: var(--card-bg);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 4px;
    transition: border-color 0.15s;
}}

#card-search:focus {{
    outline: none;
    border-color: var(--accent);
}}

#card-search::placeholder {{
    color: var(--text-secondary);
    opacity: 0.8;
}}

.card.search-hidden {{ display: none; }}

/* Integration source chips */
.card-sources {{
    margin-top: 0.7rem;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.4rem;
    font-family: 'Instrument Sans', sans-serif;
    font-size: 0.72rem;
    color: var(--text-secondary);
}}

.card-sources-label {{
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-right: 0.2rem;
}}

.source-chip {{
    display: inline-flex;
    align-items: center;
    padding: 0.15rem 0.65rem;
    background: var(--accent-light);
    color: var(--accent);
    text-decoration: none;
    border-radius: 999px;
    font-weight: 600;
    border: 1px solid transparent;
    transition: border-color 0.15s, background-color 0.15s;
    white-space: nowrap;
}}

.source-chip:hover {{
    border-color: var(--accent);
    background: var(--accent-light);
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
    <div class="header-top">
        <h1>{ctx['title']}</h1>
        <button class="dark-mode-toggle" aria-label="Toggle dark mode" onclick="toggleTheme()">
            <svg class="icon-sun" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="5"/>
                <line x1="12" y1="1" x2="12" y2="3"/>
                <line x1="12" y1="21" x2="12" y2="23"/>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                <line x1="1" y1="12" x2="3" y2="12"/>
                <line x1="21" y1="12" x2="23" y2="12"/>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
            </svg>
            <svg class="icon-moon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
        </button>
    </div>
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

<script>
// ---------- Theme toggle ----------
function toggleTheme() {{
    var current = document.documentElement.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
}}
window.matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', function(e) {{
        if (!localStorage.getItem('theme')) {{
            document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
        }}
    }});

// ---------- Tabs (with #hash routing) ----------
const VALID_TABS = ['pending', 'integrated', 'useful_later', 'noise'];

function showTab(name) {{
    if (!VALID_TABS.includes(name)) name = 'pending';
    document.querySelectorAll('.tab').forEach(function(btn) {{
        btn.setAttribute('aria-selected', btn.dataset.tab === name ? 'true' : 'false');
    }});
    document.querySelectorAll('.tab-panel').forEach(function(panel) {{
        panel.hidden = (panel.dataset.panel !== name);
    }});
    applySearchFilter();
}}

document.querySelectorAll('.tab').forEach(function(btn) {{
    btn.addEventListener('click', function() {{
        const name = btn.dataset.tab;
        history.replaceState(null, '', '#' + name);
        showTab(name);
    }});
}});

window.addEventListener('hashchange', function() {{
    showTab((location.hash || '#pending').slice(1));
}});

// ---------- Search (filters within active tab) ----------
function applySearchFilter() {{
    const input = document.getElementById('card-search');
    if (!input) return;
    const q = input.value.trim().toLowerCase();
    const active = document.querySelector('.tab-panel:not([hidden])');
    if (!active) return;
    active.querySelectorAll('.card').forEach(function(card) {{
        const hay = card.dataset.search || '';
        card.classList.toggle('search-hidden', q && hay.indexOf(q) === -1);
    }});
}}

document.addEventListener('DOMContentLoaded', function() {{
    showTab((location.hash || '#pending').slice(1));
    const input = document.getElementById('card-search');
    if (input) input.addEventListener('input', applySearchFilter);
}});

// ---------- File / reclassify / unfile ----------
async function sendFeedback(btn, fp, signal) {{
    const card = btn.closest('.card');
    const buttons = card ? card.querySelectorAll('.feedback-btn') : [btn];
    buttons.forEach(b => b.disabled = true);
    try {{
        const resp = await fetch('/api/observatory-feedback', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{fingerprint: fp, signal: signal}}),
        }});
        if (!resp.ok) throw new Error('HTTP ' + resp.status);

        // Move the card to the target panel client-side so the user
        // doesn't have to wait for the next render.
        if (card) {{
            const targetPanel = document.querySelector('.tab-panel[data-panel="' + signal + '"]');
            if (targetPanel) {{
                // Update tab counts
                adjustCount(card.closest('.tab-panel').dataset.panel, -1);
                adjustCount(signal, +1);
                // Mark active button
                buttons.forEach(b => {{
                    b.classList.toggle('active', b.dataset.signal === signal);
                    b.disabled = false;
                }});
                // Ensure the unfile button exists when moving into a filed tab
                ensureUnfileButton(card, fp, signal);
                // Strip placeholder "empty" message from the destination if present
                const empty = targetPanel.querySelector('.empty');
                if (empty) empty.closest('.section').remove();
                // Find or create a section to host the card in the target panel
                let section = targetPanel.querySelector('.section');
                if (!section) {{
                    section = document.createElement('section');
                    section.className = 'section';
                    targetPanel.appendChild(section);
                }}
                section.prepend(card);
                applySearchFilter();
            }}
        }}
    }} catch (err) {{
        console.error('feedback failed', err);
        buttons.forEach(b => b.disabled = false);
        alert('Could not save feedback: ' + err.message);
    }}
}}

function adjustCount(panelName, delta) {{
    const tab = document.querySelector('.tab[data-tab="' + panelName + '"] .tab-count');
    if (!tab) return;
    const n = parseInt(tab.textContent, 10) || 0;
    tab.textContent = Math.max(0, n + delta);
}}

function ensureUnfileButton(card, fp, signal) {{
    const wrap = card.querySelector('.card-feedback');
    if (!wrap) return;
    let unfile = wrap.querySelector('.feedback-btn[data-signal="pending"]');
    if (signal === 'pending') {{
        // We're moving back to pending: remove unfile button + clear active states
        if (unfile) unfile.remove();
        wrap.querySelectorAll('.feedback-btn').forEach(b => b.classList.remove('active'));
        return;
    }}
    if (!unfile) {{
        unfile = document.createElement('button');
        unfile.className = 'feedback-btn';
        unfile.dataset.signal = 'pending';
        unfile.title = 'Send back to Pending';
        unfile.textContent = '↩ Pending';
        unfile.addEventListener('click', () => sendFeedback(unfile, fp, 'pending'));
        wrap.appendChild(unfile);
    }}
}}
</script>
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

        # Structured integration_sources (from scan_essays.py) renders as
        # a row of clickable chips. Falls back to integration_note text
        # for cron-generated cards that don't have structured sources.
        sources = result.get("integration_sources") or []
        sources_html = ""
        if sources:
            chip_items = []
            for s in sources:
                stype = s.get("type", "")
                num = s.get("number", "?")
                slug = (s.get("slug") or "").strip()
                title_attr = (s.get("title") or "").replace('"', "&quot;")
                label = f"Essay {num}" if stype == "essay" else f"Shade {num}"
                url_path = "essays" if stype == "essay" else "shades"
                if slug:
                    chip_items.append(
                        f'<a class="source-chip" '
                        f'href="https://shadesofsingularity.com/{url_path}/{slug}" '
                        f'target="_blank" rel="noopener" title="{title_attr}">{label}</a>'
                    )
                else:
                    chip_items.append(
                        f'<span class="source-chip" title="{title_attr}">{label}</span>'
                    )
            sources_html = (
                '<div class="card-sources">'
                '<span class="card-sources-label">Cited in</span>'
                + "".join(chip_items) +
                '</div>'
            )

        integration_html = ""
        if not sources and result.get("integration_note"):
            integration_html = f'<div class="card-integration">{result["integration_note"]}</div>'

        source_badge = item.get("source", "")
        citation_quality = result.get("citation_quality", "")
        if citation_quality:
            source_badge += f" | {citation_quality.replace('_', ' ')}"

        fp = result.get("fingerprint", "").replace('"', "&quot;")

        # The card carries `signal` directly when it's a filed card (came
        # from filed_blob); otherwise look up via the feedback shim.
        prior_signal = result.get("signal") or (ctx.get("feedback") or {}).get(
            result.get("fingerprint", "")
        )

        def _btn(target_signal: str, label: str) -> str:
            cls = "feedback-btn"
            if prior_signal == target_signal:
                cls += " active"
            return (
                f'<button class="{cls}" data-signal="{target_signal}" '
                f'onclick="sendFeedback(this, \'{fp}\', \'{target_signal}\')">{label}</button>'
            )

        # For filed cards (signal already set), add an Unfile action that
        # sends the card back to Pending.
        unfile_html = ""
        if prior_signal:
            unfile_html = (
                f'<button class="feedback-btn" data-signal="pending" '
                f'onclick="sendFeedback(this, \'{fp}\', \'pending\')" '
                f'title="Send back to Pending">↩ Pending</button>'
            )

        # Searchable haystack: title + source + claim id, lowercase.
        search_blob = " ".join(filter(None, [
            item.get("title", ""),
            item.get("source", ""),
            claim_id,
            claim_desc,
        ])).lower().replace('"', "&quot;")

        return f"""
<div class="card" data-fingerprint="{fp}" data-search="{search_blob}">
    <div class="card-header">
        <div class="card-title"><a href="{item.get('url', '#')}" target="_blank" rel="noopener">{item.get('title', 'Untitled')}</a></div>
        {tag_html}
    </div>
    <div class="card-meta">{authors} | {source_badge} | {item.get('date', '')[:10]}</div>
    {claim_html}
    <div class="card-summary">{result.get('summary', '')}</div>
    {integration_html}
    {sources_html}
    <div class="card-feedback">
        {_btn('integrated', 'Integrated')}
        {_btn('useful_later', 'Useful later')}
        {_btn('noise', 'Noise')}
        {unfile_html}
    </div>
</div>"""
