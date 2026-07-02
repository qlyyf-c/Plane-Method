"""
FastAPI 入口 - 平法辅助学习 App 后端

功能：
- 初始化 FastAPI 应用
- 配置 CORS（开发环境允许所有来源）
- 注册 API 路由
- 数据库连接初始化
- 静态文件服务（用于部署到 Railway）
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models.database import SQLModel


# 数据库文件路径：相对于 pingfa_app 项目根目录
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "pingfa.db",
)

DB_URL = f"sqlite:///{DB_PATH}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时建表，关闭时清理"""
    from sqlmodel import create_engine

    engine = create_engine(DB_URL, echo=False)
    SQLModel.metadata.create_all(engine)
    app.state.db_engine = engine
    yield
    engine.dispose()


app = FastAPI(
    title="平法助手 PingFa",
    description="土木工程平法识图辅助学习工具 API",
    version="0.1.0",
    lifespan=lifespan,
)


# CORS 配置
origins = [
    "https://plane-method.vercel.app",
    "https://plane-method-git-main-yourusername.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ---- API 路由注册 ----
from app.api.data import router as data_router
from app.api.anchor import router as anchor_router
from app.api.annotation import router as annotation_router
from app.api.specification import router as specification_router

app.include_router(data_router, prefix="/api/v1/data", tags=["数据选项"])
app.include_router(anchor_router, prefix="/api/v1/anchor", tags=["锚固计算"])
app.include_router(annotation_router, prefix="/api/v1/annotation", tags=["标注解析"])
app.include_router(specification_router, prefix="/api/v1/specification", tags=["图集速查"])


# ---- 静态文件服务（必须在 API 路由之后挂载）----
# 用于部署到 Railway 时服务前端构建产物
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


@app.get("/")
async def root():
    """根路径 - 返回应用基本信息"""
    return {
        "app": "平法助手 PingFa",
        "version": "0.1.0",
        "docs": "/docs",
    }

@app.get("/api")
async def api_root():
    """API 根路径 - 返回应用基本信息"""
    return {
        "app": "平法助手 PingFa",
        "version": "0.1.0",
        "docs": "/docs",
    }
