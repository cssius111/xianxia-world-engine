import { test, expect } from '@playwright/test';

// 角色重新投掷直到进入游戏主界面的测试

test('character reroll flow', async ({ page }) => {
  // 访问首页
  await page.goto('/');

  // 检查首页按钮文本
  await expect(page.locator('text=开始游戏')).toBeVisible();
  await expect(page.locator('text=继续游戏')).toBeVisible();
  const devBtn = page.locator('text=/开发者(模式|入口)/');
  if (await devBtn.count()) {
    await expect(devBtn).toBeVisible();
  }
  await expect(page.locator('text=设置')).toBeVisible();

  // 打开并验证设置模态框
  await page.locator('text=设置').click();
  await expect(page.locator('#modal')).toBeVisible();
  await expect(page.locator('#modal-content')).toContainText('游戏设置');
  await page.evaluate(() => { (window as any).closeModal(); });

  // 开始游戏
  await page.locator('text=开始游戏').first().click();
  await page.waitForURL('**/game');

  // 欢迎界面开始游戏
  const welcomeStart = page.locator('#welcomeModal button:has-text("开始游戏")');
  if (await welcomeStart.isVisible()) {
    await welcomeStart.click();
  }

  // 等待角色创建面板
  const rollModal = page.locator('#rollModal');
  await expect(rollModal).toBeVisible();

  // 重新投掷一次并确认
  const rerollBtn = rollModal.locator('button:has-text("随机生成"), button:has-text("重新投掷")');
  if (await rerollBtn.isVisible()) {
    await rerollBtn.click();
  }
  await rollModal.locator('button:has-text("确认创建"), button:has-text("踏入此界")').click();

  // 等待进入游戏主界面
  await expect(rollModal).toBeHidden();
  await expect(page.locator('#gameContainer')).toBeVisible();
});
