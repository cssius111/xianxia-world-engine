#!/bin/bash
# XWE 监控系统健康检查脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🏥 XianXia World Engine 监控系统健康检查${NC}"
echo "============================================="
echo ""

# 检查结果计数
TOTAL_CHECKS=0
PASSED_CHECKS=0

# 检查函数
check_service() {
    local service_name=$1
    local url=$2
    local expected_code=${3:-200}

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    printf "检查 %-20s ... " "$service_name"

    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [ "$response" = "$expected_code" ]; then
            echo -e "${GREEN}✅ 正常${NC}"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            return 0
        else
            echo -e "${RED}❌ 异常 (HTTP $response)${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ 无法连接${NC}"
        return 1
    fi
}

# 检查指标函数
check_metrics() {
    local metric_name=$1

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    printf "检查指标 %-25s ... " "$metric_name"

    if curl -s http://localhost:5000/metrics | grep -q "^$metric_name"; then
        echo -e "${GREEN}✅ 存在${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ 缺失${NC}"
        return 1
    fi
}

# 1. 检查核心服务
echo -e "${YELLOW}1. 核心服务状态${NC}"
echo "-------------------"
check_service "XWE 应用" "http://localhost:5000/health"
check_service "Metrics 端点" "http://localhost:5000/metrics"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Grafana" "http://localhost:3000/api/health"
echo ""

# 2. 检查 Docker 容器
echo -e "${YELLOW}2. Docker 容器状态${NC}"
echo "-------------------"
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if docker ps | grep -E "(prometheus|grafana)" > /dev/null; then
    echo -e "${GREEN}✅ 监控容器运行中${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(prometheus|grafana)"
else
    echo -e "${RED}❌ 监控容器未运行${NC}"
fi
echo ""

# 3. 检查关键指标
echo -e "${YELLOW}3. Prometheus 指标${NC}"
echo "-------------------"
check_metrics "xwe_nlp_request_seconds"
check_metrics "xwe_nlp_token_count"
check_metrics "xwe_nlp_error_total"
check_metrics "xwe_flask_http_request"

# 统计指标总数
if METRICS_COUNT=$(curl -s http://localhost:5000/metrics | grep -c "^xwe_" 2>/dev/null); then
    echo -e "\n📊 总指标数: ${METRICS_COUNT}"
fi
echo ""

# 4. 检查 Prometheus 目标
echo -e "${YELLOW}4. Prometheus 抓取状态${NC}"
echo "-------------------------"
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if curl -s http://localhost:9090/api/v1/targets | grep -q '"health":"up"'; then
    echo -e "${GREEN}✅ Prometheus 正在抓取 XWE 指标${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}❌ Prometheus 未能抓取 XWE 指标${NC}"
fi
echo ""

# 5. 检查配置文件
echo -e "${YELLOW}5. 配置文件${NC}"
echo "-------------"
config_files=(
    "infrastructure/monitoring/docker-compose.monitoring.yml"
    "infrastructure/monitoring/prometheus.yml"
    "infrastructure/monitoring/grafana_dashboard_xwe.json"
    "toggle_metrics.sh"
)

for file in "${config_files[@]}"; do
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    printf "%-35s ... " "$file"
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ 存在${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ 缺失${NC}"
    fi
done
echo ""

# 6. 环境变量检查
echo -e "${YELLOW}6. 环境配置${NC}"
echo "-------------"
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
printf "ENABLE_PROMETHEUS 环境变量      ... "
if [ "$ENABLE_PROMETHEUS" = "true" ] || grep -q "ENABLE_PROMETHEUS=true" .env 2>/dev/null; then
    echo -e "${GREEN}✅ 已启用${NC}"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  未设置或禁用${NC}"
fi
echo ""

# 总结
echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}检查总结${NC}"
echo -e "${BLUE}===============================================${NC}"
echo -e "总检查项: ${TOTAL_CHECKS}"
echo -e "通过项: ${GREEN}${PASSED_CHECKS}${NC}"
echo -e "失败项: ${RED}$((TOTAL_CHECKS - PASSED_CHECKS))${NC}"

SUCCESS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
echo -e "健康度: ${SUCCESS_RATE}%"

if [ $SUCCESS_RATE -eq 100 ]; then
    echo -e "\n${GREEN}🎉 监控系统完全正常！${NC}"
elif [ $SUCCESS_RATE -ge 80 ]; then
    echo -e "\n${YELLOW}⚠️  监控系统基本正常，但有少量问题需要关注${NC}"
else
    echo -e "\n${RED}❌ 监控系统存在问题，请检查故障排查手册${NC}"
fi

# 提供快速修复建议
if [ $((TOTAL_CHECKS - PASSED_CHECKS)) -gt 0 ]; then
    echo -e "\n${YELLOW}💡 快速修复建议：${NC}"

    if ! check_service "XWE 应用" "http://localhost:5000/health" >/dev/null 2>&1; then
        echo "  - 启动 XWE 应用: ./start_xwe.sh"
    fi

    if ! docker ps | grep -E "(prometheus|grafana)" > /dev/null 2>&1; then
        echo "  - 启动监控栈: docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml up -d"
    fi

    if [ ! -f "infrastructure/monitoring/grafana_dashboard_xwe.json" ]; then
        echo "  - 缺少仪表盘配置，请检查文件"
    fi
fi

echo ""
echo "详细信息请访问："
echo "  - Prometheus: http://localhost:9090/targets"
echo "  - Grafana: http://localhost:3000"
