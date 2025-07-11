#!/bin/bash
# 运行特定的失败测试来验证修复

echo "运行 ContextCompressor 测试..."
python -m pytest tests/unit/test_context_compressor.py -v

echo -e "\n运行 Status 端点测试..."
python -m pytest tests/unit/test_status.py -v

echo -e "\n运行 NLP Processor 测试..."
python -m pytest tests/unit/test_nlp_processor.py -v

echo -e "\n运行 DeepSeek 异步客户端测试..."
python scripts/run_async_tests.py

echo -e "\n运行所有测试并统计..."
python -m pytest tests/ -v --tb=short | tail -20
