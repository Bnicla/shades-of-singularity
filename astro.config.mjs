// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://shadesofsingularity.com',
  redirects: {
    '/scenarios': '/shades',
    '/scenarios/[slug]': '/shades/[slug]',
    '/the-29-shades': '/shades',
    '/the-29-shades/[slug]': '/shades/[slug]',
  },
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/admin'),
    }),
  ],
});
