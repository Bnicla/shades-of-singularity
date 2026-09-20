# Addendum 3 execution notes

**Date:** September 18, 2026
**Branch:** `edition-2026-09-corrections`
**Base:** `edition-2026-09` @ `e6c10bf`
**Status:** applied on branch, unpushed, unmerged, undeployed. Awaiting Boris's review of the diff per Section 0 rule 6.

---

## Files changed on this branch

11 files. Every changed file passes the Section 0 grep (leak strings, em-dashes, `. It is `, `The question is`) with zero hits.

```
content/appendix.md                                  (Section 1.3)
content/essays/01-end-of-work.md                     (Section 3)
content/essays/02-economics-of-truth.md              (Section 4)
content/essays/03-automation-of-power.md             (Section 4)
content/essays/04-hollowing-of-the-human.md          (Section 4)
content/essays/05-inheritance-we-choose.md           (Section 4)
content/essays/06-choices-that-remain.md             (Section 2 + one leak sentence deletion)
content/scenarios/31-the-swarm.md                    (Section 5)
content/scenarios/32-autonomous-lethal-weapons.md    (Section 6)
content/short-essays/06-choices-that-remain.md       (Section 8.1-8.4)
src/pages/changelog.astro                            (Section 1.4)
```

`git diff main..HEAD` and `git diff` on this branch produce the unified diffs Boris will read before any merge.

## Section 0 grep, output on every changed file

Zero hits across all four checks (leak strings, `—`, `. It is `, `The question is`). Empty output equals pass; this was the final gate before writing this report.

## Section 1.1 cache-purge confirmation

Live fetches at execution time returned the September 2026 edition, with `September 2026 edition`, `Early 2026 edition`, and `Changelog` all present in the footer of both `/shades/` and `/essays/`. No CDN purge was required beyond the production redeploy earlier in the day. The addendum's 1.1 assertion that `/shades/` and `/essays/` were serving the pre-edition version on September 18 was true at the time the addendum was written and is no longer true after the production promotion.

## Section 1.2 archive integrity

- `/archive/2026-early/shades/` referenced 30 unique shade slugs, with the archive banner rendered on the page.
- Three archived essays checked (end-of-work, choices-that-remain, economics-of-truth): each has the archive banner and each carries a link to its live equivalent under `/essays/<slug>/`.
- No content under `/archive/2026-early/` was edited on this branch.

## Section 7 findings on Shade #14

Dump at `review/shade_14_current.md`. Findings:

- (a) Summary line: **NOT revised**. Still reads `Every major AI lab acknowledges this is unsolved.` The requirements confirmed a summary correction for #23 but did not confirm one for #14. If the summary should be revised to reflect the September developments, that is a Boris decision.
- (b) Monitorability-collapse section: **YES**. Present under the `### Monitorability collapse` subheading in the September 2026 update section.
- (c) Swarm cross-reference: **YES**. Two references to The Swarm and to `/shades/the-swarm/` in the file.
- (d) Likelihood: **~65%** in front matter, as required.

No edits were made to Shade #14 on this branch.

## Section 4.5 dump

`review/essays_2_to_5_september_sections.md` contains, for each of Essays 2 through 5, the September section after the 4.1-4.4 cleanup, plus every remaining inline URL listed beneath the section for the reviewer's convenience. Integration into the essay body is Section 9 item 6.

## Awkward joins created by strict verbatim application

Rule 1 forbade adding transitional sentences to smooth the joins left by deletions. The following places will read awkwardly on inspection and are flagged for Boris's second-pass review, per rule 1's own instruction to log them here:

1. **Essay 3, September section opener.** Section 4 removed the sentence "That dispute has since been overtaken by two developments the essay's earlier prose did not anticipate." What remains is the standalone sentence "The essay's opening centered on the Anthropic-Pentagon dispute." at the start of the section, followed directly by the Zaporizhzhia paragraph. The transition is abrupt.
2. **Essay 4, Section II creativity paragraph.** Section 4 removed the closing clause "and the essay should be read with that limitation in mind." The paragraph now ends "the empirical work has not caught up." The reader loses the softening.
3. **Essay 4, counterargument paragraph.** Section 4 removed the opener "The counterargument has force, and the essay should not pretend otherwise." The paragraph now begins with "A critic will note, correctly, that all cognition is scaffolded..." The concessive move that the deleted sentence performed is now implicit rather than stated.
4. **Essay 4, September closing paragraph.** Section 4 removed "Two shorter additions belong in the essay." The paragraph now begins with "Mustafa Suleyman's Microsoft 'Humanist AI Code of Conduct'..." with no lead-in.
5. **Essay 5, September MIT paragraph.** Section 4 removed the entire second sentence about civilizational reproduction. The paragraph now ends after the description of MIT's institutional response. The connection to the essay's own argument that the deleted sentence made is no longer stated.
6. **Essay 5, September collective-judgment paragraph.** Section 4 removed the meta-commentary sentences "The essay's earlier prose treated the public's collective-judgment capacity as an open question." and "It belongs in the essay because it is a specific data point in a domain where such data points are rare." The remaining prose is coherent but loses its explicit hinge.
7. **Essay 6, Section II jurisdictional-limit paragraph.** Section 0 rule 5 required deletion of the sentence "The populations outside those jurisdictions are not addressed by the material and epistemic foundations, and the essay should be honest that this is a real limit, not a solved problem." The paragraph now ends at "The architecture this essay describes operates within jurisdictions that can afford to build it." The reader loses the explicit acknowledgment that this is a real limit.
8. **Shade #32, Section 6.7.** The replacement sentence and the trailing pre-existing sentence ("The Maven case is not autonomous target selection in the technical sense, but the practical distinction between an AI that recommends and a human who authorizes without capacity to verify has been eroding since 2024 in the operational reporting.") now repeat each other. The addendum's REPLACE target did not include the trailing sentence, so it was left in place. A follow-up pass could consolidate the two.
9. **Shade #32, footnote placement.** The addendum's 6.2 references footnote `[^a]`, and 6.5 appends an inline `*The Times*` citation. Both were placed at the end of the shade file as a citations block because the shade's earlier citations are inline links inside paragraphs. This differs from the addendum's expectation of "add footnote a at the end of the shade's citations," and a reviewer may prefer a different placement.

