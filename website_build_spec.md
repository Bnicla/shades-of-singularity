# Shades of the Singularity — Website Build Spec

## For Claude Code: Build instructions for shadesofsingularity.com

---

## Overview

Build a static website for an essay collection called "Shades of the Singularity." The site publishes 8 long-form essays exploring AI futures through a Hamiltonian institutional design lens, plus an appendix of 28 AI scenarios. All essays are published at once — this is not a blog or a newsletter. It is a unified body of work, closer to a digital book than a content stream.

**Domain:** shadesofsingularity.com
**Tech stack:** Static site. HTML/CSS/JS. No framework required — this is a reading experience, not an app. If a static site generator is preferred for maintainability, use Astro or 11ty. No React needed. Performance and typography are the priorities.
**Hosting:** Will be deployed to Vercel, Netlify, or similar static host.

---

## Design Direction

### Tone: Editorial / Literary / Serious
Think: Noema Magazine, Aeon, Works in Progress, The Atavist, or a well-designed university press publication. NOT a tech blog. NOT a Substack. NOT a startup landing page.

This is a collection of essays about civilizational-scale problems. The design must communicate intellectual weight, seriousness, and permanence. The reader should feel they've entered a body of work, not landed on a blog post.

### Key Design Principles

**Typography-first.** The site is 95% reading. Typography must be exceptional. Use a distinctive serif for body text — something with character and excellent readability at long-form lengths. Consider: Freight Text, Newsreader, Lora, Literata, Source Serif 4, or Cormorant Garamond. Pair with a clean contrasting sans-serif for headings and navigation — something with editorial authority. Consider: DM Sans, Sora, Plus Jakarta Sans, or Instrument Sans. Line height ~1.6-1.7 for body. Max reading width ~680px. Generous paragraph spacing.

**Restrained color palette.** Dark text on light background for readability. One accent color used sparingly — a deep amber, muted gold, or warm ochre that evokes aged paper and institutional gravity. NOT blue (too tech), NOT purple (too AI-slop), NOT bright green (too startup). Think: the color of old constitutional documents, ink, institutional stone.

**Generous whitespace.** Let the essays breathe. Wide margins. No sidebar. No clutter. The design should feel like opening a well-made book, not loading a webpage.

**No visual noise.** No hero images. No stock photos. No AI-generated illustrations. No gradients. No parallax. No decorative SVGs. The content IS the design. If any visual element is used, it should be typographic — a large drop cap, a pull quote, a section divider. Restraint is the aesthetic.

**Subtle atmospheric details.** Very light paper-like texture on the background (almost imperceptible). Subtle transitions on navigation. A slight warmth to the background color — not pure white but something like #FDFBF7 or similar off-white/cream. Thin rule lines as dividers. Small, refined details that reward attention without demanding it.

