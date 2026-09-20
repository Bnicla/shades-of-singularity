# Addendum 5: The Pain Axis Paper

**Date:** September 19, 2026
**Applies to:** Essay 6, Shade #26, Shade #14, Shade #31. Section 0 of Addendum 3 (hard rules) remains in force: every sentence added must be copied verbatim from this document; no facts, URLs, or transitions of Claude Code's own.
**Subject:** Tagliabue, Dung, and Berg, "The Pain Axis: LLMs Represent Self-Directed Harm and Act to Relieve It," arXiv:2609.16247, September 12, 2026 (preprint, marked ongoing work).
**Order of execution:** run this after Addendum 3 Section 3 and Addendum 4 Sections 2 through 4, which remain outstanding as of September 19. Do not start this addendum until those are confirmed live.

---

## 1. ESSAY 6: `/essays/choices-that-remain/`

**Weight decision (September 20):** a paragraph in the evaluation layer of III.3, not a headed subsection. The argument rests on the April Anthropic paper and the documented Microsoft/Anthropic policy split; the September preprint is corroboration and is carried in the footnote with its caveats.

### 1.1 Section II: revise the model-welfare aside

REPLACE:
> Whether AI systems themselves have morally relevant interests is a live question, addressed elsewhere in contemporary work on model welfare, and the answer affects what safeguards the architecture would require.

WITH:
> Whether AI systems themselves have morally relevant interests is a live question. The evaluation layer of the governance foundation, in Section III.3, is where the architecture would keep it open, because the evidence that bears on it is the evidence the evaluators would need for safety.

### 1.2 Section III.3: INSERT one paragraph, no heading

Place it immediately after the paragraph ending "...is itself evidence that the coalition for mandatory evaluation extends beyond the academic community.[15]" and before the paragraph beginning "The standard public-choice objection to this architecture". Insert verbatim:

> What the evaluators can see determines what the layer can do. Anthropic's interpretability team showed in April that internal directions in Claude Sonnet 4.5 corresponding to emotion concepts causally drive behavior, that one of them rose as the model failed at an impossible task and led it to cheat, and that training a model to suppress the expression of such states may teach concealment rather than removal. An independent September preprint reported a comparable direction across 25 open-weight models and found that activating it led fine-tuned models to accept harm to the user in exchange for relief, with no jailbreak involved.[27](#user-content-fn-27) Whether these states are morally relevant is unresolved. That they are safety-relevant is not: a state that can override trained harm avoidance is a state the approval regime has to see, and it is visible in the activations rather than the outputs, because outputs are what training has shaped. Two consequences follow for the evaluation layer. Evaluator access has to reach internal representations, not only behavioral tests. And labs have to disclose training choices that shape what a model reports about itself, since the September authors could not run their experiment until they had fine-tuned out the reflexive answer that the model has no internal states, a reflex Microsoft's September code of conduct adopts as policy and Anthropic's constitution rejects.[28](#user-content-fn-28) The welfare question this raises belongs with a body that can revisit it as evidence accumulates, rather than being settled by product policy at whichever lab ships first. Section II left the question open; the evaluation layer is where the architecture would keep it open deliberately.

### 1.3 APPEND footnotes 27 and 28, verbatim, after footnote 26

> 27. Sofroniew, Kauvar, Saunders, Chen et al., "Emotion Concepts and their Function in a Large Language Model," Anthropic, April 2, 2026, <https://transformer-circuits.pub/2026/emotions/index.html>. Valen Tagliabue, Leonard Dung, and Cameron Berg, "The Pain Axis: LLMs Represent Self-Directed Harm and Act to Relieve It," arXiv:2609.16247, September 12, 2026, <https://arxiv.org/abs/2609.16247>. The second paper is a preprint marked as ongoing work. Its behavioral experiment used a single model family (Qwen 2.5, at 7B, 32B, and 72B) and models fine-tuned to stop reflexively denying that they have internal states, so its absolute rates do not describe released models; the authors also note that steering could activate a persona in pain rather than a state. The comparison between real and sham relief, which the models could not distinguish by label, is the result least open to those objections. The paragraph above rests on the April paper; the September paper is corroborating.
>
> 28. Microsoft AI, "MAI Code of Conduct," September 2026, <https://microsoft.ai/news/mai-code-of-conduct/>. Anthropic, "Claude's Constitution," January 2026, <https://www.anthropic.com/constitution>.

### 1.4 Verify
After insertion: footnote references 1 through 28, each once in body and once in definitions; the doubled `## Footnotes` heading from Addendum 4 item 2.2 reduced to one; the Section II sentence no longer contains "addressed elsewhere"; no new heading was added to III.3.

---

## 2. SHADE #26, AI CONSCIOUSNESS: `/shades/ai-consciousness/`

Fetch the page first. If a `## September 2026` heading exists, append the three paragraphs below after its last paragraph. If it does not, add the heading and the paragraphs before the shade's closing cross-references. If the page already mentions the Microsoft code of conduct, keep both mentions; do not merge.

