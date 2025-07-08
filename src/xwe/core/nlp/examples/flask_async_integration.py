"""
Flask 路由异步集成示例
展示如何在 Flask 应用中使用 LLMClient 的异步功能
"""

import asyncio
import time
from functools import wraps
from flask import Flask, jsonify, request
from concurrent.futures import ThreadPoolExecutor

from src.xwe.core.nlp.llm_client import LLMClient
from src.xwe.core.nlp.async_utils import AsyncHelper


# 创建 Flask 应用（示例用）
app = Flask(__name__)

# 全局 LLM 客户端
llm_client = None

# 用于在 Flask 中运行异步函数的装饰器
def async_route(f):
    """装饰器：在 Flask 路由中运行异步函数"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


@app.before_first_request
def initialize():
    """初始化 LLM 客户端"""
    global llm_client
    llm_client = LLMClient()
    print("LLM 客户端已初始化")


@app.teardown_appcontext
def cleanup(error):
    """清理资源"""
    if llm_client:
        llm_client.cleanup()


# 示例路由 1：单个异步请求
@app.route('/api/chat', methods=['POST'])
@async_route
async def chat_endpoint():
    """
    异步聊天端点
    
    请求体:
    {
        "message": "用户消息",
        "temperature": 0.7,
        "max_tokens": 150
    }
    """
    data = request.get_json()
    message = data.get('message', '')
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 150)
    
    if not message:
        return jsonify({'error': '消息不能为空'}), 400
    
    try:
        # 异步调用 LLM
        start_time = time.time()
        response = await llm_client.chat_async(
            message,
            temperature=temperature,
            max_tokens=max_tokens
        )
        duration = time.time() - start_time
        
        return jsonify({
            'response': response,
            'duration': duration,
            'tokens': len(response) // 2  # 简单估算
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 示例路由 2：批量处理
@app.route('/api/batch_parse', methods=['POST'])
@async_route
async def batch_parse_endpoint():
    """
    批量解析玩家命令
    
    请求体:
    {
        "commands": ["命令1", "命令2", "命令3"]
    }
    """
    data = request.get_json()
    commands = data.get('commands', [])
    
    if not commands:
        return jsonify({'error': '命令列表不能为空'}), 400
    
    try:
        # 并发处理所有命令
        async def parse_command(cmd):
            prompt = f"解析游戏命令：{cmd}"
            return {
                'command': cmd,
                'parsed': await llm_client.chat_async(prompt, temperature=0.0)
            }
        
        start_time = time.time()
        tasks = [parse_command(cmd) for cmd in commands]
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        return jsonify({
            'results': results,
            'total_duration': duration,
            'average_duration': duration / len(commands)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 示例路由 3：上下文对话
@app.route('/api/conversation', methods=['POST'])
@async_route
async def conversation_endpoint():
    """
    带上下文的对话
    
    请求体:
    {
        "messages": [
            {"role": "user", "content": "消息1"},
            {"role": "assistant", "content": "回复1"}
        ],
        "new_message": "新消息"
    }
    """
    data = request.get_json()
    messages = data.get('messages', [])
    new_message = data.get('new_message', '')
    
    if not new_message:
        return jsonify({'error': '新消息不能为空'}), 400
    
    try:
        # 添加新消息到对话历史
        messages.append({"role": "user", "content": new_message})
        
        # 异步获取回复
        response = await llm_client.chat_with_context_async(
            messages,
            temperature=0.7
        )
        
        # 更新对话历史
        messages.append({"role": "assistant", "content": response})
        
        return jsonify({
            'response': response,
            'conversation': messages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 示例路由 4：性能测试
@app.route('/api/performance_test', methods=['GET'])
@async_route
async def performance_test_endpoint():
    """
    性能测试端点
    
    查询参数:
    - count: 测试请求数量（默认10）
    - concurrent: 是否并发（默认true）
    """
    count = int(request.args.get('count', 10))
    concurrent = request.args.get('concurrent', 'true').lower() == 'true'
    
    test_prompts = [f"测试消息 {i}" for i in range(count)]
    
    try:
        if concurrent:
            # 并发测试
            start_time = time.time()
            tasks = [llm_client.chat_async(p) for p in test_prompts]
            results = await asyncio.gather(*tasks)
            duration = time.time() - start_time
            mode = "并发"
        else:
            # 串行测试
            start_time = time.time()
            results = []
            for p in test_prompts:
                result = await llm_client.chat_async(p)
                results.append(result)
            duration = time.time() - start_time
            mode = "串行"
        
        return jsonify({
            'mode': mode,
            'count': count,
            'total_duration': duration,
            'average_duration': duration / count,
            'qps': count / duration
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 示例：在现有同步路由中使用异步功能
@app.route('/api/mixed_sync_async', methods=['POST'])
def mixed_endpoint():
    """
    在同步路由中调用异步功能
    
    演示如何在不改变路由结构的情况下使用异步功能
    """
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': '消息不能为空'}), 400
    
    try:
        # 方法1：使用 run_async_in_sync
        from src.xwe.core.nlp.async_utils import AsyncHelper
        response = AsyncHelper.run_async_in_sync(
            llm_client.chat_async(message)
        )
        
        # 方法2：使用线程池（适合多个异步调用）
        # with ThreadPoolExecutor() as executor:
        #     future = executor.submit(asyncio.run, llm_client.chat_async(message))
        #     response = future.result()
        
        return jsonify({
            'response': response,
            'method': 'sync_route_with_async_call'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 健康检查
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'llm_client_initialized': llm_client is not None,
        'thread_pool_active': llm_client._executor_initialized if llm_client else False
    })


# 示例：创建异步任务队列
class AsyncTaskQueue:
    """简单的异步任务队列"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.results = {}
        self.running = False
    
    async def worker(self):
        """工作线程"""
        while self.running:
            try:
                task_id, prompt = await asyncio.wait_for(
                    self.queue.get(), 
                    timeout=1.0
                )
                
                # 处理任务
                result = await llm_client.chat_async(prompt)
                self.results[task_id] = {
                    'status': 'completed',
                    'result': result
                }
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.results[task_id] = {
                    'status': 'failed',
                    'error': str(e)
                }
    
    def start(self):
        """启动工作线程"""
        self.running = True
        asyncio.create_task(self.worker())
    
    def stop(self):
        """停止工作线程"""
        self.running = False
    
    async def submit(self, task_id, prompt):
        """提交任务"""
        await self.queue.put((task_id, prompt))
        self.results[task_id] = {'status': 'pending'}
        return task_id
    
    def get_result(self, task_id):
        """获取结果"""
        return self.results.get(task_id, {'status': 'not_found'})


