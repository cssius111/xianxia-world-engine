#!/usr/bin/env python3
"""简单的 DeepSeek API 连通性测试脚本"""
import os
from deepseek import DeepSeek


def main() -> None:
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    client = DeepSeek(api_key=api_key)
    try:
        response = client.chat("你好")
        print("API 响应:", response.get("text", ""))
        print("DeepSeek API 测试完成")
    except Exception as exc:
        print("DeepSeek API 测试失败:", exc)


if __name__ == "__main__":
    main()
