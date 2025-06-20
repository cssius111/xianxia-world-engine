# @dev_only
"""
更新导入脚本
确保项目使用新的服务层架构
"""

import os
import sys
from pathlib import Path


def update_run_web_ui():
    """更新run_web_ui.py以使用服务层"""

    file_path = Path("run_web_ui.py")

    if not file_path.exists():
        print(f"⚠️  {file_path} 不存在")
        return

    print(f"更新 {file_path}...")

    # 读取文件内容
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否需要更新
    if "from xwe.services import" in content:
        print("✓ 文件已经使用服务层")
        return

    # 添加服务层导入
    import_section = """
# 导入服务层
from xwe.services import ServiceContainer, register_services
"""

    # 添加服务初始化
    init_section = """
    # 初始化服务容器
    container = ServiceContainer()
    register_services(container)
    app.config['service_container'] = container
"""

    # 在适当位置插入代码
    if "from flask import Flask" in content:
        content = content.replace(
            "from flask import Flask", "from flask import Flask\n" + import_section
        )

    if "app = Flask(__name__)" in content:
        # 找到app创建后的位置
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "app = Flask(__name__)" in line:
                # 在下一个合适的位置插入
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith("app."):
                    j += 1
                lines.insert(j, init_section)
                break
        content = "\n".join(lines)

    # 写回文件
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✓ 文件更新完成")


def create_service_config():
    """创建服务配置文件"""

    config_content = """# 服务层配置
# 这个文件定义了服务层的配置选项

# 日志配置
LOG_SERVICE_CONFIG = {
    'max_logs': 10000,
    'log_file_rotation': True,
    'log_to_file': True,
    'log_directory': 'logs'
}

# 事件配置
EVENT_DISPATCHER_CONFIG = {
    'max_event_history': 10000,
    'enable_async_events': True,
    'event_timeout': 5.0
}

# 命令引擎配置
COMMAND_ENGINE_CONFIG = {
    'enable_natural_language': True,
    'command_cache_size': 100,
    'command_history_size': 100
}

# 服务生命周期配置
SERVICE_LIFETIME_CONFIG = {
    'game_service': 'singleton',
    'player_service': 'singleton',
    'combat_service': 'singleton',
    'command_engine': 'singleton',
    'event_dispatcher': 'singleton',
    'log_service': 'singleton'
}
"""

    config_path = Path("xwe/services/config.py")

    print(f"创建服务配置文件 {config_path}...")

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)

    print("✓ 配置文件创建完成")


def update_main_py():
    """更新main.py以使用服务层"""

    file_path = Path("main.py")

    if not file_path.exists():
        print(f"⚠️  {file_path} 不存在")
        return

    print(f"检查 {file_path}...")

    # 读取文件内容
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否需要更新
    if "ServiceContainer" in content:
        print("✓ main.py 已经使用服务层")
        return

    print("ℹ️  main.py 暂不需要直接使用服务层（通过game_core间接使用）")


def main():
    """主函数"""
    print("=" * 50)
    print("服务层集成更新")
    print("=" * 50)

    # 更改工作目录到项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # 执行更新
    update_run_web_ui()
    create_service_config()
    update_main_py()

    print("\n" + "=" * 50)
    print("✅ 服务层集成更新完成！")
    print("=" * 50)

    print("\n后续步骤：")
    print("1. 运行测试验证服务层: python tests/test_services.py")
    print("2. 运行示例了解用法: python service_layer_example.py")
    print("3. 启动游戏测试集成: python run_web_ui.py")


if __name__ == "__main__":
    main()
