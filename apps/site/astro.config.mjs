// @ts-check
import { defineConfig } from 'astro/config';
import vercel from '@astrojs/vercel';
import { cacheVercel } from '@astrojs/vercel/cache';

// https://astro.build/config
export default defineConfig({
  // Public company pages are on-demand rendered, then cached at Vercel's CDN.
  // This matches the hosting decision in DOCUMENTATION.md and prevents repeat
  // visitors from invoking the server function or Postgres at all.
  output: 'server',
  adapter: vercel(),
  cache: {
    provider: cacheVercel(),
  },
});
