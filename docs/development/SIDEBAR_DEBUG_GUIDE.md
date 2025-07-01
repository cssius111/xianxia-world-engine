# 🔧 侧边栏功能调试指南

## 快速诊断命令

```bash
# 1. 启动服务器（如果还没启动）
python3 start_web.py

# 2. 运行快速健康检查
npx playwright test tests/e2e/sidebar.spec.ts --headed

# 3. 检查浏览器控制台
# 打开 http://localhost:5001
# 按 F12 打开开发者工具
# 查看 Console 和 Network 标签
```

## 常见问题和解决方案

### 问题1: 侧边栏点击无反应

**症状**: 
- 点击侧边栏链接没有任何反应
- 控制台显示 `GamePanels is not defined`

**解决方案**:
```javascript
// 检查 game_panels_enhanced.js 是否正确加载
// 在浏览器控制台运行：
console.log(typeof GamePanels);  // 应该输出 "object"

// 如果是 undefined，检查脚本加载顺序
// 确保在 HTML 中正确引入：
<script src="/static/js/game_panels_enhanced.js"></script>
```

### 问题2: API 404错误

**症状**:
- 点击功能后显示 "未找到数据"
- Network标签显示404错误

**解决方案**:
```bash
# 检查是否已注册侧边栏 API
grep -n register_sidebar_apis run.py

# 查看路由
python - <<'EOF'
from run import app
for r in app.url_map.iter_rules():
    print(r)
EOF
```
### 问题3: 数据格式错误

**症状**:
- 功能可以打开但显示异常
- 控制台显示 JSON 解析错误

**解决方案**:
```javascript
// 在浏览器控制台检查API响应
fetch('/api/cultivation/status')
  .then(res => res.json())
  .then(data => console.log('API响应:', data))
  .catch(err => console.error('错误:', err));

// 确保后端返回正确的JSON格式
```

## 完整调试流程

### Step 1: 验证服务器状态
```bash
# 检查服务器是否运行
curl http://localhost:5001/status

# 应该返回类似：
# {"status": "running", "version": "1.0.0"}
```

### Step 2: 测试每个API端点
```bash
# 创建测试脚本
cat > test_apis.sh << 'EOF'
#!/bin/bash
echo "测试侧边栏API端点..."
echo "===================="

endpoints=(
    "/status"
    "/api/cultivation/status"
    "/api/achievements" 
    "/api/map"
    "/api/quests"
    "/api/intel"
    "/api/player/stats/detailed"
)

for endpoint in "${endpoints[@]}"; do
    echo -n "测试 $endpoint ... "
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001$endpoint)
    if [ "$response" = "200" ]; then
        echo "✅ OK"
    else
        echo "❌ 失败 (HTTP $response)"
    fi
done
EOF

chmod +x test_apis.sh
./test_apis.sh
```

### Step 3: 前端调试
```javascript
// 在浏览器控制台运行完整诊断
(function debugSidebar() {
    console.log('=== 侧边栏调试信息 ===');
    
    // 检查GamePanels对象
    if (typeof GamePanels !== 'undefined') {
        console.log('✅ GamePanels 已加载');
        console.log('可用方法:', Object.keys(GamePanels));
    } else {
        console.log('❌ GamePanels 未定义');
    }
    
    // 检查jQuery
    if (typeof $ !== 'undefined') {
        console.log('✅ jQuery 已加载');
    } else {
        console.log('❌ jQuery 未加载');
    }
    
    // 检查侧边栏元素
    const sidebar = document.querySelector('.game-sidebar');
    if (sidebar) {
        console.log('✅ 侧边栏元素存在');
        const links = sidebar.querySelectorAll('a[onclick]');
        console.log(`找到 ${links.length} 个功能链接`);
    } else {
        console.log('❌ 侧边栏元素不存在');
    }
    
    // 测试API调用
    console.log('\n测试API调用...');
    fetch('/api/cultivation/status')
        .then(res => {
            console.log(`修炼状态API: ${res.status} ${res.ok ? '✅' : '❌'}`);
            return res.json();
        })
        .then(data => console.log('返回数据:', data))
        .catch(err => console.error('API错误:', err));
})();
```

### Step 4: 修复脚本
如果发现问题，运行修复脚本：

```python
# fix_sidebar.py
import os
import json

def check_and_fix_sidebar():
    """检查并修复侧边栏问题"""
    
    # 1. 确保 game_panels_enhanced.js 存在
    panels_js_path = 'src/web/static/js/game_panels_enhanced.js'
    if not os.path.exists(panels_js_path):
        print("❌ game_panels_enhanced.js 不存在")
        # 这里可以添加创建文件的代码
    else:
        print("✅ game_panels_enhanced.js 存在")
    
    # 2. 检查 HTML 模板
    template_path = 'src/web/templates/game_enhanced_optimized_v2.html'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'game_panels_enhanced.js' in content:
                print("✅ HTML模板正确引用了增强脚本")
            else:
                print("❌ HTML模板未引用增强脚本")
    
    # 3. 检查API路由
    # ... 更多检查

if __name__ == '__main__':
    check_and_fix_sidebar()
```

## 临时解决方案

如果紧急需要使用，可以在浏览器控制台运行：

```javascript
// 临时修复GamePanels
window.GamePanels = {
    showStatus: () => { window.location.href = '/status'; },
    showInventory: () => { alert('背包功能开发中'); },
    showCultivation: () => { alert('修炼功能开发中'); },
    showAchievements: () => { alert('成就功能开发中'); },
    showExplore: () => { window.location.href = '/explore'; },
    showMap: () => { alert('地图功能开发中'); },
    showQuests: () => { alert('任务功能开发中'); },
    showIntel: () => { alert('情报功能开发中'); },
    showSaveLoad: () => { alert('存档功能开发中'); },
    showHelp: () => { alert('帮助:\n- 输入命令进行游戏\n- 点击侧边栏查看功能'); }
};
console.log('✅ GamePanels 临时修复完成');
```

## 日志位置

查看详细错误信息：
```bash
# Flask日志
tail -f logs/app.log

# 查看最近的错误
grep ERROR logs/app.log | tail -20

# 查看特定功能的日志
grep -i sidebar logs/app.log
```

## 联系支持

如果以上方法都无法解决问题：

1. 收集以下信息：
   - 浏览器控制台截图
   - Network标签截图
   - `logs/app.log` 最后50行
   - `npx playwright test tests/e2e/sidebar.spec.ts --headed` 输出

2. 创建问题报告：
   - 问题描述
   - 复现步骤
   - 环境信息（Python版本、浏览器版本等）

---

*调试愉快！愿bug远离你的代码！* 🚀
