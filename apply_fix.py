"""
创建一个修补文件来修复 CommandRouter 的阻塞问题
"""
import os

# 在环境变量中禁用 NLP
os.environ['USE_NLP'] = 'false'

print("=== 应用修补 ===")
print("已设置环境变量 USE_NLP=false")
print("\n现在可以运行：")
print("python run.py --debug")
print("\n或者使用修复版启动：")
print("python fixed_run.py")
