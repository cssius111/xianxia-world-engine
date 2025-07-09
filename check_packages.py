#!/usr/bin/env python
"""检查缺失的包"""
import subprocess
import sys

def check_package(package_name):
    try:
        __import__(package_name.replace('-', '_'))
        return True
    except ImportError:
        return False

packages_to_check = {
    'prometheus-flask-exporter': 'prometheus_flask_exporter',
    'objgraph': 'objgraph'
}

print("检查包的安装状态：")
print("-" * 50)

missing_packages = []
for package, import_name in packages_to_check.items():
    if check_package(import_name):
        print(f"✓ {package} 已安装")
    else:
        print(f"✗ {package} 未安装")
        missing_packages.append(package)

if missing_packages:
    print("\n需要安装的包：")
    print(f"pip install {' '.join(missing_packages)}")
else:
    print("\n所有必需的包都已安装！")
