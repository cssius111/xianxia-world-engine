# 添加类型存根
import requests  # type: ignore[import-untyped]

# 或者安装 types-requests 后就不需要 ignore


def ensure_requests() -> None:
    """Ensure the requests library is available."""
    try:
        import requests  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("The 'requests' package must be installed.") from exc
