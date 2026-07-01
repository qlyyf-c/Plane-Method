#!/bin/bash
# deploy-to-railway.sh
# 用于将pingfa_app的前端和后端整合部署到Railway的脚本

set -e  # 遇到错误退出

echo "=== 平法助手 Railway 部署脚本 ==="

# 检查必要工具
if ! command -v npm &> /dev/null; then
    echo "错误: npm 未安装"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "错误: Python 3 未安装"
    exit 1
fi

# 进入项目目录
cd /mnt/d/OPC_projects/civil_opc/development/pingfa_app

echo "1. 构建前端..."
cd frontend
npm install
npm run build

echo "2. 返回主目录并准备整合..."
cd ..

echo "3. 整合前端构建产物到后端..."
# 删除旧的dist目录（如果存在）
if [ -d "backend/dist" ]; then
    rm -rf backend/dist
fi

# 复制前端构建产物到后端目录
cp -r frontend/dist backend/dist

echo "4. 安装后端依赖..."
cd backend
pip install --no-cache-dir -r requirements.txt

echo "5. 初始化数据库..."
cd ../data
python3 init_db.py

echo "6. 运行测试验证..."
cd ..
python3 -m pytest backend/tests/ -v --tb=short

echo "7. 验证部署配置..."
# 检查Railway配置文件
if [ -f "railway.toml" ]; then
    echo "✓ Railway配置文件存在"
else
    echo "✗ Railway配置文件不存在"
    exit 1
fi

echo "8. 验证Dockerfile..."
if [ -f "docker/Dockerfile" ]; then
    echo "✓ Dockerfile存在"
else
    echo "✗ Dockerfile不存在"
    exit 1
fi

echo "=== 部署准备工作完成 ==="
echo "现在可以使用以下命令部署:"
echo "1. 使用Docker部署: docker build -t pingfa-app ."
echo "2. 或者直接部署到Railway: railway up"