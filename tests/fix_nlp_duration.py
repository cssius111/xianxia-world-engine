#!/usr/bin/env python3
"""
🔧 NLP Duration Fix - Modern AI-powered parsing enhancement
Fixes the duration extraction for cultivate commands
"""

import os
import re
import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def apply_nlp_duration_fix():
    """Apply the duration extraction fix to NLP processor"""
    print("🔧 Applying NLP Duration Fix")
    print("━" * 60)
    
    nlp_file = PROJECT_ROOT / "xwe" / "core" / "nlp" / "nlp_processor.py"
    
    if not nlp_file.exists():
        print(f"❌ NLP processor file not found: {nlp_file}")
        return False
    
    print(f"📝 Reading {nlp_file.name}...")
    
    with open(nlp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the cultivate section in _fuzzy_parse
    pattern = r'(# 修炼相关\s*if any\(w in text_lower for w in \["修炼", "修行", "打坐", "练功", "闭关"\]\):)(.*?)(return ParsedCommand\(.*?\))'
    
    def create_fixed_cultivate_section(match):
        prefix = match.group(1)
        return_stmt = match.group(3)
        
        # New implementation with proper duration extraction
        new_body = '''
            # 提取时长
            params = {}
            
            # 匹配各种时长格式
            duration_patterns = [
                (r'(\d+)\s*年', lambda m: f"{m.group(1)}年"),
                (r'(\d+)\s*个?月', lambda m: f"{m.group(1)}月"),
                (r'(\d+)\s*天', lambda m: f"{m.group(1)}天"),
                (r'(\d+)\s*日', lambda m: f"{m.group(1)}日"),
                (r'(\d+)\s*个?小?时', lambda m: f"{m.group(1)}时"),
                (r'一年', lambda m: "1年"),
                (r'两年', lambda m: "2年"),
                (r'三年', lambda m: "3年"),
                (r'半年', lambda m: "6月"),
                (r'一个月', lambda m: "1月"),
                (r'三个月', lambda m: "3月"),
                (r'一天', lambda m: "1天"),
                (r'一日', lambda m: "1日"),
            ]
            
            for pattern, formatter in duration_patterns:
                duration_match = re.search(pattern, text)
                if duration_match:
                    params["duration"] = formatter(duration_match)
                    break
            
            '''
        
        # Update the return statement to use params
        fixed_return = return_stmt.replace(
            'parameters={}',
            'parameters=params'
        ).replace(
            'parameters=params,',
            'parameters=params,'
        )
        
        return prefix + new_body + fixed_return
    
    # Apply the fix
    fixed_content = re.sub(pattern, create_fixed_cultivate_section, content, flags=re.DOTALL)
    
    if fixed_content != content:
        # Backup original
        backup_file = nlp_file.with_suffix('.py.backup_nlp_duration')
        print(f"💾 Creating backup: {backup_file.name}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Write fixed content
        print(f"✏️  Writing fixed content...")
        with open(nlp_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ NLP duration fix applied successfully!")
        return True
    else:
        print("⚠️  Could not find the pattern to fix. Manual intervention needed.")
        print("\nManual fix instructions:")
        print("1. Open xwe/core/nlp/nlp_processor.py")
        print("2. Find the _fuzzy_parse method")
        print("3. In the cultivate section, ensure duration is extracted into params")
        print("4. Make sure ParsedCommand uses parameters=params")
        return False

def test_fix():
    """Test if the fix worked"""
    print("\n🧪 Testing the fix...")
    print("━" * 60)
    
    try:
        from xwe.core.nlp.nlp_processor import NLPProcessor, NLPConfig
        from xwe.core.command_parser import CommandType
        
        config = NLPConfig(enable_llm=False)
        nlp = NLPProcessor(config=config)
        
        test_cases = [
            ("修炼一年", "1年"),
            ("我想修炼3个月", "3月"),
            ("闭关修炼10天", "10天"),
            ("修炼半年", "6月"),
        ]
        
        all_pass = True
        for text, expected_duration in test_cases:
            result = nlp.parse(text)
            
            if result.command_type == CommandType.CULTIVATE:
                actual_duration = result.parameters.get("duration")
                if actual_duration == expected_duration:
                    print(f"✅ '{text}' → duration: {actual_duration}")
                else:
                    print(f"❌ '{text}' → expected: {expected_duration}, got: {actual_duration}")
                    all_pass = False
            else:
                print(f"❌ '{text}' → wrong command type: {result.command_type}")
                all_pass = False
        
        return all_pass
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    print("🚀 NLP Duration Fix Script")
    print("Enhancing natural language processing for cultivation commands\n")
    
    # Apply the fix
    if apply_nlp_duration_fix():
        # Test the fix
        if test_fix():
            print("\n🎉 All tests passed! The fix is working correctly.")
            print("\n📊 Next steps:")
            print("• Run full test suite: python tests/vibe_test_suite.py")
            print("• Run pytest: python -m pytest tests/test_overhaul.py -v")
        else:
            print("\n⚠️  Tests failed. Check the implementation.")
    else:
        print("\n❌ Fix could not be applied automatically.")

if __name__ == "__main__":
    main()