**Dark mode support.** Should have a dark mode that inverts to a very dark warm tone (not pure black — something like #1A1814) with cream/warm white text. Toggle in navigation.

**No images anywhere in the essays.** This is pure text. The only visual elements are typographic.

---

## Site Structure

### Pages

```
/                     — Home page
/essays/              — Essays index (list of all 8)
/essays/pace-of-ruin  — Essay 1
/essays/public-mind   — Essay 2
/essays/aristocracy   — Essay 3
/essays/democratization — Essay 4
/essays/optimization  — Essay 5
/essays/hollowing     — Essay 6
/essays/sovereignty   — Essay 7
/essays/true-wealth   — Essay 8
/appendix             — The 28-scenario taxonomy
/about                — About the author and project
```

### Navigation

Minimal persistent navigation — site title on the left, a simple menu on the right. Menu items: Essays, Appendix, About. Plus dark mode toggle (sun/moon icon, no label). On mobile: hamburger menu.

On essay pages: add previous/next essay navigation at the bottom. Show essay number and title for both. This encourages reading the full collection in sequence.

---

## Page Specifications

### Home Page ( / )

The home page is the gateway. It must accomplish three things: establish the tone, state the premise, and direct readers to the essays.

**Layout:**

1. **Title block.** Large, centered. The collection title "Shades of the Singularity" in the display/heading typeface. Below it, a subtitle: "Eight Essays on the Futures We're Building and the Ones We're Drifting Into." Below that, the author name: "by Boris Schiapparelli." (Note: use the author's actual name -- this is a placeholder; the user will replace it.) Generous vertical spacing above and below. The title should feel monumental but not bombastic.

2. **The premise.** 3-4 paragraphs of text, centered column (same reading width as essays). This is the manifesto — the compressed argument. Content will be provided by the author. Placeholder text for now:

   "The most consequential technology in human history is being debated with the wrong questions, defended with remedies that solve nothing, and governed by no one.

   These eight essays offer a different way of seeing. Each one opens a window onto one dimension of the AI future — not to predict, but to make visible what the current discourse obscures. Each one dismantles the reassuring answers that dominate the conversation: skill up, regulate, trust the market, become a plumber. And each one names what we actually need — at the scale of nations and the scale of civilization — without pretending to have all the answers.

   The future is not a choice among alternatives. It is a painting composed of many shades laid one over another, each altering the color of what lies beneath. The question is not which shade arrives. It is which mixture — and whether anyone is holding the brush."

3. **Essay list.** All 8 essays listed below the premise. Each entry shows: essay number (in the accent color, small), title (as a link, in the heading typeface), the "what if" subtitle in italic, and a one-line description. Generous spacing between entries. These should feel like a table of contents in a serious book, not a blog archive.

   ```
   I     On the Pace of Ruin
         What if institutions are structurally incapable of governing AI?

   II    On the Corruption of the Public Mind
         What if AI destroys the shared reality that democracy requires?

   III   On the Aristocracy of the Algorithm
         What if AI creates a permanent cognitive caste system?

   IV    On the Democratization of Intelligence and Its Discontents
         What if AI's greatest gift is also its deepest trap?

   V     On the Folly of Universal Optimization
         What if every company acting rationally destroys the economy?

   VI    On the Hollowing of the Human
         What if we win every battle and lose what made the war worth fighting?

   VII   On the Sovereignty of Nations in the Age of Machines
         What if AI dissolves the nation-state from above, below, and within?

   VIII  On the True Wealth of the Nation
         What if the economy was never about labor in the first place?
   ```

4. **Footer.** Minimal. Links to Appendix and About. A line: "Also by the author:" with links to his other published works (placeholder for now). Copyright line.

### Essay Pages ( /essays/[slug] )

**Layout:**

1. **Essay header.** Essay number (Roman numeral, in accent color, smaller). Title in the heading typeface, large. The "what if" subtitle in italic below the title. A thin horizontal rule. Then the essay body.

2. **Essay body.** Single column, max-width ~680px, centered. Body text in the serif typeface. Standard markdown formatting: paragraphs, emphasis (italic), strong (bold), blockquotes. No images.

   **Special formatting for the three-movement structure:**
   - Each movement begins with a styled section header. Not a standard H2 — something more editorial. Options: a small-caps label ("THE LENS" / "THE FALSE REMEDIES" / "WHAT WE ACTUALLY NEED"), separated by generous whitespace and a thin rule, or an ornamental section break (three centered dots, a small decorative dash, etc.).
   - Within "The False Remedies" section, each false remedy should be visually distinct — perhaps starting with the remedy in italic as a lead-in, followed by the rebuttal. Not bullet points — flowing paragraphs with clear visual separation.
   - Within "What We Actually Need" section, "National" and "Global" subsections should be clearly delineated — could use small-caps labels or a subtle indentation/margin treatment.

3. **Reading progress indicator.** A thin, subtle progress bar at the very top of the page (in the accent color) showing how far through the essay the reader has scrolled. Unobtrusive.

4. **Estimated reading time.** Displayed near the title — small, muted text. "~12 min read" or similar.

5. **Previous / Next navigation.** At the bottom of each essay, after generous whitespace. Shows the previous and next essay (number + title), styled as clear navigation links. Essay 1 has no previous; Essay 8 links forward to the Appendix instead.

6. **No comments. No share buttons. No related posts. No newsletter signup.** This is a publication, not a platform.

### Essays Index Page ( /essays/ )

Same table-of-contents layout as the home page essay list, but as a standalone page. May include a brief introductory line: "Eight essays. Eight angles on a future arriving whether we see it or not."

### Appendix Page ( /appendix )

**Title:** "The Singularity Scenarios: A 360-Degree Analysis"
**Subtitle:** "An exhaustive taxonomy of 28 possible AI futures, ranked by likelihood"

**Layout:** The full content of the 28-scenario taxonomy document. This is a long reference page. Structure it clearly with:

- A brief introduction (the "Note on How to Read This Document" section)
- Tier headings (Tier 1 through Tier 5) as major section breaks
- Each scenario as a subsection with: name, likelihood badge (styled as a small pill/tag in muted color), outcome scores, and the full text
- The outcome matrix as a styled HTML table — clean, well-spaced, with alternating row shading
- The "What the Matrix Reveals" section
- The "Composite Picture" closing section

Add a sticky or floating table of contents sidebar (on desktop only) that lists all 28 scenarios and highlights the current one as the reader scrolls. This helps navigation in a very long document.

### About Page ( /about )

Author bio (placeholder for now). Brief explanation of the project's origins. The Hamiltonian framing — why these essays exist.

---

## Technical Requirements

- **Performance:** Lighthouse score 95+ on all metrics. This is a text site — it should be extremely fast. Minimal JS. No external dependencies beyond fonts.
- **Fonts:** Load from Google Fonts or self-host for performance. Use `font-display: swap`. Limit to 2 font families, 3-4 weights total.
- **Responsive:** Must work beautifully on mobile. Reading experience on phone should be excellent — appropriate text size, generous margins, no horizontal scroll.
- **SEO:** Proper meta tags, Open Graph tags, structured data. Each essay should have its own OG title, description, and (text-based) OG image.
- **OG Images:** Auto-generate simple text-based OG images for social sharing — essay title on a solid background in the site's typography. No photos. Can use a library like @vercel/og or pre-generate as static images.
- **Print stylesheet:** Essays should print cleanly — just the text, good margins, no navigation or UI elements.
- **Accessibility:** Proper heading hierarchy, ARIA labels on navigation, sufficient color contrast in both light and dark modes, keyboard navigable.
- **Analytics:** Include a slot for a privacy-respecting analytics script (Plausible, Fathom, or similar). Don't install one — just leave a clearly marked place in the HTML where it can be added.

---

## Content Handling

**All essay content will be provided as markdown files.** The build system should read markdown files from a `/content/essays/` directory and render them as HTML with the essay page template.

Each markdown file should support frontmatter:

```yaml
---
number: 1
numeral: "I"
title: "On the Pace of Ruin"
subtitle: "What if institutions are structurally incapable of governing AI?"
slug: "pace-of-ruin"
description: "A one-sentence description for SEO and the essay index."
---
```

The appendix content is also a markdown file in `/content/appendix.md`.

**For the initial build, populate essay markdown files with placeholder text** — use the essay briefs from this spec as the content. Mark clearly with "[DRAFT CONTENT — TO BE REPLACED]" at the top of each file. The author will replace these with the final essays.

---

## Content Editing: Decap CMS

Add Decap CMS (formerly Netlify CMS) as a lightweight admin interface for editing essays and the appendix without touching Git directly.

**Setup:**
- Add a `/admin` route with the Decap CMS single-page app (just an `index.html` and a `config.yml`)
- Authenticate via GitHub OAuth (the author logs in with their GitHub account)
- Decap reads and writes markdown files to the Git repo — no database, no server, no hosting cost
- On save, Decap commits to the repo, which triggers a rebuild via Vercel/Netlify

**Decap config should expose these content collections:**

1. **Essays** — points to `/content/essays/*.md`. Editable fields: title, subtitle, number, numeral, slug, description (from frontmatter), and body (markdown). Rich-text editor for the body with support for headings, bold, italic, blockquotes.

2. **Appendix** — points to `/content/appendix.md`. Single file, full markdown body editing.

3. **About** — points to `/content/about.md`. Single file.

4. **Home** — points to `/content/home.md`. The manifesto/premise text on the home page.

**Admin page location:** `/admin/`
**Access:** Restrict to the author only via GitHub OAuth. No public registration.

This gives the author a browser-based editing experience at `shadesofsingularity.com/admin` — log in, click an essay, edit in a rich-text interface, hit publish. The site rebuilds in seconds. No Git knowledge required for routine edits.

---

## What NOT to Build

- No heavy CMS (WordPress, Ghost, Contentful, etc.) — Decap CMS is the only content management layer
- No comments system
- No newsletter signup
- No share buttons (readers know how to copy a URL)
- No related posts / recommendation engine
- No cookie banner (don't use cookies)
- No chatbot or AI assistant
- No animations beyond subtle transitions on navigation and the reading progress bar
- No hero images, stock photos, or decorative illustrations

---

## File Structure (suggested)

```
/
  /content
    /essays
      01-pace-of-ruin.md
      02-public-mind.md
      03-aristocracy.md
      04-democratization.md
      05-optimization.md
      06-hollowing.md
      07-sovereignty.md
      08-true-wealth.md
    appendix.md
    about.md
    home.md
  /src (or /templates, depending on SSG)
    /layouts
      base.html
      essay.html
      page.html
    /styles
      main.css
    /scripts
      main.js (dark mode toggle, reading progress, appendix TOC)
  /public
    /fonts (if self-hosting)
    favicon.ico
    robots.txt
    sitemap.xml
  /dist (build output)
```

---

## Summary for Claude Code

Build a static literary essay site. Typography-driven, minimal, serious. Think digital equivalent of a well-designed university press publication. Eight essays about AI futures, each following a three-part structure (lens / false remedies / what we need). Plus a 28-scenario appendix and an about page. Content in markdown with frontmatter, editable via Decap CMS at /admin (Git-backed, no database). Extremely fast, accessible, responsive. Dark mode. Reading progress bar. No images, no clutter, no blog aesthetic. The design should make the reader feel they've entered a body of work, not landed on a webpage.
