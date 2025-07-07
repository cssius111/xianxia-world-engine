#!/usr/bin/env python3
"""
XWE DevBuddy 最终优化补丁
解决 DeepSeek API 重试、Mock 模式、Token 保护和日志优化等问题
"""

import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

class XWEOptimizationPatcher:
    """XWE DevBuddy 优化补丁器"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("XWE.Optimizer")
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def apply_optimizations(self) -> bool:
        """应用所有优化"""
        self.logger.info("🚀 开始应用 XWE DevBuddy 优化...")
        
        try:
            # 1. 清理临时文件
            self._cleanup_temporary_files()
            
            # 2. 优化 LLM 客户端
            self._optimize_llm_client()
            
            # 3. 增强 NLP 处理器
            self._enhance_nlp_processor()
            
            # 4. 优化日志配置
            self._optimize_logging_config()
            
            # 5. 更新 run.py
            self._update_run_py()
            
            # 6. 创建 CLI 工具
            self._create_cli_tool()
            
            # 7. 添加测试用例
            self._add_comprehensive_tests()
            
            self.logger.info("✅ 所有优化已成功应用!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 优化应用失败: {e}")
            return False
    
    def _cleanup_temporary_files(self):
        """清理临时文件"""
        self.logger.info("🧹 清理临时文件...")
        
        temp_files = [
            "test_nlp_fix.py",
            "fix_nlp_processor.py",
            "final_hf002_test.py",
            "test_simple_fix.py",
            "verify_fixes.py",
            "verify_hf002_fixes.py",
            "api_fixes.py",
        ]
        
        cleaned_count = 0
        for file_name in temp_files:
            file_path = PROJECT_ROOT / file_name
            if file_path.exists():
                try:
                    file_path.unlink()
                    self.logger.info(f"  🗑️ 已删除: {file_name}")
                    cleaned_count += 1
                except Exception as e:
                    self.logger.warning(f"  ⚠️ 删除失败 {file_name}: {e}")
        
        self.logger.info(f"  📊 清理了 {cleaned_count} 个临时文件")
    
    def _optimize_llm_client(self):
        """优化 LLM 客户端"""
        self.logger.info("⚡ 优化 LLM 客户端...")
        
        llm_client_path = PROJECT_ROOT / "src/xwe/core/nlp/llm_client.py"
        
        # 读取现有文件
        with open(llm_client_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经优化过
        if "USE_MOCK_LLM" in content and "XWE_MAX_LLM_RETRIES" in content:
            self.logger.info("  ✅ LLM 客户端已优化，跳过")
            return
        
        optimized_llm_client = '''"""
DeepSeek API 客户端 - 优化版本
处理与 DeepSeek API 的通信，支持可配置重试和 Mock 模式
"""

import functools
import json
import logging
import os
from time import sleep, time
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

# 尝试导入 backoff，如果不存在则使用简单的重试装饰器
try:
    import backoff
    HAS_BACKOFF = True
except ImportError:
    HAS_BACKOFF = False
    logger.warning("backoff 模块未安装，使用简单重试机制")


def simple_retry(max_tries=3, delay=1.0):
    """简单的重试装饰器（当 backoff 不可用时使用）"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_tries - 1:
                        sleep(delay * (attempt + 1))  # 递增延迟
                    else:
                        raise
            raise last_exception
        return wrapper
    return decorator


