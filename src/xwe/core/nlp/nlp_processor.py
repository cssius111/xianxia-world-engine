"""
修仙世界引擎 - DeepSeek MCP 命令解析器
基于 DeepSeek API 的自然语言指令处理模块
"""

import json
import logging
import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import time
from functools import lru_cache

from .llm_client import LLMClient
from .config import get_nlp_config
from .monitor import get_nlp_monitor
from . import tool_router
from ..context import ContextCompressor

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
        use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
        if not api_key and not use_mock:
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
        
        # 初始化上下文压缩器
        context_config = self.config.get("context_compression", {})
        if context_config.get("enabled", True):
            try:
                self.context_compressor = ContextCompressor(
                    llm_client=self.llm,
                    window_size=context_config.get("window_size", 20),
                    block_size=context_config.get("block_size", 30),
                    max_memory_blocks=context_config.get("max_memory_blocks", 10),
                    enable_compression=True
                )
                logger.info("上下文压缩器已启用")
            except Exception as e:
                logger.warning(f"初始化上下文压缩器失败: {e}，将使用传统模式")
                self.context_compressor = None
        else:
            self.context_compressor = None
            logger.info("上下文压缩已禁用")

        logger.info(f"DeepSeekNLPProcessor 初始化完成 (缓存大小: {self._cache_size})")
        
        # 历史记录（用于不支持压缩时的降级方案）
        self._conversation_history = []

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
        构建prompt，集成上下文压缩功能

        Args:
            user_input: 用户输入
            context: 上下文信息（可选）

        Returns:
            完整的prompt
        """
        # 安全地处理用户输入
        safe_input = self._sanitize_user_input(user_input)
        
        # 如果启用了上下文压缩器
        if self.context_compressor:
            try:
                # 将当前输入添加到压缩器
                self.context_compressor.append(f"用户: {safe_input}")
                
                # 获取压缩后的上下文
                compressed_context = self.context_compressor.get_context()
                
                # 构建带上下文的 prompt
                context_prompt = f"""你是"修仙世界"游戏的命令解析器模块，需要将玩家发来的中文自然语言指令解析为结构化 JSON 格式。

# 如果有上下文，显示以下内容
=== 对话上下文 ===
{compressed_context}

=== 当前输入 ===
输入: "{safe_input}"

请根据上下文和当前输入，输出符合以下格式的 JSON：
{{
  "raw": "<玩家原始输入>",
  "normalized_command": "<标准命令词>",
  "intent": "<意图类别>",
  "args": {{
    // 可选字段，根据指令提取
  }},
  "explanation": "<简短解析依据>"
}}

