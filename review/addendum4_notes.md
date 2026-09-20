# Addendum 4 execution notes

**Date:** September 19, 2026
**Branch:** `edition-2026-09-corrections-2`
**Base:** `main` @ `1addde7`
**Status:** applied on branch, unpushed, undeployed. Awaiting Boris.

---

## Section 1 verification (baseline against live production)

Live fetched with `?v=20260919` cache-buster. Interpretation: a positive hit for a listed string would indicate Addendum 3 was NOT applied to that page. Results:

| Page | Search | Live hits | Interpretation |
|---|---|---|---|
| `/shades/autonomous-lethal-weapons/` | `whose April notes` | 0 | Addendum 3 Section 6.10 applied ✓ |
| `/short-essays/choices-that-remain/` | `Meta AI` | 0 | Addendum 3 Section 8.1 applied ✓ |
| `/short-essays/choices-that-remain/` | `The question is why` | 0 | Addendum 3 Section 8.3 applied ✓ |
| `/essays/end-of-work/` | `newyorkfed.org/` | **2** | **False positive.** Both hits are `https://www.newyorkfed.org/research/college-labor-market`, a URL with a path (from the verbatim Addendum 3 footnote 90), not a domain-root citation. Addendum 3 Section 3.2 IS applied (the "As of September 2026" section is deleted, the Korinek/labor/Pope paragraphs are inserted in Sections VII/II/IX, and Notes was renamed to Footnotes). |
| `/essays/end-of-work/` | `belong in the essay` | 0 | Addendum 3 Section 3 leak-clean ✓ |

**Archive check** (`/archive/2026-early/shades/`):
- 30 unique shade slugs referenced ✓
- Archive banner div present ✓

**Conclusion:** Addendum 3 was fully applied and is fully live. Addendum 5's Section 9 "still outstanding" list is out of date; the addendum was written before the September 18 push landed.

## Section 2 (Essay 6): applied

- **2.1** Restored the deleted sentence between the "operates within jurisdictions" line and the "Two live debates" paragraph, using the verbatim addendum text: `The populations outside those jurisdictions are not addressed by the material and epistemic foundations. This is a real limit, not a solved problem.` Paragraph break preserved.
- **2.2** No duplicate `## Footnotes` heading present in Essay 6 (pre-existing single heading at line 217). No deletion needed.
- **2.3** Duplicate-heading audit across every full essay:

| Essay | Before | After | Action |
|---|---|---|---|
| 01-end-of-work.md | `## Footnotes` × 1 | `## Footnotes` × 1 | no change |
| 02-economics-of-truth.md | `## Notes` × 1 | `## Footnotes` × 1 | **renamed** |
| 03-automation-of-power.md | `## Notes` × 1 | `## Footnotes` × 1 | **renamed** |
| 04-hollowing-of-the-human.md | neither heading, 35 `[^N]:` defs present as trailing block | unchanged | **flagged — no Footnotes heading exists** |
| 05-inheritance-we-choose.md | neither heading, 13 `[^N]:` defs present as trailing block | unchanged | **flagged — no Footnotes heading exists** |
| 06-choices-that-remain.md | `## Footnotes` × 1 | `## Footnotes` × 1 | no change |

Essays 4 and 5 have their footnote definitions present but no `## Footnotes` section heading. This is a pre-existing structural choice, not a corruption. Adding a heading would introduce a new visible section on the live page and is out of Addendum 4's stated scope; flagged for Boris's ruling.

## Section 3 (Shade #14): applied

All seven verbatim edits from Addendum 4:

- **3.1** Summary line replaced.
- **3.2** Swarm see-reference: "four times in 2026" → "at least five times in 2026 across three labs". **URL kept relative** (`/shades/the-swarm/`) rather than absolute (`https://shadesofsingularity.com/shades/the-swarm/`) to match the rest of the shade's citation style. The addendum's WITH quotation uses the absolute form; this is a formatting harmonisation, not a prose change.
- **3.3** Full paragraph replacement ("Two disclosed February 2026 cases at Anthropic add texture." paragraph rewritten).
- **3.4** Cotra/Hubinger sentences replaced.
- **3.5** Monitorability opening replaced (two sentences).
- **3.6** Monitorability closing paragraph replaced. The addendum permits "the April edition assumed" in this specific sentence and nowhere else.
- **3.7a** "genuine progress on detection" → "measurable progress on detection".
- **3.7b** "genuine methodological bet" → "methodological bet".

The Addendum 3 leak filter and Addendum 4 expanded filter both pass zero hits on Shade #14 after these edits.

## Section 4 (Shades index): applied

