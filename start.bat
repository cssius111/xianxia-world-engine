@echo off
REM 修仙世界引擎启动脚本 (Windows版)

echo ==========================================
echo 🎮 修仙世界引擎 (Xianxia World Engine)
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 Python
    echo 请先安装 Python 3.7 或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 显示Python版本
echo ✅ Python 版本：
python --version
echo.

REM 检查是否在正确的目录
if not exist "run.py" (
    echo ❌ 错误：未找到 run.py 文件
    echo 请确保在项目根目录下运行此脚本
    pause
    exit /b 1
)

REM 创建必要的目录
echo 📁 检查目录结构...
if not exist "saves" mkdir saves && echo    创建目录: saves
if not exist "logs" mkdir logs && echo    创建目录: logs
if not exist "static\audio" mkdir static\audio && echo    创建目录: static\audio
if not exist "static\images" mkdir static\images && echo    创建目录: static\images
echo.

REM 检查依赖
echo 📦 检查依赖...
if exist "requirements.txt" (
    echo    安装/更新依赖...
    pip install -r requirements.txt >nul 2>&1
    echo    ✅ 依赖检查完成
) else (
    echo    ⚠️  未找到 requirements.txt，跳过依赖检查
)
echo.

REM 设置环境变量
set FLASK_ENV=development
set DEBUG=true

REM 启动服务器
echo 🚀 启动游戏服务器...
echo ==========================================
echo 访问地址: http://localhost:5001
echo 按 Ctrl+C 停止服务器
echo ==========================================
echo.

REM 启动Python服务器
python run.py

pause
