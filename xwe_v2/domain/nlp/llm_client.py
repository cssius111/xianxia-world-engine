# nlp/llm_client.py
"""
大语言模型客户端

支持多种LLM API的统一接口。
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM配置"""

    api_key: str
    api_base: str = ""
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 500
    timeout: int = 30


class LLMProvider(ABC):
    """LLM提供者基类"""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    @abstractmethod
    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """生成文本补全"""
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """对话补全"""
        pass


class DeepSeekProvider(LLMProvider):
    """DeepSeek API提供者"""

    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)
        if not config.api_base:
            config.api_base = "https://api.deepseek.com/v1"
        if not config.model:
            config.model = "deepseek-chat"

    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """DeepSeek文本补全"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return self.chat(messages)

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """DeepSeek对话补全"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        try:
            response = requests.post(
                f"{self.config.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config.timeout,
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API请求失败: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"DeepSeek API响应格式错误: {e}")
            raise


class OpenAIProvider(LLMProvider):
    """OpenAI API提供者"""

    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)
        if not config.api_base:
            config.api_base = "https://api.openai.com/v1"
        if not config.model:
            config.model = "gpt-3.5-turbo"

    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """OpenAI文本补全"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return self.chat(messages)

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """OpenAI对话补全"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        try:
            response = requests.post(
                f"{self.config.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config.timeout,
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API请求失败: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"OpenAI API响应格式错误: {e}")
            raise


class MockProvider(LLMProvider):
    """模拟提供者（用于测试）"""

    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """模拟补全"""
        logger.info(f"Mock LLM - Prompt: {prompt[:50]}...")

        # 简单的模拟响应
        if "攻击" in prompt:
            return json.dumps({"command": "attack", "target": "敌人"})
        elif "修炼" in prompt:
            return json.dumps({"command": "cultivate"})
        elif "查看" in prompt or "状态" in prompt:
            return json.dumps({"command": "status"})
        else:
            return json.dumps({"command": "unknown"})

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """模拟对话"""
        last_message = messages[-1]["content"] if messages else ""
        return self.complete(last_message)


class LLMClient:
    """
    LLM客户端

    提供统一的接口访问不同的LLM服务。
    """

    def __init__(
        self, provider: Optional[str] = None, config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        初始化LLM客户端

        Args:
            provider: 提供者名称 (deepseek, openai, mock)，可从环境变量读取
            config: 配置字典
        """
        # 优先使用传入的 provider，否则读取 .env 中 DEFAULT_LLM_PROVIDER
        self.provider_name = provider or os.getenv("DEFAULT_LLM_PROVIDER", "mock")
        self.config = self._load_config(config)
        self.provider = self._create_provider()

        logger.info(f"初始化LLM客户端: {self.provider_name}")

    def _load_config(self, config: Optional[Dict[str, Any]]) -> LLMConfig:
        """加载配置"""
        # 默认配置
        default_config = {
            "api_key": os.getenv("LLM_API_KEY", ""),
            "temperature": 0.7,
            "max_tokens": 500,
        }

        # 合并用户配置
        if config:
            default_config.update(config)

        # 从环境变量读取API密钥
        if not default_config["api_key"]:
            env_key_map = {"deepseek": "DEEPSEEK_API_KEY", "openai": "OPENAI_API_KEY"}
            env_key = env_key_map.get(self.provider_name)
            if env_key:
                default_config["api_key"] = os.getenv(env_key, "")

        return LLMConfig(**default_config)

    def _create_provider(self) -> LLMProvider:
        """创建提供者实例"""
        provider_map = {
            "deepseek": DeepSeekProvider,
            "openai": OpenAIProvider,
            "mock": MockProvider,
        }

        provider_class = provider_map.get(self.provider_name)
        if not provider_class:
            logger.warning(f"未知的LLM提供者: {self.provider_name}，使用Mock")
            provider_class = MockProvider

        return provider_class(self.config)

    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        生成文本补全

        Args:
            prompt: 用户提示
            system_prompt: 系统提示

        Returns:
            生成的文本
        """
        try:
            return self.provider.complete(prompt, system_prompt)
        except Exception as e:
            logger.error(f"LLM补全失败: {e}")
            return ""

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        对话补全

        Args:
            messages: 消息列表

        Returns:
            生成的回复
        """
        try:
            return self.provider.chat(messages)
        except Exception as e:
            logger.error(f"LLM对话失败: {e}")
            return ""

    def parse_command(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        解析用户输入为游戏命令

        Args:
            user_input: 用户输入
            context: 游戏上下文

        Returns:
            解析结果
        """
        system_prompt = """你是一个修仙游戏的命令解析器。
将玩家的自然语言输入转换为游戏命令。

可用的命令类型：
- attack: 攻击（需要target参数）
- use_skill: 使用技能（需要skill和target参数）
- defend: 防御
- flee: 逃跑
- move: 移动（需要location参数）
- explore: 探索
- talk: 对话（需要target参数）
- cultivate: 修炼
- status: 查看状态
- inventory: 查看背包
- skills: 查看技能
- map: 查看地图
- help: 帮助

请以JSON格式返回，包含：
{
    "command": "命令类型",
    "target": "目标（如果有）",
    "parameters": {
        "skill": "技能名（如果是use_skill）",
        "location": "地点（如果是move）"
    }
}

如果无法理解，返回：
{
    "command": "unknown",
    "original": "原始输入"
}
"""

        prompt = f"玩家输入：{user_input}"
        if context:
            prompt += f"\n当前上下文：{json.dumps(context, ensure_ascii=False)}"

        response = self.complete(prompt, system_prompt)

        try:
            # 尝试解析JSON响应
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            logger.error(f"无法解析LLM响应: {response}")
            return {"command": "unknown", "original": user_input}