class LLMClient:
    """
    DeepSeek API 客户端 - 优化版本
    
    新增功能：
    - 可配置重试次数 (XWE_MAX_LLM_RETRIES)
    - Mock 模式支持 (USE_MOCK_LLM=true)
    - 改进的错误处理和日志记录
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = "https://api.deepseek.com/v1/chat/completions",
        model_name: str = "deepseek-chat",
        timeout: int = 30,
        debug: bool = False,
    ):
        """
        初始化客户端

        Args:
            api_key: API密钥，如果不提供则从环境变量读取
            api_url: API端点URL
            model_name: 模型名称
            timeout: 请求超时时间（秒）
            debug: 是否启用调试模式
        """
        # 检查是否启用 Mock 模式
        self.use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
        
        if self.use_mock:
            logger.info("🎭 LLM Mock 模式已启用，将跳过网络调用")
            self.api_key = "mock_key"
        else:
            self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
            if not self.api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables")

        self.api_url = api_url
        self.model_name = model_name
        self.timeout = timeout
        self.debug = debug
        
        # 可配置的重试次数
        self.max_retries = int(os.getenv("XWE_MAX_LLM_RETRIES", "3"))

        # 请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _make_request_with_retry(self, payload: Dict) -> Dict:
        """发送请求的包装方法"""
        if self.use_mock:
            return self._mock_response(payload)
        
        if HAS_BACKOFF:
            # 使用 backoff 库的高级重试机制
            @backoff.on_exception(
                backoff.expo,
                (requests.exceptions.RequestException, requests.exceptions.Timeout),
                max_tries=self.max_retries,
                max_time=60,
            )
            def _request():
                return self._make_request(payload)
            return _request()
        else:
            # 使用简单重试机制
            @simple_retry(max_tries=self.max_retries, delay=1.0)
            def _request():
                return self._make_request(payload)
            return _request()

    def _mock_response(self, payload: Dict) -> Dict:
        """Mock 响应生成器"""
        # 从 payload 中提取用户消息
        messages = payload.get("messages", [])
        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # 简单的本地解析逻辑
        mock_responses = {
            "探索": {
                "raw": "探索",
                "normalized_command": "探索",
                "intent": "action",
                "args": {},
                "explanation": "Mock模式：探索命令"
            },
            "修炼": {
                "raw": "修炼",
                "normalized_command": "修炼",
                "intent": "train",
                "args": {},
                "explanation": "Mock模式：修炼命令"
            },
            "背包": {
                "raw": "背包",
                "normalized_command": "打开背包",
                "intent": "check",
                "args": {},
                "explanation": "Mock模式：背包命令"
            },
            "状态": {
                "raw": "状态",
                "normalized_command": "查看状态",
                "intent": "check",
                "args": {},
                "explanation": "Mock模式：状态命令"
            }
        }
        
        # 尝试匹配用户输入
        for keyword, response in mock_responses.items():
            if keyword in user_message:
                return {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(response, ensure_ascii=False)
                            }
                        }
                    ]
                }
        
        # 默认响应
        default_response = {
            "raw": user_message,
            "normalized_command": "未知",
            "intent": "unknown",
            "args": {},
            "explanation": "Mock模式：未知命令"
        }
        
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(default_response, ensure_ascii=False)
                    }
                }
            ]
        }

    def _make_request(self, payload: Dict) -> Dict:
        """
        发送请求到 DeepSeek API

        Args:
            payload: 请求载荷

        Returns:
            API响应
        """
        try:
            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.warning(f"Request to DeepSeek API timed out after {self.timeout}s")
            raise

        except requests.exceptions.RequestException as e:
            logger.warning(f"Request to DeepSeek API failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.warning(f"Response status: {e.response.status_code}")
                logger.warning(f"Response body: {e.response.text}")
            raise

    def chat(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 256,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        发送聊天请求

        Args:
            prompt: 用户提示
            temperature: 温度参数（0-1），0表示更确定的输出
            max_tokens: 最大生成token数
            system_prompt: 系统提示（可选）

        Returns:
            模型响应文本
        """
        messages = []

        # 添加系统提示（如果有）
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 添加用户消息
        messages.append({"role": "user", "content": prompt})

        # 构建请求载荷
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # 记录请求（仅在非 Mock 模式下）
        if not self.use_mock:
            logger.debug(
                f"Sending request to DeepSeek API: {json.dumps(payload, ensure_ascii=False)[:200]}..."
            )

        try:
            # 发送请求（带重试）
            start_time = time()
            response = self._make_request_with_retry(payload)
            elapsed = time() - start_time

            if self.use_mock:
                logger.debug(f"Mock response generated in {elapsed:.2f}s")
            else:
                logger.debug(f"DeepSeek API response received in {elapsed:.2f}s")
            
            if self.debug:
                logger.debug(
                    f"DeepSeek full response: {json.dumps(response, ensure_ascii=False)}"
                )

            # 提取响应文本
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0].get("message", {}).get("content", "")
                return content
            else:
                logger.error(f"Unexpected response format: {response}")
                return ""

        except Exception as e:
            logger.error(f"Error calling DeepSeek API: {e}")
            raise

    def chat_with_context(
        self, messages: list, temperature: float = 0.7, max_tokens: int = 256
    ) -> str:
        """
        带上下文的聊天

        Args:
            messages: 消息历史列表，格式为 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大生成token数

        Returns:
            模型响应文本
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = self._make_request_with_retry(payload)
            if self.debug:
                logger.debug(
                    f"DeepSeek full response: {json.dumps(response, ensure_ascii=False)}"
                )

            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0].get("message", {}).get("content", "")
                return content
            else:
                return ""

        except Exception as e:
            logger.error(f"Error in chat_with_context: {e}")
            raise

    def get_embeddings(self, text: str) -> Optional[list]:
        """
        获取文本嵌入向量（如果API支持）

        Args:
            text: 输入文本

        Returns:
            嵌入向量
        """
        # 注意：DeepSeek API可能不支持嵌入功能
        # 这里只是预留接口
        logger.warning("Embeddings API not implemented for DeepSeek")
        return None


# 保持向后兼容
class DeepSeek:
    """向后兼容的DeepSeek类"""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.client = LLMClient(api_key=api_key, model_name=model)

    def chat(self, prompt: str) -> Dict[str, Any]:
        """兼容旧接口"""
        try:
            text = self.client.chat(prompt)
            return {"text": text}
        except Exception as e:
            logger.error(f"Error in legacy chat method: {e}")
            return {"text": ""}
'''
        
        # 写入优化后的 LLM 客户端
        with open(llm_client_path, 'w', encoding='utf-8') as f:
            f.write(optimized_llm_client)
        
        self.logger.info("  ✅ LLM 客户端已优化")
    
    def _enhance_nlp_processor(self):
        """增强 NLP 处理器，添加 Token 长度保护"""
        self.logger.info("🧠 增强 NLP 处理器...")
        
        nlp_processor_path = PROJECT_ROOT / "src/xwe/core/nlp/nlp_processor.py"
        
        # 读取现有文件
        with open(nlp_processor_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经包含 Token 保护
        if "context_limit" in content and "max_prompt_tokens" in content:
            self.logger.info("  ✅ NLP 处理器已增强，跳过")
            return
        
        # 查找并替换 build_prompt 方法
        old_build_prompt = '''    def build_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
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
        
        # 修复: 安全地处理用户输入，避免KeyError
        try:
            # 清理和转义用户输入
            safe_input = self._sanitize_user_input(user_input)
            # 使用字符串替换而不是format，避免KeyError
            return self.prompt_template.replace('"{}"', f'"{safe_input}"')
        except Exception as e:
            logger.warning(f"构建prompt时出错: {e}, 使用回退方案")
            # 如果仍然出错，使用最安全的回退方案
            safe_input = self._sanitize_user_input(user_input) or "未知命令"
            return self.prompt_template.replace('"{}"', f'"{safe_input}"')'''
        
        # 新的带 Token 保护的 build_prompt 方法
        new_build_prompt = '''    def build_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        构建prompt，包含 Token 长度保护

        Args:
            user_input: 用户输入
            context: 上下文信息（可选）

        Returns:
            完整的prompt
        """
        # 这里可以根据context添加更多上下文信息
        # 例如当前位置、已知NPC、可用物品等
        
        # 修复: 安全地处理用户输入，避免KeyError
        try:
            # 清理和转义用户输入
            safe_input = self._sanitize_user_input(user_input)
            
            # 构建基础 prompt
            base_prompt = self.prompt_template.replace('"{}"', f'"{safe_input}"')
            
            # Token 长度保护
            context_limit = self.config.get("context_limit", 4096)  # 默认 4K context
            reserved_tokens = 200  # 为响应预留的 token
            max_prompt_tokens = context_limit - reserved_tokens
            
            # 简单的 token 估算 (1 token ≈ 4 characters for Chinese)
            estimated_tokens = len(base_prompt) // 4
            
            if estimated_tokens > max_prompt_tokens:
                logger.warning(
                    f"Prompt 长度超限: {estimated_tokens} > {max_prompt_tokens} tokens, "
                    f"将截断历史对话"
                )
                
                # 截断策略：保留核心系统提示和当前用户输入
                lines = base_prompt.split('\\n')
                essential_lines = []
                user_input_lines = []
                
                # 提取核心部分
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
                
                # 重新组合，保留核心部分
                truncated_prompt = '\\n'.join(essential_lines + user_input_lines)
                
                # 再次检查长度
                if len(truncated_prompt) // 4 > max_prompt_tokens:
                    # 如果还是太长，使用最小化 prompt
                    truncated_prompt = f\'\'\'你是修仙世界游戏的命令解析器。
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
\'\'\'
                
                logger.info(f"Prompt 已截断至 {len(truncated_prompt) // 4} tokens")
                return truncated_prompt
            
            return base_prompt
            
        except Exception as e:
            logger.warning(f"构建prompt时出错: {e}, 使用回退方案")
            # 如果仍然出错，使用最安全的回退方案
            safe_input = self._sanitize_user_input(user_input) or "未知命令"
            return self.prompt_template.replace('"{}"', f'"{safe_input}"')'''
        
        # 执行替换
        if old_build_prompt in content:
            content = content.replace(old_build_prompt, new_build_prompt)
            
            # 写入更新后的文件
            with open(nlp_processor_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info("  ✅ NLP 处理器已增强")
        else:
            self.logger.warning("  ⚠️ 未找到需要更新的 build_prompt 方法")
    
    def _optimize_logging_config(self):
        """优化日志配置"""
        self.logger.info("📝 优化日志配置...")
        
        logging_config_path = PROJECT_ROOT / "src/logging_config.py"
        
        # 读取现有文件
        with open(logging_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经优化过
        if "verbose: bool = False" in content:
            self.logger.info("  ✅ 日志配置已优化，跳过")
            return
        
        optimized_logging = '''import logging
