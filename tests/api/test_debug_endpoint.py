import sys
import flask


def test_debug_endpoint_returns_versions(client):
    from src.api.v1.dev.dev_routes import dev_bp

    app = client.application
    app.register_blueprint(dev_bp, url_prefix="/api/v1/dev")

    resp = client.get("/api/v1/dev/debug")
    assert resp.status_code == 200
    data = resp.get_json()

    assert data["python_version"] == sys.version.split(" ")[0]
    assert data["flask_version"] == flask.__version__
    assert "environment" not in data
