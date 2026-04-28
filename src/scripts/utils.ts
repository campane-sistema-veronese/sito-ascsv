export const urlFor = (path: string) => {
  const base = import.meta.env.BASE_URL
  if (path.startsWith(base)) {
    return path
  }
  const suffix = path.startsWith('/') ? path : `/${path}`
  return base + suffix
}
