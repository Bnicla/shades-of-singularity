// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://shadesofsingularity.com',
  redirects: {
    '/scenarios': '/the-29-shades',
    '/scenarios/[slug]': '/the-29-shades/[slug]',
    '/the-29-shades/creativity-singularity': '/the-29-shades/creative-extraction',
  },
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/admin'),
    }),
  ],
});
