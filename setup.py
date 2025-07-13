"""
修仙世界引擎安装配置
"""
from setuptools import setup, find_packages
from pathlib import Path

# 读取README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取依赖
requirements = (this_directory / "requirements.txt").read_text().splitlines()
requirements = [r for r in requirements if r and not r.startswith('#')]

setup(
    name="xianxia-world-engine",
    version="0.3.4",
    author="XianXia World Engine Team",
    author_email="dev@xianxia-engine.com",
    description="一个基于文本的修仙世界模拟游戏引擎",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xianxia-team/xianxia-world-engine",
    project_urls={
        "Bug Tracker": "https://github.com/xianxia-team/xianxia-world-engine/issues",
        "Documentation": "https://xianxia-engine.readthedocs.io",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment :: Role-Playing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.1.1",
            "pytest-cov",
            "pytest-mock",
            "black",
            "flake8",
            "isort",
            "pre-commit",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "myst-parser",
        ],
    },
    entry_points={
        "console_scripts": [
            "xwe=xwe.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "xwe": ["data/*.json", "data/*.yaml"],
    },
)
