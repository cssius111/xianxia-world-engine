# Flask 端点名称映射表

根据 run.py 中的路由定义，以下是所有可用的端点名称：

## 页面路由

| URL 路径 | 端点名称（函数名） | 说明 |
|---------|------------------|------|
| `/` | `index` | 首页（重定向到开始页面） |
| `/start` | `start_screen` | 开始页面 |
| `/intro` | `intro_screen` | 角色创建页面 |
| `/game` | `game_screen` | 游戏主界面 |
| `/roll` | `roll_screen` | 属性随机页面 |
| `/choose` | `choose_start` | 开局选择页面 |
| `/modal/<modal_name>` | `modal` | 通用模态框加载 |

## API 路由

| URL 路径 | 端点名称（函数名） | 说明 |
|---------|------------------|------|
| `/create_character` | `create_character` | 创建角色 |
| `/command` | `process_command` | 处理游戏命令 |
| `/status` | `get_status` | 获取游戏状态 |
| `/log` | `get_log` | 获取游戏日志 |
| `/data/destiny` | `get_destiny_data` | 返回命格数据 |
| `/data/fortune` | `get_fortune_data` | 返回气运数据 |
| `/data/templates` | `get_templates_data` | 返回角色模板数据 |
| `/api/parse_custom` | `parse_custom_text` | 使用LLM解析自定义背景 |

## 工具路由

| URL 路径 | 端点名称（函数名） | 说明 |
|---------|------------------|------|
| `/favicon.ico` | `favicon` | 避免favicon 404错误 |
| `/sw.js` | `service_worker` | Service Worker |

## 使用示例

### 在 Jinja2 模板中使用 url_for：
```html
<!-- 正确 -->
<a href="{{ url_for('intro_screen') }}">开始新游戏</a>
<a href="{{ url_for('game_screen') }}">游戏主界面</a>
<script src="{{ url_for('static', filename='js/game.js') }}"></script>

<!-- 错误（这些端点不存在） -->
<a href="{{ url_for('intro') }}">❌</a>
<a href="{{ url_for('game') }}">❌</a>
```

### 在 JavaScript 中使用：
```javascript
// 在模板中嵌入 url_for
window.location.href = "{{ url_for('game_screen') }}";

// 带参数
window.location.href = "{{ url_for('game_screen', mode='dev') }}";

// 直接使用路径（不推荐，但有时必要）
window.location.href = '/game';  // 可以工作，但不推荐
fetch('/create_character', {...});  // API 调用通常直接使用路径
```

## 注意事项

1. Flask 的端点名称默认是视图函数的名称
2. 如果想使用不同的端点名称，可以在装饰器中指定：
   ```python
   @app.route("/intro", endpoint="custom_name")
   def intro_screen():
       pass
   ```
3. 使用 `url_for` 的好处是当 URL 路径改变时，只需要修改路由定义，不需要修改所有模板
4. 在开发时，如果遇到 `BuildError`，检查函数名而不是 URL 路径
