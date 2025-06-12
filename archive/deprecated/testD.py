import os
import requests  # type: ignore[import-untyped]NotDeepSeek
import json

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise EnvironmentError("❌ 未设置环境变量 DEEPSEEK_API_KEY")

api_url = "https://api.deepseek.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": "你是一个 JSON 命令机器人，请将用户输入转为结构化指令，只返回 JSON，不要代码块"},
        {"role": "user", "content": "修炼一百年"}
    ],
    "temperature": 0.2,
    "max_tokens": 300
}

print("🚀 正在请求 DeepSeek API...")
response = requests.post(api_url, headers=headers, json=payload, timeout=15)

if response.status_code == 200:
    print("✅ 完整响应 JSON：")
    full = response.json()
    print(json.dumps(full, indent=2, ensure_ascii=False))

    try:
        content = full["choices"][0]["message"]["content"]
        print("\n✅ 收到 content 字段：")
        print(content)

        parsed = json.loads(content)
        print("\n✅ 成功解析为 JSON：")
        print(parsed)
    except Exception as e:
        print(f"\n⚠️ 解析失败: {e}")
else:
    print(f"❌ 请求失败，状态码: {response.status_code}")
    print(response.text)
