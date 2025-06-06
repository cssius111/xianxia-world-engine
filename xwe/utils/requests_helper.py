from pathlib import Path
import sys
import subprocess


def ensure_requests():
    """Ensure the requests library is available. Install or load stub if needed."""
    try:
        import requests  # noqa: F401
        return
    except ImportError:
        vendor_path = Path(__file__).resolve().parent.parent.parent / "vendor"
        if (vendor_path / "requests").exists():
            sys.path.insert(0, str(vendor_path))
            try:
                import requests  # noqa: F401
                print("✅ 使用 vendor 中的 requests")
                return
            except Exception:
                sys.path.remove(str(vendor_path))

        print("⚠️ 缺少 requests，尝试安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
        try:
            import requests  # noqa: F401
            print("✅ requests 安装完成")
        except ImportError:
            print("⚠️ 未能安装 requests，使用 requestsNotDeepSeek 存根")
            import requestsNotDeepSeek as requests_stub
            sys.modules['requests'] = requests_stub
