# 平法助手 - 部署说明

## 部署方式

### 方式一：直接部署后端服务

由于本项目前后端已经完全分离，我们可以直接部署后端服务，前端使用静态文件托管。

### 方式二：Docker 部署

我们已经创建了 Dockerfile 和 docker-compose.yml 文件，可以使用 Docker 进行部署。

## 部署步骤

### 1. 准备工作

```bash
# 克隆项目
git clone <repository-url>
cd pingfa_app

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
npm install
```

### 2. 构建前端

```bash
# 构建前端代码
cd frontend
npm run build
```

### 3. 数据库初始化

```bash
# 初始化数据库
cd ../data
python init_db.py
```

### 4. 启动服务

```bash
# 启动后端服务
cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 推荐部署平台

### Railway (免费额度足够)

1. 创建 Railway 账户
2. 关联 GitHub 仓库
3. 设置环境变量
4. 部署应用

### Vercel (前端) + Railway (后端)

1. 前端部署到 Vercel，指向 `/frontend/dist` 目录
2. 后端部署到 Railway

## 环境变量

- `FASTAPI_ENV=production` - 生产环境标志
- `DATABASE_URL` - 数据库连接地址（可选）

## 服务器要求

- Python 3.11+
- Node.js 18+ (用于前端构建)
- 1GB 内存以上
- 10GB 磁盘空间

## 项目结构说明

```
pingfa_app/
├── backend/           # FastAPI 后端
├── frontend/          # Vue3 前端
├── data/              # 数据文件和数据库
├── docker/            # Docker 配置文件
└── README.md          # 项目说明
```