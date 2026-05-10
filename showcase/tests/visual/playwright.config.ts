import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright config for OutfitKit visual regression tests.
 *
 * Two viewports (projects) are exercised against the deployed showcase:
 *   - desktop: 1280x800
 *   - mobile:  390x844
 *
 * Baselines live next to the spec under `__screenshots__/` and are
 * committed to git. First-run mode auto-creates a missing baseline.
 */
export default defineConfig({
  testDir: '.',
  testMatch: /.*\.spec\.ts$/,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['list'],
  ],
  outputDir: 'test-results',
  // Custom snapshot path so baselines collapse into a single
  // dir per project instead of being scattered next to each test name.
  snapshotPathTemplate:
    '{testDir}/__screenshots__/{projectName}/{arg}{ext}',
  expect: {
    // Generous threshold — we want to catch visual regressions, not
    // flag every sub-pixel anti-aliasing difference.
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.05,
      threshold: 0.1,
      animations: 'disabled',
      caret: 'hide',
      scale: 'css',
    },
  },
  use: {
    baseURL:
      process.env.OUTFITKIT_BASE_URL ?? 'https://outfitkit.github.io/outfitkit',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    ignoreHTTPSErrors: true,
  },
  projects: [
    {
      name: 'desktop',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 800 },
        deviceScaleFactor: 1,
      },
    },
    {
      name: 'mobile',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 390, height: 844 },
        deviceScaleFactor: 1,
        isMobile: false,
        hasTouch: true,
      },
    },
  ],
});
