"""
FastAPI 入口 - 平法辅助学习 App 后端

功能：
- 初始化 FastAPI 应用
- 配置 CORS（开发环境允许所有来源）
- 注册 API 路由（初始为空壳，后续逐个填充）
- 数据库连接初始化
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.database import SQLModel


# 数据库文件路径：相对于 pingfa_app 项目根目录
# 开发时 SQLite 文件放在 data/pingfa.db，与 JSON 数据同层
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),  # → pingfa_app/
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
    # 将 engine 存到 app.state 以便各 API 模块使用
    app.state.db_engine = engine
    yield
    engine.dispose()


app = FastAPI(
    title="平法助手 PingFa",
    description="土木工程平法识图辅助学习工具 API",
    version="0.1.0",
    lifespan=lifespan,
)


# CORS 配置：允许 Vercel 和本地开发
origins = [
    "https://plane-method.vercel.app",
    "https://plane-method-git-main-yourusername.vercel.app",  # Vercel 预览域名
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


# ---- 路由注册 ----
# 空壳路由，后续 Week 2-4 逐个实现

from app.api.data import router as data_router  # noqa: E402
from app.api.anchor import router as anchor_router  # noqa: E402
from app.api.annotation import router as annotation_router  # noqa: E402
from app.api.specification import router as specification_router  # noqa: E402

app.include_router(data_router, prefix="/api/v1/data", tags=["数据选项"])
app.include_router(anchor_router, prefix="/api/v1/anchor", tags=["锚固计算"])
app.include_router(annotation_router, prefix="/api/v1/annotation", tags=["标注解析"])
app.include_router(specification_router, prefix="/api/v1/specification", tags=["图集速查"])


@app.get("/")
async def root():
    """根路径 - 返回应用基本信息"""
    return {
        "app": "平法助手 PingFa",
        "version": "0.1.0",
        "docs": "/docs",
    }
