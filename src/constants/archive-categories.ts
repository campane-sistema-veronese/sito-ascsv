export const archiveCategorySlugs = [
  'censimento-campanario',
  'storia-cultura',
  'itinerari',
  'modulistica-gare',
  'suonate-classiche',
  'gare-5-campane',
  'gare-6-campane',
  'gare-9-campane',
  'altre-gare',
] as const

export type CategorySlug = (typeof archiveCategorySlugs)[number]

export type Category = {
  slug: CategorySlug
  label: string
  description: string
  icon: string
}

export const archiveCategories: Record<CategorySlug, Category> = {
  'censimento-campanario': {
    slug: 'censimento-campanario',
    label: 'Censimento campanario',
    icon: 'map',
    description:
      'Censimento dei campanili a sistema veronese, con informazioni sulle campane e sullo stato del concerto.',
  },
  'storia-cultura': {
    slug: 'storia-cultura',
    label: 'Storia e cultura',
    icon: 'history_edu',
    description: 'Materiali divulgativi e testi dedicati alla tradizione campanaria.',
  },
  itinerari: {
    slug: 'itinerari',
    label: 'Itinerari',
    icon: 'menu_book',
    description: 'Raccolta dei volumi "Itinerari" pubblicati annualmente.',
  },
  'modulistica-gare': {
    slug: 'modulistica-gare',
    label: 'Modulistica gare',
    icon: 'assignment',
    description: 'Regolamenti, schede iscrizione e documenti organizzativi delle gare.',
  },
  'suonate-classiche': {
    slug: 'suonate-classiche',
    label: 'Suonate classiche',
    icon: 'library_music',
    description: 'Partiture e repertori della tradizione del suono a sistema veronese.',
  },
  'gare-5-campane': {
    slug: 'gare-5-campane',
    label: 'Gare a 5 campane',
    icon: 'filter_5',
    description: 'Partiture delle gare a 5 campane.',
  },
  'gare-6-campane': {
    slug: 'gare-6-campane',
    label: 'Gare a 6 campane',
    icon: 'filter_6',
    description: 'Partiture delle gare a 6 campane.',
  },
  'gare-9-campane': {
    slug: 'gare-9-campane',
    label: 'Gare a 9 campane',
    icon: 'filter_9',
    description: 'Partiture delle gare a 9 campane.',
  },
  'altre-gare': {
    slug: 'altre-gare',
    label: 'Altre gare',
    icon: 'filter_none',
    description: 'Partiture di altre gare.',
  },
}
