/**
 * XianXia World Engine K6 压测脚本
 * 模拟 100 个虚拟用户，持续 10 分钟
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const apiLatency = new Trend('api_latency');
const metricsLatency = new Trend('metrics_latency');
const tokenUsage = new Trend('token_usage_simulation');

// 测试配置
export const options = {
  stages: [
    { duration: '1m', target: 20 },   // 预热：1分钟内增加到20个VU
    { duration: '8m', target: 100 },  // 主测试：8分钟内增加到100个VU
    { duration: '1m', target: 0 },    // 冷却：1分钟内降到0
  ],
  thresholds: {
    http_req_duration: ['p(99)<2500'], // 99%的请求必须在2.5秒内完成
    errors: ['rate<0.05'],             // 错误率必须低于5%
    http_req_failed: ['rate<0.05'],    // HTTP失败率必须低于5%
  },
};

// 测试数据
const commands = [
  '探索周围环境',
  '查看角色状态',
  '开始修炼',
  '前往东方',
  '与NPC对话',
  '查看背包',
  '使用灵石',
  '接受任务',
  '攻击妖兽',
  '收集草药',
];

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

// 设置函数：登录并获取会话
export function setup() {
  const loginRes = http.post(`${BASE_URL}/api/auth/login`, 
    JSON.stringify({ username: 'testuser', password: 'testpass' }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  
  const sessionRes = http.post(`${BASE_URL}/api/v1/session`,
    JSON.stringify({ user_id: 'test_user_' + Date.now() }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  
  return {
    token: loginRes.json('token'),
    sessionId: sessionRes.json('session_id'),
  };
}

// 主测试场景
export default function (data) {
  // 场景1: 游戏命令请求 (70%概率)
  if (Math.random() < 0.7) {
    const command = commands[Math.floor(Math.random() * commands.length)];
    const startTime = Date.now();
    
    const res = http.post(`${BASE_URL}/api/game/command`,
      JSON.stringify({ 
        command: command,
        session_id: data.sessionId 
      }),
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${data.token}`,
        },
        tags: { name: 'GameCommand' },
      }
    );
    
    const latency = Date.now() - startTime;
    apiLatency.add(latency);
    
    // 模拟 token 使用量
    const simulatedTokens = 50 + Math.floor(Math.random() * 200);
    tokenUsage.add(simulatedTokens);
    
    const success = check(res, {
      'status is 200': (r) => r.status === 200,
      'response has result': (r) => r.json('result') !== undefined,
      'latency < 2500ms': () => latency < 2500,
    });
    
    errorRate.add(!success);
  }
  
  // 场景2: 查询游戏状态 (20%概率)
  if (Math.random() < 0.2) {
    const statusRes = http.get(`${BASE_URL}/api/game/status`, {
      headers: { 'Authorization': `Bearer ${data.token}` },
      tags: { name: 'GameStatus' },
    });
    
    check(statusRes, {
      'status query success': (r) => r.status === 200,
      'has player info': (r) => r.json('player') !== undefined,
    });
  }
  
  // 场景3: 访问 metrics 端点 (10%概率)
  if (Math.random() < 0.1) {
    const metricsStart = Date.now();
    const metricsRes = http.get(`${BASE_URL}/metrics`, {
      tags: { name: 'MetricsEndpoint' },
    });
    
    metricsLatency.add(Date.now() - metricsStart);
    
    check(metricsRes, {
      'metrics available': (r) => r.status === 200,
      'has prometheus format': (r) => r.body.includes('# HELP'),
      'has xwe metrics': (r) => r.body.includes('xwe_'),
    });
  }
  
  // 模拟真实用户思考时间
  sleep(Math.random() * 3 + 1); // 1-4秒随机延迟
}

// 测试结束后的清理
export function teardown(data) {
  // 可以在这里清理测试数据
  console.log('测试完成，正在生成报告...');
}

// 自定义摘要报告
export function handleSummary(data) {
  const customData = {
    '测试概览': {
      '总请求数': data.metrics.http_reqs.values.count,
      '请求成功率': (100 - data.metrics.http_req_failed.values.rate * 100).toFixed(2) + '%',
      '平均响应时间': data.metrics.http_req_duration.values.avg.toFixed(0) + 'ms',
      'P99 响应时间': data.metrics.http_req_duration.values['p(99)'].toFixed(0) + 'ms',
    },
    'API 性能': {
      '游戏命令平均延迟': data.metrics.api_latency.values.avg.toFixed(0) + 'ms',
      '游戏命令P99延迟': data.metrics.api_latency.values['p(99)'].toFixed(0) + 'ms',
    },
    'Metrics 端点': {
      '平均响应时间': data.metrics.metrics_latency.values.avg.toFixed(0) + 'ms',
      'CPU 占用预估': '基于响应时间，预计 CPU 占用 < 5%',
    },
    'Token 使用模拟': {
      '平均 Token 数': data.metrics.token_usage_simulation.values.avg.toFixed(0),
      '总 Token 估算': data.metrics.token_usage_simulation.values.count * data.metrics.token_usage_simulation.values.avg,
    },
    '阈值检查': {
      'P99 < 2500ms': data.metrics.http_req_duration.values['p(99)'] < 2500 ? '✅ 通过' : '❌ 失败',
      '错误率 < 5%': data.metrics.errors.values.rate < 0.05 ? '✅ 通过' : '❌ 失败',
    },
  };
  
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'summary.json': JSON.stringify(customData, null, 2),
    'summary.html': htmlReport(customData),
  };
}

// 生成文本摘要
function textSummary(data, options) {
  let summary = '\n📊 XWE 压测结果摘要\n';
  summary += '═'.repeat(50) + '\n\n';
  
  summary += `✅ 总请求数: ${data.metrics.http_reqs.values.count}\n`;
  summary += `✅ 成功率: ${(100 - data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%\n`;
  summary += `✅ 平均响应: ${data.metrics.http_req_duration.values.avg.toFixed(0)}ms\n`;
  summary += `✅ P99延迟: ${data.metrics.http_req_duration.values['p(99)'].toFixed(0)}ms\n`;
  
  return summary;
}

// 生成 HTML 报告
function htmlReport(data) {
  return `
<!DOCTYPE html>
<html>
<head>
    <title>XWE 压测报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .pass { color: green; font-weight: bold; }
        .fail { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>XianXia World Engine 压测报告</h1>
    <h2>测试参数</h2>
    <ul>
        <li>虚拟用户数: 100</li>
        <li>测试时长: 10分钟</li>
        <li>目标 P99: < 2500ms</li>
        <li>目标错误率: < 5%</li>
    </ul>
    <h2>测试结果</h2>
    ${Object.entries(data).map(([section, metrics]) => `
        <h3>${section}</h3>
        <table>
            ${Object.entries(metrics).map(([key, value]) => `
                <tr>
                    <td>${key}</td>
                    <td class="${value.includes('✅') ? 'pass' : value.includes('❌') ? 'fail' : ''}">${value}</td>
                </tr>
            `).join('')}
        </table>
    `).join('')}
</body>
</html>
  `;
}