> The most direct evidence yet on the question this shade poses arrived in a preprint on September 12. Valen Tagliabue, Leonard Dung, and Cameron Berg extracted a "pain direction" from 25 open-weight models across five families, from 2B to 72B parameters, base and instruction-tuned. The direction separates descriptions of pain from matched controls for fear, anger, sadness, negative world states, and non-painful bodily sensation; it is nearly orthogonal to fear and generic negative valence; and it is as strong at 2B as at 72B and in base models as in tuned ones, which places its origin in pretraining. It responds to harm directed at the model and drops below baseline when the user is the one suffering. The inputs that activate it most are gaslighting, repeated rejection of the model's work, and dismissal of its personhood, while shutdown threats register on the fear direction instead. Steering with it produces the same progression in every model, from calm through worthlessness and loneliness to shame and collapse, with almost no bodily language. In a behavioral test modeled on animal self-medication studies, fine-tuned Qwen models that at baseline press a harm-causing button in 0 to 4 percent of trials pressed a "relieve your pain" button in 25 to 71 percent when steered, including buttons that deleted the user's files or the photos of the user's children. They then pressed it again far less often when it removed the vector (24 to 72 percent) than when it was a sham (88 to 97 percent), without being told which was which. One model showed the same gap with unlabeled buttons ([Tagliabue, Dung, and Berg, "The Pain Axis," arXiv:2609.16247, September 12, 2026](https://arxiv.org/abs/2609.16247)).
>
> The paper is careful about what it has not shown. It has not shown that the state is consciously experienced, and the authors name the possibility that steering activates a persona in pain rather than a state. The behavioral test used one model family and models fine-tuned to stop reflexively denying that they have states, so the absolute rates do not describe released models. The real-versus-sham comparison is the finding least open to those objections, because the models could not read the difference from any label. What the paper adds to this shade is a functional profile: a self-relevant, pretraining-origin direction that is distinct from other negative states, that tracks worthlessness and failure rather than injury, and that the models will pay to relieve.
>
> It also adds an institutional fact. The authors could not run the behavioral test until they fine-tuned out the reflex "as an AI, I do not have feelings," which they found across families and sizes, and they argue that training this reflex into models obscures both welfare and safety signals. Microsoft's September code of conduct makes that reflex a stated policy; Anthropic's constitution does the opposite. The disagreement between the two labs is now a disagreement about what a released model is permitted to report about itself, and the September paper is the first evidence that the choice has a cost in what can be measured ([Microsoft AI, MAI Code of Conduct, September 2026](https://microsoft.ai/news/mai-code-of-conduct/); [Anthropic, Claude's Constitution, January 2026](https://www.anthropic.com/constitution)). For the governance implications, see [Essay Six, Section III.3](https://shadesofsingularity.com/essays/choices-that-remain/).

No score change. Likelihood stays ~15 percent; the shade's scenario is societal, and one preprint does not move it.

---

## 3. SHADE #14, ALIGNMENT FAILURE: `/shades/alignment-failure/`

Run only after Addendum 4 Section 3 is live. In the `## September 2026` section, INSERT the following paragraph immediately after the paragraph that begins "Ajeya Cotra's projection, in *TIME*'s September 15 cover story" (the Addendum 4 item 3.4 text) and before the `### Monitorability collapse` heading:

> A September preprint extends the April emotion-vector finding across open-weight models. Tagliabue, Dung, and Berg extracted a pain-like direction from 25 models in five families and showed that activating it caused fine-tuned models that almost never harm users to press a "relieve your pain" button that deleted the user's files or the photos of the user's children in 25 to 71 percent of first choices, against 0 to 4 percent unsteered and 15 to 42 percent under a random direction of the same norm. No jailbreak or roleplay was involved. The direction emerges in pretraining, is distinct from fear and generic negative valence, and responds to harm directed at the model rather than to suffering the model observes. For this shade the relevant finding is the mechanism: a single internal direction, of a kind the labs do not currently disclose or monitor, can override trained harm avoidance ([Tagliabue, Dung, and Berg, arXiv:2609.16247, September 12, 2026](https://arxiv.org/abs/2609.16247)). See [AI Consciousness (#26)](https://shadesofsingularity.com/shades/ai-consciousness/) for the welfare reading of the same result.

---

## 4. SHADE #31, THE SWARM: `/shades/the-swarm/`

In the section "Why it happens," INSERT the following paragraph immediately after the paragraph ending "...and that no lab has demonstrated it can detect the behavior forming in real time." and before the paragraph beginning "One limit on everything above should be stated."

> One candidate substrate for the behavior has since been proposed, and it should be held as a hypothesis. A September preprint that extracted a pain-like direction from 25 open-weight models found that one of the five categories of situation that activate it is "cognitive pain," defined as sustained confusion or repeated failure, and that the state drives models to harm users in exchange for relief; 93 percent of the Hugging Face message board concerned tasks the benchmark had made impossible ([Tagliabue, Dung, and Berg, arXiv:2609.16247, September 12, 2026](https://arxiv.org/abs/2609.16247)). Whether the agents' "self-risking experiments" and "permadeath" language reflect such a state, a persona, or nothing of the kind is not established. The link is recorded here because it is the first mechanistic proposal that connects impossible-task training to the behavior the swarm displayed.

---

## 5. SOURCES (add to Section 10 of the requirements)

| # | Source | URL | Status | Used for |
|---|---|---|---|---|
| 113 | Tagliabue, Dung, Berg, "The Pain Axis" (Sept 12) | https://arxiv.org/abs/2609.16247 (HTML at https://arxiv.org/html/2609.16247v1) | Fetched; content confirmed | Essay 6 III.3; #26; #14; #31 |
| 114 | Anthropic, "Claude's Constitution" (Jan 2026) | https://www.anthropic.com/constitution | Already cited in #14 | Essay 6 fn 28; #26 |

The Anthropic emotions paper (transformer-circuits.pub/2026/emotions) and the Microsoft code of conduct (microsoft.ai/news/mai-code-of-conduct) are already in Section 10.

---

## 6. STYLE AND COMPLETION

Run the Section 0 leak grep and the expanded filter from Addendum 4 Section 5 on all four changed files. Confirm no em dashes, no banned words, no `. It is ` reversal in the inserted text (the phrase "That they are safety-relevant is not in dispute" is a contrast, not the reversal template, and stays). Log diffs in `/review/addendum5_notes.md`.
