// @ts-check
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'astro/config'

import sanity from '@sanity/astro'

// https://astro.build/config
export default defineConfig({
  // Old config for github page only
  // site: 'https://campane-sistema-veronese.github.io',
  // base: '/sito-ascsv',

  // New config for top level domain, without base path
  site: 'https://campanesistemaveronese.it',

  vite: {
    plugins: [tailwindcss()],
  },

  integrations: [
    sanity({
      projectId: 'x34my81r',
      dataset: 'production',
      useCdn: false, // for static builds
    }),
  ],
})
