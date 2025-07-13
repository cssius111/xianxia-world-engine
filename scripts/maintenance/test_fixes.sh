#!/bin/bash
# 运行特定的失败测试来验证修复

echo "测试 NLP Processor..."
pytest tests/unit/test_nlp_processor.py::TestNLPProcessor::test_invalid_response_handling -v

echo -e "\n测试 Context Compressor..."
pytest tests/unit/test_context_compressor.py::TestContextCompressor::test_message_deduplication -v
pytest tests/unit/test_context_compressor.py::TestCompressionStrategies::test_sliding_window_strategy -v  
pytest tests/unit/test_context_compressor.py::TestCompressionStrategies::test_hybrid_strategy -v

echo -e "\n测试 Async Utils..."
pytest tests/unit/test_async_utils.py::TestAsyncRequestQueue::test_blocking_operations -v
pytest tests/unit/test_async_utils.py::TestRateLimiter::test_burst_handling -v

echo -e "\n测试 API 兼容性..."
pytest tests/regression/test_nlp_regression.py::TestNLPRegression::test_api_compatibility -v

echo -e "\n测试 E2E..."
pytest tests/e2e/test_nlp_e2e.py::TestNLPEndToEnd::test_complete_user_journey -v
