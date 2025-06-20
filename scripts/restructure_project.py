# scripts/restructure_project.py

import os
import sys

EXPECTED_PATHS = [
    "xwe_v2/domain",
    "xwe_v2/application",
    "xwe_v2/infrastructure",
    "xwe_v2/presentation",
    "xwe_v2/compatibility.py",
]


def main():
    missing = []
    for path in EXPECTED_PATHS:
        if not os.path.exists(path):
            missing.append(path)
    if missing:
        print("❌ 以下必要结构缺失：")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)
    print("✅ 项目结构检查通过！")


if __name__ == "__main__":
    main()
