import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:5010';

// Utility to enable dev mode within page context
async function enableDevMode(page) {
  await page.goto(`${BASE_URL}/`);
  await page.evaluate(async () => {
    await fetch('/dev_login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: 'test' })
    });
  });
}

test('root shows welcome modal only', async ({ page }) => {
  const resp = await page.goto(`${BASE_URL}/`);
  expect(resp?.status()).toBe(200);
  await expect(page.locator('#welcomeModal')).toBeVisible();
  await expect(page.locator('text=诊断工具')).toHaveCount(0);
});

test('dev dashboard after login', async ({ page }) => {
  await enableDevMode(page);
  await page.goto(`${BASE_URL}/dev_dashboard`);
  await expect(page.locator('text=诊断工具')).toBeVisible();
});
