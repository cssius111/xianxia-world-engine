from dotenv import load_dotenv

load_dotenv()

# 确保测试环境可用 requests
from xwe.utils.requests_helper import ensure_requests

ensure_requests()

