#!/usr/bin/env python3
"""
Archive the current production site into public/archive/2026-early/.

Run AFTER `npm run build` so dist/ is fresh.

Per Phase 1 of claude_code_requirements_sept_2026_edition.md:
 - Mirror home, /about/, /essays/ + real essays, /shades/ + all shades,
   /short-essays/ + real short essays.
 - Rewrite internal page links to stay inside the archive.
 - Snapshot CSS into the archive so future style changes don't break it.
 - Add a slim banner at the top of every archived page with a link to
   the live equivalent.
 - Add `<meta name="robots" content="noindex, follow">` so the archive
   does not compete with live pages in search.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
OUT = ROOT / "public" / "archive" / "2026-early"
ARCHIVE_PREFIX = "/archive/2026-early"
BRANCH_CUT_DATE = "September 17, 2026"

# Real content pages: only these get archived. Legacy redirect stubs
# (essays/inheritance-we-leave, essays/risks-we-cannot-reverse, and the
# same two under short-essays/) are skipped because they would embed a
# meta-refresh to the live URL, which defeats the archive.
REAL_ESSAY_SLUGS = {
    "end-of-work",
    "economics-of-truth",
    "automation-of-power",
    "hollowing-of-the-human",
    "inheritance-we-choose",
    "choices-that-remain",
}
REAL_SHORT_SLUGS = REAL_ESSAY_SLUGS  # same six titles

# Page-path prefixes that should be rewritten to live INSIDE the archive.
# The order matters for the regex: longer prefixes first.
INTERNAL_PAGE_PATHS = [
    "/about/",
    "/essays/",
    "/shades/",
    "/short-essays/",
]

# CSS paths that must be snapshotted (so a future rebuild's hashed name
# doesn't 404 the archive).
CSS_SNAPSHOT_PATHS = ["/print.css"]  # plus any /_astro/*.css found in dist

BANNER_STYLE_BLOCK = """<style>
.archive-banner {
    background: #f5efe1;
    color: #4a4232;
    padding: 0.75rem 1.5rem;
    text-align: center;
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.875rem;
    line-height: 1.5;
    border-bottom: 1px solid #e0d5b8;
}
.archive-banner a { color: #B8860B; text-decoration: underline; }
html[data-theme="dark"] .archive-banner {
    background: #2a2620;
    color: #d4c9b0;
    border-bottom-color: #4a4232;
}
html[data-theme="dark"] .archive-banner a { color: #d4a44a; }
</style>"""

BANNER_TEMPLATE = (
    '<div class="archive-banner">'
    "This is the Early 2026 edition of Shades of Singularity, frozen on "
    f"{BRANCH_CUT_DATE}. It reflects the state of the argument before the "
    'events of summer 2026. <a href="{live_url}">Read the current edition →</a>'
    "</div>"
)

NOINDEX_META = '<meta name="robots" content="noindex, follow">'


def targets() -> list[tuple[Path, Path, str]]:
    """
    Yield (source dist path, output archive path, live equivalent URL) for
    every page that should be archived.
    """
    plan: list[tuple[Path, Path, str]] = []

    def add(rel: str) -> None:
        src = DIST / rel / "index.html" if rel else DIST / "index.html"
        out = OUT / rel / "index.html" if rel else OUT / "index.html"
        live_url = f"/{rel}/" if rel else "/"
        plan.append((src, out, live_url))

    add("")            # home
    add("about")
    add("essays")
    for slug in REAL_ESSAY_SLUGS:
        add(f"essays/{slug}")
    add("shades")
    for slug in sorted(p.name for p in (DIST / "shades").iterdir() if p.is_dir()):
        add(f"shades/{slug}")
    add("short-essays")
    for slug in REAL_SHORT_SLUGS:
        add(f"short-essays/{slug}")

    return plan


def rewrite_html(html: str, live_url: str, css_map: dict[str, str]) -> str:
    """Apply all archive transformations to one page's HTML."""

    # 1. Rewrite internal page links: href="/", href="/about/", href="/essays/*"
    #    etc. Only touch hrefs whose path starts with one of the known page
    #    prefixes or is exactly "/". Leave assets (favicon, images) alone.
    def replace_page_href(match: re.Match) -> str:
        quote = match.group(1)
        url = match.group(2)
        # exactly "/" (home)
        if url == "/":
            return f'href={quote}{ARCHIVE_PREFIX}/{quote}'
        for prefix in INTERNAL_PAGE_PATHS:
            if url == prefix or url.startswith(prefix):
                return f'href={quote}{ARCHIVE_PREFIX}{url}{quote}'
        return match.group(0)

    html = re.sub(
        r'href=(["\'])(/[^"\']*)\1',
        replace_page_href,
        html,
    )

    # 2. Rewrite CSS references to the snapshotted archive copies.
    for original_path, archive_path in css_map.items():
        html = html.replace(f'href="{original_path}"', f'href="{archive_path}"')
        html = html.replace(f"href='{original_path}'", f"href='{archive_path}'")

    # 3. Insert noindex meta + banner style block just before </head>.
    injection = NOINDEX_META + "\n" + BANNER_STYLE_BLOCK + "\n"
    html = re.sub(r"</head>", injection + "</head>", html, count=1)

    # 4. Insert banner div immediately after opening <body ...> tag.
    banner = BANNER_TEMPLATE.format(live_url=live_url)
    html = re.sub(r"(<body[^>]*>)", r"\1" + banner, html, count=1)

    return html


def snapshot_css() -> dict[str, str]:
    """
    Copy CSS files from dist/ into the archive. Return a map from the
    original path (as it appears in HTML) to the archive path (as it
    should appear after rewrite).
    """
    css_map: dict[str, str] = {}

    for path in CSS_SNAPSHOT_PATHS:
        src = DIST / path.lstrip("/")
        dst = OUT / path.lstrip("/")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        css_map[path] = f"{ARCHIVE_PREFIX}{path}"

    astro_dir = DIST / "_astro"
    if astro_dir.exists():
        (OUT / "_astro").mkdir(parents=True, exist_ok=True)
        for css_file in astro_dir.glob("*.css"):
            dst = OUT / "_astro" / css_file.name
            shutil.copy2(css_file, dst)
            original = f"/_astro/{css_file.name}"
            css_map[original] = f"{ARCHIVE_PREFIX}{original}"

    return css_map


def main() -> int:
    if not DIST.exists():
        print("dist/ missing. Run `npm run build` first.", file=sys.stderr)
        return 1

    if OUT.exists():
        print(f"Clearing existing archive at {OUT}")
        shutil.rmtree(OUT)

    OUT.mkdir(parents=True)

    css_map = snapshot_css()
    print(f"Snapshotted {len(css_map)} CSS file(s):")
    for k, v in css_map.items():
        print(f"  {k}  →  {v}")

    plan = targets()
    print(f"\nArchiving {len(plan)} pages...")

    for src, dst, live_url in plan:
        if not src.exists():
            print(f"  MISSING (skipped): {src.relative_to(ROOT)}")
            continue
        html = src.read_text(encoding="utf-8")
        rewritten = rewrite_html(html, live_url, css_map)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(rewritten, encoding="utf-8")
        print(f"  {src.relative_to(DIST)}  →  {dst.relative_to(ROOT)}")

    print("\nArchive complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
