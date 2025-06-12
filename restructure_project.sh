#!/bin/bash

# 项目结构重组脚本（Shell版本）
# - 保留 run_web_ui_optimized.py 为主入口
# - 整理测试、文档、脚本等文件到合理目录
# - 支持 dry-run 模式预览更改

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认为 dry-run 模式
DRY_RUN=true
PROJECT_ROOT="."

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --execute)
            DRY_RUN=false
            shift
            ;;
        --project-root)
            PROJECT_ROOT="$2"
            shift
            shift
            ;;
        -h|--help)
            echo "使用方法: $0 [选项]"
            echo "选项:"
            echo "  --execute        执行重构（默认为 dry-run 模式）"
            echo "  --project-root   项目根目录路径（默认为当前目录）"
            echo "  -h, --help       显示帮助信息"
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            exit 1
            ;;
    esac
done

# 转换为绝对路径
PROJECT_ROOT=$(cd "$PROJECT_ROOT" && pwd)

# 检查项目路径
if [ ! -f "$PROJECT_ROOT/run_web_ui_optimized.py" ]; then
    echo -e "${RED}错误：在 $PROJECT_ROOT 找不到 run_web_ui_optimized.py${NC}"
    echo "请确保在正确的项目根目录运行此脚本。"
    exit 1
fi

echo -e "${BLUE}项目路径: $PROJECT_ROOT${NC}"

# 操作计数器
COUNT_CREATE=0
COUNT_MOVE=0
COUNT_DELETE=0

# 日志函数
log_action() {
    local action=$1
    local source=$2
    local destination=$3
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN]${NC} $action: $source${destination:+ -> $destination}"
    else
        echo -e "${GREEN}[执行]${NC} $action: $source${destination:+ -> $destination}"
    fi
}

# 创建目录
ensure_dir() {
    local dir="$PROJECT_ROOT/$1"
    if [ ! -d "$dir" ]; then
        log_action "CREATE_DIR" "$1"
        ((COUNT_CREATE++))
        if [ "$DRY_RUN" = false ]; then
            mkdir -p "$dir"
        fi
    fi
}

# 移动文件
move_file() {
    local source="$PROJECT_ROOT/$1"
    local destination="$PROJECT_ROOT/$2"
    
    if [ -e "$source" ]; then
        log_action "MOVE" "$1" "$2"
        ((COUNT_MOVE++))
        if [ "$DRY_RUN" = false ]; then
            mkdir -p "$(dirname "$destination")"
            mv "$source" "$destination"
        fi
    fi
}

# 删除文件或目录
delete_file() {
    local path="$PROJECT_ROOT/$1"
    
    if [ -e "$path" ]; then
        log_action "DELETE" "$1"
        ((COUNT_DELETE++))
        if [ "$DRY_RUN" = false ]; then
            rm -rf "$path"
        fi
    fi
}

# 开始重构
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY RUN] 开始重构项目...${NC}"
else
    echo -e "${GREEN}开始重构项目...${NC}"
fi

# 1. 创建目录结构
echo -e "\n${BLUE}步骤 1: 创建目录结构${NC}"
ensure_dir "archive/deprecated/entrypoints"
ensure_dir "archive/backups"
ensure_dir "tests/unit"
ensure_dir "tests/web_ui"
ensure_dir "scripts/tools"
ensure_dir "docs/progress"
ensure_dir "docs/guides"
ensure_dir "output"

# 2. 移动废弃的入口文件
echo -e "\n${BLUE}步骤 2: 移动废弃的入口文件${NC}"
for entry in main.py run_game.py run_optimized_game.py run_web_ui.py start_game.sh; do
    move_file "$entry" "archive/deprecated/entrypoints/$entry"
done

# 3. 移动测试文件
echo -e "\n${BLUE}步骤 3: 移动测试文件${NC}"
for test_file in $PROJECT_ROOT/test_*.py; do
    if [ -f "$test_file" ]; then
        filename=$(basename "$test_file")
        if [[ "$filename" =~ "web" ]] || [[ "$filename" =~ "ui" ]]; then
            move_file "$filename" "tests/web_ui/$filename"
        else
            move_file "$filename" "tests/unit/$filename"
        fi
    fi
done

# 4. 移动工具脚本
echo -e "\n${BLUE}步骤 4: 移动工具脚本${NC}"
tool_scripts=(
    "optimize.sh"
    "deep_optimize.sh"
    "verify_phase4.py"
    "verify_system.py"
    "update_imports.py"
    "apply_refactor.py"
    "cleanup_ui.sh"
    "deploy_optimizations.sh"
    "run_tests.sh"
    "dedupe.py"
    "function_analyzer.py"
    "quality_optimizer.py"
    "quick_todo_fixer.py"
    "update_service_integration.py"
)

for script in "${tool_scripts[@]}"; do
    move_file "$script" "scripts/tools/$script"
done

# 5. 整理文档
echo -e "\n${BLUE}步骤 5: 整理文档${NC}"
# 进度文档
progress_docs=(
    "PHASE3_COMPLETE.md"
    "PHASE4_BATCH1_SUMMARY.md"
    "PHASE4_BATCH2_PLAN.md"
    "REFACTOR_PROGRESS.md"
    "REFACTOR_APPLY_REPORT.md"
    "code_quality_report.md"
    "refactor_plan_1__fuzzy_parse.md"
    "refactor_plan_2_process_command.md"
    "refactor_plan_3_validate_with_error.md"
)

for doc in "${progress_docs[@]}"; do
    move_file "$doc" "docs/progress/$doc"
done

