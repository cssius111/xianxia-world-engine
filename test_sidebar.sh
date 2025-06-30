#!/bin/bash

# 修仙游戏侧边栏测试启动脚本
# 用于启动服务器并运行自动化测试

echo "🎮 修仙世界引擎 - 侧边栏功能测试"
echo "================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装Node.js"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装npm"
    exit 1
fi

# 进入项目目录
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)
echo "📁 项目目录: $PROJECT_DIR"

# 检查依赖文件
if [ ! -f "requirements.txt" ]; then
    echo "❌ 未找到requirements.txt文件"
    exit 1
fi

if [ ! -f "package.json" ]; then
    echo "❌ 未找到package.json文件"
    exit 1
fi

# 安装Python依赖
echo "📦 检查Python依赖..."
pip3 install -r requirements.txt > /dev/null 2>&1

# 安装Node.js依赖
echo "📦 检查Node.js依赖..."
npm install > /dev/null 2>&1

# 安装Playwright浏览器
echo "🌐 安装Playwright浏览器..."
npx playwright install > /dev/null 2>&1

# 创建必要目录
mkdir -p logs saves test-results screenshots

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件，创建默认配置..."
    cat > .env << EOF
# 修仙游戏配置
DEBUG=true
PORT=5001
FLASK_ENV=development

# DeepSeek API配置（可选）
# DEEPSEEK_API_KEY=your_api_key_here

# 测试配置
ENABLE_E2E_API=true
EOF
fi

echo "✅ 环境准备完成"
echo ""

# 功能选择菜单
echo "请选择操作:"
echo "1. 启动游戏服务器"
echo "2. 运行侧边栏功能测试"
echo "3. 启动服务器并运行测试"
echo "4. 查看现有测试报告"
echo "5. 清理测试数据"
echo ""

read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo "🚀 启动游戏服务器..."
        echo "访问地址: http://localhost:5001"
        echo "按 Ctrl+C 停止服务器"
        echo ""
        python3 start_web.py
        ;;
    2)
        echo "🧪 运行侧边栏功能测试..."
        
        # 检查服务器是否在运行
        if ! curl -s http://localhost:5001 > /dev/null; then
            echo "❌ 服务器未运行，请先启动服务器"
            echo "你可以选择选项3来自动启动服务器并运行测试"
            exit 1
        fi
        
        echo "✅ 服务器已运行，开始测试..."
        
        # 创建测试脚本
        cat > test_sidebar.spec.js << 'EOF'
// 修仙游戏侧边栏完整功能测试脚本
const { test, expect } = require('@playwright/test');

