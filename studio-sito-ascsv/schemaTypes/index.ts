import {defineField, defineType} from 'sanity'

export const documentType = defineType({
  name: 'allegato',
  title: 'Allegato',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Titolo',
      type: 'string',
      description: 'Titolo leggibile per gli utenti',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      description: 'solo minuscole, numeri e trattini',
      options: {
        source: 'title',
        slugify: (input) =>
          input
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)+/g, ''),
      },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Descrizione',
      type: 'text',
    }),
    defineField({
      name: 'date',
      title: 'Data',
      type: 'datetime',
      options: {
        dateFormat: 'YYYY-MM-DD',
      },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'category',
      title: 'Categoria',
      type: 'string',
      options: {
        list: [
          'censimento-campanario',
          'storia-cultura',
          'itinerari',
          'modulistica-gare',
          'suonate-classiche',
          'gare-5-campane',
          'gare-6-campane',
          'gare-9-campane',
          'altre-gare',
        ],
      },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'file',
      title: 'File',
      type: 'file',
      validation: (rule) => rule.required(),
    }),
  ],
})

export const schemaTypes = [documentType]
