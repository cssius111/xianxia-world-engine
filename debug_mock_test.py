#!/usr/bin/env python3
"""Debug the mock test"""

import os
from unittest.mock import patch

# Setup environment
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dotenv import load_dotenv
load_dotenv()

# Test the mock mode
with patch.dict(os.environ, {"USE_MOCK_LLM": "true"}):
    from src.xwe.core.nlp.nlp_processor import DeepSeekNLPProcessor
    
    processor = DeepSeekNLPProcessor()
    
    # Test the exact command from the test
    test_commands = [
        "探索周围环境",
        "修炼提升实力",
        "查看当前状态",
        "打开背包看看"
    ]
    
    for command in test_commands:
        print(f"\nTesting command: '{command}'")
        
        # Build the prompt to see what's actually being sent
        prompt = processor.build_prompt(command)
        print(f"Prompt last line: {prompt.split('输入:')[-1][:100]}")
        
        result = processor.parse(command)
        print(f"Result: raw='{result.raw}', normalized='{result.normalized_command}', intent='{result.intent}'")