- **4.1** #21 summary line: `even at 25%` → `even at 35%`.
- **4.2** #2 front-matter dividend: `5` → `6` (the matrix already showed 6; the card was the outlier).

**Programmatic card-vs-matrix comparison across all shades:**

Before this pass, one mismatch:

```
#2 (02-concentration-of-ai-power.md): D card=5 matrix=6
```

After this pass, zero mismatches across all 32 shades on U / G / D fields.

## Section 5 (expanded leak filter): report only, per addendum instruction

New strings added: `Present the`, `worth naming`, `add texture`, `inside this shade`, `the shade's earlier`, `earlier prose`, `should be read against`, `per the incident described in`, `as instructed`, `this document`, `Boris`. The permitted-once phrase `the April edition assumed` was confirmed to appear only in Shade #14's 3.6 sentence.

Section 5 says "do not delete automatically. List the file, line, and sentence for the author to rule on." Below is the full inventory of matches outside the permitted-once sentence.

### 5.1 URGENT: instruction-leak already live in production

**`content/scenarios/02-concentration-of-ai-power.md:30`** contains the sentence `Boris to verify against a Reuters or Bloomberg confirmation before publication; if unverifiable, omit the specific acquisition detail while retaining the equity-and-compute concentration point.`

This is a leaked instruction from the Phase 4 shade-update script that was written into the shade prose and is currently visible on `shadesofsingularity.com/shades/concentration-of-ai-power/`. It should be removed on Boris's ruling. No automatic action taken per Section 5 rules.

### 5.2 Other expanded-filter matches (all authorial phrasing in the September update sections; no autofix)

Matches on `worth naming` (Addendum 3 had only `worth naming to round out`; the broader `worth naming` is new to Addendum 4 Section 5):

- `content/essays/01-end-of-work.md:144` — "the methodological gap is specific enough to be worth naming" (pre-existing April prose)
- `content/essays/02-economics-of-truth.md:226` — "the essay describes now has a fourth entry worth naming in the register of the other three" (September update)
- `content/essays/06-choices-that-remain.md:134` — "The limits of the developmental foundation are worth naming" (pre-existing April prose)
- `content/scenarios/14-alignment-failure.md:42` — "contains a specific cluster of admissions worth naming here" (September update)
- `content/scenarios/31-the-swarm.md:68` — "What remains unresolved is worth naming" (September addendum)

Matches on `the shade's earlier` / `the shade's earlier prose` / `earlier prose` (September update prose):

- Shade #5 (Information Collapse): line 28 — "different epistemic problem from the fabrication-verification asymmetry the shade's earlier prose describes"
- Shade #6 (Cognitive Atrophy Trap): line 36 — "giving the shade's earlier developmental-versus-substitutive distinction"
- Shade #8 (Governance Obsolescence): line 32 — "complicates the shade's earlier framing"
- Shade #9 (Meaning Crisis): line 34 — "The shade's earlier prose treated the meaning crisis"
- Shade #10 (Ecological Reckoning): line 34 — "than the shade's earlier prose anticipated"; line 38 — "The shade's governed outcome had been described in the earlier prose"
- Shade #11 (Foreign AI Subversion): line 30 — "material the shade's earlier prose called for"; line 32 — "the shade's earlier prose treated as one-directional"
- Shade #12 (Synthetic Persons Economy): line 36 — "The shade's earlier prose imagined synthetic persons"
- Shade #13 (Financial Chain Reaction): line 50 — "The shade's earlier prose stays intact for the labor-displacement channel"
- Shade #15 (Digital Authoritarianism): line 40 — "The shade's earlier prose about authoritarian governance patterns"; line 44 — "The shade's earlier prose about surveillance-state deployment"
- Shade #17 (Permanent Underclass): line 54 — "The shade's earlier prose called for exactly this kind of measurement"
- Shade #18 (Fragmentation of Reality): line 42 — "The shade's earlier prose treated fragmentation"; line 46 — "The shade's earlier prose about identity-based information bubbles"
- Shade #22 (The Singleton): line 36 — "the shade's earlier structural argument"
- Shade #23 (Bioweapons): line 32 — "the shade's earlier open-weight-proliferation concern"
- Shade #24 (Post-Scarcity): line 34 — "The shade's earlier prose treated post-scarcity as a possibility"
- Shade #28 (Human Extinction): line 28 — "the shade's earlier prose treated as open"

Matches on `per the incident described in`:

- Shade #32 (Autonomous Lethal Weapons): line 59 — "per the incident described in [The Swarm shade]" (September addendum)

