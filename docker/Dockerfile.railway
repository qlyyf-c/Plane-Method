# 平法助手 Dockerfile - 一体化部署版本
# 用于Railway部署，包含前后端

FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖并安装
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 复制数据文件（JSON 源数据）
COPY data/ ./data/

# 复制前端构建产物（如果存在）
COPY frontend/dist ./frontend/dist

# 初始化数据库（从 JSON 导入数据）
RUN python data/init_db.py

# 设置环境变量
ENV PYTHONPATH=/app/backend
ENV FASTAPI_ENV=production
ENV PORT=8001

# 暴露端口
EXPOSE 8001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

# 启动应用
CMD ["sh", "-c", "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT"]