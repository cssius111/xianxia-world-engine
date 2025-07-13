#!/bin/bash
# 设置所有监控相关脚本的执行权限

echo "🔧 设置脚本执行权限..."

# 设置执行权限的脚本列表
scripts=(
    "start_xwe.sh"
    "toggle_metrics.sh"
    "import_grafana_dashboard.sh"
    "quick_start_monitoring.sh"
    "fix_prometheus_integration.py"
    "health_check_monitoring.sh"
    "setup_monitoring_permissions.sh"
)

# 设置权限
for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo "✅ $script"
    else
        echo "⚠️  $script 不存在"
    fi
done

echo ""
echo "✨ 完成！现在可以运行："
echo "   ./quick_start_monitoring.sh"
echo "来启动完整的监控系统"