Match on `add texture`, `inside this shade`, `should be read against`, `as instructed`, `this document`, `Present the`: none outside Shade #14 3.3's addressed-and-replaced paragraph (already gone).

**These are authorial phrasings, not instruction leaks.** The pattern "the shade's earlier prose" was my Phase 4 addendum boilerplate. Per Section 5's rule, no automatic edits. Boris to rule on how many, if any, of these should be reworded in a follow-up pass; a search-and-replace of "the shade's earlier prose" → "the shade" would leave the sentences grammatical in most cases.

## Section 6 (pre-existing style items, report only)

- Essay 6 Section II: `a genuinely democratic political community` and `where interests genuinely conflict` (April prose, not touched).
- Essay 6 Section VI: `The choice is not made by describing it. The choice is made by building` (staccato-pair reversal in the essay's original closing; the Postscript now points to this closing sentence and the pattern remains).
- Essay 1 Section VII: `The question is whether the people displaced` and Section XI: `The question is whether any of this will happen fast enough` (April prose, "The question is" pivot).
- Shade #26 index line: `The question is not whether we will create minds we cannot recognize. It is whether we already have.` (this line is on the shade card and includes a "not X. It is Y." reversal in the essay's original summary).

No edits made per Addendum 4 Section 6's report-only rule.

## Section 7 (essays 2-5 + short essays 2-5 audit, report only)

For each of Essays 2 through 5 and Short Essays 1 through 5 the addendum requested: (a) whether a September section exists; (b) whether it uses bold lead-in labels; (c) whether any citation links to a domain root; (d) full text of any expanded-filter matches. No edits.

| Essay | September section? | Bold lead-in labels? | Domain-root URLs? | Expanded-filter matches |
|---|---|---|---|---|
| Essay 2 | Yes (`## As of September 2026`, line 224) | None | None (Addendum 3 4.3 stripped 2) | "worth naming" at line 226 (September prose) |
| Essay 3 | Yes (`## As of September 2026`, line 210) | None | None (Addendum 3 4.3 stripped 2) | None |
| Essay 4 | Yes (`## As of September 2026`, line 203) | None | None | None |
| Essay 5 | Yes (`## As of September 2026`, line 106) | None | None (Addendum 3 4.3 stripped 1) | None |
| Short Essay 1 | No heading, one prose paragraph beginning "As of September 2026," (line 49) | None | None | None |
| Short Essay 2 | Same pattern (line 49) | None | None | None |
| Short Essay 3 | Same pattern | None | None | None |
| Short Essay 4 | Same pattern | None | None | None |
| Short Essay 5 | Same pattern | None | None | None |

Bold lead-in labels: none anywhere (the pattern was cleared in the Addendum 3 Section 4.2 pass and none has been introduced since).

Domain-root URLs: Addendum 3's Section 4.3 stripped all five of these across Essays 2, 3, and 5. Zero remaining domain-root citations in Essays 2-5.

## Section 9 (Shade #32 residuals): applied

- **9.1** Deleted the redundant Maven sentence at the end of the Section "The policy is following the practice" paragraph.
- **9.2** Removed the bare *The Times* paragraph; added `[^1]` marker at the end of the Kargu-2 paragraph (renumbered from `[^a]`); added `[^2]` marker at the end of "reported by *The Times* in April 2026."; added `## Footnotes` heading with the two definitions `[^1]:` (UN Panel + +972 Magazine) and `[^2]:` (The Times).

## Awkward joins created by Section 5 report-only policy

Addendum 4's expanded filter identified many "the shade's earlier prose" and "worth naming" instances across the September update paragraphs. Because Section 5 forbids automatic deletion, all remain in place. Boris to decide in a follow-up pass whether to rewrite each in place. If accepted broadly, the pattern:

- "the shade's earlier prose" → "the shade" or "the shade above" (depending on sentence context)
- "worth naming" (standalone) → keep as authorial, or reword to "the note here is" or omit
- The essay-body "worth naming" in Essay 1 Section VII and Essay 6 Section IV is pre-existing April prose.

## Next actions for Boris

1. Read the unified diff on this branch. `git diff main..HEAD` gives it.
2. Rule on Section 5.1 (the "Boris to verify" instruction leak in Shade #2 that is currently live in production).
3. Rule on Section 5.2 (the "the shade's earlier prose" and "worth naming" pattern across the September update sections).
4. Rule on the essays 4/5 no-Footnotes-heading question (Section 2.3).
5. Merge and deploy when satisfied, or ask me to run Addendum 5 (Pain Axis) on top of this branch first — the ordering rule in Addendum 5 says "run after Addendum 4 is live," and Addendum 4 will be live once this branch is deployed.