# 指南文档
guide_docs=(
    "FEATURES_GUIDE.md"
    "TODO_LIST.md"
    "AGENTS.md"
)

for doc in "${guide_docs[@]}"; do
    move_file "$doc" "docs/guides/$doc"
done

# 6. 移动输出文件
echo -e "\n${BLUE}步骤 6: 移动输出文件${NC}"
output_files=(
    "game_log.html"
    "test_output.html"
    "xianxia_game.html"
)

for file in "${output_files[@]}"; do
    move_file "$file" "output/$file"
done

# 移动所有 .save 文件
for save_file in $PROJECT_ROOT/*.save; do
    if [ -f "$save_file" ]; then
        filename=$(basename "$save_file")
        move_file "$filename" "archive/backups/$filename"
    fi
done

# 移动所有 .json 文件（除了配置文件）
for json_file in $PROJECT_ROOT/*.json; do
    if [ -f "$json_file" ]; then
        filename=$(basename "$json_file")
        if [[ "$filename" != "package.json" ]] && [[ "$filename" != "tsconfig.json" ]]; then
            move_file "$filename" "archive/backups/$filename"
        fi
    fi
done

# 7. 清理缓存文件
echo -e "\n${BLUE}步骤 7: 清理缓存文件${NC}"
# 清理 __pycache__ 文件夹
find "$PROJECT_ROOT" -type d -name "__pycache__" | while read -r pycache; do
    relative_path=${pycache#$PROJECT_ROOT/}
    delete_file "$relative_path"
done

# 清理 .pyc 文件
find "$PROJECT_ROOT" -name "*.pyc" | while read -r pyc; do
    relative_path=${pyc#$PROJECT_ROOT/}
    delete_file "$relative_path"
done

# 8. 移动示例和集成文件
echo -e "\n${BLUE}步骤 8: 移动示例和集成文件${NC}"
integration_files=(
    "api_integration_example.py"
    "demo_ai_features.py"
    "phase4_integration_example.py"
    "service_integration_example.py"
    "service_layer_example.py"
    "optimization_test_script.py"
)

for file in "${integration_files[@]}"; do
    move_file "$file" "scripts/$file"
done

# 9. 更新 README.md
echo -e "\n${BLUE}步骤 9: 更新 README.md${NC}"
if [ -f "$PROJECT_ROOT/README.md" ]; then
    log_action "UPDATE" "README.md"
    
    if [ "$DRY_RUN" = false ]; then
        # 创建项目结构说明
        RESTRUCTURE_NOTE="
## 项目结构说明（重构于 $(date +%Y-%m-%d)）

### 主入口
- \`run_web_ui_optimized.py\` - **主入口文件**，运行 Flask Web UI

### 目录结构
- \`xwe/\` - 核心游戏引擎模块
- \`templates/\` - Flask 模板文件
- \`static/\` - 静态资源文件
- \`scripts/\` - 辅助脚本和示例代码
  - \`tools/\` - 项目工具脚本
- \`tests/\` - 测试文件
  - \`unit/\` - 单元测试
  - \`web_ui/\` - Web UI 相关测试
- \`docs/\` - 项目文档
  - \`guides/\` - 使用指南
  - \`progress/\` - 开发进度记录
- \`archive/\` - 归档文件
  - \`deprecated/entrypoints/\` - 废弃的入口文件
  - \`backups/\` - 备份文件
- \`output/\` - 输出文件（HTML报告等）
- \`plugins/\` - 插件系统
- \`mods/\` - 游戏模组

### 废弃入口说明
以下入口文件已归档至 \`archive/deprecated/entrypoints/\`：
- \`main.py\` - 原命令行入口
- \`run_game.py\` - 原游戏运行脚本
- \`run_web_ui.py\` - 原Web UI入口
- 其他旧版入口文件

---
"
        
        # 检查是否已经包含项目结构说明
        if ! grep -q "## 项目结构说明" "$PROJECT_ROOT/README.md"; then
            # 在第一个 ## 之前插入
            awk -v note="$RESTRUCTURE_NOTE" '
                !inserted && /^## / && NR > 1 {
                    print note
                    inserted = 1
                }
                { print }
                END {
                    if (!inserted) {
                        print ""
                        print note
                    }
                }
            ' "$PROJECT_ROOT/README.md" > "$PROJECT_ROOT/README.md.tmp"
            
            mv "$PROJECT_ROOT/README.md.tmp" "$PROJECT_ROOT/README.md"
        fi
    fi
fi

# 打印总结
echo -e "\n${BLUE}$('='*60)${NC}"
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}重构操作总结 (DRY RUN)${NC}"
else
    echo -e "${GREEN}重构操作总结 (已执行)${NC}"
fi
echo -e "${BLUE}$('='*60)${NC}"

echo -e "\n创建目录: ${GREEN}$COUNT_CREATE${NC} 个"
echo -e "移动文件: ${GREEN}$COUNT_MOVE${NC} 个"
echo -e "删除文件: ${GREEN}$COUNT_DELETE${NC} 个"
echo -e "更新文件: ${GREEN}1${NC} 个 (README.md)"
echo -e "\n总计: ${GREEN}$((COUNT_CREATE + COUNT_MOVE + COUNT_DELETE + 1))${NC} 个操作"

if [ "$DRY_RUN" = true ]; then
    echo -e "\n${YELLOW}这是 DRY RUN 模式，没有实际执行任何操作。${NC}"
    echo -e "使用 ${BLUE}--execute${NC} 参数来真正执行重构。"
else
    echo -e "\n${GREEN}重构完成！${NC}"
fi
