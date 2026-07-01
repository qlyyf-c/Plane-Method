#!/bin/bash
# deploy_docker.sh
# 用于Docker模式部署平法助手应用

set -e  # 遇到错误退出

echo "=== 平法助手 Docker 部署脚本 ==="

# 检查必要工具
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    exit 1
fi

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

echo "3. 构建Docker镜像..."
# 复制Dockerfile并构建
cp docker/Dockerfile.docker Dockerfile
docker build -t pingfa-app .

echo "4. 验证Docker镜像..."
docker run --rm -d -p 8001:8001 --name pingfa-test pingfa-app
sleep 5

echo "5. 测试服务是否正常运行..."
if curl -f http://localhost:8001/ > /dev/null; then
    echo "✓ Docker服务启动成功"
    docker stop pingfa-test
else
    echo "✗ Docker服务启动失败"
    docker stop pingfa-test 2>/dev/null || true
    exit 1
fi

echo "=== Docker部署准备完成 ==="
echo "现在可以使用以下命令运行应用:"
echo "docker run -p 8001:8001 pingfa-app"
echo ""
echo "或者推送到Docker仓库:"
echo "docker tag pingfa-app your-registry/pingfa-app:latest"
echo "docker push your-registry/pingfa-app:latest"