import os
from logging import Handler
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Dict

LOG_FMT = "%(asctime)s [%(levelname).1s] %(name)s: %(message)s"


class ThrottleFilter(logging.Filter):
    """Filter that limits log output frequency per logger."""

    def __init__(self, interval: float = 10.0) -> None:
        super().__init__()
        self.interval = interval
        self.last_emit: Dict[str, float] = {}

    def filter(self, record: logging.LogRecord) -> bool:
        last = self.last_emit.get(record.name)
        if last is None or record.created - last >= self.interval:
            self.last_emit[record.name] = record.created
            return True
        return False


class ChangeOnlyFilter(logging.Filter):
    """Filter that emits logs only when the message changes."""

    def __init__(self) -> None:
        super().__init__()
        self.last_message: Dict[str, str] = {}

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        last = self.last_message.get(record.name)
        if last != msg:
            self.last_message[record.name] = msg
            return True
        return False


def _add_handler(logger: logging.Logger, handler: Handler) -> None:
    logger.addHandler(handler)


def setup_logging(verbose: bool = False) -> None:
    """
    Configure root logger for the application.
    
    Args:
        verbose: 是否启用详细日志 (DEBUG 级别)
    """
    # 检查环境变量和参数
    debug_env = os.getenv("DEBUG_LOG") in {"1", "true", "True"}
    verbose_env = os.getenv("VERBOSE_LOG") in {"1", "true", "True"}
    
    level = logging.DEBUG if (debug_env or verbose_env or verbose) else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)

    # Remove existing handlers to avoid duplicate logs
    for h in list(root.handlers):
        root.removeHandler(h)

    formatter = logging.Formatter(LOG_FMT, "%H:%M:%S")

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    console.addFilter(ChangeOnlyFilter())
    console.addFilter(ThrottleFilter())
    _add_handler(root, console)

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    debug_file = TimedRotatingFileHandler(log_dir / "app_debug.log", when="D", backupCount=7, encoding="utf-8")
    debug_file.setLevel(logging.DEBUG)
    debug_file.setFormatter(formatter)
    _add_handler(root, debug_file)

    info_file = TimedRotatingFileHandler(log_dir / "app.log", when="D", backupCount=7, encoding="utf-8")
    info_file.setLevel(logging.INFO)
    info_file.setFormatter(formatter)
    _add_handler(root, info_file)
    
    # 优化第三方库日志级别（除非启用详细模式）
    if not verbose:
        # 将 backoff 和 urllib3 日志级别设为 ERROR
        logging.getLogger("backoff").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
        logging.getLogger("requests").setLevel(logging.WARNING)
        
        # 其他可能噪音较多的库
        logging.getLogger("werkzeug").setLevel(logging.WARNING)
        logging.getLogger("flask").setLevel(logging.WARNING)
    else:
        # 详细模式下恢复第三方库的正常日志级别
        logging.getLogger("backoff").setLevel(logging.INFO)
        logging.getLogger("urllib3").setLevel(logging.INFO)
