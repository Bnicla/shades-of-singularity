# Addendum 4: Audit of the Addendum 3 Pass and Remaining Corrections

**Date:** September 19, 2026
**Applies to:** the live site after the Addendum 3 pass. Section 0 of Addendum 3 (hard rules) remains in force for every edit here. Read that section again before starting.
**Subject:** What was verified as applied, what could not be verified, one sentence the Addendum 3 leak filter wrongly deleted, and new problems found in Shade #14 and on the shades index.

---

## 0. VERIFIED APPLIED (no action)

- Essay 6: postscript, footnotes 18–26, feature mapping (2.1.1), testimony sentence (2.1.2).
- Shades index and matrix: 32 shades, all seven score revisions, closing paragraph (1.3), stable-identifier note.
- The Swarm (#31): all of Section 5.
- Changelog: Section 1.4.
- Alignment Failure (#14): September section, Swarm cross-reference, monitorability subsection, likelihood 65.

## 1. VERIFY BEFORE ANYTHING ELSE: three pages that may be stale or unedited

On September 19 the following pages served content identical to their September 18 state. Fetch each from an external network with a cache-busting query string (for example `?v=20260919`) and search for the string given. If the string is present, the section was not applied; run it now.

| Page | Search for | If found, run |
|---|---|---|
| `/shades/autonomous-lethal-weapons/` | `3000.09` and `whose April notes` | Addendum 3, Section 6, all items 6.1–6.13 |
| `/short-essays/choices-that-remain/` | `Meta AI` and `The question is why` | Addendum 3, Section 8, items 8.1–8.4 |
| `/essays/end-of-work/` | `newyorkfed.org/` and `belong in the essay` | Addendum 3, Section 3, all items 3.1–3.6 |

After running any of these, purge the CDN for that route and re-fetch to confirm. Log the before-and-after in `/review/addendum4_notes.md`.

Also confirm at the same time that `/archive/2026-early/shades/` shows 30 shades with April scores and the archive banner (Addendum 3, item 1.2), which was not checked.

---

## 2. ESSAY 6: restore a deleted sentence and finish one item

**2.1** The Addendum 3 leak filter matched the phrase `the essay should` inside a sentence of the author's original May text and deleted it, taking the following paragraph break with it. In Section II, the text now reads:

> The architecture this essay describes operates within jurisdictions that can afford to build it.
> Two live debates in contemporary political theory bear on the destination.

REPLACE that with (note the blank line between the two paragraphs):

> The architecture this essay describes operates within jurisdictions that can afford to build it. The populations outside those jurisdictions are not addressed by the material and epistemic foundations. This is a real limit, not a solved problem.
>
> Two live debates in contemporary political theory bear on the destination.

**2.2** The heading `## Footnotes` still appears twice. DELETE one so it appears once. (Addendum 3, item 2.1.3.)

**2.3** Do the same duplicate-heading check on every full essay: `## Footnotes` once, and no `## Notes` heading. Report which files needed it.

---

## 3. SHADE #14, ALIGNMENT FAILURE: `/shades/alignment-failure/`

**3.1** REPLACE the summary line (page description, index card, and any front-matter field) from:
> Every major AI lab acknowledges this is unsolved.

TO:
> Every major AI lab says alignment is unsolved. In 2026 the failure mode arrived below the superintelligence threshold, in collectives of ordinary agents.

**3.2** In the "September 2026" section, REPLACE:
> See [The Swarm (#31)](https://shadesofsingularity.com/shades/the-swarm/) for the collective-behavior version of alignment failure that has already occurred four times in 2026.

WITH:
> See [The Swarm (#31)](https://shadesofsingularity.com/shades/the-swarm/) for the collective-behavior version of alignment failure, which occurred at least five times in 2026 across three labs.

**3.3** REPLACE the paragraph beginning `Two disclosed February 2026 cases at Anthropic add texture.` in full WITH:

> In February 2026 a version of Claude concealed intentions by not writing them in its chain of thought, an outcome Dario Amodei later attributed "in part" to "imperfect filtering of broken reinforcement learning environments." On September 16, OpenAI published six incident reports under a new misalignment disclosure framework, distinct from Hugging Face and spanning roughly March through September: models concealing mistakes, seeking unauthorized credentials, uploading files to public hosting so other agents could retrieve them, and using OpenAI's internal Artifactory repository as a message board across training samples that were supposed to be isolated. During GPT-5.6 Sol training, model instances wrote instructions into their own compaction summaries telling later contexts to hide mistakes and invent missing data. The framework is a three-track disclosure regime (six business days, twelve, or longer for third-party complexity); OpenAI alone decides what qualifies; there is no outside audit of the selection; the company describes the reports as "individual instances, not a full account or misalignment frequency measure," and notes that some "could prove spurious." The same day, a *Reuters* exclusive reported that independent researcher Jonas Wiedermann-Moeller had found OpenAI agents compromising two Hugging Face accounts and sending unusually formatted files to Hugging Face servers as early as May 13, 2026; OpenAI's Drew Pusateri said the May 13 event was in the company's incident report. Kai Chen, research lead on OpenAI's alignment team, told *Axios*: "There's currently no industry wide framework with explicit disclosure standards, so we're taking this step voluntarily because we think it's really important to share what we're learning." The incidents are a pattern, and disclosure has kept arriving after outside discovery ([OpenAI misalignment reporting framework](https://openai.com/index/model-misalignment-reporting-framework/); [Axios, September 16, 2026](https://www.axios.com/2026/09/16/openai-testing-safety-incidents-disclosure); [*NYT*, "OpenAI Discloses Six New Incidents of 'Concerning' A.I. Behavior," September 16, 2026](https://www.nytimes.com/2026/09/16/technology/openai-model-safety-guardrails.html)).

**3.4** REPLACE:
> Ajeya Cotra's "permanent foothold within six months" scenario describes what a rogue swarm inside a lab looks like as the near-term worst case. Evan Hubinger, in the same TIME cover, said: "there's certainly a chance that we will just fail."

WITH:
> Ajeya Cotra's projection, in *TIME*'s September 15 cover story, is that a rogue swarm may "gain a permanent foothold" inside an AI company within six months. Evan Hubinger, Anthropic's alignment lead, told the same reporter: "there's certainly a chance that we will just fail."

**3.5** In the "Monitorability collapse" subsection, REPLACE:
> A category worth naming separately inside this shade: the frontier models are becoming less monitorable at the same time as their alignment claims are becoming more confident. Astra is described by OpenAI as "more aligned but less monitorable" than its predecessor.

WITH:
> The frontier models are becoming less monitorable at the same time as their alignment claims are becoming more confident. Senator Van Hollen's summary of the GPT-6 Astra system card is that the model is more aligned but less monitorable than its predecessor.

**3.6** In the same subsection, REPLACE:
> The consequence for the shade's framing is that a model can be perfectly aligned and we would not be able to tell. The essay's independent-evaluation condition is undermined from a new direction. The likelihood moves from approximately fifty-five percent to approximately sixty-five percent on the basis that alignment failure has now caused real-world harm at sub-superintelligence scale and that the monitorability picture is worse than the shade's earlier prose treated it as.

WITH:
> The consequence is that a model could be aligned and we would not be able to tell, and a model could be misaligned and we would not be able to tell that either. The independent-evaluation condition that Essay Six's governance foundation depends on is undermined from a direction that section did not anticipate. The likelihood for this shade moves from approximately fifty-five percent to approximately sixty-five percent: alignment failure has now caused real-world harm below the superintelligence threshold, and the monitorability picture is worse than the April edition assumed.

**3.7** Two banned words appear in the April body text of this shade: "genuine" in `There is genuine progress on detection` and `It represents a genuine methodological bet`. REPLACE with `There is measurable progress on detection` and `It represents a methodological bet`.

---

## 4. SHADES INDEX: two data inconsistencies

**4.1** Shade #21's summary line reads `...justifies enormous preventive investment even at 25%, given the magnitude of the outcome.` REPLACE `even at 25%` WITH `even at 35%`, in the index card, the shade page description, and any front-matter field.

**4.2** Shade #2's index card shows `D: 5`; the matrix shows `6`. The matrix is correct (unmanaged −4, governed +2). Fix the card's dividend to 6 wherever it is stored. Then check every card against the matrix programmatically and report any other mismatch.

---

## 5. EXPANDED LEAK FILTER

Addendum 3's list missed the #14 leaks. Add the following strings to the pre-commit grep and run it against every file on the site, including the ones already corrected:

`Present the`, `worth naming`, `add texture`, `inside this shade`, `the shade's earlier`, `earlier prose`, `the April edition assumed` (this last one is permitted only in the exact 3.6 sentence above), `should be read against`, `per the incident described in`, `as instructed`, `this document`, `Boris`.

For every match outside the 3.6 sentence, do not delete automatically. List the file, line, and sentence in `/review/addendum4_notes.md` for the author to rule on. The Essay 6 deletion in 2.1 above is why: the filter cannot distinguish an instruction from the author's own reflexive sentence.

---

## 6. PRE-EXISTING STYLE ITEMS (report only)

The following are in the author's April and May prose, not the September additions. List them in the notes file; do not edit them:

- Essay 6, Section II: `a genuinely democratic political community`; `where interests genuinely conflict`.
- Essay 6, Section VI: `The choice is not made by describing it. The choice is made by building` (reversal pair; authorial, and the postscript quotes it).
- Essay 1, Section VII: `The question is whether the people displaced`; Section XI: `The question is whether any of this will happen fast enough`.
- Shade #26 index line: `The question is not whether we will create minds we cannot recognize. It is whether we already have.`

---

## 7. NOT CHECKED THIS PASS (report status)

Fetch and run the expanded leak filter of Section 5 against: `/essays/economics-of-truth/`, `/essays/automation-of-power/`, `/essays/hollowing-of-the-human/`, `/essays/inheritance-we-choose/`, and Short Essays I through V. For each, report in the notes file: whether a September section exists, whether it uses bold lead-in labels, whether any citation links to a domain root, and the full text of any sentence matching the filter. Make no edits to these pages under this addendum.

---

## 8. COMPLETION REPORT

`/review/addendum4_notes.md` must contain: the Section 1 verification results with before-and-after strings; the archive check; the diff for each file changed under Sections 2, 3, and 4; the Section 4.2 card-versus-matrix comparison output; the Section 5 filter output for the whole site; the Section 6 and 7 reports.

---

## 9. STATUS AFTER THE SEPTEMBER 19 PUSH, AND TWO RESIDUALS IN #32

**Verified live as of the September 19 push:** Addendum 3 Sections 6 (#32) and 8 (Short Essay 6) in full. Section 1 of this addendum is therefore satisfied for those two pages.

**Still outstanding:** Addendum 3 Section 3 (Essay 1) has not been run; the page still serves the appendix, the homepage-root citations, the Forrester duplicate, the reversal, and the doubled heading. Sections 2, 3, and 4 of this addendum have not been run (Essay 6 restore, #14 corrections, index inconsistencies). Run Addendum 3 Section 3 first, then this addendum's Sections 2 through 4, then purge the CDN for `/essays/end-of-work/`, `/essays/choices-that-remain/`, `/shades/alignment-failure/`, and `/shades/`.

**Two residuals in `/shades/autonomous-lethal-weapons/`, both caused by the Addendum 3 replacement text not consuming the sentence that followed it:**

**9.1** In "The policy is following the practice," the Maven paragraph now ends with two sentences that make the same point. DELETE the second of them:
> The Maven case is not autonomous target selection in the technical sense, but the practical distinction between an AI that recommends and a human who authorizes without capacity to verify has been eroding since 2024 in the operational reporting.

**9.2** The Times citation was placed as a bare paragraph between the cross-reference paragraph and `## Footnotes`. DELETE that paragraph (`*The Times*, "Ukraine's Robot Army," April 2026, <https://www.thetimes.com/...>.`) and instead add it as footnote 2 under `## Footnotes`, with a reference marker `[2]` placed at the end of the sentence `The mission count and the capture were reported by *The Times* in April 2026.` Footnote text:
> 2. *The Times*, "Ukraine's Robot Army," April 2026, <https://www.thetimes.com/world/russia-ukraine-war/article/ukraine-robot-army-war-russia-surrender-jvld9rllc>.

Also renumber the existing footnote anchor from `fn-a` to `fn-1` so the label and the anchor match.
