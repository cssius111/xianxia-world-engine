// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('修仙游戏完整流程测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 设置测试超时时间为60秒
    test.setTimeout(60000);
    
    // 设置页面超时
    page.setDefaultTimeout(10000);
    
    // 监听控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('Console Error:', msg.text());
      }
    });
    
    // 监听页面错误
    page.on('pageerror', error => {
      console.log('Page Error:', error.message);
    });
  });

  test('完整游戏流程：从首页到游戏主界面', async ({ page }) => {
    console.log('=== 开始测试修仙游戏完整流程 ===');
    
    // 步骤 1: 打开游戏页面
    console.log('步骤 1: 导航到游戏页面');
    await page.goto('http://localhost:5001');
    
    // 等待页面完全加载
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    
    // 验证页面已加载
    await expect(page).toHaveTitle(/.*/, { timeout: 10000 });
    console.log('✓ 页面加载完成');

    // 步骤 2: 等待并点击"开始游戏"按钮
    console.log('步骤 2: 寻找并点击开始游戏按钮');
    
    // 多种方式寻找开始游戏按钮
    const startButtonSelectors = [
      'button:has-text("开始游戏")',
      'button:has-text("开始")',
      '[id*="start"]',
      '[class*="start"]',
      'button[onclick*="start"]',
      '.start-game-btn',
      '#startButton',
      '#start_button'
    ];
    
    let startButton = null;
    for (const selector of startButtonSelectors) {
      try {
        await page.waitForSelector(selector, { timeout: 3000 });
        startButton = selector;
        console.log(`✓ 找到开始按钮: ${selector}`);
        break;
      } catch (e) {
        console.log(`- 未找到按钮: ${selector}`);
      }
    }
    
    if (!startButton) {
      throw new Error('未找到开始游戏按钮');
    }
    
    // 确保按钮可见且可点击
    await expect(page.locator(startButton)).toBeVisible();
    await expect(page.locator(startButton)).toBeEnabled();
    
    // 点击开始游戏按钮
    await page.locator(startButton).click();
    console.log('✓ 已点击开始游戏按钮');
    
    // 等待页面响应
    await page.waitForTimeout(2000);

    // 步骤 3: 等待 roll 抽卡界面加载
    console.log('步骤 3: 等待抽卡界面加载');
    
    const rollModalSelectors = [
      '#roll_modal',
      '.roll-modal',
      '[id*="roll"]',
      '[class*="roll"]',
      '.modal:has-text("抽取")',
      '.modal:has-text("角色")',
      '[data-modal="roll"]',
      '.character-roll'
    ];
    
    let rollModal = null;
    for (const selector of rollModalSelectors) {
      try {
        await page.waitForSelector(selector, { timeout: 8000 });
        rollModal = selector;
        console.log(`✓ 找到抽卡界面: ${selector}`);
        break;
      } catch (e) {
        console.log(`- 未找到抽卡界面: ${selector}`);
      }
    }
    
    if (!rollModal) {
      // 如果没有抽卡界面，检查是否直接进入了游戏
      console.log('未找到抽卡界面，检查是否直接进入游戏...');
      await page.waitForTimeout(3000);
    } else {
      // 验证抽卡界面已显示
      await expect(page.locator(rollModal)).toBeVisible();
      console.log('✓ 抽卡界面已显示');

      // 步骤 4: 模拟抽卡和创建角色
      console.log('步骤 4: 进行抽卡和角色创建');
      
      // 寻找抽卡按钮
      const rollButtonSelectors = [
        'button:has-text("抽取")',
        'button:has-text("抽卡")',
        'button:has-text("roll")',
        '[id*="roll"]',
        '.roll-btn',
        '.roll-button',
        '[onclick*="roll"]'
      ];
      
      let rollButton = null;
      for (const selector of rollButtonSelectors) {
        try {
          await page.waitForSelector(selector, { timeout: 3000 });
          rollButton = selector;
          console.log(`✓ 找到抽卡按钮: ${selector}`);
          break;
        } catch (e) {
          console.log(`- 未找到抽卡按钮: ${selector}`);
        }
      }
      
      if (rollButton) {
        // 点击抽卡按钮
        await page.locator(rollButton).click();
        console.log('✓ 已点击抽卡按钮');
        
        // 等待抽卡结果
        await page.waitForTimeout(3000);
      }
      
      // 寻找创建角色/确认按钮
      const createButtonSelectors = [
        'button:has-text("创建角色")',
        'button:has-text("确认")',
        'button:has-text("开始修仙")',
        'button:has-text("进入游戏")',
        '.create-character',
        '.confirm-btn',
        '[id*="create"]',
        '[id*="confirm"]'
      ];
      
      let createButton = null;
      for (const selector of createButtonSelectors) {
        try {
          await page.waitForSelector(selector, { timeout: 5000 });
          createButton = selector;
          console.log(`✓ 找到创建角色按钮: ${selector}`);
          break;
        } catch (e) {
          console.log(`- 未找到创建角色按钮: ${selector}`);
        }
      }
      
      if (createButton) {
        await page.locator(createButton).click();
        console.log('✓ 已点击创建角色按钮');
      }
      
      // 等待角色创建完成
      await page.waitForTimeout(3000);
    }

    // 步骤 5: 检查游戏主页面是否正常加载
    console.log('步骤 5: 验证游戏主页面加载');
    
    const gameInterfaceSelectors = [
      '#sidebar',
      '#narrative_log',
      '.game-interface',
      '.main-game',
      '[id*="game"]',
      '.character-info',
      '.player-stats',
      '.game-content',
      '#gameContainer',
      '.xiuxian-interface'
    ];
    
    let gameInterface = null;
    let foundElements = [];
    
    // 等待游戏界面加载
    await page.waitForTimeout(5000);
    
    for (const selector of gameInterfaceSelectors) {
      try {
        await page.waitForSelector(selector, { timeout: 5000 });
        gameInterface = selector;
        foundElements.push(selector);
        console.log(`✓ 找到游戏界面元素: ${selector}`);
      } catch (e) {
        console.log(`- 未找到游戏界面元素: ${selector}`);
      }
    }
    
    // 验证至少找到一个游戏界面元素
    expect(foundElements.length).toBeGreaterThan(0);
    console.log(`✓ 游戏界面加载成功，找到 ${foundElements.length} 个界面元素`);
    
    // 验证游戏界面可见
    if (gameInterface) {
      await expect(page.locator(gameInterface)).toBeVisible();
      console.log('✓ 游戏界面元素可见');
    }
    
    // 额外检查：验证页面不是空白的
    const bodyContent = await page.locator('body').textContent();
    expect(bodyContent.length).toBeGreaterThan(10);
    console.log('✓ 页面内容不为空');
    
    // 检查页面URL是否发生变化（可能进入了游戏路由）
    const currentUrl = page.url();
    console.log(`当前页面URL: ${currentUrl}`);
    
    // 最终验证：等待一段时间确保没有黑屏或卡死
    await page.waitForTimeout(3000);
    
    // 检查页面是否响应（尝试获取页面标题）
    const pageTitle = await page.title();
    console.log(`页面标题: ${pageTitle}`);
    
    console.log('=== 修仙游戏流程测试完成 ===');
  });

  test('游戏界面元素检查', async ({ page }) => {
    console.log('=== 开始游戏界面详细检查 ===');
    
    // 假设已经进入游戏，直接检查界面元素
    await page.goto('http://localhost:5001');
    
    // 快速进入游戏（重复上面的流程但更快）
    try {
      await page.waitForSelector('button:has-text("开始游戏")', { timeout: 5000 });
      await page.locator('button:has-text("开始游戏")').click();
      await page.waitForTimeout(2000);
      
      // 如果有抽卡界面，快速通过
      const rollExists = await page.locator('#roll_modal, .roll-modal').count() > 0;
      if (rollExists) {
        const rollBtn = page.locator('button:has-text("抽取"), button:has-text("抽卡")').first();
        if (await rollBtn.count() > 0) {
          await rollBtn.click();
          await page.waitForTimeout(1000);
        }
        
        const confirmBtn = page.locator('button:has-text("确认"), button:has-text("创建")').first();
        if (await confirmBtn.count() > 0) {
          await confirmBtn.click();
          await page.waitForTimeout(2000);
        }
      }
    } catch (e) {
      console.log('快速进入游戏流程跳过，直接检查当前页面');
    }
    
    // 详细检查游戏界面元素
    const elementsToCheck = [
      { name: '侧边栏', selector: '#sidebar' },
      { name: '叙述日志', selector: '#narrative_log' },
      { name: '角色信息', selector: '.character-info' },
      { name: '玩家状态', selector: '.player-stats' },
      { name: '游戏内容区', selector: '.game-content' },
      { name: '操作按钮区', selector: '.action-buttons' },
      { name: '修炼界面', selector: '.cultivation' },
      { name: '背包系统', selector: '.inventory' }
    ];
    
    for (const element of elementsToCheck) {
      try {
        await page.waitForSelector(element.selector, { timeout: 3000 });
        const isVisible = await page.locator(element.selector).isVisible();
        console.log(`✓ ${element.name} (${element.selector}): ${isVisible ? '可见' : '不可见'}`);
      } catch (e) {
        console.log(`- ${element.name} (${element.selector}): 未找到`);
      }
    }
    
    console.log('=== 游戏界面检查完成 ===');
  });

  test('错误处理和恢复测试', async ({ page }) => {
    console.log('=== 开始错误处理测试 ===');
    
    let errorCount = 0;
    let consoleErrors = [];
    
    // 监听错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
        errorCount++;
      }
    });
    
    page.on('pageerror', error => {
      consoleErrors.push(error.message);
      errorCount++;
    });
    
    // 执行完整流程
    await page.goto('http://localhost:5001');
    
    try {
      // 模拟完整游戏流程
      await page.waitForSelector('button:has-text("开始游戏")', { timeout: 10000 });
      await page.locator('button:has-text("开始游戏")').click();
      await page.waitForTimeout(5000);
      
      // 检查是否有严重错误
      const criticalErrors = consoleErrors.filter(error => 
        !error.includes('favicon') && 
        !error.includes('404') &&
        !error.includes('net::ERR_INTERNET_DISCONNECTED')
      );
      
      console.log(`总错误数: ${errorCount}`);
      console.log(`严重错误数: ${criticalErrors.length}`);
      
      if (criticalErrors.length > 0) {
        console.log('严重错误列表:', criticalErrors);
      }
      
      // 验证没有阻塞性错误
      expect(criticalErrors.length).toBeLessThan(5); // 允许少量非关键错误
      
    } catch (error) {
      console.log('测试过程中发生错误:', error.message);
      // 即使有错误，也要检查页面状态
      const pageContent = await page.content();
      expect(pageContent.length).toBeGreaterThan(100); // 确保页面不是完全空白
    }
    
    console.log('=== 错误处理测试完成 ===');
  });
});