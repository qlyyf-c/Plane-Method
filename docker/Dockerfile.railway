# 平法助手 Dockerfile - 用于 Railway 部署
# 包含前后端一体化构建

FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（包括 Node.js 用于前端构建）
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

# 复制前端源码并构建
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm install
COPY frontend/ ./frontend/
RUN cd frontend && npm run build

# 初始化数据库（从 JSON 导入数据）
RUN python data/init_db.py

# 设置环境变量
ENV PYTHONPATH=/app/backend
ENV FASTAPI_ENV=production

# Railway 会自动注入 PORT 环境变量

# 暴露端口
EXPOSE 8001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

# 启动应用
CMD ["sh", "-c", "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT"]
