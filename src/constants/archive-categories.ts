export const ARCHIVE_CATEGORIES = [
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

export type ArchiveCategory = (typeof ARCHIVE_CATEGORIES)[number]

const slugifyCategory = (category: string) =>
  category
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')

export const ARCHIVE_CATEGORY_SLUGS = ARCHIVE_CATEGORIES.map((category) => ({
  label: category,
  slug: slugifyCategory(category),
}))

export const ARCHIVE_CATEGORY_META = ARCHIVE_CATEGORY_SLUGS.map((item) => {
  if (item.slug === 'modulistica-gare') {
    return {
      ...item,
      icon: 'assignment',
      description: 'Regolamenti, schede iscrizione e documenti organizzativi delle gare.',
    }
  }

  if (item.slug === 'itinerari') {
    return {
      ...item,
      icon: 'menu_book',
      description: 'Raccolta dei volumi "itinerari" pubblicati annualmente.',
    }
  }

  if (item.slug === 'storia-e-cultura') {
    return {
      ...item,
      icon: 'history_edu',
      description: 'Materiali divulgativi e testi dedicati alla tradizione campanaria.',
    }
  }

  if (item.slug === 'gare-a-5-campane') {
    return {
      ...item,
      icon: 'filter_5',
      description: 'Partiture delle gare a 5 campane.',
    }
  }

  if (item.slug === 'gare-a-6-campane') {
    return {
      ...item,
      icon: 'filter_6',
      description: 'Partiture delle gare a 6 campane.',
    }
  }

  if (item.slug === 'gare-a-8-campane') {
    return {
      ...item,
      icon: 'filter_8',
      description: 'Partiture delle gare a 8 campane.',
    }
  }

  if (item.slug === 'gare-a-9-campane') {
    return {
      ...item,
      icon: 'filter_9',
      description: 'Partiture delle gare a 9 campane.',
    }
  }

  if (item.slug === 'altre-gare') {
    return {
      ...item,
      icon: 'filter_none',
      description: 'Partiture di altre gare.',
    }
  }

  return {
    ...item,
    icon: 'music_note',
    description: 'Partiture e repertori della tradizione del suono a sistema veronese.',
  }
})

export const ARCHIVE_CATEGORY_BY_SLUG = Object.fromEntries(
  ARCHIVE_CATEGORY_SLUGS.map((item) => [item.slug, item.label]),
) as Record<string, ArchiveCategory>
