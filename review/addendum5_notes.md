# Addendum 5 execution notes

**Date:** September 19, 2026
**Branch:** `edition-2026-09-corrections-2`
**Base:** Addendum 4 commit `65011b4`
**Status:** applied on branch, ready to deploy.

---

## Addendum 5 (Pain Axis) applied

- **Essay 6 Section 1.1**: Section II model-welfare aside replaced verbatim.
- **Essay 6 Section 1.2**: paragraph verbatim inserted in Section III.3, immediately after the paragraph ending "...extends beyond the academic community.[^15]" and before "The standard public-choice objection".
- **Essay 6 Section 1.3**: footnotes 27 and 28 appended verbatim after footnote 26.
- **Shade #26 AI Consciousness Section 2**: three paragraphs appended verbatim to the existing `## September 2026` section.
- **Shade #14 Alignment Failure Section 3**: paragraph verbatim inserted after the Cotra/Hubinger paragraph (Addendum 4 3.4 text) and before the `### Monitorability collapse` heading.
- **Shade #31 The Swarm Section 4**: paragraph verbatim inserted in "Why it happens", after "no lab has demonstrated it can detect the behavior forming in real time." and before "One limit on everything above should be stated." (the Addendum 3 5.6 paragraph).

Citation-marker harmonisation applied to footnotes 27, 28 (`[27](#user-content-fn-27)` → `[^27]`, `> N. text` → `[^N]: text`) so the site's markdown-it footnote system renders the citations correctly. Same rule Addendum 3 and 4 have already established.

Cross-links in Sections 2 and 3 kept relative (`/shades/ai-consciousness/`, `/essays/choices-that-remain/`) to match the site's own citation convention. Addendum 5 uses absolute Shadesofsingularity URLs in its FROM/WITH quotations.

## Also fixed on this branch (from mid-turn instruction from Boris)

- **Boris-leak fix in Shade #2** (Concentration of AI Power): deleted the sentence "Boris to verify against a Reuters or Bloomberg confirmation before publication; if unverifiable, omit the specific acquisition detail while retaining the equity-and-compute concentration point." that was leaked into shade prose from the Phase 4 update script and had been live in production.
- **Essay 4 and Essay 5 structural consistency**: restored the standard [body] → [September section] → [Footnotes heading] → [footnote defs] order that Essays 2, 3, and 6 already use. Previously Essays 4 and 5 had [body] → [footnote defs] → [September section] with no `## Footnotes` heading at all. September prose was moved verbatim; only the position changed. `## Footnotes` heading added before each essay's first footnote definition.

## Explanation of the "shade's earlier prose" boilerplate

Addendum 4 Section 5's expanded leak filter flagged 15+ occurrences of the phrase "the shade's earlier prose" across the shade September addendum paragraphs I wrote in Phase 4. Boris asked me to explain what "boilerplate" meant here.

The phrase was a stylistic tic in the Phase 4 addendum-writing script: a repeating template I used to refer to the pre-September text of the same shade. Examples across the corpus:

- Shade #5 (Information Collapse): "a specifically different epistemic problem from the fabrication-verification asymmetry the shade's earlier prose describes"
- Shade #9 (Meaning Crisis): "The shade's earlier prose treated the meaning crisis primarily as a consequence of..."
- Shade #10 (Ecological Reckoning): "than the shade's earlier prose anticipated" and "the shade's earlier sense"
- Shade #11 (Foreign AI Subversion): "material the shade's earlier prose called for" and "the shade's earlier prose treated as one-directional"
- Shade #12 (Synthetic Persons Economy): "The shade's earlier prose imagined synthetic persons in human markets"
- Shade #13, #15, #17, #18, #22, #23, #24, #28: similar constructions.

It is not an instruction leak. It is a repeating authorial phrasing that reads as awkwardly meta on close inspection ("the shade's earlier prose called for X" is essentially the author saying "my own earlier writing on this topic called for X"). Addendum 4's Section 5 flagged the pattern and left the rewrite decision to Boris. The Section 5 notes in `addendum4_notes.md` list every instance if he wants to rewrite.

If Boris rules that these should be reworded, a bulk pass could convert:
- "the shade's earlier prose" → "the shade" or "the shade above"
- "the shade's earlier framing" → "the shade's framing"
- "the shade's earlier sense" → "that sense"

with case-by-case grammar checks. Say the word and I run it.

## Style verification on the four Addendum 5 files

- Em-dashes: 0 across all four files.
- Full leak filter (Addendum 3 + Addendum 4 expanded): 0 real matches. One false positive in Shade #26 line 34 where the substring "as instructed" is caught inside the pre-existing prose "has instructed the model on how to reason about them" (the addendum filter is a substring match, not a whole-word match; this is not a real instruction leak).

## Two other consistency items flagged for Boris's ruling

1. **Essay 6 uses `## Postscript, September 2026`; Essays 2-5 use `## As of September 2026`.** Both are variants of the same "September update" section. The Essay 6 heading is verbatim from Addendum 3 Section 2.3, so rewriting it now would violate the verbatim rule that has been in force. Ruling: leave as-is? Or standardise on one label across all essays in a separate pass?
2. **Essay 6's Postscript uses different section numbering** ("Section V", "Section III.3") in its verbatim addendum-provided prose, while other essays use Roman numerals ("Section V", "Section IX") as headers. This is consistent inside Essay 6 but not across essays.

## Build and deploy

`npm run build` passes: 51 pages, no errors. Ready to deploy.
