"""
锚固计算 API - /api/v1/anchor/

提供锚固长度计算接口：
- POST /calculate — 计算锚固长度
- GET  /options   — 获取计算器选项
"""
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.anchor_calc import calculate_anchor, AnchorResult
import os


router = APIRouter()


# === 请求/响应模型 ===

class AnchorCalculateRequest(BaseModel):
    """锚固计算请求体"""
    concrete_grade: str = Field(..., description="混凝土等级，如'C30'")
    rebar_type: str = Field(..., description="钢筋类型，如'HRB400'")
    diameter: int = Field(..., description="钢筋直径 (mm)")
    seismic_grade: str = Field(..., description="抗震等级（一级/二级/三级/四级/非抗震）")
    modifier_ids: Optional[List[str]] = Field(default=None, description="修正系数 ID 列表")


class LabResult(BaseModel):
    """基本锚固长度结果"""
    d_value: int = Field(..., description="lab 的 d 倍数")
    mm_value: int = Field(..., description="lab 的毫米值")


class LaResult(BaseModel):
    """受拉锚固长度结果"""
    d_value: float = Field(..., description="la 的 d 倍数")
    mm_value: int = Field(..., description="la 的毫米值")
    modifier: float = Field(..., description="修正系数 ζa")
    modifier_note: str = Field(..., description="修正说明")


class LaEResult(BaseModel):
    """抗震锚固长度结果"""
    d_value: float = Field(..., description="laE 的 d 倍数")
    mm_value: int = Field(..., description="laE 的毫米值")
    seismic_modifier: float = Field(..., description="抗震系数 ζaE")
    seismic_note: str = Field(..., description="抗震说明")


class AnchorCalculateResponse(BaseModel):
    """锚固计算响应体"""
    lab: LabResult
    la: LaResult
    laE: LaEResult
    reference: dict
    related_spec_id: Optional[str] = None


@router.post("/calculate", response_model=AnchorCalculateResponse)
async def calculate_anchor_api(request: AnchorCalculateRequest):
    """计算锚固长度
    
    输入参数：
    - concrete_grade: 混凝土等级（如"C30"）
    - rebar_type: 钢筋类型（如"HRB400"）
    - diameter: 钢筋直径 (mm)
    - seismic_grade: 抗震等级（一级/二级/三级/四级/非抗震）
    - modifier_ids: 可选的修正系数 ID 列表
    
    返回：
    - lab: 基本锚固长度
    - la: 受拉钢筋锚固长度
    - laE: 抗震锚固长度
    - reference: 引用信息
    """
    try:
        result = calculate_anchor(
            concrete_grade=request.concrete_grade,
            rebar_type=request.rebar_type,
            diameter=request.diameter,
            seismic_grade=request.seismic_grade,
            modifier_ids=request.modifier_ids,
        )
        
        # 构建响应
        modifier_note = "无修正" if not result.modifiers_applied else ", ".join(result.modifiers_applied)
        seismic_note_map = {
            "一级": "一级抗震",
            "二级": "二级抗震", 
            "三级": "三级抗震",
            "四级": "四级抗震",
            "非抗震": "非抗震",
        }
        
        return AnchorCalculateResponse(
            lab=LabResult(d_value=result.lab_d, mm_value=result.lab_mm),
            la=LaResult(
                d_value=result.la_d,
                mm_value=result.la_mm,
                modifier=1.0 if not result.modifiers_applied else round(
                    result.la_d / result.lab_d, 2
                ),
                modifier_note=modifier_note,
            ),
            laE=LaEResult(
                d_value=result.laE_d,
                mm_value=result.laE_mm,
                seismic_modifier=result.seismic_factor,
                seismic_note=seismic_note_map.get(request.seismic_grade, ""),
            ),
            reference=result.reference,
            related_spec_id="spec-anchor-general",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算错误：{str(e)}")


@router.get("/options")
async def get_anchor_options():
    """获取锚固计算器所有选项
    
    返回所有可用的下拉选项数据，包括：
    - 混凝土等级
    - 钢筋类型  
    - 抗震等级
    - 钢筋直径
    - 修正系数
    """
    from sqlmodel import Session, select
    from sqlalchemy import create_engine
    from app.models.database import ConcreteGrade, RebarType, SeismicModifier, RebarDiameter, AnchorModifier
    
    _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    DB_PATH = os.path.join(_root, "data", "pingfa.db")
    DB_URL = f"sqlite:///{DB_PATH}"
    
    with Session(create_engine(DB_URL)) as session:
        # 混凝土等级
        concrete_grades = [
            {"grade": g.grade, "ft_value": g.ft_value}
            for g in session.exec(select(ConcreteGrade).order_by(ConcreteGrade.grade))
        ]
        
        # 钢筋类型
        rebar_types = [
            {"type": r.type, "fy_value": r.fy_value, "alpha": r.alpha}
            for r in session.exec(select(RebarType))
        ]
        
        # 抗震等级
        seismic_grades = [
            {"grade": s.grade, "factor": s.factor, "note": s.note}
            for s in session.exec(select(SeismicModifier).order_by(SeismicModifier.grade))
        ]
        
        # 钢筋直径
        diameters = [
            {"diameter": d.diameter, "note": d.note}
            for d in session.exec(select(RebarDiameter).order_by(RebarDiameter.diameter))
        ]
        
        # 修正系数
        modifiers = [
            {
                "modifier_id": m.modifier_id,
                "name": m.name,
                "condition": m.condition,
                "factor": m.factor,
                "note": m.note,
            }
            for m in session.exec(select(AnchorModifier))
        ]
    
    return {
        "concrete_grades": concrete_grades,
        "rebar_types": rebar_types,
        "seismic_grades": seismic_grades,
        "diameters": diameters,
        "modifiers": modifiers,
    }
