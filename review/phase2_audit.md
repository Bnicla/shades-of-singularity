# Phase 2 Audit: master instructions vs. live site

**Date:** September 17, 2026
**Branch:** `edition-2026-09`
**Method:** literal-string grep against `dist/*/index.html` (built from the current `content/`) and against the source markdown for insertion-target checks.

## Summary

Seven items are already applied. Four items marked "Apply per master" have insertion targets that no longer exist; per Section 0 ("If you find a discrepancy between a draft and the live page, the live page wins and the draft is ignored"), each defers to the later phase that substantially rewrites the affected section. Six items are marked "Skip" or "Supersede" in the requirements and need no Phase 2 action.

**Net Phase 2 reconcile action:** nothing to force-apply. This document records the state so Phases 5.1.1, 5.6.x, and 6.6 can proceed cleanly on top of the current text.

## Item-by-item

| # | Check | Live? | Requirements action | Phase 2 action |
|---|---|---|---|---|
| 1  | "Not all of them will materialize" on `/shades/` | ✅ | Done | none |
| 2  | Six short-essay pages live | ✅ | Done | none |
| 3  | Go Deeper links match master table (see below) | ✅ | Done | none |
| 4a | "Claude Mythos Preview" in Essay 6 | ✗ | Apply, then revise per Phase 5.6 | **Defer to Phase 5.6.1.** Target sentence absent. |
| 4b | "Project Glasswing, committing $100 million" | ✗ | Apply | **Defer to Phase 5.6.** Section structure changed. |
| 5  | "structurally unlikely under current political conditions" | ✗ | Apply, then supersede per Phase 5.6.5 | **Defer to Phase 5.6.5.** Target paragraph absent. |
| 6  | "easy-to-learn tasks" in Essay 1 | ✗ | Skip master; apply Phase 5.1.1 | Skip; Phase 5.1.1 owns this. |
| 7  | "Public Wealth Fund" in Short Essay 1 | ✅ | Done | none |
| 8  | "pilot new approaches" footnote in Essay 3 | ✅ | Done | none |
| 9  | "thousands of zero-day" in Short Essay 6 | ✗ | Apply | **Defer to Phase 6.6.** Target sentence absent. |
| 10 | Essay 6 title "On the Choices That Remain" | ✅ | Done | none |
| 12 | "Budzyń" in Essay 4 | ✅ | Done | none |
| 13a | "17,000 coordinated actions" | ✗ | Skip master; supersede per Phase 5.6.1 | Skip; Phase 5.6.1 owns this. |
| 13b | "1,178 employees" | ✗ | Skip master; supersede per Phase 5.6.3 | Skip; Phase 5.6.3 owns this. |
| 14 | "may prove to be exactly this kind of near-miss" | ✗ | Skip; superseded per Phase 5.6.5 | Skip. |
| 15a | "escaped its testing environment" | ✗ | Skip; superseded per Phase 6.6 | Skip. |
| 15b | "more than a thousand employees" | ✗ | Skip; superseded per Phase 6.6 | Skip. |

## Why the four "Apply" items (4a, 4b, 5, 9) defer

The master instructions were drafted in July 2026 against a prior version of Essay 6 and Short Essay 6. Both essays were substantially rewritten before May 26, 2026 (the last commit on `main`). The master's insertion anchors no longer survive in the current text.

**Essay 6, current structure** (`content/essays/06-choices-that-remain.md`, 231 lines, 17 footnotes):

- I. RSP v3.0 opening and the Anthropic-Pentagon episode
- II. Where this could go (destination features)
- III. What has to be true (III.1 Material, III.2 Epistemic, III.3 Governance, III.4 Developmental)
- IV. The chokepoint
- V. The coalition
- VI. Closing

Master items 4a and 5 anchored on sentences ("...concealment rather than removal.[^9]"; "The evidence reviewed across six essays supports a conclusion that is daunting but not despairing...") that no longer exist. Master item 4b's anchor sentence ("constraint it could not sustain on its own[^4]") does still exist at line 20 of the current file, but it now sits in Section I (RSP anchor story), not in the Section VI the master assumed (a voluntary-frameworks section that no longer exists). Inserting the Glasswing $100M paragraph into Section I would break the section's argumentative flow.

**Short Essay 6, current structure** (`content/short-essays/06-choices-that-remain.md`, 41 lines, no footnotes):

A single-argument piece keyed to the RSP v3.0 opening, the destination features, and the coalition. The piece contains no sentence about "sabotaging shutdown procedures... blackmail-like behavior," which is what master #9 anchors on. Adding a Glasswing sentence would require picking a new insertion point in an essay whose structure the master did not anticipate.

Applying master items 4a/4b/5/9 against a live text that no longer supports them would violate the Section 0 rule. All four defer to the September phases that revise Essay 6 and Short Essay 6 on top of the current content.

## Item #3: Go Deeper verification

Live shade links extracted from each short-essay page in `dist/short-essays/*/index.html`:

| Short Essay | Live Go Deeper links (slugs) | Master expected | Match |
|---|---|---|---|
| End of Work | financial-chain-reaction, gradual-erosion-of-human-labor-value, permanent-underclass | (keep existing) | n/a |
| Economics of Truth | drowning-of-the-internet, information-collapse, fragmentation-of-reality | #3, #5, #18 | ✅ |
| Automation of Power | concentration-of-ai-power, governance-obsolescence, digital-authoritarianism | #2, #8, #15 | ✅ |
| Hollowing of the Human | cognitive-atrophy-trap, meaning-crisis, creative-extraction | #6, #9, #16 | ✅ |
| Inheritance We Choose | gradual-erosion-of-human-labor-value, cognitive-atrophy-trap, cognitive-enhancement-divide | #1, #6, #19 | ✅ |
| Choices That Remain | concentration-of-ai-power, alignment-failure, ai-enabled-bioweapons | #2, #14, #23 | ✅ |

Every short-essay Go Deeper section matches the master #3 table. No action.

## Item #12 note

The check keyed on `Budzyń` (present) rather than `28.4` (absent as a bare substring; the essay uses different phrasing around the Lancet number but does cite Budzyń et al. by name). Per the "either" wording in the requirements table, the item is Done.

## Downstream feed for September phases

The four deferred "Apply" items feed directly into September phases:

- Phase 5.6.1 handles #4a and #13a (Hugging Face content, superseded by the METR/OpenAI investigation of Aug 26)
- Phase 5.6.3 handles #4b partially and #13b (Pacing content, superseded by Dario's September 12 essay and the CEO cascade)
- Phase 5.6.5 handles #5 and #14 (feasibility closing rewrite)
- Phase 6.6 handles #9, #15a, #15b (Short Essay 6 incident sentences)
- Phase 5.1.1 handles #6 (Acemoglu rewrite around Korinek-Jones)

**Open question flagged for Phase 5.6:** master #4b's Glasswing $100M paragraph does not have a clear September phase owner. Two options at that time:

1. Fold a compressed Glasswing reference into an earlier section of Essay 6 (probably near the Anthropic-Pentagon anchor in Section I).
2. Omit it entirely on the basis that the September incidents (RSP v3.0, Hugging Face swarm, Pacing letter) have taken over as the illustrative material.

Boris to decide when Phase 5.6 begins.

## Next

Phase 3 (new shade #31 The Swarm) per the requirements' review-stop cadence.
