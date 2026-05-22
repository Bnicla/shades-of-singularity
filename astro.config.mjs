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
    '/essays/inheritance-we-leave': '/essays/inheritance-we-choose',
    '/essays/risks-we-cannot-reverse': '/essays/choices-that-remain',
    '/short-essays/inheritance-we-leave': '/short-essays/inheritance-we-choose',
    '/short-essays/risks-we-cannot-reverse': '/short-essays/choices-that-remain',
  },
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/admin'),
    }),
  ],
});
