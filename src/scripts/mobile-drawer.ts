function initMobileDrawer() {
  const btn = document.getElementById('mobile-menu-button') as HTMLButtonElement
  const menu = document.getElementById('mobile-menu') as HTMLElement
  if (!btn || !menu) return

  const panel = menu.querySelector('aside') as HTMLElement | null
  const overlay = menu.querySelector('[data-menu-overlay]') as HTMLElement | null
  const closeBtn = document.getElementById('mobile-menu-close') as HTMLButtonElement | null
  let previouslyFocused: Element | null = null

  const FOCUSABLE_SELECTOR =
    'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, [tabindex]:not([tabindex="-1"])'

  function isVisible(el: Element): boolean {
    const e = el as HTMLElement
    return !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length)
  }

  function getFocusableElements(container: HTMLElement | null): HTMLElement[] {
    if (!container) return []
    return Array.from(container.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)).filter(isVisible)
  }

  function disableMainFocus(): void {
    const main = document.querySelector<HTMLElement>('main')
    if (!main) return
    main.setAttribute('aria-hidden', 'true')
    const focusables = getFocusableElements(main)
    focusables.forEach((el) => {
      if (el.hasAttribute('tabindex')) {
        el.setAttribute('data-prev-tabindex', el.getAttribute('tabindex') ?? '')
      } else {
        el.setAttribute('data-prev-tabindex', '')
      }
      el.setAttribute('tabindex', '-1')
    })
  }

  function restoreMainFocus(): void {
    const main = document.querySelector<HTMLElement>('main')
    if (!main) return
    main.removeAttribute('aria-hidden')
    const restored = main.querySelectorAll<HTMLElement>('[data-prev-tabindex]')
    restored.forEach((el) => {
      const prev = el.getAttribute('data-prev-tabindex')
      if (prev === '') el.removeAttribute('tabindex')
      else el.setAttribute('tabindex', prev ?? '')
      el.removeAttribute('data-prev-tabindex')
    })
  }

  function onKeyDown(e: KeyboardEvent): void {
    if (e.key === 'Escape') {
      closeMenu()
      return
    }
    if (e.key === 'Tab') {
      if (!panel) return
      const focusable = getFocusableElements(panel)
      if (!focusable.length) {
        e.preventDefault()
        return
      }
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }
  }

  function openMenu(): void {
    previouslyFocused = document.activeElement
    btn.setAttribute('aria-expanded', 'true')
    menu.classList.remove('hidden')
    menu.setAttribute('aria-hidden', 'false')
    disableMainFocus()
    requestAnimationFrame(() => {
      if (overlay) {
        overlay.classList.remove('opacity-0')
        overlay.classList.add('opacity-100')
        overlay.classList.remove('pointer-events-none')
        overlay.classList.add('pointer-events-auto')
      }
      if (panel) {
        // Force a new frame so the browser sees the starting transform,
        // then switch classes to trigger the CSS transition.
        panel.classList.remove('translate-x-full')
        panel.classList.add('translate-x-0')
        const focusable = getFocusableElements(panel)
        if (focusable.length) focusable[0].focus()
      }
    })
    document.addEventListener('keydown', onKeyDown)
  }

  function closeMenu(): void {
    btn.setAttribute('aria-expanded', 'false')
    if (panel) {
      panel.classList.remove('translate-x-0')
      panel.classList.add('translate-x-full')
    }
    if (overlay) {
      overlay.classList.remove('opacity-100')
      overlay.classList.add('opacity-0')
      overlay.classList.remove('pointer-events-auto')
      overlay.classList.add('pointer-events-none')
    }
    menu.setAttribute('aria-hidden', 'true')
    document.removeEventListener('keydown', onKeyDown)
    setTimeout(() => {
      menu.classList.add('hidden')
      restoreMainFocus()
      if (previouslyFocused instanceof HTMLElement) previouslyFocused.focus()
    }, 220)
  }

  btn.addEventListener('click', () => {
    const expanded = btn.getAttribute('aria-expanded') === 'true'
    if (expanded) closeMenu()
    else openMenu()
  })

  if (closeBtn) closeBtn.addEventListener('click', closeMenu)
  if (overlay) overlay.addEventListener('click', closeMenu)
  if (panel)
    panel.addEventListener('click', (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (target.tagName === 'A') closeMenu()
    })
}

initMobileDrawer()
