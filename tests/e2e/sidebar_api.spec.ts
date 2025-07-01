import { test, expect } from '@playwright/test';

const getEndpoints = [
  { url: '/api/cultivation/status', key: 'data' },
  { url: '/api/achievements', key: 'achievements' },
  { url: '/api/map', key: 'data' },
  { url: '/api/quests', key: 'quests' },
  { url: '/api/intel', key: 'data' },
  { url: '/api/player/stats/detailed', key: 'data' },
];

const postEndpoints = [
  { url: '/api/cultivation/start', data: { hours: 1 }, key: 'result' },
];

test.describe('侧边栏 API 路由', () => {
  for (const ep of getEndpoints) {
    test(`GET ${ep.url}`, async ({ request }) => {
      const response = await request.get(ep.url);
      expect(response.status()).toBe(200);
      const json = await response.json();
      expect(json).toHaveProperty('success');
      expect(json).toHaveProperty(ep.key);
    });
  }

  for (const ep of postEndpoints) {
    test(`POST ${ep.url}`, async ({ request }) => {
      const response = await request.post(ep.url, { data: ep.data });
      expect(response.status()).toBe(200);
      const json = await response.json();
      expect(json).toHaveProperty('success');
      expect(json).toHaveProperty(ep.key);
    });
  }
});
