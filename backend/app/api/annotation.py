"""
标注解析 API - /api/v1/annotation/

提供平法标注解析接口：
- POST /parse    — 解析标注字符串
- GET  /examples — 获取常用标注示例
- GET  /types    — 获取支持的标注类型
- GET  /glossary — 获取符号释义表
"""
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.annotation_parser import (
    parse_annotation,
    get_examples,
    get_types,
    get_glossary_all,
)


router = APIRouter()


# === 请求/响应模型 ===

class ParseRequest(BaseModel):
    """标注解析请求"""
    text: str = Field(..., description="标注文本，如 'KL7(3) 300x650'")


class ParsedResult(BaseModel):
    """解析结果"""
    component_type: str
    component_name: str
    number: Optional[int] = None
    span_count: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class GlossaryItem(BaseModel):
    """释义项"""
    symbol: str
    meaning: str
    description: str


class ParseResponse(BaseModel):
    """标注解析响应"""
    success: bool
    parsed: Optional[ParsedResult] = None
    glossary: List[GlossaryItem] = []
    related_spec_id: Optional[str] = None
    error: Optional[str] = None
    suggestion: Optional[str] = None
    partial: Optional[Dict[str, Any]] = None


class ExampleResponse(BaseModel):
    """示例列表响应"""
    examples: List[str]


class TypeResponse(BaseModel):
    """类型列表响应"""
    types: List[Dict[str, str]]


class GlossaryResponse(BaseModel):
    """完整释义表响应"""
    glossary: List[GlossaryItem]


@router.post("/parse", response_model=ParseResponse)
async def parse_annotation_api(request: ParseRequest):
    """解析平法标注字符串
    
    Args:
        request: 包含标注文本的请求
    
    Returns:
        解析结果，包括构件信息、符号释义和错误提示
    """
    result = parse_annotation(request.text)
    
    if result.success and result.parsed:
        return ParseResponse(
            success=True,
            parsed=ParsedResult(
                component_type=result.parsed.component_type,
                component_name=result.parsed.component_name,
                number=result.parsed.number,
                span_count=result.parsed.span_count,
                width=result.parsed.width,
                height=result.parsed.height,
            ),
            glossary=[
                GlossaryItem(symbol=g["symbol"], meaning=g["meaning"], description=g["description"])
                for g in (result.glossary or [])
            ],
            related_spec_id=result.related_spec_id,
            suggestion=result.suggestion,
        )
    else:
        return ParseResponse(
            success=False,
            error=result.error,
            suggestion=result.suggestion,
            partial=result.partial,
        )


@router.get("/examples", response_model=ExampleResponse)
async def get_examples_api():
    """获取常用标注示例"""
    examples = get_examples()
    return ExampleResponse(examples=examples[:10])  # 限制返回数量


@router.get("/types", response_model=TypeResponse)
async def get_types_api():
    """获取支持的标注类型"""
    types = get_types()
    return TypeResponse(types=types)


@router.get("/glossary", response_model=GlossaryResponse)
async def get_glossary_api():
    """获取完整符号释义表"""
    glossary = get_glossary_all()
    return GlossaryResponse(
        glossary=[
            GlossaryItem(symbol=g["symbol"], meaning=g["meaning"], description=g["description"])
            for g in glossary
        ]
    )
