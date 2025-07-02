"""
修仙世界引擎 - DeepSeek MCP 命令解析器
基于 DeepSeek API 的自然语言指令处理模块
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import time
from functools import lru_cache

from .llm_client import LLMClient
from .config import get_nlp_config
from .monitor import get_nlp_monitor

# 专用日志记录器
logger = logging.getLogger("xwe.nlp")


@dataclass
class ParsedCommand:
    """解析后的命令结构"""

    raw: str  # 原始输入
    normalized_command: str  # 标准化命令
    intent: str  # 意图类别
    args: Dict[str, Any]  # 参数
    explanation: str  # 解析说明
    confidence: float = 1.0  # 置信度（可选）


class DeepSeekNLPProcessor:
    """
    基于 DeepSeek 的命令解析器
    使用 MCP (Model as Command Parser) 方式解析玩家自然语言指令
    """

    def __init__(self, api_key: Optional[str] = None, cache_size: int = None):
        """
        初始化处理器

        Args:
            api_key: DeepSeek API 密钥
            cache_size: 缓存大小
        """
        # 加载配置
        self.config = get_nlp_config()
        self.monitor = get_nlp_monitor()

        # 初始化LLM客户端
        api_key = api_key or self.config.get_api_key()
        if not api_key:
            raise ValueError(
                "Missing DEEPSEEK_API_KEY. Please set it in your environment or .env file."
            )
        self.llm = LLMClient(
            api_key=api_key,
            api_url=self.config.get("api_url"),
            model_name=self.config.get("model", "deepseek-chat"),
            timeout=self.config.get("timeout", 30),
            debug=self.config.get("debug_mode", False),
        )

        # 初始化缓存
        self._cache_size = cache_size or self.config.get("cache_size", 128)
        self._init_cache()

        # 初始化本地回退处理器
        self._init_fallback_handler()

        # 加载prompt模板
        self._init_prompt_template()

        logger.info(f"DeepSeekNLPProcessor 初始化完成 (缓存大小: {self._cache_size})")

    def _init_cache(self):
        """初始化缓存"""

        # 使用LRU缓存装饰器创建缓存函数
        @lru_cache(maxsize=self._cache_size)
        def _cached_parse(text: str) -> str:
            prompt = self.build_prompt(text)
            return self._call_deepseek_api(prompt)

        self._cached_parse = _cached_parse

    def _init_fallback_handler(self):
        """初始化本地回退处理器"""
        self.fallback_patterns = {
            # 基础命令
            "探索": [
                "探索",
                "四处看看",
                "四处游玩",
                "四处闲逛",
                "随便走走",
                "逛逛",
                "转转",
            ],
            "修炼": ["修炼", "打坐", "闭关", "炼功", "修行", "练功", "休息"],
            "查看状态": ["状态", "查看状态", "角色信息", "看看状态", "瞧瞧状态"],
            "打开背包": ["背包", "物品", "查看背包", "打开背包", "看看背包"],
            "前往": ["去", "前往", "移动", "走", "过去"],
            "攻击": ["攻击", "打", "揍", "击打", "出手"],
            "对话": ["对话", "交谈", "说话", "聊天", "聊"],
            "使用": ["使用", "用", "服用", "吃"],
        }

    def _init_prompt_template(self):
        """初始化prompt模板"""
        self.prompt_template = """你是"修仙世界"游戏的命令解析器模块，需要将玩家发来的中文自然语言指令解析为结构化 JSON 格式，供游戏引擎调用。

游戏支持的核心命令包括（但不限于）：
- 探索、修炼、查看状态、打开背包、前往、使用物品、交谈、交易、战斗、退出、保存等。

输出格式必须遵循以下 JSON 结构（仅输出 JSON，不要任何多余文本）：
{
  "raw": "<玩家原始输入>",
  "normalized_command": "<标准命令词，若无法匹配填\\"未知\\">",
  "intent": "<意图类别，如 action/check/train/move/use/talk/etc/unknown>",
  "args": {
    // 可选字段，根据指令提取，如 "duration": "1时辰", "location": "丹药铺", "item": "回春丹", "quantity": 1
  },
  "explanation": "<简短解析依据，不超过20字>"
}

### 示例：
输入: "四处探索一下"  
输出:
{
  "raw": "四处探索一下",
  "normalized_command": "探索",
  "intent": "action",
  "args": {},
  "explanation": "同义词探索意图明确"
}

输入: "我想休息一个时辰"  
输出:
{
  "raw": "我想休息一个时辰",
  "normalized_command": "修炼",
  "intent": "train",
  "args": {"duration": "1时辰"},
  "explanation": "休息即修炼，提取时长1时辰"
}

输入: "打开一下背包看看"  
输出:
{
  "raw": "打开一下背包看看",
  "normalized_command": "打开背包",
  "intent": "check",
  "args": {},
  "explanation": "打开背包查看物品"
}

输入: "给我瞧瞧当前状态"  
输出:
{
  "raw": "给我瞧瞧当前状态",
  "normalized_command": "查看状态",
  "intent": "check",
  "args": {},
  "explanation": "查看状态意图"
}

输入: "快速闭关三小时"  
输出:
{
  "raw": "快速闭关三小时",
  "normalized_command": "修炼",
  "intent": "train",
  "args": {"duration": "3小时", "mode": "快速闭关"},
  "explanation": "闭关修炼，提取时长3小时"
}

输入: "去丹药铺买药"  
输出:
{
  "raw": "去丹药铺买药",
  "normalized_command": "前往",
  "intent": "move",
  "args": {"location": "丹药铺"},
  "explanation": "前往丹药铺"
}

输入: "先探索再修炼"  
输出:
{
  "raw": "先探索再修炼",
  "normalized_command": ["探索","修炼"],
  "intent": "action_sequence",
  "args": [{"command":"探索","args":{}},{"command":"修炼","args":{}}],
  "explanation": "多步指令拆分"
}

输入: "使用回春丹恢复血量"
输出:
{
  "raw": "使用回春丹恢复血量",
  "normalized_command": "使用物品",
  "intent": "use",
  "args": {"item": "回春丹"},
  "explanation": "使用物品回春丹"
}

输入: "和李掌柜聊聊天"
输出:
{
  "raw": "和李掌柜聊聊天",
  "normalized_command": "交谈",
  "intent": "talk",
  "args": {"target": "李掌柜"},
  "explanation": "与NPC李掌柜交谈"
}

如果输入无法识别任何命令或过于模糊，请：
- normalized_command 填 "未知"
- intent 填 "unknown"
- args 为空对象
- explanation 说明"模糊"或"无法解析"

现在请根据上述要求，仅输出符合格式的 JSON，不要其他文本。

