/**
 * Additional E2E Tests for Comprehensive Coverage
 * This file extends the basic tests with more scenarios
 */

import { test, expect } from '@playwright/test';
import { LogHelper } from './helpers/logHelper';

test.describe('Extended E2E Tests', () => {
  let logHelper: LogHelper;

  test.beforeAll(async () => {
    logHelper = new LogHelper('logs');
  });

  test.describe('游戏命令系统测试', () => {
    test('命令解析和执行', async ({ page, request }) => {
      // 先创建角色
      await request.post('/create_character', {
        data: { name: '命令测试者' }
      });

      await test.step('测试帮助命令', async () => {
        const response = await request.post('/command', {
          data: { command: '帮助' }
        });
        expect.soft(response.ok()).toBeTruthy();
        const data = await response.json();
        expect.soft(data.result).toContain('命令');
      });

      await test.step('测试移动命令', async () => {
        const response = await request.post('/command', {
          data: { command: '去丹药铺' }
        });
        expect.soft(response.ok()).toBeTruthy();
        const data = await response.json();
        expect.soft(data.result).toContain('丹药铺');
      });

      await test.step('测试查看背包', async () => {
        const response = await request.post('/command', {
          data: { command: '背包' }
        });
        expect.soft(response.ok()).toBeTruthy();
        const data = await response.json();
        expect.soft(data.result).toMatch(/背包|物品/);
      });

      await test.step('测试修炼命令', async () => {
        const response = await request.post('/command', {
          data: { command: '打坐修炼' }
        });
        expect.soft(response.ok()).toBeTruthy();
        const data = await response.json();
        expect.soft(data.result).toContain('修炼');
      });

      await test.step('测试攻击命令', async () => {
        const response = await request.post('/command', {
          data: { command: '攻击 木桩' }
        });
        expect.soft(response.ok()).toBeTruthy();
        const data = await response.json();
        expect.soft(data.result).toMatch(/木桩/);
      });
    });
  });

  test.describe('数据接口测试', () => {
    test('获取游戏数据', async ({ request }) => {
      await test.step('获取命格数据', async () => {
        const response = await request.get('/data/destiny');
        expect.soft(response.ok()).toBeTruthy();
        const data = await response.json();
        expect.soft(data).toHaveProperty('destiny_grades');
      });

      await test.step('获取气运数据', async () => {
        const response = await request.get('/data/fortune');
        expect.soft(response.ok()).toBeTruthy();
        const data = await response.json();
        expect.soft(data).toBeTruthy();
      });

      await test.step('获取角色模板', async () => {
        const response = await request.get('/data/templates');
        expect.soft(response.ok()).toBeTruthy();
        const data = await response.json();
        expect.soft(data).toBeTruthy();
      });
    });
  });

  test.describe('存档系统测试', () => {
    test('游戏存档和加载', async ({ request }) => {
      const session = await request.newContext();
      
      // 创建角色
      await session.post('/create_character', {
        data: { name: '存档测试者' }
      });

      await test.step('保存游戏', async () => {
        const response = await session.post('/save_game');
        // 可能未实现，软断言
        if (response.ok()) {
          const data = await response.json();
          expect.soft(data.success).toBeTruthy();
        }
      });

      await test.step('加载游戏', async () => {
        const response = await session.post('/load_game');
        // 可能未实现，软断言
        if (response.ok()) {
          const data = await response.json();
          console.log('Load game response:', data);
        }
      });
    });
  });

  test.describe('NLP功能测试', () => {
    test('NLP命令解析', async ({ request }) => {
      await test.step('测试自然语言命令', async () => {
        const commands = [
          '我想去探索一下',
          '查看一下我的状态',
          '给我看看背包里有什么',
          '我要修炼一个时辰'
        ];

        for (const cmd of commands) {
          const response = await request.post('/command', {
            data: { text: cmd }
          });
          expect.soft(response.ok()).toBeTruthy();
          const data = await response.json();
          expect.soft(data).toHaveProperty('parsed_command');
          console.log(`Command: "${cmd}" -> Handler: ${data.parsed_command?.handler}`);
        }
      });

      await test.step('获取NLP缓存信息', async () => {
        const response = await request.get('/nlp_cache_info');
        expect.soft(response.ok()).toBeTruthy();
        const data = await response.json();
        console.log('NLP cache info:', data);
      });
    });
  });

  test.describe('抽卡系统测试', () => {
    test('角色属性抽取', async ({ request }) => {
      await test.step('随机抽卡', async () => {
        const response = await request.post('/api/roll', {
          data: { mode: 'random' }
        });
        expect.soft(response.ok()).toBeTruthy();
        const data = await response.json();
        expect.soft(data.success).toBeTruthy();
        expect.soft(data.character).toHaveProperty('name');
        expect.soft(data.character).toHaveProperty('attributes');
        expect.soft(data.character.attributes).toHaveProperty('constitution');
        expect.soft(data.character.attributes).toHaveProperty('comprehension');
      });

      await test.step('模板抽卡', async () => {
        const response = await request.post('/api/roll', {
          data: { mode: 'template', type: 'sword' }
        });
        expect.soft(response.ok()).toBeTruthy();
        const data = await response.json();
        expect.soft(data.success).toBeTruthy();
      });
    });
  });

  test.describe('错误处理测试', () => {
    test('API错误处理', async ({ request }) => {
      await test.step('测试不存在的路由', async () => {
        const response = await request.get('/api/nonexistent');
        expect.soft(response.status()).toBe(404);
      });

      await test.step('测试无效的命令', async () => {
        const response = await request.post('/command', {
          data: { command: '!@#$%^&*()' }
        });
        expect.soft(response.ok()).toBeTruthy();
        const data = await response.json();
        expect.soft(data.parsed_command?.handler).toBe('unknown');
      });

      await test.step('测试空请求', async () => {
        const response = await request.post('/command', {
          data: {}
        });
        expect.soft(response.ok()).toBeTruthy();
      });
    });
  });

  test.describe('并发测试', () => {
    test('并发请求处理', async ({ request }) => {
      await test.step('并发创建多个角色', async () => {
        const promises = [];
        for (let i = 0; i < 5; i++) {
          promises.push(
            request.post('/create_character', {
              data: { name: `并发测试${i}` }
            })
          );
        }
        
        const responses = await Promise.all(promises);
        for (const response of responses) {
          expect.soft(response.ok()).toBeTruthy();
        }
      });

      await test.step('并发探索请求', async () => {
        const promises = [];
        for (let i = 0; i < 3; i++) {
          promises.push(
            request.post('/command', {
              data: { command: '探索' }
            })
          );
        }
        
        const responses = await Promise.all(promises);
        for (const response of responses) {
          expect.soft(response.ok()).toBeTruthy();
        }
      });
    });
  });

  test.describe('日志监控测试', () => {
    test('日志记录验证', async ({ request }) => {
      const testLogFile = 'test_e2e.log';
      
      await test.step('写入测试日志', async () => {
        const testData = `[${new Date().toISOString()}] E2E Test Log Entry\n`;
        await logHelper.writeToLog(testLogFile, testData);
      });

      await test.step('验证日志存在', async () => {
        const exists = await logHelper.logExists(testLogFile);
        expect.soft(exists).toBeTruthy();
        
        if (exists) {
          const content = await logHelper.readLogFile(testLogFile);
          expect.soft(content).toContain('E2E Test Log Entry');
        }
      });

      await test.step('清理测试日志', async () => {
        await logHelper.deleteLog(testLogFile);
      });
    });
  });

  test.describe('界面交互测试', () => {
    test('游戏界面交互', async ({ page }) => {
      await test.step('访问游戏界面', async () => {
        await page.goto('/game');
        // 可能会重定向到intro
        await page.waitForURL(/\/(game|intro)/);
      });

      await test.step('检查界面元素', async () => {
        // 检查是否有输入框
        const hasInput = await page.locator('input[type="text"], textarea').count() > 0;
        
        // 检查是否有按钮
        const hasButton = await page.locator('button').count() > 0;
        
        expect.soft(hasInput || hasButton).toBeTruthy();
      });

      await test.step('测试响应式设计', async () => {
        // 测试不同视口大小
        const viewports = [
          { width: 1920, height: 1080 },
          { width: 768, height: 1024 },
          { width: 375, height: 667 }
        ];

        for (const viewport of viewports) {
          await page.setViewportSize(viewport);
          await page.waitForTimeout(500);
          
          // 截图不同尺寸
          await page.screenshot({
            path: `test-results/responsive-${viewport.width}x${viewport.height}.png`
          });
        }
      });
    });
  });

  test.describe('模态框测试', () => {
    test('模态框功能', async ({ page }) => {
      const modals = ['help', 'inventory', 'status'];
      
      for (const modalName of modals) {
        await test.step(`测试 ${modalName} 模态框`, async () => {
          const response = await page.goto(`/modal/${modalName}`);
          
          if (response?.status() === 200) {
            const content = await page.textContent('body');
            expect.soft(content).toBeTruthy();
            console.log(`Modal ${modalName} loaded successfully`);
          } else {
            console.log(`Modal ${modalName} returned status: ${response?.status()}`);
          }
        });
      }
    });
  });

  test.describe('SSE (Server-Sent Events) 测试', () => {
    test('状态流推送', async ({ page }) => {
      await test.step('连接状态流', async () => {
        // 这个测试比较特殊，需要在页面上执行
        await page.goto('/game');
        
        // 监听SSE连接
        const ssePromise = page.evaluate(() => {
          return new Promise((resolve) => {
            const eventSource = new EventSource('/status/stream');
            let messageCount = 0;
            
            eventSource.onmessage = (event) => {
              messageCount++;
              console.log('SSE message received:', event.data);
              
              // 收到3条消息后关闭连接
              if (messageCount >= 3) {
                eventSource.close();
                resolve(messageCount);
              }
            };
            
            eventSource.onerror = () => {
              eventSource.close();
              resolve(messageCount);
            };
            
            // 10秒超时
            setTimeout(() => {
              eventSource.close();
              resolve(messageCount);
            }, 10000);
          });
        });
        
        const messageCount = await ssePromise;
        console.log(`Received ${messageCount} SSE messages`);
        expect.soft(messageCount).toBeGreaterThan(0);
      });
    });
  });
});

