"""
图集速查 API - /api/v1/specification/

提供 22G101 条文查询接口：
- GET /search       — 关键字搜索条文(title/content_html)
- GET /categories   — 获取章节分类列表
- GET /by-category  — 按分类获取条文列表
- GET /detail/{id}  — 获取单条条文详情(含 HTML 内容)
- GET /related/{id} — 获取关联内容(计算/标注类型)
"""
import os
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from sqlalchemy import create_engine

from app.models.database import Specification

# 数据库 URL(动态路径，兼容 WSL/Linux/Windows)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(_PROJECT_ROOT, "data", "pingfa.db")
DB_URL = f"sqlite:///{DB_PATH}"


def get_db_session():
    """获取数据库会话"""
    engine = create_engine(DB_URL)
    return Session(engine)


router = APIRouter()


@router.get("/search")
async def search_specifications(keyword: str = ""):
    """搜索条文 - 根据关键字在 title 和 content_html 中搜索"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"Search request received: keyword='{keyword}'")

    if not keyword.strip():
        return {"results": [], "message": "请输入搜索关键字"}

    with get_db_session() as session:
        # 检查数据库中是否有数据
        count = session.exec(select(Specification)).all()
        logger.info(f"Total specifications in database: {len(count)}")

        if len(count) == 0:
            logger.error("Database is empty! No specifications found.")
            return {"results": [], "message": "数据库为空，请联系管理员"}

    with get_db_session() as session:
        # 简单 LIKE 模糊搜索
        results = session.exec(
            select(Specification).where(
                (Specification.title.contains(keyword)) |
                (Specification.content_html.contains(keyword))
            )
        ).all()

        return {
            "results": [
                {
                    "id": spec.id,
                    "clause_number": spec.clause_number,
                    "title": spec.title,
                    "category": spec.category,
                    "snippet": spec.content_html[:100] + "..." if len(spec.content_html) > 100 else spec.content_html,
                }
                for spec in results
            ],
            "count": len(results),
        }


@router.get("/categories")
async def get_categories():
    """获取所有分类列表(去重)"""
    with get_db_session() as session:
        # SQLite 不支持 DISTINCT on，手动去重
        all_specs = session.exec(select(Specification)).all()
        categories = list(set(spec.category for spec in all_specs))
        categories.sort()  # 按拼音排序

        return {"categories": categories}


@router.get("/by-category")
async def get_by_category(category: str = ""):
    """按分类获取条文列表"""
    if not category:
        return {"specifications": [], "message": "请指定分类参数 category"}

    with get_db_session() as session:
        results = session.exec(
            select(Specification)
            .where(Specification.category == category)
            .order_by(Specification.clause_number)
        ).all()

        return {
            "category": category,
            "specifications": [
                {
                    "id": spec.id,
                    "clause_number": spec.clause_number,
                    "title": spec.title,
                    "related_calc": spec.related_calc,
                    "related_ann_type": spec.related_ann_type,
                }
                for spec in results
            ],
            "count": len(results),
        }


@router.get("/detail/{id}")
async def get_detail(id: str):
    """获取单条条文详情"""
    with get_db_session() as session:
        spec = session.get(Specification, id)

        if not spec:
            raise HTTPException(status_code=404, detail=f"条文 {id} 不存在")

        return {
            "id": spec.id,
            "clause_number": spec.clause_number,
            "title": spec.title,
            "category": spec.category,
            "content_html": spec.content_html,
            "related_calc": spec.related_calc,
            "related_ann_type": spec.related_ann_type,
        }


@router.get("/related/{id}")
async def get_related(id: str):
    """获取关联内容
    - related_calc: 返回关联的计算类型(如 anchor)
    - related_ann_type: 返回关联的标注类型(如 beam/column)
    """
    with get_db_session() as session:
        spec = session.get(Specification, id)

        if not spec:
            raise HTTPException(status_code=404, detail=f"条文 {id} 不存在")

        related = {
            "calculation": None,
            "annotation_type": None,
            "cross_references": [],
        }

        # 关联计算
        if spec.related_calc:
            related["calculation"] = {
                "type": spec.related_calc,
                "url": f"/api/v1/{spec.related_calc}/calculate",
            }

        # 关联标注类型
        if spec.related_ann_type:
            related["annotation_type"] = spec.related_ann_type

        # 交叉引用：同一分类的其他条文
        same_category = session.exec(
            select(Specification)
            .where(Specification.category == spec.category)
            .where(Specification.id != id)
        ).all()

        related["cross_references"] = [
            {"id": s.id, "title": s.title, "clause_number": s.clause_number}
            for s in same_category
        ]

        return related