'''
        
        # 写入优化后的日志配置
        with open(logging_config_path, 'w', encoding='utf-8') as f:
            f.write(optimized_logging)
        
        self.logger.info("  ✅ 日志配置已优化")
    
    def _update_run_py(self):
        """更新 run.py 以支持新的日志配置"""
        self.logger.info("🔧 更新 run.py...")
        
        run_py_path = PROJECT_ROOT / "run.py"
        
        # 读取现有文件
        with open(run_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经更新过
        if "verbose_mode" in content:
            self.logger.info("  ✅ run.py 已更新，跳过")
            return
        
        # 查找并替换 setup_logging 调用
        old_setup = '''from logging_config import setup_logging
setup_logging()'''
        
        new_setup = '''from logging_config import setup_logging
# 检查是否启用详细日志
verbose_mode = os.getenv("VERBOSE_LOG", "false").lower() == "true"
setup_logging(verbose=verbose_mode)'''
        
        if old_setup in content:
            content = content.replace(old_setup, new_setup)
            
            # 写入更新后的文件
            with open(run_py_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info("  ✅ run.py 已更新")
        else:
            self.logger.warning("  ⚠️ 未找到需要更新的 setup_logging 调用")
    
    def _create_cli_tool(self):
        """创建 CLI 工具"""
        self.logger.info("🖥️ 创建 CLI 工具...")
        
        cli_tool_path = PROJECT_ROOT / "scripts" / "xwe_cli.py"
        
        # 检查是否已经存在
        if cli_tool_path.exists():
            self.logger.info("  ✅ CLI 工具已存在，跳过")
            return
        
        cli_content = '''#!/usr/bin/env python3
