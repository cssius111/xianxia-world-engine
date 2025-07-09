#!/usr/bin/env python
"""快速修复缺失的依赖包"""
import subprocess
import sys

def install_package(package):
    """安装单个包"""
    print(f"正在安装 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ {package} 安装失败")
        return False

# 缺失的包列表
missing_packages = [
    "prometheus-flask-exporter==0.23.0",
    "objgraph==3.6.2"
]

print("开始安装缺失的依赖包...")
print("=" * 50)

success_count = 0
for package in missing_packages:
    if install_package(package):
        success_count += 1
    print("-" * 30)

print("=" * 50)
print(f"安装完成：{success_count}/{len(missing_packages)} 个包安装成功")

if success_count == len(missing_packages):
    print("\n✅ 所有依赖包已成功安装！")
    print("现在可以运行 pytest 了")
else:
    print("\n⚠️  部分包安装失败，请检查错误信息")
