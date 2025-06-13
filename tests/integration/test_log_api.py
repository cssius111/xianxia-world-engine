"""API 日志接口集成测试"""

from run_web_ui_optimized import app
from xwe.services import register_services, get_service_container


def test_log_endpoint():
    """调用 /api/v1/game/log 并检查返回结构"""
    # 初始化服务容器，确保日志服务可用
    register_services(get_service_container())

    with app.test_client() as client:
        resp = client.get('/api/v1/game/log')
        assert resp.status_code == 200

        data = resp.get_json()
        assert data['success'] is True
        logs = data['data']['logs']
        assert isinstance(logs, list)
        assert logs, "日志列表应包含至少一条记录"

        for entry in logs:
            for key in ['id', 'timestamp', 'level', 'category', 'message']:
                assert key in entry, f"缺少字段: {key}"
