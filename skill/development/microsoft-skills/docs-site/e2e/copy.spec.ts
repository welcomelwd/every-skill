import { test, expect } from '@playwright/test';

test.describe('Copy to Clipboard', () => {
  test.beforeEach(async ({ page, context }) => {
    await context.grantPermissions(['clipboard-read', 'clipboard-write']);
    await page.goto('./');
    await page.waitForLoadState('networkidle');
  });

  test('copy button is visible on skill cards', async ({ page }) => {
    const skillCard = page.locator('.skills-grid > div').first();
    await skillCard.waitFor({ state: 'visible', timeout: 10000 });

    await skillCard.hover();

    const copyButton = skillCard.locator('button:has-text("Copy")');
    await expect(copyButton).toBeVisible();
  });

  test('clicking copy button shows success feedback', async ({ page }) => {
    const skillCard = page.locator('.skills-grid > div').first();
    await skillCard.waitFor({ state: 'visible', timeout: 10000 });
    await skillCard.hover();

    const copyButton = skillCard.locator('button:has-text("Copy")');
    await expect(copyButton).toBeVisible();
    await copyButton.click();

    const copiedButton = skillCard.locator('button:has-text("Copied!")');
    await expect(copiedButton).toBeVisible({ timeout: 3000 });
  });

  const commandCases = [
    { source: 'direct', name: 'mcp-builder', command: 'npx skills add microsoft/skills --skill mcp-builder' },
    { source: 'azure-skills plugin', name: 'microsoft-foundry', command: 'npx skills add microsoft/azure-skills --skill microsoft-foundry' },
    { source: 'generic plugin', name: 'azure-ai-projects-py', command: 'npx skills add https://github.com/microsoft/skills/tree/main/.github/plugins/azure-sdk-python/skills/azure-ai-projects-py' },
  ];

  for (const { source, name, command } of commandCases) {
    test(`copy button has exact install command for ${source} skill (${name})`, async ({ page }) => {
      await page.getByTestId('search-input').fill(name);
      const skillCard = page.locator('.skills-grid > div').filter({
        has: page.getByRole('heading', { level: 3, name, exact: true }),
      });
      await skillCard.waitFor({ state: 'visible', timeout: 10000 });

      const copyButton = skillCard.getByRole('button', { name: 'Copy' });
      await expect(copyButton).toHaveAttribute('title', `Copy: ${command}`);
    });
  }
});