## Editorial choices made under rule 1's constraints

- **Citation format harmonisation.** The addendum's postscript (Section 2.3), Essay 1 insertions (Section 3.3-3.5), and appended footnotes (Sections 2.4 and 3.6) use GitHub-style anchor references (`[N](#user-content-fn-N)` inline and `> N. ...` for footnote text). The essays use markdown-it convention (`[^N]` inline and `[^N]: ...` for the definition), which is what Astro's build pipeline renders as functioning footnotes. The prose was copied verbatim, and only the citation markup was converted so the citations render as clickable footnotes in the site build. If Boris prefers to keep the addendum's markup exactly, the site can be reconfigured to render GitHub-style anchors instead, but the change would affect every essay's existing footnote system.
- **`## Notes` vs `## Footnotes`.** Section 3.1.3 said to delete `## Notes` so `## Footnotes` appears once. Essay 1 had one `## Notes` heading and no `## Footnotes`; interpreting the stated intent, the heading was renamed from `## Notes` to `## Footnotes` so Essay 1 matches Essay 6's convention. The addendum's stated goal ("`## Footnotes` appears once") is satisfied.
- **Essay 6 duplicate `## Footnotes`.** Section 2.1.3 called for deleting a duplicate `## Footnotes` heading. The pre-cleanup Essay 6 had only one such heading, so no deletion was performed. Flagged for confirmation.

## Section 9 deferred items (report only)

These require Boris's judgment and were not executed on this branch. Section targets included per the addendum for continuity.

1. **Essay 6, Section III.3:** move the Astra evidence (currently in the postscript) into the body as the instance the section argues from precedent for. Decision: leave in postscript or integrate.
2. **Essay 6, Section III.3:** compare embedded supervision (Amodei, bank-examiner model, antitrust waiver) with regulatory markets (Hadfield-Clark). The postscript flags this as open. A full treatment is a new subsection.
3. **Essay 6, Sections III.3 and IV:** interpretability and monitorability as a precondition for the approval regime. No section currently owns this.
4. **Essay 6, Section IV chokepoint refresh:** H20 and H200 export reversals; Nvidia's Hugging Face acquisition if confirmed; DeepSeek V4.1-Flash under MIT license (September 14); Epoch's finding that Chinese labs trail by months; the CISA distillation advisory. The three-to-seven-year window estimate should be re-examined.
5. **Essays 1 and 6:** both run the Athens-with-slavery analogy at length. One should yield.
6. **Essays 2 through 5:** integration of the September sections into essay bodies, after the review of `review/essays_2_to_5_september_sections.md`.
7. **Shade #31, Shade #14, Essay 6:** the Hugging Face facts appear in three places at similar length. Essay 6's postscript is already shortened and points to the Swarm shade; Shade #14 should point to the Swarm shade rather than repeat.
8. **Shade #32:** the 85 percent likelihood should be re-read against 6.2 and 6.12. With Kargu-2 and Lavender in the record, "documented practice" was true before 2026; the shade's tier is defensible, but the "arrived in summer 2026" framing is not.

## What was verified but not modified

- Shade #14 (Section 7): dump only.
- The 4.5 September-section dumps (Section 4.5): captured verbatim after the 4.1-4.4 cleanup, no further editing.
- The `blueprint` placeholder page's `## Notes` label and its own "six essays" language: not in the addendum's scope.

## Next actions for Boris

1. Read the unified diff on this branch. `git diff main..HEAD` gives it; the changelog entries above list the section each change came from.
2. Decide the Section 9 items.
3. Decide whether to accept the citation-format harmonisation, or whether to reconfigure the site to render GitHub-style anchors.
4. Merge `edition-2026-09-corrections` into `main` and deploy, or push the branch for a Vercel preview URL before deploying.
