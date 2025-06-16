# @dev_only
"""
API集成示例
展示如何将新的RESTful API集成到现有的Flask应用
"""

from flask import Flask, render_template, session
import os

# 导入API注册函数
from api import register_api


def create_app_with_api():
    """
    创建带有API的Flask应用
    """
    # 创建Flask应用
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates_enhanced')
    
    # 配置密钥（用于session）
    app.secret_key = os.environ.get('SECRET_KEY', 'xianxia-world-engine-secret-key')
    
    # 配置session
    app.config.update(
        SESSION_COOKIE_NAME='xwe_session',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=86400  # 24小时
    )
    
    # 注册API
    register_api(app)
    
    # 保留原有的页面路由
    @app.route('/')
    def index():
        """主页"""
        return render_template('game_main.html')
    
    @app.route('/game')
    def game():
        """游戏页面"""
        return render_template('game_main.html')
    
    # 健康检查（非API版本）
    @app.route('/health')
    def health():
        """简单的健康检查"""
        return 'OK', 200
    
    return app


def upgrade_existing_app(app):
    """
    升级现有的Flask应用，添加API支持
    
    Args:
        app: 现有的Flask应用实例
    """
    # 注册API到现有应用
    register_api(app)
    
    print("✅ API已成功集成到现有应用")
    print("📍 API端点前缀: /api/v1")
    print("📚 API文档: /api/v1/docs (需要额外配置)")


# 示例：修改现有的run_web_ui_optimized.py
def example_integration():
    """
    示例：如何修改现有的启动文件
    """
    print("""
    === 集成步骤 ===
    
    1. 在你的启动文件（如 run_web_ui_optimized.py）中添加：
    
    ```python
    from api import register_api
    
    # 在创建app之后，运行app之前添加：
    register_api(app)
    ```
    
    2. 更新前端JavaScript调用：
    
    旧代码：
    ```javascript
    fetch('/command', {
        method: 'POST',
        body: JSON.stringify({cmd: command})
    })
    ```
    
    新代码：
    ```javascript
    fetch('/api/v1/game/command', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: command})
    })
    ```
    
    3. 处理新的响应格式：
    
    ```javascript
    const response = await fetch('/api/v1/game/command', {...});
    const data = await response.json();
    
    if (data.success) {
        // 处理成功响应
        console.log(data.data.result);
    } else {
        // 处理错误
        console.error(data.error.message);
    }
    ```
    """)


if __name__ == '__main__':
    # 创建示例应用
    app = create_app_with_api()
    
    # 打印所有注册的路由
    print("\n=== 已注册的API端点 ===")
    for rule in app.url_map.iter_rules():
        if '/api/' in rule.rule:
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"{methods:8} {rule.rule}")
    
    # 运行应用
    print("\n启动应用...")
    app.run(debug=True, port=5000)
