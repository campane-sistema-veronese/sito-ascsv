import { glob } from 'astro/loaders'
import { z } from 'astro/zod'
import { defineCollection } from 'astro:content'

const categories = [
  'Modulistica gare',
  'Itinerari',
  'Storia e cultura',
  'Gare a 5 campane',
  'Gare a 6 campane',
  'Gare a 8 campane',
  'Gare a 9 campane',
  'Altre gare',
  'Suonate classiche',
] as const

const documents = defineCollection({
  loader: glob({
    base: '.',
    pattern: 'src/content/documents/**/*.md',
  }),
  schema: z.object({
    title: z.string().min(5),
    slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
    description: z.string().min(10),
    date: z.coerce.date(),
    category: z.enum(categories),
    file: z.string().regex(/^\/docs\/.+\.pdf$/),
  }),
})

export const collections = {
  documents,
}
