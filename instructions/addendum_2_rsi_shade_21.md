# Addendum 2 to the September 2026 Edition Requirements

**Date:** September 17, 2026
**Applies to:** `/instructions/claude_code_requirements_sept_2026_edition.md` and Addendum 1 (both already in the repo). Read those first. This addendum modifies Phase 4, shade #21, and the corresponding line in Section 9, decision 5. It adds four sources to Section 10. Nothing else changes.
**Subject:** Recursive self-improvement (RSI): definitional structure for Shade #21 and a revision of its likelihood from the confirmed 45% to 35%.

---

## Why this addendum exists

The requirements confirmed a likelihood revision for Shade #21 (Intelligence Explosion / Hard Takeoff) from ~25% to ~45%, on the basis that both leading labs now say RSI is underway. That reasoning conflated two different claims. Statements like Amodei's ("recursive self-improvement is starting to happen across the industry, including at Anthropic") describe AI-automated AI research: agents doing machine-learning engineering under human direction. The shade's scenario is a self-accelerating loop in which each improvement cycle measurably speeds the next. The first is near-certain and already occurring. The second has not been demonstrated by anyone, and the only public measurement of the loop's magnitude is small. The likelihood of the shade's scenario should rise because its precondition now exists, but 45% overstates the evidence. This addendum corrects it to 35% and gives the shade a definitional structure so the correction is legible to readers.

## The facts (all new material must trace to the sources in Section D)

- Google's release note for Gemini 3.8 Flash and 3.8 Flash Cyber (September 2026) states that both models were "further accelerated by long-running agentic loops designed to recursively evaluate and refine the underlying models." This is the most direct public claim any lab has made about using recursive agent loops in model development, and it is a primary source.
- Fortune (Sept 3): Google shipped four Flash models in 106 days. The progression: a two-agent "self-improvement loop" for a game (May); a three-agent loop helping train a robotics model (August); loops refining the Gemini models themselves (3.8 Flash). Fortune notes it is unclear what this portends for larger models, and that the cadence has not extended to the flagship Pro line, which remains unreleased despite a promised summer launch, reportedly because internal prototypes showed too little progress over Flash to justify release.
- Brin's internal memo (The Information, via Fortune): improving coding is a step toward self-improving AI; DeepMind should turn its models into "primary developers" of code. Business Insider (Sept 9): Brin runs Gemini from a converted microkitchen at headquarters, next to DeepMind's current head, with Pichai visiting several times a week; a former employee describes him as "AGI-pilled" and heavily invested in RSI; an internal program monitors some employees' coding sessions to train Gemini's coding capabilities. Reuters (August): Brin pushing DeepMind to accelerate and tilt resources toward RSI since an April all-hands. Roughly a thousand researchers reportedly on related initiatives.
- Structural signals at Google: Hassabis handing over operational leadership of DeepMind to focus on AGI; chief scientist Jeff Dean departing.
- The only public quantitative measurement of an AI-driven improvement loop at Google: AlphaEvolve improved a matrix-multiplication kernel by roughly 23 percent, reducing Gemini's training time by roughly 1 percent (per the Zeniteq analysis cited by Trending Topics; Claude Code should cite the AlphaEvolve paper or DeepMind blog directly at execution).
- The September 2026 rumor: a leaker's tweet with capitalized letters spelling "RSI" congratulating Google DeepMind trended on X and was treated by parts of the industry as confirmation. No model, paper, benchmark, or date accompanied it. Google employees are reported to be tempering expectations. Do not cite the rumor as evidence of anything except the state of the discourse.
- The test for a genuine demonstration (Trending Topics, which is correct on this): several consecutive improvement cycles in which a system rebuilds its own research process without human intervention, at a measurably rising rate. Nothing public meets it.
- Discourse fact: the term "recursive self-improvement" migrated in roughly six months from AI-safety forums into a Google product announcement, a Reuters report on a co-founder's strategy, and a Business Insider profile. The labs now use it as a selling point.

---

## A. Modify Phase 4, shade #21 (Intelligence Explosion / Hard Takeoff)

Replace the entire #21 entry with:

