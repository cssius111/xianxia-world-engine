#!/usr/bin/env python3
"""检查端口占用情况"""
import socket
import subprocess
import sys

def check_port(port):
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0  # 0 表示端口已被占用
    except:
        return False

def find_process_using_port(port):
    """查找占用端口的进程"""
    try:
        # macOS 使用 lsof 命令
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout:
            return result.stdout
        return None
    except:
        return None

print("=== 端口检查工具 ===\n")

ports_to_check = [5001, 5002, 5003, 5004, 5000]

for port in ports_to_check:
    is_used = check_port(port)
    print(f"端口 {port}: {'已占用 ❌' if is_used else '可用 ✅'}")
    
    if is_used:
        process_info = find_process_using_port(port)
        if process_info:
            print(f"  占用进程信息:")
            print(f"  {process_info.strip()}")
        print()

print("\n建议:")
print("1. 如果端口被占用，可以使用 'kill -9 <PID>' 终止进程")
print("2. 或者使用其他可用端口启动应用")
