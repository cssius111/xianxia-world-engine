#!/bin/bash
# 清理重复文件和更新引用的完整流程

# 设置错误时退出
set -e

echo "开始清理重复文件和更新引用..."

# 1. 创建安全分支
echo "创建安全分支..."
git checkout -b refactor/clean-ui || {
    echo "分支已存在，切换到该分支"
    git checkout refactor/clean-ui
}

# 2. 运行重复文件检测（预览模式）
echo -e "\n运行重复文件检测（预览）..."
python dedupe.py

# 3. 执行重复文件移动
echo -e "\n确认执行重复文件移动..."
python dedupe.py --apply

# 4. 重命名保留的文件为统一名称
echo -e "\n重命名文件..."
# 查找所有 run_web_ui_*.py 文件并重命名为 run_web_ui.py
for file in run_web_ui_v3.py start_enhanced_ui.py; do
    if [ -f "$file" ]; then
        echo "重命名 $file -> run_web_ui.py"
        git mv "$file" run_web_ui.py 2>/dev/null || mv "$file" run_web_ui.py
    fi
done

# 5. 运行引用更新（预览模式）
echo -e "\n运行引用更新（预览）..."
python update_imports.py

# 6. 执行引用更新
echo -e "\n确认执行引用更新..."
python update_imports.py --apply

# 7. 运行测试
echo -e "\n运行测试..."
pytest -q || {
    echo "测试失败！请检查错误并手动修复。"
    exit 1
}

# 8. 检查 run_web_ui.py
echo -e "\n检查 run_web_ui.py..."
if [ -f "run_web_ui.py" ]; then
    python run_web_ui.py --check 2>/dev/null || {
        # 如果没有 --check 参数，尝试导入检查
        python -c "import run_web_ui" && echo "run_web_ui.py 导入成功" || {
            echo "run_web_ui.py 检查失败！"
            exit 1
        }
    }
else
    echo "警告: run_web_ui.py 不存在"
fi

# 9. Git 操作
echo -e "\n执行 Git 操作..."
git add -A
git commit -m "refactor: 清理重复的 UI 启动脚本，统一为 run_web_ui.py

- 移除 run_web_ui_v3.py 等旧脚本
- 统一所有引用为 run_web_ui.py
- 通过所有测试"

# 10. 推送分支
echo -e "\n推送分支..."
git push -u origin refactor/clean-ui

echo -e "\n✅ 所有操作完成！"
