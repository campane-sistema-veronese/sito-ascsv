export const urlFor = (path: string) => {
  const base = import.meta.env.BASE_URL || '/'

  // Absolute URL: return as is
  if (/^[a-z][a-z0-9+.-]*:\/\//i.test(path)) {
    return path
  }

  // Protocol-relative URL: return as is
  if (path.startsWith('//')) {
    return path
  }

  const normalizedBase = base.endsWith('/') ? base.slice(0, -1) : base
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${normalizedBase}${normalizedPath}`
}
