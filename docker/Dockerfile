# 平法助手 Dockerfile
# 多阶段构建：前端构建 + 后端运行

# --------------------
# 第一阶段：构建前端
# --------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# 复制 package 相关文件
COPY frontend/package*.json ./
RUN npm ci

# 复制前端源码
COPY frontend/ ./

# 构建前端
RUN npm run build

# --------------------
# 第二阶段：构建后端
# --------------------
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# 安装编译依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements 文件
COPY backend/requirements.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# --------------------
# 第三阶段：最终运行环境
# --------------------
FROM python:3.11-slim

WORKDIR /app

# 复制 Python 依赖
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# 复制前端构建结果
COPY --from=frontend-builder /app/dist ./frontend/dist

# 复制后端代码
COPY backend/ ./backend/

# 复制数据文件
COPY data/ ./data/

# 设置环境变量
ENV PYTHONPATH=/app/backend
ENV FASTAPI_ENV=production

# 创建非root用户
RUN adduser --disabled-password --gecos '' appuser
USER appuser
WORKDIR /app

# 暴露端口
EXPOSE 8001

# 启动命令
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8001"]