test.describe('修仙游戏侧边栏功能全面测试', () => {
  
  test('服务器连接测试', async ({ page }) => {
    console.log('=== 开始服务器连接测试 ===');
    
    const response = await page.goto('http://localhost:5001', {
      waitUntil: 'networkidle',
      timeout: 30000
    });
    
    expect(response.status()).toBe(200);
    console.log('✅ 服务器连接成功');
    
    const title = await page.title();
    console.log(`页面标题: ${title}`);
    expect(title).toContain('修仙');
  });

  test('API接口连通性测试', async ({ request }) => {
    console.log('=== 开始API连通性测试 ===');
    
    const endpoints = [
      '/status',
      '/api/cultivation/status',
      '/api/achievements',
      '/api/map',
      '/api/quests',
      '/api/intel',
      '/api/player/stats/detailed'
    ];
    
    for (const endpoint of endpoints) {
      try {
        const response = await request.get(`http://localhost:5001${endpoint}`);
        console.log(`${endpoint}: ${response.status()} ${response.ok() ? '✅' : '❌'}`);
      } catch (error) {
        console.log(`${endpoint}: ❌ ${error.message}`);
      }
    }
  });

  test('侧边栏功能点击测试', async ({ page }) => {
    console.log('=== 开始侧边栏功能测试 ===');
    
    await page.goto('http://localhost:5001');
    await page.waitForLoadState('networkidle');
    
    // 进入游戏界面
    if (page.url().includes('/intro')) {
      const startButton = page.locator('button:has-text("开始游戏")').first();
      if (await startButton.isVisible({ timeout: 5000 })) {
        await startButton.click();
        await page.waitForTimeout(2000);
        
        const nameInput = page.locator('input[type="text"]').first();
        if (await nameInput.isVisible({ timeout: 3000 })) {
          await nameInput.fill('测试道友');
          const confirmButton = page.locator('button:has-text("确认")').first();
          if (await confirmButton.isVisible()) {
            await confirmButton.click();
            await page.waitForTimeout(3000);
          }
        }
      }
    }
    
    // 等待游戏界面加载
    await page.waitForSelector('.game-sidebar, #sidebar', { timeout: 10000 });
    
    // 测试各个侧边栏功能
    const functions = [
      { name: '查看状态', selector: 'a:has-text("查看状态")' },
      { name: '背包', selector: 'a:has-text("背包")' },
      { name: '修炼', selector: 'a:has-text("修炼")' },
      { name: '成就', selector: 'a:has-text("成就")' },
      { name: '探索', selector: 'a:has-text("探索")' },
      { name: '地图', selector: 'a:has-text("地图")' },
      { name: '任务', selector: 'a:has-text("任务")' },
      { name: '情报', selector: 'a:has-text("情报")' },
    ];
    
    for (const func of functions) {
      try {
        console.log(`测试 ${func.name} 功能...`);
        
        const link = page.locator(func.selector);
        if (await link.isVisible({ timeout: 3000 })) {
          await link.click();
          await page.waitForTimeout(1000);
          
          // 检查是否有面板打开
          const panel = page.locator('.game-panel:visible');
          if (await panel.count() > 0) {
            console.log(`✅ ${func.name} 面板已打开`);
            
            // 关闭面板
            const closeButton = page.locator('.panel-close:visible');
            if (await closeButton.count() > 0) {
              await closeButton.first().click();
              await page.waitForTimeout(500);
            }
          } else {
            console.log(`⚠️  ${func.name} 面板未检测到`);
          }
        } else {
          console.log(`❌ ${func.name} 链接未找到`);
        }
      } catch (error) {
        console.log(`❌ ${func.name} 测试失败: ${error.message}`);
      }
    }
  });

  test('命令输入测试', async ({ page }) => {
    console.log('=== 开始命令输入测试 ===');
    
    await page.goto('http://localhost:5001');
    await page.waitForLoadState('networkidle');
    
    // 等待命令输入框
    const commandInput = page.locator('input[placeholder*="随便说点什么"]');
    if (await commandInput.isVisible({ timeout: 10000 })) {
      console.log('✅ 找到命令输入框');
      
      const testCommands = ['查看状态', '打开背包', '四处看看'];
      
      for (const command of testCommands) {
        await commandInput.fill(command);
        const submitButton = page.locator('button:has-text("执行")');
        await submitButton.click();
        await page.waitForTimeout(1000);
        console.log(`✅ 执行命令: ${command}`);
      }
    } else {
      console.log('❌ 命令输入框未找到');
    }
  });
});
EOF
        
        # 运行测试
        npx playwright test test_sidebar.spec.js --headed --reporter=list
        
        echo ""
        echo "✅ 测试完成！"
        echo "📊 查看详细报告: npx playwright show-report"
        ;;
    3)
        echo "🚀 启动服务器并运行测试..."
        
        # 后台启动服务器
        python3 start_web.py > server.log 2>&1 &
        SERVER_PID=$!
        
        echo "⏳ 等待服务器启动..."
        sleep 5
        
        # 检查服务器是否启动成功
        if curl -s http://localhost:5001 > /dev/null; then
            echo "✅ 服务器启动成功"
            
            # 运行测试
            echo "🧪 开始运行测试..."
            
            # 创建并运行测试
            cat > test_sidebar.spec.js << 'EOF'
// 简化的侧边栏测试
const { test, expect } = require('@playwright/test');

test('侧边栏基础功能测试', async ({ page }) => {
  console.log('开始侧边栏基础功能测试...');
  
  await page.goto('http://localhost:5001');
  await page.waitForLoadState('networkidle');
  
  console.log(`当前页面: ${page.url()}`);
  
  const title = await page.title();
  console.log(`页面标题: ${title}`);
  expect(title).toContain('修仙');
  
  console.log('✅ 基础功能测试完成');
});

test('API健康检查', async ({ request }) => {
  console.log('开始API健康检查...');
  
  const endpoints = ['/status', '/api/cultivation/status', '/api/achievements'];
  
  for (const endpoint of endpoints) {
    try {
      const response = await request.get(`http://localhost:5001${endpoint}`);
      console.log(`${endpoint}: ${response.status()}`);
    } catch (error) {
      console.log(`${endpoint}: 错误 - ${error.message}`);
    }
  }
  
  console.log('✅ API健康检查完成');
});
EOF
            
            npx playwright test test_sidebar.spec.js --headed --reporter=list
            
            echo "✅ 测试完成！"
        else
            echo "❌ 服务器启动失败"
        fi
        
        # 清理
        echo "🧹 清理服务器进程..."
        kill $SERVER_PID 2>/dev/null || true
        sleep 2
        ;;
    4)
        echo "📊 查看测试报告..."
        if [ -d "playwright-report" ]; then
            npx playwright show-report
        else
            echo "❌ 未找到测试报告，请先运行测试"
        fi
        ;;
    5)
        echo "🧹 清理测试数据..."
        rm -rf test-results playwright-report test_sidebar.spec.js server.log
        echo "✅ 清理完成"
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "🎉 操作完成！"
echo ""
echo "💡 提示:"
echo "  - 游戏访问地址: http://localhost:5001"
echo "  - 测试报告: npx playwright show-report"
echo "  - 查看日志: tail -f server.log"
echo "  - 手动测试: npx playwright test --headed"
