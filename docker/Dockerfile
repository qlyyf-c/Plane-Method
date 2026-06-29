# 平法助手 Dockerfile
# 单阶段构建，简化部署

FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖并安装
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 复制数据文件
COPY data/ ./data/

# 设置环境变量
ENV PYTHONPATH=/app/backend
ENV FASTAPI_ENV=production
ENV PORT=8001

# 暴露端口（使用环境变量）
EXPOSE $PORT

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# 启动应用（使用 $PORT 环境变量）
CMD ["sh", "-c", "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT"]