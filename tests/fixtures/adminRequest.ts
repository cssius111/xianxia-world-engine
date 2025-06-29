import { test as base, APIRequestContext, request } from '@playwright/test';

// 定义自定义 fixtures 的类型
type AdminFixtures = {
  adminRequest: APIRequestContext;
};

// 扩展基础的 test 对象，添加自定义 fixture
export const test = base.extend<AdminFixtures>({
  adminRequest: async ({}, use) => {
    // 创建带有管理员权限的 API context
    const ctx = await request.newContext({
      baseURL: process.env.BASE_URL || 'http://localhost:5001',
      extraHTTPHeaders: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        // 如果需要绕过 CSRF 或添加认证令牌，在这里添加
        // 'X-CSRF-Token': 'bypass',
        // 'Authorization': 'Bearer admin-token',
      },
      // 其他配置选项
      timeout: 30000,
      ignoreHTTPSErrors: true,
    });

    // 使用 context
    await use(ctx);

    // 清理
    await ctx.dispose();
  },
});

// 导出 expect 以便在测试中使用
export { expect } from '@playwright/test';
