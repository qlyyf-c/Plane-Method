# 平法助手 Dockerfile - 用于 Railway 部署
# 多阶段构建：前端构建 + 后端服务

# ========== 第一阶段：构建前端 ==========
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖并安装
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

# 复制前端源码并构建
COPY frontend/ ./
RUN npm run build

# ========== 第二阶段：运行后端 ==========
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

# 复制数据文件（JSON 源数据）
COPY data/ ./data/

# 从第一阶段复制构建好的前端产物
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

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
