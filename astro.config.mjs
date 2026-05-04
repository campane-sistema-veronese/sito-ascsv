// @ts-check
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'astro/config'

import sanity from '@sanity/astro'

// https://astro.build/config
export default defineConfig({
  site: 'https://campane-sistema-veronese.github.io',
  base: '/sito-ascsv',

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