"""
XWE DevBuddy CLI 工具
提供命令行界面，支持 --verbose 选项和 Mock 模式
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from logging_config import setup_logging


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="XWE DevBuddy - 修仙世界引擎开发工具"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="启用详细日志输出 (DEBUG 级别)"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=5001,
        help="服务器端口 (默认: 5001)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用 Flask 调试模式"
    )
    
    parser.add_argument(
        "--mock-llm",
        action="store_true",
        help="启用 LLM Mock 模式"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="LLM API 最大重试次数 (默认: 3)"
    )
    
    args = parser.parse_args()
    
    # 设置环境变量
    if args.verbose:
        os.environ["VERBOSE_LOG"] = "true"
    
    if args.debug:
        os.environ["DEBUG"] = "true"
    
    if args.mock_llm:
        os.environ["USE_MOCK_LLM"] = "true"
    
    if args.max_retries:
        os.environ["XWE_MAX_LLM_RETRIES"] = str(args.max_retries)
    
    # 设置日志
    setup_logging(verbose=args.verbose)
    
    logger = logging.getLogger("XWE.CLI")
    
    # 显示启动信息
    print("=" * 60)
    print("🎮 XWE DevBuddy 启动中...")
    print("=" * 60)
    logger.info(f"📍 端口: {args.port}")
    logger.info(f"🔧 调试模式: {'启用' if args.debug else '禁用'}")
    logger.info(f"📝 详细日志: {'启用' if args.verbose else '禁用'}")
    logger.info(f"🎭 Mock 模式: {'启用' if args.mock_llm else '禁用'}")
    logger.info(f"🔄 最大重试: {args.max_retries}")
    print("=" * 60)
    
    # 设置端口
    os.environ["PORT"] = str(args.port)
    
    # 启动应用
    try:
        # 修改 run.py 中的 setup_logging 调用
        import run
        
        # 直接调用 main
        run.main()
    except KeyboardInterrupt:
        logger.info("👋 服务器已停止")
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
        
        # 写入 CLI 工具
        with open(cli_tool_path, 'w', encoding='utf-8') as f:
            f.write(cli_content)
        
        # 设置执行权限
        os.chmod(cli_tool_path, 0o755)
        
        self.logger.info("  ✅ CLI 工具已创建")
    
    def _add_comprehensive_tests(self):
        """添加综合测试用例"""
        self.logger.info("🧪 添加综合测试用例...")
        
        # 创建测试目录
        test_dir = PROJECT_ROOT / "tests/unit/optimizations"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        e2e_test_dir = PROJECT_ROOT / "tests/e2e/optimizations"
        e2e_test_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. LLM 客户端优化测试
        llm_test_path = test_dir / "test_llm_client_optimizations.py"
        if not llm_test_path.exists():
            llm_test_content = '''"""
