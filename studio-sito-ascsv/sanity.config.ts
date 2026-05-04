import {visionTool} from '@sanity/vision'
import {defineConfig} from 'sanity'
import {structureTool} from 'sanity/structure'
import {schemaTypes} from './schemaTypes'

export default defineConfig({
  name: 'default',
  title: 'Sito ASCSV',

  projectId: 'x34my81r',
  dataset: 'staging',

  plugins: [structureTool(), visionTool()],

  schema: {
    types: schemaTypes,
  },
})
