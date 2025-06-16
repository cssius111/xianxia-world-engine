#!/usr/bin/env python3
"""
🚀 Quick Status Check for XianXia World Engine
"""

import os

# Add project to path

def check_status():
    """Quick status check"""
    print("🌟 XianXia World Engine - Quick Status")
    print("═" * 50)
    
    # Test imports
    print("\n📦 Module Imports:")
    try:
        from xwe.core import GameCore
        from xwe.npc import DialogueSystem
        from xwe.core.nlp.nlp_processor import NLPProcessor
        from xwe.npc.emotion_system import EmotionState
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
    
    # Test NLP
    print("\n🧠 NLP Duration Test:")
    try:
        from xwe.core.nlp.nlp_processor import NLPProcessor, NLPConfig
        config = NLPConfig(enable_llm=False)
        nlp = NLPProcessor(config=config)
        
        result = nlp.parse("修炼一年")
        duration = result.parameters.get("duration")
        if duration:
            print(f"✅ Duration extraction working: {duration}")
        else:
            print("❌ Duration not extracted")
    except Exception as e:
        print(f"❌ NLP test error: {e}")
    
    # Check API config
    print("\n🔌 API Configuration:")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if "your_deepseek_api_key_here" in content:
                print("⚠️  API key is placeholder (mock mode)")
            else:
                print("✅ API key configured")
    
    print("\n💡 Run 'python tests/vibe_test_suite.py' for full status")
    print("═" * 50)

if __name__ == "__main__":
    check_status()
