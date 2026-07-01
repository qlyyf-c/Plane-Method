#!/bin/bash
# Railway 启动脚本

# 将 backend 目录添加到 PYTHONPATH
export PYTHONPATH="$PWD/backend:$PYTHONPATH"

# 设置数据库路径（相对于项目根目录）
export DB_PATH="$PWD/data/pingfa.db"

# 如果存在前端构建产物，则设置静态文件路径
if [ -d "$PWD/frontend/dist" ]; then
    export STATIC_DIR="$PWD/frontend/dist"
fi

# 启动应用
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT