"""
标注解析引擎 - 平法辅助学习 App

依据 22G101-1 图集，解析梁/柱平法标注：
- KL7(3) 300×650 → 框架梁，编号 7，3 跨，截面 300×650
- KZ1 500×500 → 框架柱，编号 1，截面 500×500

工作机制：
1. 从数据库加载标注规则(annotation_rules 表)
2. 按类型逐条匹配正则 pattern
3. 命中后提取捕获组字段
4. 关联 glossary 组装释义
"""
import os
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

from sqlmodel import Session, select
from sqlalchemy import create_engine

from app.models.database import AnnotationRule, Glossary


# 数据库路径(动态路径，兼容 WSL/Linux/Windows)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(_PROJECT_ROOT, "data", "pingfa.db")
DB_URL = f"sqlite:///{DB_PATH}"


@dataclass
class ParsedAnnotation:
    """解析结果"""
    component_type: str  # KL, KZ 等
    component_name: str  # 框架梁，框架柱
    number: int  # 编号
    span_count: Optional[str] = None  # 跨数描述，如"3跨，两端有悬挑"
    width: Optional[int] = None  # 截面宽
    height: Optional[int] = None  # 截面高


@dataclass
class AnnotationParseResult:
    """完整解析结果"""
    success: bool
    parsed: Optional[ParsedAnnotation] = None
    glossary: List[Dict[str, str]] = None
    related_spec_id: Optional[str] = None
    related_calc_params: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    suggestion: Optional[str] = None
    partial: Optional[Dict[str, Any]] = None


def get_db_session():
    """获取数据库会话"""
    engine = create_engine(DB_URL)
    return Session(engine)


def load_rules() -> List[AnnotationRule]:
    """从数据库加载所有标注规则"""
    with get_db_session() as session:
        return list(session.exec(select(AnnotationRule)).all())


def load_glossary(glossary_ids: List[str]) -> List[Dict[str, str]]:
    """根据 ID 列表查询释义表"""
    with get_db_session() as session:
        results = session.exec(
            select(Glossary).where(Glossary.id.in_(glossary_ids))
        ).all()
        return [
            {"symbol": g.symbol, "meaning": g.meaning, "description": g.description}
            for g in results
        ]


