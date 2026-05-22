#!/bin/bash
# Regenerate shareable/ files from current source content.
# These files are shareable snapshots for pasting into Claude conversations.
# Run from project root: ./scripts/regenerate-shareable.sh

set -e
cd "$(dirname "$0")/.."

DATE=$(date +%Y-%m-%d)

# 01: Site overview (homepage + about)
{
  echo "# Shades of Singularity — Site Overview"
  echo "# Generated: $DATE"
  echo "# Site: https://shadesofsingularity.com"
  echo ""
  echo "---"
  echo ""
  echo "# HOMEPAGE"
  echo ""
  cat content/home.md
  echo ""
  echo "---"
  echo ""
  echo "# ABOUT PAGE"
  echo ""
  cat content/about.md
} > shareable/01_site_overview.md

# 02: All essays (full)
{
  echo "# ALL ESSAYS"
  echo ""
  for f in content/essays/*.md; do
    base=$(basename "$f")
    echo "---"
    echo ""
    echo "## $base"
    echo ""
    cat "$f"
    echo ""
  done
} > shareable/02_all_essays.md

# 03: All shades
{
  echo "# ALL SHADES"
  echo ""
  for f in content/scenarios/*.md; do
    base=$(basename "$f")
    echo "---"
    echo ""
    echo "## $base"
    echo ""
    cat "$f"
    echo ""
  done
} > shareable/03_all_shades.md

# 05: Appendix (outcome matrix)
{
  echo "# APPENDIX (OUTCOME MATRIX)"
  echo ""
  cat content/appendix.md
} > shareable/05_appendix.md

# 06: All short essays
{
  echo "# ALL SHORT ESSAYS"
  echo ""
  for f in content/short-essays/*.md; do
    base=$(basename "$f")
    echo "---"
    echo ""
    echo "## $base"
    echo ""
    cat "$f"
    echo ""
  done
} > shareable/06_all_short_essays.md

echo "Regenerated shareable/ files:"
ls -la shareable/
