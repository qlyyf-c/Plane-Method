#!/bin/bash
# 部署脚本 - 用于部署平法助手应用

set -e  # 遇到错误退出

echo "=== 平法助手部署脚本 ==="

# 检查环境
echo "1. 检查环境..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: Python 3 未安装"
    exit 1
fi

# 检查Node环境
if ! command -v node &> /dev/null; then
    echo "警告: Node.js 未安装，但可以忽略（仅用于构建）"
fi

# 进入项目目录
cd /mnt/d/OPC_projects/civil_opc/development/pingfa_app

echo "2. 安装Python依赖..."
cd backend
pip install -r requirements.txt

echo "3. 验证数据库..."
cd ../data
python3 init_db.py
cd ..

echo "4. 运行测试验证..."
python3 -m pytest tests/ -v --tb=short

echo "5. 启动后端服务进行部署验证..."
# 启动服务并检查是否正常运行
timeout 30s python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --log-level error &
SERVER_PID=$!

# 等待服务启动
sleep 5

# 检查服务是否在监听
if lsof -i:8001 > /dev/null 2>&1; then
    echo "服务启动成功，端口8001正在监听"

    # 测试API
    echo "6. 测试API..."
    if curl -f -s http://localhost:8001/ > /dev/null; then
        echo "API测试成功"
    else
        echo "API测试失败"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi

    kill $SERVER_PID 2>/dev/null || true
    echo "部署验证通过！"
else
    echo "服务启动失败"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

echo "=== 部署完成 ==="