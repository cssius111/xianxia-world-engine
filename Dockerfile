# 基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装额外的依赖（用于监控和API文档）
RUN pip install --no-cache-dir \
    flask-swagger-ui==4.11.1 \
    psutil==5.9.8 \
    prometheus-client==0.19.0

# 复制项目文件
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 创建非root用户
RUN useradd -m -u 1000 xwe && chown -R xwe:xwe /app
USER xwe

# 暴露端口
EXPOSE 5001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/api/v1/system/health || exit 1

# 启动命令
CMD ["python", "entrypoints/run_web_ui_optimized.py"]
