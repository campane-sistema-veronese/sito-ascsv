import type { CategorySlug } from '@/constants/archive-categories'
import { sanityClient } from 'sanity:client'

export type Allegato = {
  title: string
  description?: string
  date: string
  fileUrl: string
}

/**
 * Fetch documents from Sanity for a specific category
 */
export async function fetchDocuments(category: CategorySlug): Promise<Allegato[]> {
  try {
    const documents = await sanityClient.fetch<Allegato[]>(
      `*[_type == "allegato" && category == $category] {
        title,
        description,
        date,
        "fileUrl": file.asset->url
      } | order(title asc)`,
      { category },
    )
    return documents
  } catch (error) {
    console.error(`Failed to fetch documents for category ${category}:`, error)
    throw error
  }
}

/**
 * Fetch all categories with document counts
 */
export async function fetchCategoriesWithCount(): Promise<Array<{ category: string; count: number }>> {
  try {
    const allegati = await sanityClient.fetch<{ category: string }[]>(`*[_type == "allegato"] { category }`)

    // Group by category and count
    const categoryMap = new Map<string, number>()
    allegati.forEach(({ category }) => {
      categoryMap.set(category, (categoryMap.get(category) ?? 0) + 1)
    })

    return Array.from(categoryMap.entries()).map(([category, count]) => ({
      category,
      count,
    }))
  } catch (error) {
    console.error('Failed to fetch categories with count:', error)
    throw error
  }
}
