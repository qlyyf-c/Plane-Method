#!/bin/bash
set -e

echo "=== Installing dependencies ==="

# 升级 pip
python -m pip install --upgrade pip

# 安装依赖（确保 uvicorn 被安装）
python -m pip install --no-cache-dir -r backend/requirements.txt

# 验证 uvicorn 是否安装成功
echo "=== Verifying installation ==="
python -m uvicorn --version || echo "WARNING: uvicorn not found"

echo "=== Installation complete ==="