LLM 客户端优化功能测试
测试重试次数配置、Mock 模式等新功能
"""

import json
import os
import pytest
from unittest.mock import Mock, patch

from src.xwe.core.nlp.llm_client import LLMClient


class TestLLMClientOptimizations:
    """LLM 客户端优化测试"""
    
    def test_mock_mode_enabled(self):
        """测试 Mock 模式启用"""
        with patch.dict(os.environ, {"USE_MOCK_LLM": "true"}):
            client = LLMClient()
            assert client.use_mock is True
            
            # 测试 Mock 响应
            response = client.chat("探索")
            assert "探索" in response
            
    def test_mock_mode_disabled(self):
        """测试 Mock 模式禁用"""
        with patch.dict(os.environ, {"USE_MOCK_LLM": "false", "DEEPSEEK_API_KEY": "test"}):
            client = LLMClient()
            assert client.use_mock is False
    
    def test_configurable_retries(self):
        """测试可配置重试次数"""
        with patch.dict(os.environ, {"XWE_MAX_LLM_RETRIES": "5", "DEEPSEEK_API_KEY": "test"}):
            client = LLMClient()
            assert client.max_retries == 5
    
    def test_default_retries(self):
        """测试默认重试次数"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test"}, clear=True):
            client = LLMClient()
            assert client.max_retries == 3
    
    def test_mock_response_generation(self):
        """测试 Mock 响应生成"""
        with patch.dict(os.environ, {"USE_MOCK_LLM": "true"}):
            client = LLMClient()
            
            # 测试不同命令的 Mock 响应
            test_cases = [
                ("探索", "探索"),
                ("修炼", "修炼"),
                ("背包", "打开背包"),
                ("状态", "查看状态"),
                ("未知命令xxx", "未知")
            ]
            
            for user_input, expected_command in test_cases:
                response = client.chat(user_input)
                parsed = json.loads(response)
                
                assert parsed["raw"] == user_input
                assert expected_command in parsed["normalized_command"]