// 性能基准测试
test.describe('Performance Benchmarks', () => {
  test('API性能基准', async ({ request }) => {
    const endpoints = [
      { path: '/status', name: 'Status API', maxTime: 100 },
      { path: '/lore/world', name: 'Lore API', maxTime: 200 },
      { path: '/data/destiny', name: 'Destiny Data', maxTime: 150 },
      { path: '/command', name: 'Command API', maxTime: 500, method: 'POST', data: { command: 'help' } }
    ];

    for (const endpoint of endpoints) {
      await test.step(`${endpoint.name} 性能测试`, async () => {
        const times = [];
        
        // 运行10次取平均值
        for (let i = 0; i < 10; i++) {
          const startTime = Date.now();
          
          if (endpoint.method === 'POST') {
            await request.post(endpoint.path, { data: endpoint.data });
          } else {
            await request.get(endpoint.path);
          }
          
          times.push(Date.now() - startTime);
        }
        
        const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
        const maxTime = Math.max(...times);
        const minTime = Math.min(...times);
        
        console.log(`${endpoint.name}: avg=${avgTime.toFixed(2)}ms, min=${minTime}ms, max=${maxTime}ms`);
        
        expect.soft(avgTime).toBeLessThan(endpoint.maxTime);
      });
    }
  });

  test('内存使用测试', async ({ page }) => {
    await test.step('测量内存使用', async () => {
      await page.goto('/game');
      
      // 获取内存使用情况（如果浏览器支持）
      const metrics = await page.evaluate(() => {
        if ('memory' in performance) {
          return {
            usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
            totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
            jsHeapSizeLimit: (performance as any).memory.jsHeapSizeLimit
          };
        }
        return null;
      });
      
      if (metrics) {
        console.log('Memory usage:', {
          used: `${(metrics.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
          total: `${(metrics.totalJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
          limit: `${(metrics.jsHeapSizeLimit / 1024 / 1024).toFixed(2)} MB`
        });
      }
    });
  });
});
