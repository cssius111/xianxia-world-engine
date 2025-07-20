#!/bin/bash
# XWE 监控系统快速启动脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 XianXia World Engine 监控系统快速启动${NC}"
echo "================================================"

# 步骤1：检查依赖
echo -e "\n${YELLOW}步骤 1: 检查依赖${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装，请先安装 Docker Compose${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 依赖检查通过${NC}"

# 步骤2：修复和安装 Python 依赖
echo -e "\n${YELLOW}步骤 2: 安装 Python 依赖${NC}"
if [ -f "fix_prometheus_integration.py" ]; then
    python fix_prometheus_integration.py
fi

pip install -r requirements.txt
echo -e "${GREEN}✅ Python 依赖安装完成${NC}"

# 步骤3：启动监控栈
echo -e "\n${YELLOW}步骤 3: 启动监控栈${NC}"
docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml up -d
echo -e "${GREEN}✅ Prometheus 和 Grafana 已启动${NC}"

# 步骤4：等待服务就绪
echo -e "\n${YELLOW}步骤 4: 等待服务就绪${NC}"
sleep 10

# 检查 Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null; then
    echo -e "${GREEN}✅ Prometheus 就绪${NC}"
else
    echo -e "${RED}⚠️  Prometheus 可能未就绪${NC}"
fi

# 检查 Grafana
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo -e "${GREEN}✅ Grafana 就绪${NC}"
else
    echo -e "${RED}⚠️  Grafana 可能未就绪${NC}"
fi

# 步骤5：启动 XWE 应用
echo -e "\n${YELLOW}步骤 5: 启动 XWE 应用${NC}"
if [ -f "start_xwe.sh" ]; then
    chmod +x start_xwe.sh
    ./start_xwe.sh &
    sleep 5
    echo -e "${GREEN}✅ XWE 应用已启动${NC}"
else
    echo -e "${YELLOW}⚠️  请手动启动 XWE 应用${NC}"
fi

# 步骤6：导入 Grafana 仪表盘
echo -e "\n${YELLOW}步骤 6: 导入 Grafana 仪表盘${NC}"
if [ -f "scripts/maintenance/import_grafana_dashboard.sh" ] && [ -f "infrastructure/monitoring/grafana_dashboard_xwe.json" ]; then
    chmod +x scripts/maintenance/import_grafana_dashboard.sh
    sleep 5
    ./scripts/maintenance/import_grafana_dashboard.sh
else
    echo -e "${YELLOW}⚠️  请手动导入 Grafana 仪表盘${NC}"
fi

# 步骤7：运行测试
echo -e "\n${YELLOW}步骤 7: 运行测试验证${NC}"
if [ -f "tests/test_prometheus_metrics.py" ]; then
    pytest tests/test_prometheus_metrics.py -v || echo -e "${YELLOW}⚠️  部分测试失败${NC}"
else
    echo -e "${YELLOW}⚠️  测试文件未找到${NC}"
fi

# 完成
echo -e "\n${GREEN}🎉 监控系统启动完成！${NC}"
echo -e "\n访问以下地址："
echo -e "  • XWE 应用: ${BLUE}http://localhost:5000${NC}"
echo -e "  • 指标端点: ${BLUE}http://localhost:5000/metrics${NC}"
echo -e "  • Prometheus: ${BLUE}http://localhost:9090${NC}"
echo -e "  • Grafana: ${BLUE}http://localhost:3000${NC} (admin/admin)"
echo -e "\n${YELLOW}提示:${NC}"
echo -e "  • 使用 './toggle_metrics.sh status' 查看监控状态"
echo -e "  • 使用 'docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml logs -f' 查看日志"
echo -e "  • 使用 'docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml down' 停止监控栈"
