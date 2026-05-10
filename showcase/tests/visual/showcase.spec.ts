import { test, expect, Page } from '@playwright/test';

/**
 * Visual regression suite for the OutfitKit showcase.
 *
 * Each entry in PAGES becomes one test per project (desktop + mobile).
 * Baselines auto-create on first run and are stored under
 * __screenshots__/<project>/<slug>.png. Diffs land in test-results/.
 */
const PAGES = [
  // Components — most-used and recently-fixed
  '/components/button.html',
  '/components/card.html',
  '/components/datatable.html',
  '/components/modal.html',
  '/components/drawer.html',
  '/components/sidebar_nav.html',
  '/components/topbar.html',
  '/components/tabbar.html',
  '/components/app_shell.html',
  '/components/tree.html',
  '/components/calendar.html',
  '/components/kanban.html',
  '/components/pos.html',
  // Apps — one per major section
  '/apps/dashboard/saas.html',
  '/apps/dashboard/hub.html',
  '/apps/employees/list.html',
  '/apps/hubs/active.html',
  '/apps/billing/invoices.html',
  '/apps/marketplace/saas-shop.html',
  '/apps/marketplace/saas-checkout.html',
  '/apps/system/index.html',
  '/apps/auth/login-saas.html',
  '/apps/profile/saas.html',
  '/apps/settings/preferences.html',
];

/**
 * Convert a page path to a slug for the screenshot filename.
 *   /components/button.html        -> components-button
 *   /apps/marketplace/saas-shop.html -> apps-marketplace-saas-shop
 */
function pageSlug(path: string): string {
  return path
    .replace(/\.html$/, '')
    .replace(/^\//, '')
    .replace(/\//g, '-');
}

/**
 * Prep the page so screenshots are deterministic:
 *   - clear localStorage so theme defaults apply
 *   - wait for DOM
 *   - wait for Iconify lazy-loaded icons (CDN, async)
 *   - disable CSS animations / transitions
 */
async function prepare(page: Page, path: string): Promise<void> {
  // Clear any persisted theme/preferences before the real navigation
  // by hitting the origin once to gain access to localStorage.
  await page.goto(path, { waitUntil: 'domcontentloaded' });
  await page.evaluate(() => {
    try {
      localStorage.clear();
      sessionStorage.clear();
    } catch (_) {
      /* opaque origin in some test runners — safe to ignore */
    }
  });

  // Reload so the page boots with a clean storage state.
  await page.goto(path, { waitUntil: 'domcontentloaded' });

  // Iconify icons are injected asynchronously from CDN.
  await page.waitForTimeout(1500);

  // Kill animations so frame timing doesn't cause flaky diffs.
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
        scroll-behavior: auto !important;
      }
    `,
  });

  // Best-effort: wait for fonts so first-paint glyph metrics are stable.
  await page.evaluate(async () => {
    if (document.fonts && document.fonts.ready) {
      await document.fonts.ready;
    }
  });
}

for (const path of PAGES) {
  const slug = pageSlug(path);
  test(`visual: ${slug}`, async ({ page }) => {
    await prepare(page, path);

    // fullPage: false — capture only the viewport. Apps under /apps/* are
    // shown inside an iframe of the showcase shell, and capturing the
    // outer page is exactly what the user sees.
    await expect(page).toHaveScreenshot(`${slug}.png`, {
      fullPage: false,
      maxDiffPixelRatio: 0.05,
    });
  });
}
