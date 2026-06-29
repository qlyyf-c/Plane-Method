"""
数据选项 API - /api/v1/data/

提供锚固计算器所需的下拉选项数据和修正系数列表：
- 混凝土等级列表
- 钢筋类型列表
- 抗震等级列表
- 钢筋直径列表
- 修正系数列表（可勾选）
"""
import os
from typing import List, Dict, Any

from fastapi import APIRouter
from sqlmodel import Session, select
from sqlalchemy import create_engine

from app.models.database import (
    ConcreteGrade,
    RebarType,
    SeismicModifier,
    RebarDiameter,
    AnchorModifier,
)

# 数据库 URL (动态路径，兼容 WSL/Linux/Windows)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(_PROJECT_ROOT, "data", "pingfa.db")
DB_URL = f"sqlite:///{DB_PATH}"

router = APIRouter()


def get_db_session():
    """获取数据库会话"""
    engine = create_engine(DB_URL)
    return Session(engine)


@router.get("/concrete-grades")
async def get_concrete_grades():
    """获取混凝土等级列表"""
    with get_db_session() as session:
        results = session.exec(select(ConcreteGrade).order_by(ConcreteGrade.grade))
        grades = [{"grade": g.grade, "ft_value": g.ft_value} for g in results]
        return {"grades": grades}


@router.get("/rebar-types")
async def get_rebar_types():
    """获取钢筋类型列表"""
    with get_db_session() as session:
        results = session.exec(select(RebarType))
        types = [{"type": r.type, "fy_value": r.fy_value, "alpha": r.alpha} for r in results]
        return {"types": types}


@router.get("/seismic-grades")
async def get_seismic_grades():
    """获取抗震等级列表"""
    with get_db_session() as session:
        results = session.exec(select(SeismicModifier).order_by(SeismicModifier.factor))
        grades = [{"grade": g.grade, "factor": g.factor, "note": g.note} for g in results]
        return {"grades": grades}


@router.get("/diameters")
async def get_diameters():
    """获取钢筋直径列表"""
    with get_db_session() as session:
        results = session.exec(select(RebarDiameter).order_by(RebarDiameter.diameter))
        diameters = [{"diameter": d.diameter, "note": d.note} for d in results]
        return {"diameters": diameters}


@router.get("/modifiers")
async def get_modifiers():
    """获取修正系数列表（用于 la 计算时的可勾选项）

    返回格式：
    [
      {"modifier_id": "diameter", "name": "直径修正", "condition": ">25mm", "factor": 1.10},
      ...
    ]

    前端使用时：
    - 用户勾选某些修正项
    - 后端计算时按连乘叠加：ζa = ζ1 × ζ2 × ...
    """
    with get_db_session() as session:
        results = session.exec(select(AnchorModifier))
        modifiers = [
            {
                "modifier_id": m.modifier_id,
                "name": m.name,
                "condition": m.condition,
                "factor": m.factor,
                "note": m.note,
            }
            for m in results
        ]
        return {"modifiers": modifiers}
