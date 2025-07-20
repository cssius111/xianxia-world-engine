#!/bin/bash
# 导入 Grafana 仪表盘脚本

GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-admin}"
DASHBOARD_FILE="monitoring/grafana_dashboard_xwe.json"

echo "📊 导入 XWE Grafana 仪表盘..."
echo "🔗 Grafana URL: $GRAFANA_URL"

# 检查 Grafana 是否运行
if ! curl -s "$GRAFANA_URL/api/health" > /dev/null; then
    echo "❌ 无法连接到 Grafana，请确保 Grafana 正在运行"
    echo "💡 提示: docker-compose up -d grafana"
    exit 1
fi

# 导入仪表盘
curl -X POST \
    -H "Content-Type: application/json" \
    -u "$GRAFANA_USER:$GRAFANA_PASSWORD" \
    -d "@$DASHBOARD_FILE" \
    "$GRAFANA_URL/api/dashboards/db"

if [ $? -eq 0 ]; then
    echo "✅ 仪表盘导入成功！"
    echo "🌐 访问: $GRAFANA_URL/d/xwe-monitoring/xianxia-world-engine-jian-kong-mian-ban"
else
    echo "❌ 仪表盘导入失败"
fi
