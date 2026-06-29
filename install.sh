#!/bin/bash
# Railway 构建脚本

# 安装依赖
python -m pip install -r backend/requirements.txt

# 将 backend 目录添加到 PYTHONPATH
export PYTHONPATH="$PWD/backend:$PYTHONPATH"

# 验证导入
python -c "import sys; print('PYTHONPATH:', sys.path); from app.main import app; print('Import OK')"