输入: "{}"
输出:
"""

    def build_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        构建prompt

        Args:
            user_input: 用户输入
            context: 上下文信息（可选）

        Returns:
            完整的prompt
        """
        # 这里可以根据context添加更多上下文信息
        # 例如当前位置、已知NPC、可用物品等
        return self.prompt_template.format(user_input)

    def _call_deepseek_api(self, prompt: str) -> str:
        """
        调用DeepSeek API

        Args:
            prompt: 完整的prompt

        Returns:
            API返回的JSON字符串
        """
        try:
            # 调用LLM客户端
            response = self.llm.chat(
                prompt,
                temperature=self.config.get("temperature", 0.0),
                max_tokens=self.config.get("max_tokens", 256),
            )

            logger.debug(f"DeepSeek raw response: {response}")

            # 尝试提取JSON部分
            response = response.strip()

            # 如果响应被包裹在代码块中，提取出来
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            # 若包含多余文本，尝试截取首个JSON对象
            match = re.search(r"{.*}", response, re.DOTALL)
            if match:
                response = match.group(0)

            response = response.strip()

            logger.debug(f"DeepSeek sanitized JSON: {response}")

            # 验证JSON格式
            json.loads(response)

            return response

        except Exception as e:
            logger.error(f"DeepSeek API 调用失败: {e}", exc_info=True)
            raise

    def local_fallback(self, user_input: str) -> Dict:
        """
        本地回退解析

        Args:
            user_input: 用户输入

        Returns:
            解析结果字典
        """
        user_input_lower = user_input.lower().strip()

        # 尝试匹配本地模式
        for command, patterns in self.fallback_patterns.items():
            for pattern in patterns:
                if pattern in user_input_lower:
                    # 基础解析
                    result = {
                        "raw": user_input,
                        "normalized_command": command,
                        "intent": self._get_intent_from_command(command),
                        "args": {},
                        "explanation": "本地模式匹配",
                    }

                    # 尝试提取参数
                    if command == "前往":
                        # 提取地点
                        words = user_input.split()
                        if len(words) > 1:
                            location = " ".join(words[1:])
                            result["args"]["location"] = location

                    elif command == "使用":
                        # 提取物品
                        words = user_input.split()
                        if len(words) > 1:
                            item = " ".join(words[1:])
                            result["args"]["item"] = item

                    logger.debug(f"Local fallback match: {result}")
                    return result

        # 无法识别
        result = {
            "raw": user_input,
            "normalized_command": "未知",
            "intent": "unknown",
            "args": {},
            "explanation": "无法识别命令",
        }
        logger.debug(f"Local fallback default: {result}")
        return result

    def _get_intent_from_command(self, command: str) -> str:
        """根据命令获取意图类别"""
        intent_map = {
            "探索": "action",
            "修炼": "train",
            "查看状态": "check",
            "打开背包": "check",
            "前往": "move",
            "攻击": "action",
            "对话": "talk",
            "交谈": "talk",
            "使用": "use",
            "使用物品": "use",
        }
        return intent_map.get(command, "unknown")

    def parse(
        self, user_input: str, use_cache: bool = True, context: Optional[Dict] = None
    ) -> ParsedCommand:
        """
        解析用户输入

        Args:
            user_input: 用户输入的命令
            use_cache: 是否使用缓存
            context: 上下文信息

        Returns:
            解析后的命令对象
        """
        logger.debug(f"Raw user input: {user_input}")

        start_time = time.time()
        success = False
        error_msg = None
        use_fallback = False

        try:
            # 检查是否启用NLP
            if not self.config.is_enabled():
                logger.debug("NLP未启用，使用本地回退")
                use_fallback = True
                raise ValueError("NLP未启用")

            # 构建prompt
            prompt = self.build_prompt(user_input, context)
            logger.debug(f"DeepSeek prompt: {prompt}")

            # 调用API（带缓存）
            if use_cache:
                json_response = self._cached_parse(user_input)
            else:
                json_response = self._call_deepseek_api(prompt)

            logger.debug(f"DeepSeek response string: {json_response}")

            # 解析JSON
            try:
                result = json.loads(json_response)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {e}; 响应内容: {json_response}")
                raise

            # 验证结果格式
            if not self._validate_result(result):
                raise ValueError("返回结果格式不正确")

            # 记录性能
            elapsed = time.time() - start_time
            logger.debug(f"DeepSeek解析耗时: {elapsed:.3f}秒")

            # 创建ParsedCommand对象
            parsed = ParsedCommand(
                raw=result["raw"],
                normalized_command=result["normalized_command"],
                intent=result["intent"],
                args=result.get("args", {}),
                explanation=result.get("explanation", ""),
                confidence=result.get("confidence", 1.0),
            )
            logger.info(f"Parsed command: {parsed}")

            success = True
            return parsed

        except Exception as e:
            error_msg = str(e)
            logger.error(f"DeepSeek解析失败，使用本地回退: {e}", exc_info=True)
            use_fallback = True

            # 使用本地回退
            if self.config.get("fallback_enabled", True):
                fallback_result = self.local_fallback(user_input)

                parsed = ParsedCommand(
                    raw=fallback_result["raw"],
                    normalized_command=fallback_result["normalized_command"],
                    intent=fallback_result["intent"],
                    args=fallback_result.get("args", {}),
                    explanation=fallback_result.get("explanation", "本地回退解析"),
                    confidence=0.5,  # 回退解析置信度较低
                )
                logger.info(f"Parsed command (fallback): {parsed}")

                success = True
                return parsed
            else:
                raise

        finally:
            # 记录监控数据
            if self.config.get("performance_monitoring", True):
                duration = time.time() - start_time
                self.monitor.record_request(
                    command=user_input,
                    handler=(
                        parsed.normalized_command if "parsed" in locals() else "unknown"
                    ),
                    duration=duration,
                    success=success,
                    confidence=parsed.confidence if "parsed" in locals() else 0,
                    use_cache=use_cache and not use_fallback,
                    error=error_msg,
                    token_count=0,  # TODO: 实际token计数
                )

    def _validate_result(self, result: Dict) -> bool:
        """验证解析结果格式"""
        required_fields = ["raw", "normalized_command", "intent"]
        return all(field in result for field in required_fields)

    def batch_parse(self, inputs: List[str]) -> List[ParsedCommand]:
        """
        批量解析命令

        Args:
            inputs: 命令列表

        Returns:
            解析结果列表
        """
        results = []
        for input_text in inputs:
            results.append(self.parse(input_text))
        return results

    def clear_cache(self):
        """清除缓存"""
        self._cached_parse.cache_clear()
        logger.info("命令解析缓存已清除")

    def get_cache_info(self) -> Dict:
        """获取缓存信息"""
        info = self._cached_parse.cache_info()
        return {
            "hits": info.hits,
            "misses": info.misses,
            "maxsize": info.maxsize,
            "currsize": info.currsize,
            "hit_rate": (
                info.hits / (info.hits + info.misses)
                if (info.hits + info.misses) > 0
                else 0
            ),
        }