# 使用任务队列的示例
task_queue = AsyncTaskQueue()


@app.route('/api/async_task', methods=['POST'])
@async_route
async def submit_async_task():
    """提交异步任务"""
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'prompt 不能为空'}), 400
    
    # 生成任务 ID
    import uuid
    task_id = str(uuid.uuid4())
    
    # 提交任务
    await task_queue.submit(task_id, prompt)
    
    return jsonify({
        'task_id': task_id,
        'status': 'submitted'
    })


@app.route('/api/async_task/<task_id>', methods=['GET'])
def get_async_task_result(task_id):
    """获取异步任务结果"""
    result = task_queue.get_result(task_id)
    return jsonify(result)


if __name__ == '__main__':
    print("""
    Flask + LLMClient 异步集成示例
    
    可用端点:
    - POST /api/chat - 单个聊天请求
    - POST /api/batch_parse - 批量解析命令
    - POST /api/conversation - 上下文对话
    - GET /api/performance_test - 性能测试
    - POST /api/mixed_sync_async - 同步路由中的异步调用
    - POST /api/async_task - 提交异步任务
    - GET /api/async_task/<task_id> - 获取任务结果
    - GET /health - 健康检查
    
    注意：这只是示例代码，实际使用时需要根据项目结构调整
    """)
    
    # 注意：实际项目中应该使用 create_app() 函数
    # 这里只是演示目的
    app.run(debug=True)
