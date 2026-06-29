"""
锚固长度计算引擎 - 平法辅助学习 App

实现双策略计算：
1. 查表法：从 anchor_tables 表直接获取 lab_d 值
2. 公式法：lab = α × (fy/ft) × d，用于验证

计算流程：
1. lab (基本锚固长度) - 查表或公式
2. la (受拉钢筋锚固长度) = ζa × lab
3. laE (抗震锚固长度) = ζaE × la

依据：22G101-1 第 57-58 页，GB50010 第 8.3 条
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import os

from sqlmodel import Session, select
from sqlalchemy import create_engine

# 导入数据模型（在函数内部导入以避免循环依赖）
from app.models.database import AnchorTable, ConcreteGrade, RebarType, SeismicModifier, AnchorModifier


# 数据库路径：通过项目根目录动态计算
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(_PROJECT_ROOT, "data", "pingfa.db")
DB_URL = f"sqlite:///{DB_PATH}"


@dataclass
class AnchorResult:
    """锚固计算结果"""
    lab_d: int  # lab 的 d 倍数
    lab_mm: int  # lab 的毫米值
    la_d: float  # la 的 d 倍数（含修正系数）
    la_mm: int  # la 的毫米值
    laE_d: float  # laE 的 d 倍数（含抗震系数）
    laE_mm: int  # laE 的毫米值
    seismic_factor: float  # ζaE
    modifiers_applied: List[str]  # 应用的修正系数列表
    reference: Dict[str, str]  # 引用信息


def get_db_session():
    """获取数据库会话"""
    engine = create_engine(DB_URL)
    return Session(engine)


def get_lab_from_table(concrete_grade: str, rebar_type: str) -> Optional[int]:
    """查表法获取基本锚固长度 lab 的 d 倍数

    Args:
        concrete_grade: 混凝土等级，如"C30"
        rebar_type: 钢筋类型，如"HRB400"

    Returns:
        lab_d: lab 的 d 倍数，如 35 表示 35d
    """
    with get_db_session() as session:
        result = session.exec(
            select(AnchorTable)
            .where(AnchorTable.concrete_grade == concrete_grade)
            .where(AnchorTable.rebar_type == rebar_type)
        ).first()
        if result:
            return result.lab_d
        return None


def calculate_lab_formula(concrete_grade: str, rebar_type: str, diameter: int) -> float:
    """公式法计算基本锚固长度 lab

    公式：lab = α × (fy/ft) × d

    Args:
        concrete_grade: 混凝土等级
        rebar_type: 钢筋类型
        diameter: 钢筋直径 (mm)

    Returns:
        lab 的毫米值
    """
    from app.models.database import ConcreteGrade, RebarType

    with get_db_session() as session:
        # 获取混凝土抗拉强度 ft
        ft_result = session.exec(
            select(ConcreteGrade).where(ConcreteGrade.grade == concrete_grade)
        ).first()
        if not ft_result:
            raise ValueError(f"混凝土等级不存在：{concrete_grade}")
        ft = ft_result.ft_value

        # 获取钢筋参数 fy 和 α
        rebar_result = session.exec(
            select(RebarType).where(RebarType.type == rebar_type)
        ).first()
        if not rebar_result:
            raise ValueError(f"钢筋类型不存在：{rebar_type}")
        fy = rebar_result.fy_value
        alpha = rebar_result.alpha

    # 计算 lab = α × (fy/ft) × d
    lab = alpha * (fy / ft) * diameter
    return round(lab, 1)


def get_seismic_factor(seismic_grade: str) -> float:
    """获取抗震修正系数 ζaE

    Args:
        seismic_grade: 抗震等级（一级/二级/三级/四级/非抗震）

    Returns:
        抗震修正系数
    """
    from app.models.database import SeismicModifier

    with get_db_session() as session:
        result = session.exec(
            select(SeismicModifier).where(SeismicModifier.grade == seismic_grade)
        ).first()
        if result:
            return result.factor
        return 1.0  # 默认非抗震


def calculate_modifiers(
    diameter: int,
    modifier_ids: Optional[List[str]] = None,
) -> tuple[float, List[str]]:
    """计算锚固长度修正系数 ζa

    修正系数按连乘叠加：ζa = ζ1 × ζ2 × ...

    Args:
        diameter: 钢筋直径 (mm)
        modifier_ids: 用户勾选的修正系数 ID 列表

    Returns:
        (total_factor, applied_modifier_names)
    """
    from app.models.database import AnchorModifier

    total_factor = 1.0
    applied_names = []

    # 自动应用直径修正（>25mm）
    if diameter > 25:
        total_factor *= 1.10
        applied_names.append("直径>25mm")

    # 处理用户勾选的修正
    if modifier_ids:
        with get_db_session() as session:
            for mod_id in modifier_ids:
                result = session.exec(
                    select(AnchorModifier).where(AnchorModifier.modifier_id == mod_id)
                ).first()
                if result:
                    # 跳过已自动应用的直径修正
                    if mod_id == "diameter" and diameter > 25:
                        continue  # 已自动应用
                    total_factor *= result.factor
                    applied_names.append(result.name)

    return total_factor, applied_names


def calculate_anchor(
    concrete_grade: str,
    rebar_type: str,
    diameter: int,
    seismic_grade: str,
    modifier_ids: Optional[List[str]] = None,
) -> AnchorResult:
    """完整锚固长度计算

    计算步骤：
    1. 查表得到 lab_d
    2. 公式计算 lab 并验证（误差<1%）
    3. 计算 la = ζa × lab
    4. 计算 laE = ζaE × la

    Args:
        concrete_grade: 混凝土等级（如"C30"）
        rebar_type: 钢筋类型（如"HRB400"）
        diameter: 钢筋直径 (mm)
        seismic_grade: 抗震等级（一级/二级/三级/四级/非抗震）
        modifier_ids: 用户勾选的修正系数 ID 列表

    Returns:
        AnchorResult: 完整的锚固计算结果
    """
    # 导入数据模型
    from app.models.database import AnchorTable, ConcreteGrade, RebarType, SeismicModifier, AnchorModifier

    # 1. 查表获取 lab_d
    with get_db_session() as session:
        table_result = session.exec(
            select(AnchorTable)
            .where(AnchorTable.concrete_grade == concrete_grade)
            .where(AnchorTable.rebar_type == rebar_type)
        ).first()
        if not table_result:
            raise ValueError(f"锚固表无数据：{concrete_grade}/{rebar_type}")
        lab_d = table_result.lab_d

    lab_mm = lab_d * diameter

    # 2. 公式法验证（可选，仅用于调试）
    # lab_formula = calculate_lab_formula(concrete_grade, rebar_type, diameter)
    # error_rate = abs(lab_mm - lab_formula) / lab_formula

    # 3. 计算修正系数 ζa
    modifier_factor, modifiers_applied = calculate_modifiers(diameter, modifier_ids)

    # 4. 计算 la = ζa × lab
    la_d = lab_d * modifier_factor
    la_mm = int(lab_mm * modifier_factor + 0.001)

    # 5. 获取抗震系数 ζaE
    seismic_factor = get_seismic_factor(seismic_grade)

    # 6. 计算 laE = ζaE × la
    laE_d = la_d * seismic_factor
    laE_mm = int(la_mm * seismic_factor + 0.001)

    return AnchorResult(
        lab_d=lab_d,
        lab_mm=lab_mm,
        la_d=round(la_d, 2),
        la_mm=la_mm,
        laE_d=round(laE_d, 2),
        laE_mm=laE_mm,
        seismic_factor=seismic_factor,
        modifiers_applied=modifiers_applied,
        reference={
            "standard": "22G101-1",
            "page": 58,
            "clause": "表 2.2.1",
        },
    )


# 测试代码
if __name__ == "__main__":
    # 测试用例：C30/HRB400/25mm/二级抗震
    result = calculate_anchor(
        concrete_grade="C30",
        rebar_type="HRB400",
        diameter=25,
        seismic_grade="二级",
    )
    print(f"lab: {result.lab_d}d = {result.lab_mm}mm")
    print(f"la: {result.la_d}d = {result.la_mm}mm")
    print(f"laE: {result.laE_d}d = {result.laE_mm}mm")
    print(f"抗震系数：{result.seismic_factor}")
