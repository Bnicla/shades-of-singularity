import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const essays = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './content/essays' }),
  schema: z.object({
    number: z.number(),
    numeral: z.string(),
    title: z.string(),
    subtitle: z.string(),
    slug: z.string(),
    description: z.string(),
    draft: z.boolean().optional().default(false),
  }),
});

const appendix = defineCollection({
  loader: glob({ pattern: 'appendix.md', base: './content', generateId: ({ entry }) => entry.replace(/\.md$/, '') }),
  schema: z.object({
    title: z.string(),
    subtitle: z.string().optional(),
  }),
});

const pages = defineCollection({
  loader: glob({ pattern: '{about,home}.md', base: './content', generateId: ({ entry }) => entry.replace(/\.md$/, '') }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
  }),
});

export const collections = { essays, appendix, pages };
