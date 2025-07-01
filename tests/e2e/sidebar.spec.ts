import { test, expect } from '@playwright/test';

const sidebarItems = [
  { text: '查看状态', panel: '#statusPanel' },
  { text: '背包', panel: '#inventoryPanel' },
  { text: '修炼', panel: '#cultivationPanel' },
  { text: '成就', panel: '#achievementsPanel' },
  { text: '探索', panel: '#explorePanel' },
  { text: '地图', panel: '#mapPanel' },
  { text: '任务', panel: '#questsPanel' },
  { text: '情报', panel: '#intelPanel' },
  { text: '保存/加载', panel: '#saveLoadPanel' },
  { text: '帮助', panel: '#helpPanel' },
];

// Utility to close current panel
async function closePanel(page) {
  const overlay = page.locator('#panelOverlay');
  if (await overlay.isVisible()) {
    await overlay.click({ position: { x: 5, y: 5 } });
    await expect(overlay).toBeHidden();
  }
}

test.describe('Sidebar functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5001/game');
    await page.waitForSelector('#sidebar');
  });

  for (const item of sidebarItems) {
    test(`open ${item.text} panel`, async ({ page }) => {
      await page.locator(`.game-sidebar a:has-text("${item.text}")`).click();
      await expect(page.locator('#panelOverlay')).toBeVisible();
      await expect(page.locator(item.panel)).toBeVisible();
      await closePanel(page);
    });
  }
});
