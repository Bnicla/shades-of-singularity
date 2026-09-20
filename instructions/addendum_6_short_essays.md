# Addendum 6: Short Essays I through V

**Date:** September 20, 2026
**Applies to:** `content/short-essays/01-end-of-work.md`, `02-economics-of-truth.md`, `03-automation-of-power.md`, `05-inheritance-we-choose.md`. Short Essay IV needs no change. Section 0 of Addendum 3 (hard rules) applies: every sentence added is copied verbatim from below; nothing else changes in these files.
**Subject:** Corrections to the September 2026 paragraphs after review of the source files on the main branch.

---

## 1. SHORT ESSAY V, `05-inheritance-we-choose.md` (must fix)

REPLACE the paragraph beginning `As of September 2026, the argument that institutional response is possible` in full WITH:

> The strongest evidence that institutional response is possible is in the child-protection record. The GUARD Act, from Senators Hawley and Blumenthal, passed the Senate Judiciary Committee 22 to 0 in April 2026; it would ban AI companions for users under 18 and impose fines up to $250,000. Character.AI and Google settled five wrongful-death suits brought by families of teenagers early in the year. Four states ban AI therapy outright and four more regulate companions. In August, MIT's committee on AI use adopted productive struggle as an institutional principle for the whole university. Harm to minors is legible, and where the harm is legible the policy response has moved on a timescale of months rather than decades.

Reason: the phrase "at the author's own university" was a private note about the author, not a sourced fact, and the site is published under initials. Delete it everywhere it may appear on the site (grep `author's own` across all content).

## 2. SHORT ESSAY I, `01-end-of-work.md`

REPLACE the paragraph beginning `As of September 2026, the entry-level figures have moved.` in full WITH:

> By September 2026 the entry-level figures had moved further. Recent college graduates aged 22 to 27 were unemployed at 5.6 percent against 4.2 percent for the broader labor force, 42 percent of them were underemployed, and Stanford's tracking put employment in AI-exposed occupations for 22-to-25-year-olds at 19 percent below trend. AI had been the top employer-cited reason for layoffs for five straight months. In the same month Anthropic's own economists published a formal model, reviewed by Acemoglu among others, in which the extreme scenario has the economy growing by a third by 2030 while total labor income stays roughly flat and the labor share falls from sixty percent to 45.2 percent. The sequencing this essay describes, entry-level first and aggregate later, is now the pattern on the record.

Reason: "the 2025 essay" was wrong (April 2026); "peer-reviewed-adjacent" is working jargon from the research notes; "the essay's" is third-person self-reference.

## 3. SHORT ESSAY II, `02-economics-of-truth.md`

**3.1** DELETE the paragraph beginning `As of September 2026, a new epistemic asymmetry belongs alongside` in full (it currently sits between the bridge paragraph and the closing paragraph).

**3.2** INSERT the following paragraph immediately after the paragraph ending `Each cycle degrades the epistemic infrastructure on which the next cycle depends.` and before the paragraph beginning `There are counterweights.`:

> A fourth asymmetry appeared in September 2026, and it runs in the opposite direction from the three above. On September 8 OpenAI reported that ten thousand agents running for eighty-eight hours had produced a machine-verified proof for the Navier-Stokes equations, one of the seven Millennium Prize problems, and Terence Tao described the result as a decoupling, new this year, between getting answers and getting understanding. Here verification succeeds and comprehension does not follow. The same pattern is visible in code, where researchers at the frontier labs have said publicly that they can no longer read what their own systems write.

Reason: placement interrupted the closing movement; "the essay names" and "the essay tracks" are third-person self-reference; "unprecedented" is removed by paraphrasing Tao rather than quoting him.

## 4. SHORT ESSAY III, `03-automation-of-power.md`

REPLACE the paragraph beginning `As of September 2026, the human-in-the-loop question the essay opened with` in full WITH:

> The human-in-the-loop question this essay opened with was decided on the battlefield during the summer of 2026. On July 6 a Russian drone chose its own target at a gas station in Zaporizhzhia and killed three civilians. Ukraine's Hornet drones are sent to designated kill zones with autonomous target selection, the UK Ministry of Defence is examining a policy change that would authorize the practice, and Anthropic's September threat report documents Russian drone designs built to select human targets without approval. On the regulatory side, the White House's own June order lapsed on August 1 with no deliverables, the European Union postponed and simplified the AI Act's heaviest obligations over the summer, and Congress has six bills and no vote. Every institution this essay describes has acknowledged the question, and none has answered it.

Reason: "the EU softened the AI Act in a June 29 vote" states an unverified date as fact (Section 10, Part C of the requirements flagged it); the replacement says only what is confirmed. "The essay opened with" and "the essay describes" are third-person self-reference. The two-sentence ending is merged.

## 5. SHORT ESSAY IV, `04-hollowing-of-the-human.md`

No change.

## 6. VERIFY

After edits: run the Section 0 grep and the Addendum 4 Section 5 expanded filter on all four files; confirm `author's own` returns nothing anywhere in `content/`; confirm each file still has exactly one September 2026 paragraph; purge the CDN for the four short-essay routes. Log diffs in `/review/addendum6_notes.md`.