def parse_annotation(text: str) -> AnnotationParseResult:
    """解析标注字符串

    Args:
        text: 标注文本，如 "KL7(3) 300x650" 或 "KL7(3) 300×650"

    Returns:
        AnnotationParseResult: 完整的解析结果
    """
    import re

    # 标准化输入：将 x/X 替换为 ×(兼容两种输入方式)，转大写
    normalized_text = text.replace("x", "×").replace("X", "×").strip().upper()

    rules = load_rules()

    # 尝试匹配每条规则
    for rule in rules:
        try:
            pattern = rule.pattern
            match = re.match(pattern, normalized_text)

            if match:
                # 提取字段
                groups = match.groups()

                field_map = json.loads(rule.field_map)

                parsed_data = {}
                for group_idx, field_name in field_map.items():
                    idx = int(group_idx)
                    if idx < len(groups) and groups[idx] is not None:
                        parsed_data[field_name] = groups[idx]

                # 构建解析结果
                component_type = parsed_data.get("component_type", "")
                number = int(parsed_data.get("number", 0)) if parsed_data.get("number") else 0

                # 解析跨数及悬挑信息
                # 平法规则：
                #   (3)    → 3跨，两端都无悬挑
                #   (3A)   → 3跨，一端有悬挑
                #   (3B)   → 3跨，两端有悬挑
                span_count = None

                span_count_raw = parsed_data.get("span_count_raw")
                if span_count_raw:
                    # 去掉括号
                    clean_span = span_count_raw.strip("()")
                    # 分离数字和字母
                    m = re.match(r'^(\d+)([AB]*)$', clean_span)
                    if m:
                        n = m.group(1)
                        tag = m.group(2)
                        if not tag:
                            span_count = f"{n}跨"
                        elif tag == "A":
                            span_count = f"{n}跨，一端有悬挑"
                        elif tag == "B":
                            span_count = f"{n}跨，两端有悬挑"
                        else:
                            span_count = f"{n}跨，两端都有悬挑"

                # 解析截面尺寸
                width_str = parsed_data.get("width")
                height_str = parsed_data.get("height")
                width = int(width_str) if width_str else None
                height = int(height_str) if height_str else None

                # 组件名称映射
                name_map = {
                    "KL": "框架梁",
                    "L": "非框架梁",
                    "WKL": "屋面框架梁",
                    "XL": "悬挑梁",
                    "KZ": "框架柱",
                    "Z": "柱",
                    "QZ": "剪力墙上柱",
                }
                component_name = name_map.get(component_type, component_type)

                parsed = ParsedAnnotation(
                    component_type=component_type,
                    component_name=component_name,
                    number=number,
                    span_count=span_count,
                    width=width,
                    height=height,
                )

                # 查询释义
                glossary_entries = json.loads(rule.glossary_entries)
                glossary = load_glossary(glossary_entries)

                return AnnotationParseResult(
                    success=True,
                    parsed=parsed,
                    glossary=glossary,
                    related_spec_id=rule.related_spec_id,
                    related_calc_params={
                        "rebar_type": rule.default_rebar_type,
                        "diameter": None,  # 无法从标注推断
                    },
                )
        except Exception:
            continue

    # 完全失败，尝试部分匹配
    partial = partial_match(text)

    return AnnotationParseResult(
        success=False,
        error="无法识别标注格式",
        suggestion="支持的标注格式：\n- 梁：KL/L/WKL/XL 编号 (跨数) 宽×高\n- 柱：KZ/Z/QZ 编号 宽×高",
        partial=partial,
    )


def partial_match(text: str) -> Optional[Dict[str, Any]]:
    """尝试部分匹配，返回已识别的部分信息"""
    import re
    
    # 尝试识别构件类型
    type_pattern = r"^(KL|L|WKL|XL|KZ|Z|QZ)(\d+)"
    match = re.match(type_pattern, text.strip(), re.IGNORECASE)
    
    if match:
        return {
            "component_type": match.group(1).upper(),
            "number": int(match.group(2)),
        }
    
    return None


def get_examples() -> List[str]:
    """获取常用标注示例"""
    rules = load_rules()
    examples = []
    for rule in rules:
        try:
            ex_list = json.loads(rule.examples)
            examples.extend(ex_list)
        except json.JSONDecodeError:
            pass
    return examples


def get_types() -> List[Dict[str, str]]:
    """获取支持的标注类型"""
    types_map = {
        "beam": "梁标注 (KL/L/WKL/XL)",
        "column": "柱标注 (KZ/Z/QZ)",
    }
    return [{"type": k, "name": v} for k, v in types_map.items()]


def get_glossary_all() -> List[Dict[str, str]]:
    """获取完整释义表"""
    with get_db_session() as session:
        results = session.exec(select(Glossary)).all()
        return [
            {"id": g.id, "symbol": g.symbol, "meaning": g.meaning, "description": g.description}
            for g in results
        ]


# 测试代码
if __name__ == "__main__":
    # 测试用例
    test_cases = [
        "KL7(3) 300×650",
        "L2(1A) 250×500",
        "WKL3(2) 300×700",
        "KZ1 500×500",
        "Z2 400×600",
        "INVALID",
    ]
    
    for text in test_cases:
        result = parse_annotation(text)
        print(f"\n输入：{text}")
        print(f"成功：{result.success}")
        if result.success and result.parsed:
            print(f"解析：{asdict(result.parsed)}")
            print(f"释义：{len(result.glossary)} 条")
        else:
            print(f"错误：{result.error}")
            print(f"建议：{result.suggestion}")
