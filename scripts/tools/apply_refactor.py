#!/usr/bin/env python3
"""
修仙世界引擎 - 第1阶段重构应用脚本
自动应用前端重构的所有更改
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class RefactorApplier:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log = []
        
    def log_action(self, action, status="✅"):
        """记录操作日志"""
        msg = f"{status} {action}"
        print(msg)
        self.log.append(msg)
        
    def backup_file(self, file_path):
        """备份文件"""
        if file_path.exists():
            relative_path = file_path.relative_to(self.project_root)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            self.log_action(f"备份: {relative_path}")
            
    def create_directories(self):
        """创建必要的目录结构"""
        directories = [
            "static/css",
            "static/js/modules",
            "templates_enhanced/components",
            "patches/phase1",
            "patches/phase2"
        ]
        
        for dir_path in directories:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            self.log_action(f"创建目录: {dir_path}")
            
    def update_flask_config(self):
        """更新Flask配置文件"""
        config_file = self.project_root / "run_web_ui_optimized.py"
        if not config_file.exists():
            self.log_action("未找到 run_web_ui_optimized.py", "⚠️")
            return
            
        self.backup_file(config_file)
        
        # 读取文件内容
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查是否需要更新
        if "game_main.html" not in content:
            # 替换模板引用
            content = content.replace(
                "game_enhanced_optimized.html",
                "game_main.html"
            )
            
            # 确保静态文件夹配置正确
            if "static_folder" not in content:
                content = content.replace(
                    "Flask(__name__",
                    "Flask(__name__, static_folder='static'"
                )
                
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.log_action("更新Flask配置")
        else:
            self.log_action("Flask配置已是最新", "ℹ️")
            
    def apply_refactor(self):
        """应用重构"""
        print("=" * 50)
        print("修仙世界引擎 - 第1阶段重构应用")
        print("=" * 50)
        
        # 1. 创建备份目录
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.log_action(f"创建备份目录: {self.backup_dir.name}")
        
        # 2. 备份原始文件
        original_template = self.project_root / "templates_enhanced/game_enhanced_optimized.html"
        if original_template.exists():
            self.backup_file(original_template)
            
        # 3. 创建目录结构
        self.create_directories()
        
        # 4. 更新Flask配置
        self.update_flask_config()
        
        # 5. 生成报告
        self.generate_report()
        
        print("\n" + "=" * 50)
        print("✅ 第1阶段重构应用完成！")
        print("=" * 50)
        
    def generate_report(self):
        """生成应用报告"""
        report_path = self.project_root / "REFACTOR_APPLY_REPORT.md"
        
        report_content = f"""# 重构应用报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 操作日志

"""
        for log_entry in self.log:
            report_content += f"- {log_entry}\n"
            
        report_content += f"""

## 下一步操作

1. **复制新文件**
   - 将 patches/phase1 中的文件复制到对应位置
   - 确保所有组件文件都已创建

2. **测试运行**
   ```bash
   python run_web_ui_optimized.py
   ```

3. **验证功能**
   - 检查页面是否正常显示
   - 测试命令输入功能
   - 确认状态更新正常

## 备份位置

所有原始文件已备份到: `{self.backup_dir.name}/`

## 回滚方法

如需回滚，执行：
```bash
cp -r {self.backup_dir.name}/* .
```

---
报告生成完成
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        self.log_action(f"生成报告: REFACTOR_APPLY_REPORT.md")


def main():
    """主函数"""
    # 获取项目根目录
    script_path = Path(__file__).resolve()
    project_root = script_path.parent
    
    print(f"项目根目录: {project_root}")
    
    # 确认操作
    response = input("\n是否继续应用第1阶段重构? (y/n): ")
    if response.lower() != 'y':
        print("操作已取消")
        return
        
    # 应用重构
    applier = RefactorApplier(project_root)
    applier.apply_refactor()
    
    print("\n提示: 请手动复制 static/ 和 templates_enhanced/components/ 中的新文件")
    print("详细信息请查看 REFACTOR_APPLY_REPORT.md")


if __name__ == "__main__":
    main()
