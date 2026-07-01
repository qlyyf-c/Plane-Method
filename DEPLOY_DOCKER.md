# Docker 部署说明

本文件介绍了如何将平法助手应用使用Docker模式进行部署。

## 部署架构

采用Docker容器化部署模式，将应用打包为一个容器镜像：
- 后端：FastAPI 应用
- 前端：Vue3 应用构建产物（静态文件）
- 数据库：SQLite

## 部署步骤

### 1. 准备环境
```bash
cd /mnt/d/OPC_projects/civil_opc/development/pingfa_app
```

### 2. 执行Docker部署脚本
```bash
./deploy_docker.sh
```

### 3. 运行容器
```bash
# 运行容器
docker run -p 8001:8001 pingfa-app

# 或者在后台运行
docker run -d -p 8001:8001 --name pingfa-app pingfa-app
```

## Dockerfile说明

文件位置：`docker/Dockerfile.docker`

### 特性
- 基于python:3.11-slim镜像
- 安装必要的系统依赖
- 复制并安装Python依赖
- 复制后端代码和数据文件
- 构建前端并整合到容器中
- 配置环境变量和端口暴露
- 添加健康检查

## 环境变量

- `PORT`: 应用监听端口（默认8001）
- `FASTAPI_ENV`: 应用环境（production）
- `PYTHONPATH`: Python模块路径

## 运行示例

### 本地运行
```bash
docker run -p 8001:8001 pingfa-app
```

### 后台运行
```bash
docker run -d -p 8001:8001 --name pingfa-app pingfa-app
```

### 与外部网络连接
```bash
docker run -d -p 0.0.0.0:8001:8001 --name pingfa-app pingfa-app
```

## 验证部署

部署后可以通过以下方式验证：

1. 访问应用根路径：`http://localhost:8001/`
2. 访问API文档：`http://localhost:8001/docs`
3. 确认服务响应正常

## 注意事项

1. 需要确保Docker服务正在运行
2. 端口8001需要在主机上可用
3. 前端构建产物需要预先生成
4. 数据库文件会随容器一起存储
5. 生产环境中应使用卷挂载持久化数据

## Docker Compose部署

也可以使用Docker Compose进行部署：

```yaml
version: '3.8'
services:
  pingfa-app:
    build: .
    ports:
      - "8001:8001"
    volumes:
      - ./data:/app/data
    environment:
      - FASTAPI_ENV=production
    restart: unless-stopped
```