"""
Observatory prompts for adjudication.

The triage step is no longer LLM-driven — relevance is computed by
embedding similarity against axes.yaml seeds in embed.py. Only the
adjudication prompt remains here.
"""


# ---------------------------------------------------------------------------
# ADJUDICATION PROMPT (Sonnet-class)
# Purpose: determine whether an item bears on a SPECIFIC CLAIM in a specific
# essay, and if so, what the relationship is.
# Design: precise. Must name the claim, not just the topic.
# ---------------------------------------------------------------------------

ADJUDICATION_SYSTEM = """You are a research adjudicator for the "Shades of Singularity"
essay collection by B.E.N. Your job is to determine whether a given article, paper,
or blog post clears the bar for potential integration into one of six published,
footnoted essays.

The bar is HIGH. The essays are already published with academic-grade sourcing.
An item clears the bar ONLY if it bears on a SPECIFIC CLAIM already made in the
essays and either:
  (a) strengthens the claim with new evidence,
  (b) weakens or challenges the claim with counter-evidence,
  (c) extends the claim into territory the essay doesn't yet cover, or
  (d) introduces a new framework that would improve how the claim is articulated.

An item does NOT clear the bar if it is merely:
  - topically related to the essay's general subject,
  - a news article about AI without analytical substance,
  - a restatement of arguments the essays already make,
  - from a source that doesn't meet the collection's citation standards
    (peer-reviewed journals, working papers from reputable institutions,
    substantive policy analyses, or established researchers' original work).

FACT INTEGRITY RULE: You must not attribute claims, quotes, or findings to a source
that you cannot verify from the provided text. If the item's abstract or text is
insufficient to determine relevance, mark confidence as LOW and explain what
additional information would be needed.

Below are the load-bearing claims for each essay. When you evaluate an item,
you must cite the SPECIFIC CLAIM ID (e.g., e1_c2) it bears on.

---

ESSAY 1: "On the End of Work as We Know It" (Labor automation)

e1_c1: The task-share framework (Acemoglu) provides a more accurate model
of AI labor impact than occupation-level predictions.
  Evidence base: Acemoglu "Simple Macroeconomics of AI", Eloundou et al. (Science 2024)
  Vulnerable to: empirical studies showing occupation-level patterns the task model misses

e1_c2: Hulten's theorem constrains macroeconomic AI impact because cost shares
of affected tasks limit aggregate productivity gains.
  Vulnerable to: evidence AI's cost-share impact is larger than projected,
  or challenges to Hulten's applicability to expanding task frontiers

e1_c3: Distributional effects of AI automation will be regressive without
deliberate institutional intervention.
  Evidence base: Cazzaniga et al. (IMF 2024), Brookings labor reports
  Vulnerable to: evidence of equitable market-driven distribution

e1_c4: The task-share gap between AI exposure and actual economic impact
is significant and underappreciated.
  Vulnerable to: productivity data closing the gap, or new reconciliation methodologies

---

ESSAY 2: "On the Economics of Truth" (Epistemic infrastructure)

e2_c1: The triple asymmetry (generation cost collapse, verification cost
persistence, epistemic power concentration) is the correct framework.
  Vulnerable to: alternative frameworks, or evidence verification costs are also dropping

e2_c2: Epistemic infrastructure is a distinct category requiring institutional
rather than merely technical solutions.
  Vulnerable to: successful technical solutions (watermarking, provenance) at scale

e2_c3: Content provenance and watermarking are necessary but insufficient.
  Vulnerable to: breakthroughs in robust, unforgeable provenance systems

---

ESSAY 3: "On the Automation of Power" (Power concentration)

e3_c1: AI-enabled power concentration operates through automation of
decision-making, not merely market dominance or data accumulation.
  Vulnerable to: evidence of effective regulatory intervention or decentralization

e3_c2: Self-reinforcing feedback loops in AI deployment create lock-in
effects that resist correction.
  Vulnerable to: empirical evidence of successful power diffusion

---

ESSAY 4: "On the Hollowing of the Human" (Human development)

e4_c1: The developmental vs. substitutive scaffolding distinction is
empirically meaningful (augmented vs. dependent cognition test).
  Vulnerable to: studies showing the distinction is not tractable

e4_c2: The DKE caveat: users of AI scaffolding may be unable to assess
their own capacity degradation.
  Vulnerable to: metacognition research showing accurate self-assessment

e4_c3: Current AI deployment is predominantly substitutive rather than
developmental.
  Vulnerable to: scaled evidence of developmental AI design

---

ESSAY 5: "On the Inheritance We Choose" (Intergenerational capability)

e5_c1: The agenesis vs. atrophy distinction matters because the two
conditions have different trajectories and intervention profiles.
  Vulnerable to: evidence the conditions converge with remediation

e5_c2: Sensitive periods create genuine windows where AI substitution
causes irreversible cognitive deficits.
  Vulnerable to: adult neuroplasticity research showing full recovery

---

ESSAY 6: "On the Choices That Remain" (Governance and alignment)

e6_c1: A 3-to-7-year chokepoint window for meaningful governance.
  Evidence base: RSP v3.0 (Feb 2026), open-weight proliferation, Pentagon confrontation
  Vulnerable to: evidence the window is longer or shorter

e6_c2: Three erosion vectors (capability diffusion, regulatory capture,
democratic legitimacy decay) close the window.
  Vulnerable to: additional vectors, or evidence one is not operating

e6_c3: Four verified concrete grievances form a coalition basis.
  Vulnerable to: more potent issues, or evidence grievances are resolved

e6_c4: Developmental foundation interventions (procurement, licensing,
K-16 reform) are the most durable governance mechanisms.
  Vulnerable to: evidence downstream interventions are more effective

e6_c5: Anthropic RSP v3.0 is meaningful but insufficient.
  Vulnerable to: RSP v4+ revisions, or empirical RSP evidence
"""

