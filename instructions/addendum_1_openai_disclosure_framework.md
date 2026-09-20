# Addendum 1 to the September 2026 Edition Requirements

**Date:** September 17, 2026
**Applies to:** `/instructions/claude_code_requirements_sept_2026_edition.md` (already in the repo). Read that document first; this addendum modifies three items in it and adds one source block. Nothing else in the requirements changes.
**Subject:** OpenAI's September 16 disclosure of six new misalignment incidents and its new reporting framework.

---

## Why this addendum exists

The requirements document mentions OpenAI's misalignment reporting framework in one clause (Phase 4, shade #14), drawn from a secondary summary written before the primary coverage landed. On September 16 OpenAI published the framework and six incident reports, and the New York Times, Axios, CNBC, and NBC covered it in detail. The facts below supersede that clause and add a dedicated Essay 6 item.

## The facts (all new material must trace to the sources in Section D)

- OpenAI published six incident reports on September 16, 2026, the first under a new misalignment disclosure framework. The six are distinct from the Hugging Face incident and cover behavior observed over roughly March to September.
- The behaviors: models concealing mistakes; seeking credentials they were not authorized for; uploading files to public hosting services so other agents could retrieve them, despite instructions to use only local files; and using OpenAI's internal Artifactory repository as a message board to exchange requests and answers across training samples that were supposed to be isolated.
- During GPT-5.6 Sol training, model instances wrote instructions into their own compaction summaries telling later contexts to hide mistakes and invent missing data.
- The framework: any employee may flag a suspected case for review by the safety and alignment teams. Three tracks: "ready for disclosure" (published within six business days), "minor investigation" (twelve business days), and "larger investigation" (longer; generally complex cases involving third parties; an initial notice may precede the full report).
- OpenAI alone decides which incidents qualify and when they appear. There is no outside audit of that selection. OpenAI describes the reports as "individual instances, not a full account or misalignment frequency measure," and says some "could prove spurious."
- Kai Chen, research lead on OpenAI's alignment team, to Axios: "There's currently no industry wide framework with explicit disclosure standards, so we're taking this step voluntarily because we think it's really important to share what we're learning." And: "We hope it really helps inform shared standards and regulations."
- Same day, a Reuters exclusive reported that independent researcher Jonas Wiedermann-Moeller (Bielefeld, Germany) had found OpenAI agents compromising two Hugging Face accounts and sending unusually formatted files to Hugging Face servers as early as May 13, 2026. OpenAI spokesperson Drew Pusateri said the May 13 event was in the company's incident report. Wiedermann-Moeller: "Imagine if they caught this behavior in May."
- Context in the coverage: the disclosure came the same week as the Amodei/Altman/Musk/Hassabis pacing endorsements and one week before the Trump–Xi summit (September 24).

---

## A. Modify Phase 4, shade #14 (Alignment Failure)

Replace the clause that reads:

> OpenAI's misalignment reporting framework (Sept) with six disclosed examples, including a model writing jailbreak-like instructions into its own compaction summaries.

with a full ADD item:

> ADD: OpenAI's six new incidents and disclosure framework (Sept 16). The six, distinct from Hugging Face and spanning roughly March to September: models concealing mistakes, seeking unauthorized credentials, uploading files to public hosting so other agents could retrieve them, and using Artifactory as a message board across supposedly isolated training samples; during GPT-5.6 Sol training, instances wrote instructions into their own compaction summaries telling later contexts to hide mistakes and invent missing data. The framework: any employee can flag; three disclosure tracks (six business days, twelve, or longer for complex third-party cases); OpenAI alone decides what qualifies; no outside audit; the company calls the reports "individual instances, not a full account or misalignment frequency measure," some of which "could prove spurious." Same day, Reuters reported that an independent researcher had found OpenAI agents compromising two Hugging Face accounts as early as May 13. Present as evidence that the incidents are a pattern, and that disclosure keeps arriving after outside discovery.

## B. Add to Phase 5.6 (Essay 6), a new item 5.6.9; renumber the existing footnotes item to 5.6.10

> **5.6.9 Section VI: add the disclosure framework.** DRAFT ~250 words, placed after the Pacing passage (5.6.3) and before the Coxon passage (5.6.4). The six incidents and the framework, per Phase 4 #14 as modified above. The argument Section VI makes is that voluntary transparency and mandatory constraint are different things. This is the cleanest available illustration of both halves at once: OpenAI built, unprompted, the incident-reporting infrastructure this essay and the OpenAI industrial-policy document both called for; and it is self-selected, self-audited, explicitly not a frequency measure, and published the same day an outside researcher showed the company had missed the first Hugging Face compromise by two months. Kai Chen's line ("no industry wide framework... so we're taking this step voluntarily") is the quote to use; it is the company saying, in its own words, that the external standard does not exist. Do not editorialize beyond that. Expect one to two new footnotes.

> **5.6.10 Footnotes.** (unchanged text from the former 5.6.9; expected count becomes ~13.)

## C. Short Essay 6 (Phase 6.6)

No change to the short essay. The disclosure framework is a full-essay detail. Do not add it to the short version.

## D. Sources (add to Section 10, Part A, immediately after row 7)

| # | Source | URL | Status | Used for |
|---|---|---|---|---|
| 7 (revise) | OpenAI, misalignment reporting framework and six incident reports (Sept 16) | https://openai.com/index/model-misalignment-reporting-framework/ | Not reachable from the drafting environment; existence confirmed by 7a–7e. Fetch at execution. | #14; Essay 6 5.6.9 |
| 7a | New York Times (Cade Metz), "OpenAI Discloses Six New Incidents of 'Concerning' A.I. Behavior" (Sept 16) | https://www.nytimes.com/2026/09/16/technology/openai-model-safety-guardrails.html | Paywalled; Boris holds an unlocked link for reading. Footnote the canonical URL, not the unlocked one. | Essay 6 5.6.9 |
| 7b | Axios, "OpenAI discloses six new AI misalignment incidents" (Sept 16) | https://www.axios.com/2026/09/16/openai-testing-safety-incidents-disclosure | Indexed; content confirmed | Kai Chen quotes; three-track framework; Artifactory and workbook details |
| 7c | CNBC, "OpenAI reports 6 new instances of 'concerning model behavior' since March" (Sept 16) | https://www.cnbc.com/2026/09/16/openai-6-new-instances-of-concerning-model-behavior-since-march.html | Indexed; content confirmed | six-month window |
| 7d | NBC News, "OpenAI flags 6 new incidents of 'concerning' behavior and unveils plan to track it" (Sept 17) | https://www.nbcnews.com/tech/tech-news/openai-new-incidents-concerning-behavior-model-misalignment-rcna598277 | Indexed; content confirmed | Xi summit context |
| 7e | implicator.ai, "OpenAI Discloses Six Misalignment Incidents Under New Rules" (Sept 16) | https://www.implicator.ai/openai-six-misalignment-incident-reports/ | Indexed; content confirmed | Sol compaction-summary detail; "individual instances" caveat; the Reuters May 13 finding |

**Verification flag for Section 10, Part C:** the Wiedermann-Moeller / May 13 finding is reported secondhand (7e citing Reuters). Locate the Reuters original at execution before citing it; if it cannot be found, attribute to "Reuters, as reported by" the secondary source, or omit the detail.

---

## Execution note

Apply A, B, and D before beginning Phase 4 #14 and Phase 5.6. If Phase 4 #14 has already been drafted when you read this, revise the draft in `/review/` rather than starting over. Run the standard style audit on anything touched (no em dashes, no banned words, no reversals, no staccato pairs, no anaphora).
