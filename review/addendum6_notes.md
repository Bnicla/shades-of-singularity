# Addendum 6 execution notes

**Date:** September 20, 2026
**Branch:** `main`
**Base:** `e7139ea`

## What was applied

- **Section 1** Short Essay V September paragraph replaced verbatim.
- **Section 2** Short Essay I September paragraph replaced verbatim.
- **Section 3.1** Short Essay II September paragraph deleted.
- **Section 3.2** Short Essay II new fourth-asymmetry paragraph inserted verbatim between the "Each cycle degrades..." paragraph and "There are counterweights."
- **Section 4** Short Essay III September paragraph replaced verbatim.
- **Section 5** Short Essay IV: no change.
- **`author's own` scrub** across `content/`: two occurrences found. One was inside the Short Essay V paragraph that Section 1 replaced (removed by the replacement itself). The other was in Essay 4 line 136: "at the level of institutional policy at the author's own university." Removed the trailing "at the author's own university," clause per Addendum 6 Section 1's Reason ("delete it everywhere it may appear on the site"). Sentence now reads "The committee's finding lines up with the essay's central distinction, at the level of institutional policy."

## Verification

- `grep "author's own" content/` → 0 hits ✓
- Every short essay contains exactly one September paragraph ✓
- Section 0 leak grep + Addendum 4 expanded filter on all five changed files → 0 hits ✓
- Em-dashes on all five changed files → 0 ✓
- `npm run build` → 51 pages, no errors ✓

## Next

Deploy + purge CDN for the four short-essay routes + `/essays/hollowing-of-the-human/`.
