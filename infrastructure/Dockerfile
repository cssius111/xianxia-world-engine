FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ ./src/
COPY data/ ./data/
COPY app.py .

# 创建必要的目录
RUN mkdir -p logs saves

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV FLASK_APP=app.py

# 暴露端口
EXPOSE 5001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/health || exit 1

# 启动应用
CMD ["python", "app.py"]
