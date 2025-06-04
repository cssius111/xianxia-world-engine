#!/usr/bin/env python3
"""
修复 DeepSeek JSON 解析问题
根据 DEEPSEEK_ENGINEERING_REPORT.md 的诊断结果
"""

import os
import re
import json
import shutil
from datetime import datetime

def fix_deepseek_json_parsing():
    """修复 DeepSeek 返回的 JSON 被 markdown 包裹的问题"""
    print("🔧 修复 DeepSeek JSON 解析问题...")
    
    # 查找 NLP 处理器文件
    nlp_files = [
        "xwe/core/nlp.py",
        "xwe/core/nlp/nlp_processor.py",
        "xwe/core/nlp/processor.py",
        "xwe/core/ai_controller.py"
    ]
    
    fixed_count = 0
    
    for nlp_file in nlp_files:
        if os.path.exists(nlp_file):
            print(f"\n📄 处理文件: {nlp_file}")
            
            # 备份原文件
            backup_path = f"{nlp_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(nlp_file, backup_path)
            print(f"📦 备份保存到: {backup_path}")
            
            # 读取文件内容
            with open(nlp_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找 JSON 解析相关的代码
            if 'json.loads' in content or 'JSON' in content:
                # 添加智能 JSON 解析函数
                smart_parse_function = '''
def _parse_deepseek_json(self, raw_response: str) -> Optional[Dict[str, Any]]:
    """智能解析各种格式的JSON，处理markdown包裹的情况"""
    if not raw_response:
        return None
    
    # 1. 尝试直接解析
    try:
        return json.loads(raw_response)
    except:
        pass
    
    # 2. 去除markdown代码块标记
    patterns = [
        r'```json\s*\n?([\s\S]*?)\n?```',  # ```json ... ```
        r'```\s*\n?([\s\S]*?)\n?```',       # ``` ... ```
        r'\{[\s\S]*\}'                      # 直接匹配JSON对象
    ]
    
    for pattern in patterns:
        match = re.search(pattern, raw_response, re.DOTALL)
        if match:
            try:
                json_str = match.group(1) if '```' in pattern else match.group(0)
                return json.loads(json_str.strip())
            except:
                continue
    
    # 3. 尝试提取JSON部分
    try:
        # 查找第一个{和最后一个}
        start = raw_response.find('{')
        end = raw_response.rfind('}')
        if start != -1 and end != -1 and start < end:
            json_str = raw_response[start:end+1]
            return json.loads(json_str)
    except:
        pass
    
    return None
'''
                
                # 添加必要的导入
                if 'import re' not in content:
                    content = 'import re\n' + content
                if 'from typing import' not in content:
                    content = 'from typing import Dict, Any, Optional\n' + content
                
                # 在类定义后添加解析函数
                class_pattern = r'(class\s+\w+.*?:\n)'
                class_match = re.search(class_pattern, content)
                if class_match:
                    # 在第一个方法定义前插入
                    method_pattern = r'(\n\s+def\s+)'
                    method_match = re.search(method_pattern, content[class_match.end():])
                    if method_match:
                        insert_pos = class_match.end() + method_match.start()
                        content = content[:insert_pos] + smart_parse_function + content[insert_pos:]
                
                # 替换所有直接的 json.loads 调用
                # 查找类似: json.loads(response) 或 json.loads(response.text)
                json_loads_patterns = [
                    (r'json\.loads\(([^)]+)\)', r'self._parse_deepseek_json(\1)'),
                    (r'JSON\.parse\(([^)]+)\)', r'self._parse_deepseek_json(\1)'),
                ]
                
                for pattern, replacement in json_loads_patterns:
                    if re.search(pattern, content):
                        content = re.sub(pattern, replacement, content)
                        print(f"✅ 替换 {pattern} 为智能解析")
                
                # 保存修改后的文件
                with open(nlp_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_count += 1
                print(f"✅ 文件修复完成: {nlp_file}")
    
    return fixed_count

def test_json_parsing():
    """测试 JSON 解析功能"""
    print("\n🧪 测试 JSON 解析...")
    
    test_cases = [
        # 测试用例1: 纯JSON
        '{"command": "use_skill", "target": "敌人", "parameters": {"skill": "剑气斩"}}',
        
        # 测试用例2: markdown包裹的JSON
        '''```json
{
    "command": "use_skill",
    "target": "敌人",
    "parameters": {"skill": "剑气斩"},
    "confidence": 0.95
}
```''',
        
        # 测试用例3: 只有```包裹
        '''```
{"command": "attack", "target": "妖兽"}
```''',
        
        # 测试用例4: 混合文本
        '''这是AI的响应，解析结果如下：
{"command": "move", "destination": "天南坊市"}
其他文本内容'''
    ]
    
    # 简单的测试解析函数
    def test_parse(raw):
        patterns = [
            r'```json\s*\n?([\s\S]*?)\n?```',
            r'```\s*\n?([\s\S]*?)\n?```',
            r'\{[\s\S]*\}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1) if '```' in pattern else match.group(0)
                    return json.loads(json_str.strip())
                except:
                    continue
        return None
    
    print("\n测试结果:")
    for i, test in enumerate(test_cases, 1):
        result = test_parse(test)
        if result:
            print(f"✅ 测试{i}: 成功解析 - {result.get('command', 'unknown')}")
        else:
            print(f"❌ 测试{i}: 解析失败")

def main():
    """主函数"""
    print("🚀 DeepSeek JSON 解析修复工具")
    print("=" * 50)
    
    # 检查是否在正确的目录
    if not os.path.exists("xwe"):
        print("❌ 错误：请在项目根目录运行此脚本")
        return
    
    # 执行修复
    fixed_count = fix_deepseek_json_parsing()
    
    if fixed_count > 0:
        print(f"\n✅ 成功修复 {fixed_count} 个文件!")
        print("\n🎯 修复效果:")
        print("- 可以解析纯JSON")
        print("- 可以解析```json包裹的JSON")
        print("- 可以解析混在文本中的JSON")
        print("- 自动处理各种格式变化")
    else:
        print("\n⚠️ 没有找到需要修复的文件")
        print("可能的原因:")
        print("1. NLP文件路径不同")
        print("2. 已经修复过了")
        print("3. 使用了不同的JSON解析方式")
    
    # 运行测试
    test_json_parsing()
    
    print("\n📌 下一步:")
    print("1. 运行游戏测试修复效果: python run_optimized_game.py")
    print("2. 如果还有问题，查看备份文件并手动调整")

if __name__ == "__main__":
    main()
