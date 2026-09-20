---
name: boris-writing-style
description: Writing style guide for Boris (B.E.N.), author of Shades of Singularity. Use this skill whenever writing, editing, or reviewing any content for Boris, including essays, short essays, site copy, instructions, or any prose. Triggers on any writing task in the Shades of Singularity project, any request to draft or edit text for Boris, any review or audit of existing content, or any mention of Boris's editorial standards. This skill defines hard constraints (things that must never appear) and positive style guidance (how the writing should read). Read this before writing a single word.
---

# Boris Writing Style Guide

This skill defines the writing standards for Boris (B.E.N.) and the Shades of Singularity project. Every piece of written content, whether a 10,000-word essay, a 2,000-word short essay, site copy, or edit instructions, must conform to these rules.

## HARD CONSTRAINTS (never violate)

### Zero em dashes
No em dashes anywhere, ever. Use commas, colons, semicolons, parentheses, or restructure the sentence. Run `grep '—'` on every output file before delivering.

### Zero AI slop words
Never use: tapestry, landscape, multifaceted, delve, crucial, paradigm, robust, pivotal, underscore, leverage, navigate, foster, harness, realm, holistic, synergy, unprecedented, stakeholder, ecosystem (unless precisely describing a technology stack), genuinely, straightforward, honestly, impactful, transformative, game-changer, streamline.

### Zero AI rhetorical patterns
These are the patterns that make writing sound machine-generated. Catch them all:

**"Not X, it is Y" reversals:**
- BAD: "This is not a prediction. It is a description."
- BAD: "The question is not whether. The question is who."
- BAD: "This path requires no policy failure. It requires no malice."
- GOOD: Restructure as a single sentence or state the positive claim directly.

**Staccato declarative pairs for fake profundity:**
- BAD: "The technology doesn't choose. We do."
- BAD: "The economy grows. Inequality widens."
- BAD: "This path is achievable. The policy tools exist."
- GOOD: Combine into flowing prose. These pairs are AI's attempt to sound punchy. They sound manufactured.

**Anaphora (repeated sentence starters for rhetorical effect):**
- BAD: "It writes. It codes. It analyzes. It diagnoses. It negotiates. It designs."
- BAD: "If the answer is X... If the answer is Y... If the answer is Z..."
- GOOD: Use a list within a sentence, or vary the structure.

**"The question is" / "The real question" / "The only question":**
- These are AI's favorite way to pivot. Rewrite to state the point directly.

**"A common mistake is..." / "A related mistake is..." / "Another common mistake is...":**
- This is prompt-shaped writing. The essay is responding to an invisible checklist. Integrate the points as a continuous argument, not as corrections to misconceptions.

**One-sentence paragraphs for dramatic effect:**
- BAD: "This is already happening." (as its own paragraph)
- BAD: "Three paths lead from here." (as its own paragraph)
- GOOD: Fold into the surrounding paragraph or extend with substance.

**Poster sentences (designed to be quoted rather than to advance the argument):**
- BAD: "The ambition of the response must match the scale of the transformation."
- BAD: "Whether the severing is liberation or catastrophe."
- Test: Would this sentence look natural on a motivational poster? If yes, rewrite it.

**"Worth noting" / "It's important to" / "It's worth taking seriously":**
- Didactic, lecturer voice. If it's worth noting, just note it.

### Zero hardcoded counts
Never write "six essays," "thirty shades," "forty-four footnotes," or any specific count of project elements anywhere on the site or in instructions. Counts change. The text should never need updating when content is added.

## POSITIVE STYLE GUIDANCE

### Voice
Direct, analytical, warm but not soft. Think long-form magazine essay (New Yorker, Atlantic) crossed with policy analysis. Not combative. Not academic. Not false modesty, but no grandiose comparisons either. The reader is an intelligent adult who will give you ten minutes if you earn it and leave if you waste their time.

### Sentence structure
Varied. Mix long sentences with short ones naturally, the way a human writer does. Avoid the AI pattern of alternating between short punchy declarations and longer explanatory sentences in a predictable rhythm. Read the paragraph aloud. If it sounds like it was composed by an algorithm optimizing for "engagement," rewrite it.

### Paragraph structure
Substantial. Each paragraph should develop one idea fully. Avoid the AI pattern of using many short paragraphs with one or two sentences each. Paragraphs in analytical writing are typically 4-8 sentences. They should flow into the next without needing subheadings or bullet points to signal transitions.

### Counterarguments
Engage the strongest version. State the objection fairly, then explain where it fails. Do not straw-man. Do not dismiss with a wave. The reader should feel that the objection was taken seriously and found wanting on specific grounds.

### Assertions and sourcing
Every factual claim in a full essay must be footnoted. Facts must be accurately represented, never shaped to fit narrative. If a fact doesn't quite support the point being made, either find a better fact or adjust the argument. Standing editorial standard from the Scott Shambaugh/GitHub PR incident: accuracy over narrative convenience, always.

### Short essays specifically
No footnotes. No hedging. No counterargument engagement (that's the full essay's job). Written from scratch, not compressed from the long version. Target audience: professionals willing to give ten minutes. The short essay should convey the core argument with enough clarity and force that someone who never reads the long version still gets the essential insight.

### Transitions
Natural. Not "Additionally," "Furthermore," "Moreover," or "It's also worth noting." Build the argument so each paragraph's opening connects to the previous paragraph's conclusion through the logic of the ideas, not through transitional crutches.

## SELF-CHECK PROTOCOL

Before delivering any written content to Boris, run through this checklist internally:

1. Search for em dashes (the character —). If found, fix.
2. Search for every slop word in the list above. If found, replace.
3. Read every sentence that contains "not" followed by a period. Is it a "not X / it is Y" reversal? If so, restructure.
4. Read every paragraph opener. Are three or more paragraphs in a row opening with the same structure ("A common mistake..." / "Another mistake..." / "It's also...")? If so, rewrite for flow.
5. Read every sentence shorter than 8 words. Is it a standalone dramatic declaration? If so, fold it into its paragraph or extend it.
6. Read the closing paragraph. Does it sound like a TED talk ending? If so, rewrite it as a continuation of the argument rather than a mic drop.
7. Read the entire piece aloud in your head. Does any passage sound like it was written to be impressive rather than to be clear? If so, rewrite for clarity.

## WHAT BORIS VALUES

- Surgical edits over scattershot suggestions
- Each essay staying on its own axis (no scope creep between essays)
- Concrete examples grounding abstract arguments
- Acknowledgment of what's uncertain alongside what's claimed
- The reader's intelligence respected (no over-explanation)
- Speed of delivery balanced with quality (don't pad, don't rush)
- Honest assessment when something isn't working, even if it means redoing significant work