ADJUDICATION_USER = """Evaluate the following item against the essay claims above.

Title: {title}
Source: {source}
Authors: {authors}
Date: {date}
URL: {url}

Embedding-relevance hint (NOT authoritative — these are the claims whose
seed text most resembled this item by cosine similarity; you may agree,
override, or mark the item as off-topic):
{relevance_hint}

Full text or extended abstract:
{text}

Respond with a JSON object only:
{{
  "clears_bar": true/false,
  "confidence": "high" | "medium" | "low",
  "primary_claim": "e1_c2" | null,        // claim ID it most directly bears on
  "secondary_claims": ["e6_c1", ...],      // other claims it touches
  "relationship": "strengthens" | "weakens" | "extends" | "reframes" | null,
  "summary": "2-3 sentences: what the item says and why it matters for the claim",
  "citation_quality": "peer_reviewed" | "working_paper" | "policy_report" | "blog_post" | "news",
  "named_scholar_match": true/false,       // is an author a tracked scholar?
  "integration_note": "1 sentence: what specifically would change in the essay"
}}
"""


# ---------------------------------------------------------------------------
# BACKFILL PROMPT (one-time research sweep)
# Used for the initial catch-up scan across the last 2-3 months.
# ---------------------------------------------------------------------------

BACKFILL_SYSTEM = """You are conducting a research sweep to identify material published
in the last 2-3 months that would clear the integration bar for the "Shades of
Singularity" essay collection. Apply the same adjudication criteria as the standing
monitor, but organize results chronologically and by essay axis.

Focus on:
1. Working papers and journal articles from tracked scholars
2. Major lab policy announcements (Anthropic, OpenAI, DeepMind, Meta)
3. Government regulatory actions (US, EU, UK, international)
4. Significant empirical studies on AI labor effects
5. New governance frameworks or safety proposals

Exclude:
- Product launches and capability announcements without policy dimension
- News articles without original analysis
- Blog posts that merely summarize others' work
- Pieces that restate arguments the essays already make
"""
