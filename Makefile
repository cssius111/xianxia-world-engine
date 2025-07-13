# 修仙世界引擎 Makefile

.PHONY: help test test-fast test-nlp test-context test-async report coverage clean

help:
	@echo "修仙世界引擎 - 可用命令:"
	@echo "  make test       - 运行所有测试"
	@echo "  make test-fast  - 运行快速测试"
	@echo "  make test-nlp   - 运行 NLP 测试"
	@echo "  make test-context - 运行上下文压缩测试"
	@echo "  make test-async - 运行异步工具测试"
	@echo "  make report     - 生成测试报告"
	@echo "  make coverage   - 生成覆盖率报告"
	@echo "  make clean      - 清理临时文件"


test:
	@echo "运行所有测试..."
	@pytest -v

test-fast:
	@echo "运行快速测试..."
	@pytest -v -m "not slow and not flaky"

test-nlp:
	@echo "运行 NLP 测试..."
	@python scripts/maintenance/run_tests.py nlp

test-context:
	@echo "运行上下文压缩测试..."
	@python scripts/maintenance/run_tests.py context

test-async:
	@echo "运行异步工具测试..."
	@python scripts/maintenance/run_tests.py async

report:
	@echo "生成测试报告..."
	@python scripts/maintenance/validate_fixes.py

coverage:
	@echo "生成覆盖率报告..."
	@pytest --cov=xwe --cov-report=html --cov-report=term
	@echo "HTML 报告: htmlcov/index.html"

clean:
	@echo "清理临时文件..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name ".pytest_cache" -delete
	@rm -rf htmlcov/
	@rm -f .coverage
	@rm -f fix_report.json
	@echo "清理完成!"

# 快捷命令
t: test
tf: test-fast
r: report
c: coverage
