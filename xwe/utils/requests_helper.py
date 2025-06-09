def ensure_requests():
    """Ensure the requests library is available."""
    try:
        import requests  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("The 'requests' package must be installed.") from exc
