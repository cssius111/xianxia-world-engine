# 测试检查清单

## 启动前检查

- [ ] Python 3.7+ 已安装
- [ ] 依赖已安装：
  - Flask
  - psutil
  - httpx
  - python-dotenv
  - 安装命令：`pip install -r requirements.txt`
- [ ] 项目目录结构完整
- [ ] `.env` 文件已配置（可选）

## 启动测试

1. **启动服务器**
   ```bash
   cd /path/to/xianxia_world_engine
   python -m xwe.cli.run_server
   ```
   - [ ] 服务器成功启动
   - [ ] 显示访问地址：http://localhost:5001
   - [ ] 无错误信息

2. **访问主页**
   - [ ] 浏览器可以访问 http://localhost:5001
   - [ ] 页面正确显示"修仙世界引擎"标题
   - [ ] 显示三个按钮：开始新游戏、继续游戏（如有存档）、开发者模式

## 游戏流程测试

### 1. 新游戏流程
- [ ] 点击"开始新游戏"跳转到角色创建页面
- [ ] 显示加载画面
- [ ] 自动显示欢迎页面

### 2. 欢迎页面测试
- [ ] 欢迎页面正确显示
- [ ] 背景音乐播放（如有音频文件）
- [ ] 三个按钮功能正常：
  - [ ] "开始游戏" - 进入角色创建
  - [ ] "继续游戏" - 显示"开发中"提示
  - [ ] "开发者模式" - 弹出密码输入框

### 3. 角色创建测试
- [ ] 角色创建面板正确显示
- [ ] 可以输入角色姓名
- [ ] 可以选择性别
- [ ] 属性点分配功能正常（总点数30）
- [ ] 背景选择功能正常
- [ ] "随机生成"按钮工作正常
- [ ] "确认创建"按钮可以提交

### 4. 世界介绍测试
- [ ] 世界介绍页面正确显示
- [ ] 显示游戏背景故事
- [ ] 显示游戏提示
- [ ] "开始冒险"按钮可以进入游戏

### 5. 游戏主界面测试
- [ ] 游戏主界面正确加载
- [ ] 头部显示角色信息
- [ ] 侧边栏显示正确
- [ ] 叙事日志区域显示欢迎信息
- [ ] 命令输入框可以使用

## 功能面板测试

### 侧边栏链接
- [ ] 查看状态 - 打开状态面板
- [ ] 背包 - 打开背包面板
- [ ] 修炼 - 打开修炼面板
- [ ] 成就 - 打开成就面板
- [ ] 探索 - 打开探索面板
- [ ] 地图 - 打开地图面板
- [ ] 任务 - 打开任务面板
- [ ] 情报 - 显示"开发中"
- [ ] 保存/加载 - 显示"开发中"
- [ ] 帮助 - 打开帮助面板
- [ ] 返回主菜单 - 返回开始页面

### 命令系统测试
- [ ] 输入"探索"命令有响应
- [ ] 输入"修炼"命令有响应
- [ ] 输入"帮助"命令有响应
- [ ] 命令历史功能（上下键）
- [ ] 命令提示功能
- [ ] 快捷命令按钮

### 快捷键测试
- [ ] ESC 关闭当前面板
- [ ] Ctrl+S 打开保存面板（游戏内）

## 开发模式测试

1. **进入开发模式**
   - [ ] 输入 `DEV_PASSWORD` 设置的密码成功进入
   - [ ] 控制台显示"开发者模式已启用"

2. **开发模式快捷键**
   - [ ] Ctrl+Shift+S - 跳过到角色创建
   - [ ] Ctrl+Shift+W - 跳过到世界介绍
   - [ ] Ctrl+Shift+G - 直接进入游戏

## 响应式测试

- [ ] 在1920x1080分辨率下显示正常
- [ ] 在1366x768分辨率下显示正常
- [ ] 在平板设备尺寸下显示正常
- [ ] 在手机设备尺寸下显示正常

## 浏览器兼容性

- [ ] Chrome/Edge 最新版
- [ ] Firefox 最新版
- [ ] Safari 最新版

## 常见问题排查

### 如果页面显示不正常
1. 检查浏览器控制台是否有错误
2. 确认所有静态文件路径正确
3. 清除浏览器缓存后重试

### 如果功能无响应
1. 检查网络请求是否成功（F12开发者工具）
2. 查看服务器控制台是否有错误信息
3. 确认相关API端点已实现

### 如果样式缺失
1. 检查CSS文件是否正确加载
2. 确认文件路径正确
3. 检查是否有CSS语法错误

## 性能检查

- [ ] 页面加载时间 < 3秒
- [ ] 命令响应时间 < 500ms
- [ ] 面板切换流畅无卡顿
- [ ] 内存使用正常（无内存泄漏）

## 安全检查

- [ ] 输入验证正常（防XSS）
- [ ] 无敏感信息暴露
- [ ] 开发模式需要密码保护

---

测试完成后，如发现问题请记录在下方：

### 发现的问题：
1.
2.
3.

### 改进建议：
1.
2.
3.