仅输出 JSON，不要任何多余文本。
输出:
"""
                
                # 检查长度
                context_limit = self.config.get("context_limit", 4096)
                estimated_tokens = len(context_prompt) // 4
                
                if estimated_tokens > context_limit - 200:
                    logger.warning(f"即使压缩后，prompt 仍然过长: {estimated_tokens} tokens")
                    # 可以进一步处理，但现在先保持简单
                
                return context_prompt
                
            except Exception as e:
                logger.warning(f"使用压缩器时出错: {e}，回退到传统模式")
                # 回退到传统模式
        
        # 传统模式（无压缩或压缩失败时）
        try:
            # 添加到历史记录
            self._conversation_history.append(f"用户: {safe_input}")
            if len(self._conversation_history) > 50:  # 限制历史长度
                self._conversation_history = self._conversation_history[-30:]
            
            # 构建基础 prompt
            base_prompt = self.prompt_template.replace('"{}"', f'"{safe_input}"')
            
            # Token 长度保护
            context_limit = self.config.get("context_limit", 4096)
            reserved_tokens = 200
            max_prompt_tokens = context_limit - reserved_tokens
            
            estimated_tokens = len(base_prompt) // 4
            
            if estimated_tokens > max_prompt_tokens:
                logger.warning(
                    f"Prompt 长度超限: {estimated_tokens} > {max_prompt_tokens} tokens, "
                    f"将截断历史对话"
                )
                
                # 截断策略
                lines = base_prompt.split('\n')
                essential_lines = []
                user_input_lines = []
                
                in_examples = False
                for line in lines:
                    if '### 示例：' in line:
                        in_examples = True
                        continue
                    elif f'输入: "{safe_input}"' in line:
                        in_examples = False
                        user_input_lines.extend(lines[lines.index(line):])
                        break
                    elif not in_examples:
                        essential_lines.append(line)
                
                truncated_prompt = '\n'.join(essential_lines + user_input_lines)
                
                if len(truncated_prompt) // 4 > max_prompt_tokens:
                    truncated_prompt = f'''你是修仙世界游戏的命令解析器。
将用户输入转换为JSON格式：
{{
  "raw": "<用户输入>",
  "normalized_command": "<标准命令>",
  "intent": "<意图>",
  "args": {{}},
  "explanation": "<说明>"
}}

输入: "{safe_input}"
输出:
'''
                
                logger.info(f"Prompt 已截断至 {len(truncated_prompt) // 4} tokens")
                return truncated_prompt
            
            return base_prompt
            
        except Exception as e:
            logger.warning(f"构建prompt时出错: {e}, 使用回退方案")
            safe_input = self._sanitize_user_input(user_input) or "未知命令"
            return self.prompt_template.replace('"{}"', f'"{safe_input}"')
    
    def _sanitize_user_input(self, user_input: str) -> str:
        """
        清理和转义用户输入，防止格式化错误
        
        Args:
            user_input: 原始用户输入
            
        Returns:
            清理后的用户输入
        """
        if not user_input:
            return ""
        
        try:
            # 1. 确保输入是字符串
            cleaned = str(user_input).strip()
            
            # 2. 移除或替换可能导致问题的字符
            # 移除控制字符（包括换行符、制表符等）
            cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', cleaned)
            
            # 3. 转义可能导致JSON解析问题的字符
            # 转义反斜杠
            cleaned = cleaned.replace('\\', '\\\\')
            # 转义双引号
            cleaned = cleaned.replace('"', '\\"')
            # 移除花括号，防止被误解为格式化占位符
            cleaned = cleaned.replace('{', '').replace('}', '')
            
            # 4. 清理多余的空白字符
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
            # 5. 限制长度防止过长输入
            if len(cleaned) > 500:
                cleaned = cleaned[:500] + "..."
            
            # 6. 如果清理后为空，返回默认值
            if not cleaned:
                cleaned = "未知命令"
                
            return cleaned
            
        except Exception as e:
            logger.warning(f"清理用户输入时出错: {e}")
            return "未知命令"

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
            
            # 检查空响应
            if not response or response.strip() == '':
                logger.error("DeepSeek API 返回空响应")
                # 返回一个默认的 JSON 响应而不是抛出异常
                return json.dumps({
                    "raw": prompt.split('"')[-2] if '"' in prompt else "未知命令",
                    "normalized_command": "未知",
                    "intent": "unknown",
                    "args": {},
                    "explanation": "API返回空响应"
                })

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
            
            # 再次检查是否为空
            if not response:
                logger.error("处理后的响应为空")
                raise ValueError("Processed response is empty")

            logger.debug(f"DeepSeek sanitized JSON: {response}")

            # 验证JSON格式
            try:
                json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}, 响应内容: {response}")
                raise

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
            # 确保 raw 始终是用户的原始输入
            parsed = ParsedCommand(
                raw=user_input,  # 使用原始用户输入而不是 API 返回的值
                normalized_command=result["normalized_command"],
                intent=result["intent"],
                args=result.get("args", {}),
                explanation=result.get("explanation", ""),
                confidence=result.get("confidence", 1.0),
            )
            logger.info(f"Parsed command: {parsed}")
            
            # 将系统响应添加到上下文（如果启用了压缩器）
            if self.context_compressor:
                response_msg = f"系统: 解析为{parsed.normalized_command}命令 ({parsed.explanation})"
                self.context_compressor.append(response_msg)
            elif hasattr(self, '_conversation_history'):
                response_msg = f"系统: 解析为{parsed.normalized_command}命令"
                self._conversation_history.append(response_msg)

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
                
                # 获取压缩器统计（如果可用）
                context_stats = {}
                if self.context_compressor:
                    context_stats = self.context_compressor.get_stats()
                
                monitor = get_nlp_monitor()
                monitor.record_request(
                    command=user_input,
                    handler=(
                        parsed.normalized_command if "parsed" in locals() else "unknown"
                    ),
                    duration=duration,
                    success=success,
                    confidence=parsed.confidence if "parsed" in locals() else 0,
                    use_cache=use_cache and not use_fallback,
                    error=error_msg,
                    token_count=context_stats.get("estimated_total_tokens", 0),
                    context_compression_enabled=self.context_compressor is not None,
                    context_compression_ratio=context_stats.get("compression_ratio", 1.0)
                )

    def _validate_result(self, result: Dict) -> bool:
        """验证解析结果格式"""
        required_fields = ["normalized_command", "intent"]
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
    
    def clear_context(self) -> None:
        """清空上下文压缩器和历史记录"""
        if self.context_compressor:
            self.context_compressor.clear()
            logger.info("上下文压缩器已清空")
        self._conversation_history.clear()
        logger.info("对话历史已清空")
    
    def get_context_stats(self) -> Dict[str, Any]:
        """获取上下文压缩器统计信息"""
        if self.context_compressor:
            return self.context_compressor.get_stats()
        else:
            return {
                "enabled": False,
                "conversation_history_length": len(self._conversation_history)
            }
    
    def save_context_memory(self, filepath: str) -> bool:
        """
        保存上下文记忆到文件
        
        Args:
            filepath: 保存路径
            
        Returns:
            是否成功
        """
        if not self.context_compressor:
            logger.warning("上下文压缩器未启用")
            return False
        
        try:
            memory_data = self.context_compressor.export_memory()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
            logger.info(f"上下文记忆已保存到 {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存上下文记忆失败: {e}")
            return False
    
    def load_context_memory(self, filepath: str) -> bool:
        """
        从文件加载上下文记忆
        
        Args:
            filepath: 加载路径
            
        Returns:
            是否成功
        """
        if not self.context_compressor:
            logger.warning("上下文压缩器未启用")
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            self.context_compressor.import_memory(memory_data)
            logger.info(f"从 {filepath} 加载上下文记忆")
            return True
        except Exception as e:
            logger.error(f"加载上下文记忆失败: {e}")
            return False


# 保持向后兼容
class NLPProcessor:
    """向后兼容的 NLP 处理器包装器"""

    def __init__(self, use_context_compression: bool = False):
        """初始化 NLPProcessor

        Args:
            use_context_compression: 是否启用上下文压缩器
        """
        config = get_nlp_config()
        api_key = config.get_api_key()

        self.processor: Optional[DeepSeekNLPProcessor] = None
        self.enabled = False
        self.llm_client: Optional[LLMClient] = None
        self.context_compressor: Optional[ContextCompressor] = None

        if config.is_enabled() and config.validate_config() and api_key:
            try:
                self.processor = DeepSeekNLPProcessor(api_key=api_key)
                if not use_context_compression:
                    self.processor.context_compressor = None
                self.llm_client = self.processor.llm
                self.context_compressor = self.processor.context_compressor
                self.enabled = True
            except Exception as e:  # pragma: no cover - initialization failure
                logger.error(f"初始化DeepSeekNLPProcessor失败: {e}")
        else:
            logger.warning("\u26a0\ufe0f DeepSeek NLP disabled (missing or invalid API key)")

        if self.llm_client is None and api_key:
            self.llm_client = LLMClient(api_key=api_key)

    def process(self, user_input: Any, context: Optional[List[Dict[str, Any]]] = None, 
               max_tokens: Optional[int] = None, temperature: Optional[float] = None,
               **kwargs) -> Dict[str, Any]:
        """高层封装，返回 dict 结果
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            max_tokens: 最大token数限制
            temperature: 温度参数
            **kwargs: 其他参数
            
        Returns:
            解析结果字典
        """

        try:
            text = str(user_input) if user_input is not None else ""
        except Exception:  # pragma: no cover
            text = ""

        if not text.strip():
            return {
                "raw": text,
                "normalized_command": text.strip(),
                "intent": "unknown",
                "args": {},
                "explanation": "empty input",
            }

        if self.processor and self.enabled:
            try:
                if self.llm_client is not None:
                    self.processor.llm = self.llm_client
                parsed = self.processor.parse(text, context=context)
                return asdict(parsed)
            except Exception as e:  # pragma: no cover - error path
                logger.error(f"处理命令时出错: {e}")

        # 简单回退
        return {
            "raw": text,
            "normalized_command": text,
            "intent": "unknown",
            "args": {},
            "explanation": "NLP disabled",
        }

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
            # 在成功解析后分派到工具
            tool_router.dispatch(parsed.normalized_command, parsed.args)
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