'''
            
            with open(llm_test_path, 'w', encoding='utf-8') as f:
                f.write(llm_test_content)
        
        # 2. E2E 集成测试
        e2e_test_path = e2e_test_dir / "test_optimization_integration.py"
        if not e2e_test_path.exists():
            e2e_test_content = '''"""
优化功能 E2E 集成测试
测试 Mock 模式、重试机制的端到端功能
"""

import os
import pytest
from unittest.mock import patch

from src.xwe.core.nlp.nlp_processor import DeepSeekNLPProcessor


class TestOptimizationIntegration:
    """优化功能集成测试"""
    
    def test_mock_mode_end_to_end(self):
        """测试 Mock 模式端到端流程"""
        with patch.dict(os.environ, {"USE_MOCK_LLM": "true"}):
            processor = DeepSeekNLPProcessor()
            
            # 测试完整的解析流程
            test_commands = [
                "探索周围环境",
                "修炼提升实力",
                "查看当前状态",
                "打开背包看看"
            ]
            
            for command in test_commands:
                result = processor.parse(command)
                
                # 验证结果格式
                assert result.raw == command
                assert result.normalized_command is not None
                assert result.intent is not None
                assert isinstance(result.args, dict)
    
    def test_fallback_on_api_failure_simulation(self):
        """测试模拟 API 失败的回退机制"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test"}):
            processor = DeepSeekNLPProcessor()
            
            # 模拟 DeepSeek API 调用失败
            with patch.object(processor, '_call_deepseek_api', side_effect=Exception("API Error")):
                result = processor.parse("探索")
                
                # 应该回退到本地解析
                assert result.normalized_command == "探索"
                assert result.intent == "action"
                assert result.confidence == 0.5  # 回退模式置信度
'''
            
            with open(e2e_test_path, 'w', encoding='utf-8') as f:
                f.write(e2e_test_content)
        
        # 3. 创建测试配置
        for test_dir_path in [test_dir, e2e_test_dir]:
            conftest_path = test_dir_path / "conftest.py"
            if not conftest_path.exists():
                conftest_content = '''"""
优化功能测试配置
"""

import pytest
import os
import sys
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """项目根目录"""
    return Path(__file__).parent.parent.parent.parent


@pytest.fixture(autouse=True)
def setup_test_env(project_root):
    """设置测试环境"""
    # 添加 src 目录到 Python 路径
    src_path = str(project_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
'''
                
                with open(conftest_path, 'w', encoding='utf-8') as f:
                    f.write(conftest_content)
        
        self.logger.info("  ✅ 综合测试用例已添加")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="XWE DevBuddy 优化补丁")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 创建补丁器
    patcher = XWEOptimizationPatcher(verbose=args.verbose)
    
    # 应用优化
    if patcher.apply_optimizations():
        patcher.logger.info("🎉 优化应用成功!")
        
        # 输出使用说明
        print("\n" + "="*60)
        print("📖 优化功能使用说明:")
        print("="*60)
        print("1. 使用新的 CLI 工具:")
        print("   python scripts/xwe_cli.py --verbose")
        print("   python scripts/xwe_cli.py --mock-llm --max-retries 5")
        print("")
        print("2. 环境变量配置:")
        print("   export USE_MOCK_LLM=true      # 启用 Mock 模式")
        print("   export XWE_MAX_LLM_RETRIES=5  # 设置重试次数")
        print("   export VERBOSE_LOG=true       # 启用详细日志")
        print("")
        print("3. 运行优化测试:")
        print("   pytest tests/unit/optimizations/ -v")
        print("   pytest tests/e2e/optimizations/ -v")
        print("")
        print("4. 功能特性:")
        print("   ✅ 可配置 API 重试次数")
        print("   ✅ Mock 模式跳过网络调用")
        print("   ✅ Token 长度自动保护")
        print("   ✅ 优化的日志级别控制")
        print("   ✅ CLI 详细模式支持")
        print("="*60)
        
        return True
    else:
        patcher.logger.error("❌ 优化应用失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
