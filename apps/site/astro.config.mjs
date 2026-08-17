// @ts-check
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

// https://astro.build/config
export default defineConfig({
  // server-rendered, not fully static -- doc 17's page reads live from
  // Postgres per request/build; ISR/on-demand revalidation is a Part 14
  // hosting concern, not decided here. Node adapter for local dev/preview;
  // production would likely swap to Vercel's adapter (DOCUMENTATION.md's
  // hosting choice), not decided here either.
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
