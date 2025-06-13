"""API 日志接口集成测试"""

from run_web_ui_optimized import app
from xwe.services import register_services, get_service_container, ILogService


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


def test_log_filter_by_level():
    """验证按级别过滤日志"""
    register_services(get_service_container())
    container = get_service_container()
    log_service = container.resolve(ILogService)

    log_service.clear_logs()
    log_service.log_info("info msg", category="test")
    log_service.log_error("error msg", category="test")

    with app.test_client() as client:
        resp = client.get('/api/v1/game/log?level=error')
        assert resp.status_code == 200

        data = resp.get_json()
        assert data['success'] is True
        logs = data['data']['logs']

        assert len(logs) == 1
        assert all(entry['level'] == 'error' for entry in logs)
