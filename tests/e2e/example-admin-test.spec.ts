/**
 * 示例：如何使用自定义的 adminRequest fixture
 */

import { test, expect } from './fixtures/adminRequest';

test.describe('使用自定义 fixture 的测试', () => {
  test('调用管理员 API', async ({ adminRequest }) => {
    // adminRequest 已经配置好了 baseURL 和 headers
    const response = await adminRequest.post('/api/explore_async', {
      data: { location: '青云城' }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('Response:', data);
  });

  test('多个 API 调用', async ({ adminRequest }) => {
    // 创建角色
    const createResponse = await adminRequest.post('/create_character', {
      data: { name: '测试道友' }
    });
    expect(createResponse.ok()).toBeTruthy();

    // 执行命令
    const commandResponse = await adminRequest.post('/command', {
      data: { command: '探索' }
    });
    expect(commandResponse.ok()).toBeTruthy();

    // 获取状态
    const statusResponse = await adminRequest.get('/status');
    expect(statusResponse.ok()).toBeTruthy();
  });
});

// 你也可以混合使用默认的 request fixture 和自定义的 adminRequest
test('混合使用 fixtures', async ({ request, adminRequest }) => {
  // 使用默认的 request fixture（没有额外配置）
  const publicResponse = await request.get('http://localhost:5001/lore/world');
  
  // 使用自定义的 adminRequest fixture（带有管理员配置）
  const adminResponse = await adminRequest.post('/admin/api/endpoint');
  
  expect(publicResponse.ok()).toBeTruthy();
  // adminResponse 可能会失败，如果端点不存在
});