# 保持向后兼容
class NLPProcessor:
    """向后兼容的NLP处理器"""

    def __init__(self):
        """向后兼容的 NLPProcessor 初始化"""
        config = get_nlp_config()
        api_key = config.get_api_key()

        if config.is_enabled() and config.validate_config():
            try:
                self.processor = DeepSeekNLPProcessor(api_key=api_key)
                self.enabled = True
            except Exception as e:
                logger.error(f"初始化DeepSeekNLPProcessor失败: {e}")
                self.processor = None
                self.enabled = False
        else:
            self.processor = None
            self.enabled = False

        if api_key:
            self.llm = LLMClient(api_key=api_key)
        else:
            self.llm = None
            logger.warning("\u26a0\ufe0f DeepSeek NLP disabled (missing API key)")

    def chat(self, prompt: str) -> str:
        """聊天功能"""
        if not self.llm:
            raise RuntimeError("DeepSeek LLM client not initialized")
        return self.llm.chat(prompt)

    def analyze(self, text: str) -> dict:
        """分析文本"""
        if not self.llm:
            raise RuntimeError("DeepSeek LLM client not initialized")
        return {
            "summary": self.llm.chat("请帮我总结以下内容:" + text),
            "keywords": [],
            "sentiment": "neutral",
        }

    def parse_command(self, text: str) -> Dict:
        """解析命令（新增方法）"""
        if self.enabled and self.processor:
            parsed = self.processor.parse(text)
            return asdict(parsed)
        else:
            # 简单的本地解析
            return {
                "raw": text,
                "normalized_command": "未知",
                "intent": "unknown",
                "args": {},
                "explanation": "NLP未启用",
                "confidence": 0,
            }