> ### #21 Intelligence Explosion (Hard Takeoff)
> - RESTRUCTURE: give the shade a three-tier definition near the top, and keep it throughout. (1) **Automated AI research**: AI agents performing machine-learning engineering, evaluation, data curation, and code under human direction. (2) **Component self-improvement**: AI systems improving specific parts of their own training or inference stack with measurable gains. (3) **Recursive self-improvement proper**: a loop in which a system redesigns its own research process without human intervention and each cycle measurably accelerates the next. The shade's scenario is (3). Most public use of "RSI" in 2026 refers to (1) or (2). State this plainly; the collection's readers will encounter the term constantly and most of what they encounter will be (1) described as (3).
> - ADD, under tier (1): Amodei (Sept 12): RSI "starting to happen across the industry, including at Anthropic," and his description of what it means at Anthropic (models writing most code and increasingly designing experiments; the automation of AI R&D). Jack Clark's February observation of colleagues managing Claudes that manage Claudes (TIME Aug 7). OpenAI: AI models helped supervise Astra's training (Van Hollen letter, citing the system card). Altman's stated target of a "true automated AI researcher" by March 2028. Opus 4.6 and GPT-5.3-Codex system cards describing the era. ICML 2026's RSI workshop. Brin's "primary developers" memo and the microkitchen program. Anthropic's recursive self-improvement report (institute page). Simon Lermen's distinction between true RSI and AI-automated AI R&D; keep it.
> - ADD, under tier (2): Google's 3.8 Flash release note ("long-running agentic loops designed to recursively evaluate and refine the underlying models") and the May-to-August progression Fortune documents; four Flash models in 106 days. AlphaEvolve's ~23% kernel improvement and ~1% training-time reduction as the only public measurement of magnitude. Navier-Stokes in 88 hours and Neon (1,300 H200s, surpassing Astra on a materials benchmark) as evidence of what automated research produces, noting neither is a self-accelerating loop.
> - ADD, under tier (3): nothing public meets the demonstration test (consecutive unassisted cycles at a rising rate). The skeptical check: Google's flagship Pro model has not shipped in months because internal prototypes showed insufficient progress over Flash; a lab that had achieved (3) would not have a stalled flagship. Hubinger's bet that his team would catch a self-improving misaligned model, and "certainly a chance that we will just fail." The September rumor, described only as a rumor and as evidence of the industry's nervousness.
> - ADD (one paragraph): the migration of the term from safety discourse into corporate strategy and product marketing in roughly six months, and why the AlphaEvolve number matters as the thing that keeps the migration honest.
> - CONFIRMED (revised by Addendum 2): Likelihood ~25% → **~35%**, not 45%. The precondition (tier 1) is met and every major lab is pursuing tiers 2 and 3 explicitly, which is why the number rises. It does not rise further because tier 3 is undemonstrated and the measured loop magnitude is on the order of one percent. Governed/unmanaged scores unchanged (−5 / +5 / D 10).

## B. Modify Section 9, decision 5

Replace "#21 likelihood 25→45" with "#21 likelihood 25→35 (revised by Addendum 2)."

## C. Outcome matrix and index (Phase 4, "Outcome matrix and index")

Apply 35% for #21, not 45%. If the display order was already computed with 45%, recompute.

## D. Sources (add to Section 10, Part A)

| # | Source | URL | Status | Used for |
|---|---|---|---|---|
| 109 | Google, "Introducing Gemini 3.8 Flash and 3.8 Flash Cyber" (Sept 2026) | https://blog.google/innovation-and-ai/models-and-research/gemini-models/3-8-flash-and-3-8-flash-cyber/ | Indexed; the "recursively evaluate and refine" quote confirmed verbatim | #21 tier (2); primary source |
| 110 | Fortune, "Google shipped four Gemini Flash models in 106 days. But its flagship frontier model is still nowhere to be seen." (Sept 3) | https://fortune.com/2026/09/03/google-shipped-four-gemini-flash-models-in-106-days-but-its-flagship-frontier-model-is-still-nowhere-to-be-seen/ | Indexed; content confirmed | #21 tiers (2) and (3); Brin memo via The Information; May/August loop progression; stalled Pro |
| 111 | Business Insider, Brin's microkitchen and RSI push (Sept 9) | (locate canonical URL at execution; the 36kr summary at https://eu.36kr.com/en/p/3981566976080643 quotes it at length) | To locate | #21 tier (1); "AGI-pilled"; coding-session monitoring |
| 112 | Trending Topics (Steinschaden), "Three Letters Set the AI World Buzzing: Has Google Cracked RSI?" (Sept 14) | https://www.trendingtopics.eu/three-letters-set-the-ai-world-buzzing-has-google-cracked-rsi/ | Fetched; content confirmed | #21 tier (3): the rumor, the demonstration test, the AlphaEvolve figures (secondary; cite the AlphaEvolve primary), Hassabis/Dean reshuffle |

**Verification flags for Section 10, Part C:**
- AlphaEvolve's 23% / 1% figures: cite the DeepMind AlphaEvolve paper or blog post directly, not the secondary summary.
- Reuters (August) on Brin and RSI: locate the original before citing; otherwise attribute via Fortune or Business Insider.
- Hassabis stepping back and Dean departing: confirm against a primary announcement or a tier-one outlet before including.

---

## Execution note

Apply A through D before drafting #21. If #21 has already been drafted with the 45% figure, revise the draft in `/review/` and recompute the matrix. Run the standard style audit on anything touched.
