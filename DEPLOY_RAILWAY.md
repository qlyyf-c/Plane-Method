# Railway 部署说明

本文件介绍了如何将平法助手应用部署到 Railway 平台。

## 部署架构

采用单服务部署模式，将前端和后端整合在一个容器中：
- 后端：FastAPI 应用
- 前端：Vue3 应用构建产物（静态文件）
- 数据库：SQLite

## 部署步骤

1. **准备环境**：
   ```bash
   cd /mnt/d/OPC_projects/civil_opc/development/pingfa_app
   ```

2. **执行部署脚本**：
   ```bash
   ./deploy_to_railway.sh
   ```

3. **或者直接使用Railway CLI**：
   ```bash
   railway up
   ```

## 配置说明

### Railway 配置文件 (railway.toml)
- 构建命令：执行部署脚本
- 启动命令：运行启动脚本
- 健康检查：根路径 `/`

### Dockerfile (docker/Dockerfile.railway)
- 使用Python 3.11 Slim镜像
- 安装Node.js和npm用于前端构建
- 集成前端构建产物到后端目录
- 配置健康检查

## 环境变量

- `PORT`: 应用监听端口（由Railway提供）
- `STATIC_DIR`: 静态文件目录，默认为 `./frontend/dist`
- `DB_PATH`: 数据库文件路径

## 部署验证

部署完成后，可以通过以下方式验证：

1. 访问应用根路径：`/`
2. 访问API文档：`/docs`
3. 访问前端界面：`/`（会返回index.html）

## 注意事项

1. 需要确保前端构建产物存在于 `frontend/dist` 目录中
2. 数据库路径在Railway环境下会被正确处理
3. 静态文件服务会自动加载前端构建产物