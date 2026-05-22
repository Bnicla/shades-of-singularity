# Shades of Singularity

Source for [shadesofsingularity.com](https://shadesofsingularity.com) — an essay collection on AI futures and the institutional choices that determine which future arrives.

## Stack

- **Framework:** [Astro 5](https://astro.build/) (static site, minimal JS)
- **Hosting:** Vercel (manual deploy: `npx vercel --prod`)
- **Typography:** Source Serif 4 (body) / Instrument Sans (headings)
- **Design:** Warm amber accent (#B8860B), cream background (#FDFBF7)

## Project structure

```
content/
├── home.md                 # Homepage intro copy
├── about.md                # About page copy
├── appendix.md             # Outcome matrix (rendered inside /shades/)
├── essays/                 # Full essays (6 essays, numbered 01-06)
├── short-essays/           # Short essays (10-min argument versions)
└── scenarios/              # The 30 "shades" (one per file)

src/
├── components/             # Astro components (Header, Footer, EssayCard, etc.)
├── content.config.ts       # Zod schemas for every collection
├── layouts/                # BaseLayout, EssayLayout, PageLayout
├── pages/                  # Routes (index, about, essays, short-essays, shades, blueprint)
└── styles/                 # Global + per-section CSS

instructions/               # Working folder for current-session instructions and drafts
shareable/                  # Flat snapshots of content for sharing with Claude chats
scripts/                    # Project maintenance scripts
public/                     # Static assets (favicon, print.css, robots.txt)
```

## Collections

Defined in `src/content.config.ts`:

| Collection    | Path                  | Used by                                        |
|---------------|----------------------|------------------------------------------------|
| `essays`      | `content/essays/`     | `/essays/`, `/essays/[slug]/`                  |
| `shortEssays` | `content/short-essays/` | `/short-essays/`, `/short-essays/[slug]/`    |
| `scenarios`   | `content/scenarios/`  | `/shades/`, `/shades/[slug]/`                  |
| `pages`       | `content/home.md`, `content/about.md` | `/`, `/about/`                 |
| `appendix`    | `content/appendix.md` | Outcome matrix rendered inside `/shades/`      |

## Navigation

`Short Essays | Full Essays | The Shades | About`

The `/blueprint/` URL still serves a placeholder page ("in development") but has no content collection, no sub-pages, and is not linked from nav. If the section is reactivated, its content collection and sub-pages will need to be rebuilt.

Legacy URL redirects configured in `astro.config.mjs`:
- `/scenarios/*` and `/the-29-shades/*` redirect to `/shades/*`
- `/essays/inheritance-we-leave` and `/essays/risks-we-cannot-reverse` redirect to new slugs
- `/short-essays/inheritance-we-leave` and `/short-essays/risks-we-cannot-reverse` redirect to new slugs

## Scripts

```bash
npm run dev      # Start dev server
npm run build    # Build static site
npm run preview  # Preview built site

./scripts/regenerate-shareable.sh  # Rebuild shareable/ snapshots from content
```

## Style rules (enforced)

- Zero em dashes
- Zero "genuinely", "crucial", "comprehensive", "paradigm", "robust", "transformative", "leverage", or other AI-slop markers
- No forced profundity or aphoristic closings
- No "not X but Y" constructions
- No hardcoded counts in nav, headings, or SEO (e.g. "The 30 Shades")

## Deployment

```bash
npx vercel --prod
```

Custom domain: `shadesofsingularity.com`

## Content status

- **Shades (30):** All expanded and sourced
- **Full Essays (6):** All published
- **Short Essays (6):** All published
- **Blueprint:** Section deactivated; placeholder page only
- **Appendix:** Outcome matrix embedded in `/shades/` page

## Author

B.E.N. — MIT graduate, product manager in Big Tech deploying generative AI.
