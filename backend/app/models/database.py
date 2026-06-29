"""
SQLModel 数据模型 - 平法辅助学习 App

依据 docs/design.md 第5节定义所有数据表结构。
所有数值数据来源 22G101-1 图集 / GB50010，由用户提供后经 init_db.py 导入。
"""
from typing import Optional

from sqlmodel import SQLModel, Field


class ConcreteGrade(SQLModel, table=True):
    """混凝土等级 - C20, C25, C30... 及其抗拉强度设计值 ft"""

    id: int = Field(default=None, primary_key=True)
    grade: str = Field(index=True, unique=True)  # C20, C25, C30...
    ft_value: float  # 混凝土轴心抗拉强度设计值 (N/mm²)


class RebarType(SQLModel, table=True):
    """钢筋类型 - HRB300/HRB400/HRB500，含抗拉强度设计值 fy 与外形系数 α"""

    id: int = Field(default=None, primary_key=True)
    type: str = Field(index=True, unique=True)  # HRB300, HRB400, HRB500
    fy_value: int  # 钢筋抗拉强度设计值 (N/mm²)
    alpha: float  # 锚固外形系数（光圆 0.16，带肋 0.14）


class SeismicModifier(SQLModel, table=True):
    """抗震修正系数 - ζaE，按抗震等级取值"""

    id: int = Field(default=None, primary_key=True)
    grade: str = Field(index=True, unique=True)  # 一级/二级/三级/四级/非抗震
    factor: float  # ζaE 系数
    note: str = ""


class AnchorModifier(SQLModel, table=True):
    """锚固长度修正系数 - 用于 la 计算时的可勾选选项

    修正系数按连乘叠加：ζa = ζ1 × ζ2 × ... × ζn
    未勾选的修正项不参与计算（相当于 1.0）
    """

    id: int = Field(default=None, primary_key=True)
    modifier_id: str = Field(index=True, unique=True)  # diameter / coating / disturbance / cover_3d / cover_5d
    name: str  # 中文名，如"直径修正"
    condition: str  # >25mm / 环氧涂层 / 施工扰动 / 保护层厚度 3d / 5d
    factor: float  # 修正系数（>1.0 为增大，<1.0 为减小）
    note: str = ""  # 补充说明


class AnchorTable(SQLModel, table=True):
    """预置锚固表 - 查表法直接取 lab 的 d 倍数

    来源 22G101-1 p.58 受拉钢筋基本锚固长度表。
    真实数值待用户提供后导入。
    """

    id: int = Field(default=None, primary_key=True)
    concrete_grade: str = Field(index=True)  # C20..C60
    rebar_type: str = Field(index=True)  # HRB300/HRB400/HRB500
    lab_d: int  # lab 的 d 倍数


class Specification(SQLModel, table=True):
    """图集条文 - 22G101 条文转写为 HTML"""

    id: str = Field(primary_key=True)  # spec-anchor-general 等
    clause_number: str = Field(index=True)  # 2.2.1
    title: str
    category: str = Field(index=True)  # 柱/梁/墙/一般构造
    content_html: str
    related_calc: Optional[str] = None  # 关联计算类型，如 anchor
    related_ann_type: Optional[str] = None  # 关联标注类型，如 beam


class AnnotationRule(SQLModel, table=True):
    """标注解析规则 - 正则 + 字段映射 + 释义关联

    pattern / field_map / glossary_entries / examples 均存 JSON 字符串，
    由 annotation_parser 解析时 json.loads 还原。
    """

    id: int = Field(default=None, primary_key=True)
    type: str = Field(index=True)  # beam / column
    pattern: str  # 正则表达式
    name: str  # 规则名称
    examples: str  # JSON 数组字符串，如 ["KL7(3) 300×650"]
    field_map: str  # JSON 映射字符串，捕获组序号 -> 字段名
    glossary_entries: str  # JSON 数组字符串，关联 glossary.id 列表
    related_spec_id: Optional[str] = None
    default_rebar_type: Optional[str] = None


class Glossary(SQLModel, table=True):
    """符号释义表 - 标注符号的含义说明"""

    id: str = Field(primary_key=True)  # glossary-KL 等
    symbol: str = Field(index=True)  # KL, (3), 300×650
    meaning: str  # 框架梁
    description: str  # 详细说明


class RebarDiameter(SQLModel, table=True):
    """钢筋直径列表 - GB50010 规定的标准直径"""

    id: int = Field(default=None, primary_key=True)
    diameter: int = Field(index=True, unique=True)  # 6, 8, 10...50
    note: str = ""  # 常用/大直径
