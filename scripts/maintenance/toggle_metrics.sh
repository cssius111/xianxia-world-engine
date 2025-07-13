#!/bin/bash
# XWE 监控灰度开关脚本
# 用法: ./toggle_metrics.sh enable|disable|status

set -e

# 配置
APP_URL="${XWE_APP_URL:-http://localhost:5000}"
METRICS_ENV_VAR="XWE_METRICS"
ENV_FILE=".env"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 函数：显示用法
usage() {
    echo "用法: $0 {enable|disable|status}"
    echo ""
    echo "命令:"
    echo "  enable   - 启用 Prometheus 监控"
    echo "  disable  - 禁用 Prometheus 监控" 
    echo "  status   - 查看当前监控状态"
    echo ""
    echo "环境变量:"
    echo "  XWE_APP_URL - 应用 URL (默认: http://localhost:5000)"
    exit 1
}

# 函数：检查应用状态
check_app() {
    if ! curl -s "${APP_URL}/health" > /dev/null; then
        echo -e "${RED}❌ 无法连接到应用 ${APP_URL}${NC}"
        exit 1
    fi
}

# 函数：更新环境变量
update_env() {
    local key=$1
    local value=$2
    
    # 创建 .env 文件（如果不存在）
    touch "$ENV_FILE"
    
    # 更新或添加环境变量
    if grep -q "^${key}=" "$ENV_FILE"; then
        # 使用临时文件避免 sed -i 的跨平台问题
        sed "s/^${key}=.*/${key}=${value}/" "$ENV_FILE" > "${ENV_FILE}.tmp"
        mv "${ENV_FILE}.tmp" "$ENV_FILE"
    else
        echo "${key}=${value}" >> "$ENV_FILE"
    fi
}

# 函数：获取当前状态
get_status() {
    # 尝试访问 /metrics 端点
    local response=$(curl -s -o /dev/null -w "%{http_code}" "${APP_URL}/metrics")
    
    if [ "$response" = "200" ]; then
        echo "enabled"
    else
        echo "disabled"
    fi
}

# 函数：启用监控
enable_metrics() {
    echo -e "${YELLOW}🔄 启用 Prometheus 监控...${NC}"
    
    # 更新环境变量
    update_env "$METRICS_ENV_VAR" "on"
    update_env "ENABLE_PROMETHEUS" "true"
    
    # 发送信号重新加载配置（如果应用支持）
    # kill -HUP $(pgrep -f "gunicorn.*app:app") 2>/dev/null || true
    
    # 验证
    sleep 2
    local status=$(get_status)
    
    if [ "$status" = "enabled" ]; then
        echo -e "${GREEN}✅ 监控已启用${NC}"
        echo "📊 访问 ${APP_URL}/metrics 查看指标"
    else
        echo -e "${YELLOW}⚠️  监控已设置为启用，可能需要重启应用${NC}"
        echo "💡 运行: ./start_xwe.sh"
    fi
}

# 函数：禁用监控
disable_metrics() {
    echo -e "${YELLOW}🔄 禁用 Prometheus 监控...${NC}"
    
    # 更新环境变量
    update_env "$METRICS_ENV_VAR" "off"
    update_env "ENABLE_PROMETHEUS" "false"
    
    # 验证
    sleep 2
    local status=$(get_status)
    
    if [ "$status" = "disabled" ]; then
        echo -e "${GREEN}✅ 监控已禁用${NC}"
    else
        echo -e "${YELLOW}⚠️  监控已设置为禁用，可能需要重启应用${NC}"
        echo "💡 运行: ./start_xwe.sh"
    fi
}

# 函数：显示状态
show_status() {
    echo -e "${YELLOW}📊 检查监控状态...${NC}"
    
    local status=$(get_status)
    local env_status=$(grep "^${METRICS_ENV_VAR}=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
    
    echo ""
    echo "当前状态:"
    if [ "$status" = "enabled" ]; then
        echo -e "  运行时: ${GREEN}已启用${NC}"
    else
        echo -e "  运行时: ${RED}已禁用${NC}"
    fi
    
    if [ -n "$env_status" ]; then
        echo -e "  环境变量: ${METRICS_ENV_VAR}=${env_status}"
    else
        echo -e "  环境变量: 未设置"
    fi
    
    # 检查指标数量
    if [ "$status" = "enabled" ]; then
        local metrics_count=$(curl -s "${APP_URL}/metrics" | grep -c "^xwe_" || echo "0")
        echo -e "  指标数量: ${metrics_count}"
    fi
}

# 主逻辑
case "$1" in
    enable)
        check_app
        enable_metrics
        ;;
    disable)
        check_app
        disable_metrics
        ;;
    status)
        check_app
        show_status
        ;;
    *)
        usage
        ;;
esac