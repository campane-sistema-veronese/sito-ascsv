import { glob } from 'astro/loaders'
import { z } from 'astro/zod'
import { defineCollection } from 'astro:content'
import { ARCHIVE_CATEGORIES } from './constants/archive-categories'

const documents = defineCollection({
  loader: glob({
    base: '.',
    pattern: 'src/content/documents/**/*.md',
  }),
  schema: z.object({
    title: z.string().min(5),
    slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
    description: z.string().optional(),
    date: z.coerce.date(),
    category: z.enum(ARCHIVE_CATEGORIES),
    file: z.string().regex(/^\/docs\/.+\.pdf$/),
  }),
})

export const collections = {
  documents,
}
