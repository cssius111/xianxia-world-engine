# 第2阶段 - API标准化方案

## 目标
建立清晰、一致的前后端接口契约，实现真正的前后端分离。

## 现状分析

### 当前问题
1. 路由混乱：游戏逻辑、API接口、页面渲染混在一起
2. 响应格式不统一：有时返回JSON，有时返回HTML片段
3. 错误处理不一致：缺乏统一的错误响应格式
4. 缺乏API版本管理

### 现有接口
- `/command` - POST 执行命令
- `/status` - GET 获取状态
- `/log` - GET 获取日志
- `/need_refresh` - GET 检查是否需要刷新
- `/save_game` - POST 保存游戏
- `/load_game` - POST 加载游戏

## API设计方案

### 1. RESTful路由结构
```
/api/v1/
├── /game/
│   ├── GET    /status      # 游戏状态
│   ├── POST   /command     # 执行命令
│   ├── GET    /log         # 获取日志
│   └── GET    /events      # 获取事件
├── /player/
│   ├── GET    /info        # 玩家信息
│   ├── GET    /inventory   # 背包物品
│   ├── GET    /skills      # 技能列表
│   └── GET    /achievements # 成就列表
├── /save/
│   ├── GET    /list        # 存档列表
│   ├── POST   /create      # 创建存档
│   ├── GET    /{id}        # 获取存档
│   ├── PUT    /{id}        # 更新存档
│   └── DELETE /{id}        # 删除存档
└── /system/
    ├── GET    /time        # 游戏时间
    ├── GET    /version     # 版本信息
    └── GET    /commands    # 可用命令列表
```

### 2. 统一响应格式

#### 成功响应
```json
{
    "success": true,
    "data": {
        // 实际数据
    },
    "meta": {
        "timestamp": 1234567890,
        "version": "1.0.0"
    }
}
```

#### 错误响应
```json
{
    "success": false,
    "error": {
        "code": "INVALID_COMMAND",
        "message": "无效的命令",
        "details": {
            "command": "未知命令",
            "suggestions": ["攻击", "防御", "逃跑"]
        }
    },
    "meta": {
        "timestamp": 1234567890,
        "version": "1.0.0"
    }
}
```

### 3. 错误代码规范
```python
class ErrorCodes:
    # 通用错误 (1000-1999)
    INVALID_REQUEST = "INVALID_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    
    # 游戏错误 (2000-2999)
    INVALID_COMMAND = "INVALID_COMMAND"
    PLAYER_DEAD = "PLAYER_DEAD"
    NOT_ENOUGH_MANA = "NOT_ENOUGH_MANA"
    INVALID_TARGET = "INVALID_TARGET"
    
    # 存档错误 (3000-3999)
    SAVE_NOT_FOUND = "SAVE_NOT_FOUND"
    SAVE_CORRUPTED = "SAVE_CORRUPTED"
    SAVE_LIMIT_EXCEEDED = "SAVE_LIMIT_EXCEEDED"
```

### 4. API版本管理
- URL路径包含版本号：`/api/v1/`
- 支持版本协商：通过Header `Accept-Version: 1.0`
- 向后兼容：旧版本API保留至少6个月

## 实施计划

### Phase 2.1 - API蓝图创建
1. 创建 `api/` 目录结构
2. 实现基础中间件（CORS、认证、日志）
3. 创建响应格式化工具

### Phase 2.2 - 核心API实现
1. 重构 `/command` 接口
2. 重构 `/status` 接口
3. 添加错误处理机制

### Phase 2.3 - 扩展API实现
1. 实现玩家信息API
2. 实现存档管理API
3. 实现系统信息API

### Phase 2.4 - 文档和测试
1. 使用Swagger生成API文档
2. 编写API测试用例
3. 性能优化

## 代码示例

### API蓝图结构
```python
# api/__init__.py
from flask import Blueprint
from .game import game_bp
from .player import player_bp
from .save import save_bp
from .system import system_bp

def register_api(app):
    """注册所有API蓝图"""
    app.register_blueprint(game_bp, url_prefix='/api/v1/game')
    app.register_blueprint(player_bp, url_prefix='/api/v1/player')
    app.register_blueprint(save_bp, url_prefix='/api/v1/save')
    app.register_blueprint(system_bp, url_prefix='/api/v1/system')
```

### 响应格式化装饰器
```python
# api/utils.py
from functools import wraps
from flask import jsonify
import time

def api_response(f):
    """统一API响应格式"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            
            # 如果已经是响应对象，直接返回
            if hasattr(result, 'get_json'):
                return result
                
            # 格式化响应
            response = {
                'success': True,
                'data': result,
                'meta': {
                    'timestamp': int(time.time()),
                    'version': '1.0.0'
                }
            }
            return jsonify(response)
            
        except APIError as e:
            response = {
                'success': False,
                'error': {
                    'code': e.code,
                    'message': e.message,
                    'details': e.details
                },
                'meta': {
                    'timestamp': int(time.time()),
                    'version': '1.0.0'
                }
            }
            return jsonify(response), e.status_code
            
    return decorated_function
```

### 示例API实现
```python
# api/game.py
from flask import Blueprint, request
from .utils import api_response, validate_request
from .errors import InvalidCommandError

game_bp = Blueprint('game', __name__)

@game_bp.route('/command', methods=['POST'])
@api_response
@validate_request({
    'type': 'object',
    'properties': {
        'command': {'type': 'string', 'minLength': 1}
    },
    'required': ['command']
})
def execute_command():
    """执行游戏命令"""
    command = request.json['command']
    
    # 处理命令
    result = game_engine.process_command(command)
    
    if not result.valid:
        raise InvalidCommandError(
            command=command,
            suggestions=result.suggestions
        )
    
    return {
        'command': command,
        'result': result.output,
        'state_changed': result.state_changed
    }
```

## 前端适配

### 更新API客户端
```javascript
// static/js/modules/api.js
class ApiClient {
    constructor(baseUrl = '/api/v1') {
        this.baseUrl = baseUrl;
        this.version = '1.0.0';
    }
    
    async request(method, endpoint, data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Accept-Version': this.version
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${this.baseUrl}${endpoint}`, options);
        const result = await response.json();
        
        if (!result.success) {
            throw new APIError(result.error);
        }
        
        return result.data;
    }
}
```

## 测试计划

### 单元测试
- 测试每个API端点
- 测试错误处理
- 测试数据验证

### 集成测试
- 测试完整的游戏流程
- 测试并发请求
- 测试性能

### 示例测试
```python
# tests/test_api.py
def test_execute_command(client):
    """测试执行命令API"""
    response = client.post('/api/v1/game/command', json={
        'command': '状态'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'data' in data
    assert 'meta' in data
```

## 迁移策略

1. **并行运行**：新旧API同时运行，逐步迁移
2. **版本标记**：在响应中标记API版本
3. **弃用通知**：旧API返回弃用警告
4. **监控迁移**：跟踪新旧API使用情况

---

第2阶段将彻底解决前后端通信的混乱问题，为后续的功能扩展打下坚实基础。
