"""
标注解析引擎 - 平法辅助学习 App

依据 22G101-1 图集，智能解析梁/柱平法标注：
- KL7(3) 300×650 → 完全匹配，返回完整信息
- KL4（5）→ 支持中文括号，部分匹配
- KL           → 仅类型也能识别
- L3           → 部分匹配，识别类型 + 编号
- WKL6(5)      → 部分匹配，识别类型 + 编号 + 跨数
- KZ1 500×500  → 完全匹配

工作机制：
1. 标准化输入（统一括号、统一乘号）
2. 优先尝试完全匹配标准格式
3. 其次部分匹配，提取能识别的信息
4. 智能提示用户补充缺失内容
"""
import os
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

from sqlmodel import Session, select
from sqlalchemy import create_engine

from app.models.database import Glossary


# 数据库路径 (动态路径，兼容 WSL/Linux/Windows)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(_PROJECT_ROOT, "data", "pingfa.db")
DB_URL = f"sqlite:///{DB_PATH}"


def get_db_session():
    """获取数据库会话"""
    engine = create_engine(DB_URL)
    return Session(engine)


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


def normalize_text(text: str) -> str:
    """标准化输入文本
    - 统一括号：中文括号 → 英文括号
    - 统一乘号：x/X → ×
    - 去除多余空格
    - 转大写
    """
    # 统一括号：中文括号 → 英文括号
    text = text.replace("(", "(").replace(")", ")")
    # 统一乘号
    text = text.replace("x", "×").replace("X", "×")
    # 去除多余空格（但保留数字和符号间的必要空格）
    text = re.sub(r'\s+', ' ', text.strip())
    # 转大写
    return text.upper()


@dataclass
class ParsedAnnotation:
    """解析结果"""
    component_type: str  # KL, KZ 等
    component_name: str  # 框架梁，框架柱
    number: int  # 编号
    span_count: Optional[str] = None  # 跨数描述
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


def parse_annotation(text: str) -> AnnotationParseResult:
    """解析标注字符串

    采用分层解析策略：
    1. 标准化输入（统一括号、乘号）
    2. 优先完全匹配标准格式
    3. 其次部分匹配，提取能识别的信息
    4. 最后智能提示缺失内容

    Args:
        text: 标注文本，如 "KL7(3) 300x650"、"KL"、"KL4（5）" 等

    Returns:
        AnnotationParseResult: 完整的解析结果
    """
    # 标准化输入
    normalized_text = normalize_text(text)

    # 1. 优先尝试完全匹配标准格式
    full_result = try_full_match(normalized_text)
    if full_result:
        return full_result

    # 2. 完全匹配失败，尝试部分匹配
    partial = partial_match(normalized_text)

    if partial and partial.get("component_type"):
        return build_partial_result(partial)

    # 3. 完全无法识别
    return AnnotationParseResult(
        success=False,
        error="无法识别该标注",
        suggestion=get_help_suggestion(),
    )


def try_full_match(text: str) -> Optional[AnnotationParseResult]:
    """尝试完全匹配标准格式的标注"""
    # 梁的标准格式：KL/L/WKL/XL + 编号 + (跨数)[A/B]? + 截面
    beam_pattern = r'^(KL|L|WKL|XL)(\d+)(\(([0-9]+[AB]?)\))?\s*(\d+)\s*[×x]\s*(\d+)$'
    # 柱的标准格式：KZ/Z/QZ 等 + 编号 + 截面
    column_pattern = r'^(KZ|Z|QZ|LZ|ZH|XZ)(\d+)\s*(\d+)\s*[×x]\s*(\d+)$'

    # 尝试梁的匹配
    match = re.match(beam_pattern, text, re.IGNORECASE)
    if match:
        return build_beam_result(match)

    # 尝试柱的匹配
    match = re.match(column_pattern, text, re.IGNORECASE)
    if match:
        return build_column_result(match)

    return None


def build_beam_result(match) -> AnnotationParseResult:
    """构建梁的完全匹配结果"""
    component_type = match.group(1).upper()
    number = int(match.group(2))
    span_group = match.group(3)  # 包含括号的跨数
    span_clean = match.group(4)  # 纯数字跨数
    width = int(match.group(5))
    height = int(match.group(6))

    # 解析跨数及悬挑信息
    span_count = None
    if span_group:
        clean_span = span_group.strip("()")
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

    # 组件名称映射
    name_map = {"KL": "框架梁", "L": "非框架梁", "WKL": "屋面框架梁", "XL": "悬挑梁"}
    component_name = name_map.get(component_type, component_type)

    parsed = ParsedAnnotation(
        component_type=component_type,
        component_name=component_name,
        number=number,
        span_count=span_count,
        width=width,
        height=height,
    )

    glossary_ids = ["glossary-KL", "glossary-span", "glossary-section"]
    glossary = load_glossary(glossary_ids)

    return AnnotationParseResult(
        success=True,
        parsed=parsed,
        glossary=glossary,
        related_spec_id="spec-beam-notation",
        related_calc_params={"rebar_type": "HRB400", "diameter": None},
    )


def build_column_result(match) -> AnnotationParseResult:
    """构建柱的完全匹配结果"""
    component_type = match.group(1).upper()
    number = int(match.group(2))
    width = int(match.group(3))
    height = int(match.group(4))

    name_map = {
        "KZ": "框架柱", "Z": "非框架柱",
        "QZ": "墙上柱", "LZ": "梁上柱",
        "ZH": "转换柱", "XZ": "芯柱",
    }
    component_name = name_map.get(component_type, component_type)

    parsed = ParsedAnnotation(
        component_type=component_type,
        component_name=component_name,
        number=number,
        width=width,
        height=height,
    )

    # 根据构件类型加载对应的释义
    # QZ/LZ 返回其自身的"已取消"说明，KZ/Z/ZH/XZ 返回各自释义
    glossary_id_map = {
        "KZ": "glossary-KZ",
        "Z": "glossary-Z",
        "QZ": "glossary-QZ",
        "LZ": "glossary-LZ",
        "ZH": "glossary-ZH",
        "XZ": "glossary-XZ",
    }
    glossary_id = glossary_id_map.get(component_type, "glossary-KZ")
    glossary = load_glossary([glossary_id, "glossary-section"])

    return AnnotationParseResult(
        success=True,
        parsed=parsed,
        glossary=glossary,
        related_spec_id="spec-column-notation",
        related_calc_params={"rebar_type": "HRB400", "diameter": None},
    )


def partial_match(text: str) -> Optional[Dict[str, Any]]:
    """尝试部分匹配，返回已识别的部分信息

    支持的情况：
    - KL → 仅类型
    - L3 → 类型 + 编号
    - WKL6(5) → 类型 + 编号 + 跨数
    - KL7 300×650 → 类型 + 编号 + 截面
    - KL4（5）→ 中文括号也能识别
    """
    result = {}

    # 识别构件类型（支持只有类型的情况）
    type_only_pattern = r'^(KL|L|WKL|XL|KZ|Z|QZ|LZ|ZH|XZ)$'
    type_with_number_pattern = r'^(KL|L|WKL|XL|KZ|Z|QZ|LZ|ZH|XZ)(\d+)'

    # 先尝试类型 + 编号
    match = re.match(type_with_number_pattern, text, re.IGNORECASE)
    if match:
        result["component_type"] = match.group(1).upper()
        result["number"] = int(match.group(2))
    else:
        # 只有类型
        match = re.match(type_only_pattern, text, re.IGNORECASE)
        if match:
            result["component_type"] = match.group(1).upper()
            result["number"] = 0  # 无编号时设为 0
        else:
            return None

    component_type = result["component_type"]

    # 根据类型提取更多信息
    if component_type in ["KL", "L", "WKL", "XL"]:
        # 梁：尝试提取跨数（支持中英文括号）
        span_pattern = r'[（(](\d+)[AB]?[）)]'
        span_match = re.search(span_pattern, text, re.IGNORECASE)
        if span_match:
            span_clean = span_match.group(1)
            full_span = span_match.group(0)
            tag = ""
            if "A" in full_span.upper():
                tag = "A"
            elif "B" in full_span.upper():
                tag = "B"

            if not tag:
                result["span_count"] = f"{span_clean}跨"
            elif tag == "A":
                result["span_count"] = f"{span_clean}跨，一端有悬挑"
            elif tag == "B":
                result["span_count"] = f"{span_clean}跨，两端有悬挑"

        # 尝试提取截面（支持中英文乘号）
        section_pattern = r'(\d+)\s*[×xx]\s*(\d+)'
        section_match = re.search(section_pattern, text, re.IGNORECASE)
        if section_match:
            result["width"] = int(section_match.group(1))
            result["height"] = int(section_match.group(2))

    elif component_type in ["KZ", "Z", "QZ", "LZ", "ZH", "XZ"]:
        # 柱：尝试提取截面
        section_pattern = r'(\d+)\s*[×x x]\s*(\d+)'
        section_match = re.search(section_pattern, text, re.IGNORECASE)
        if section_match:
            result["width"] = int(section_match.group(1))
            result["height"] = int(section_match.group(2))

    return result


def build_partial_result(partial: Dict[str, Any]) -> AnnotationParseResult:
    """构建部分匹配结果"""
    component_type = partial["component_type"]
    number = partial["number"]

    # 组件名称映射
    name_map = {
        "KL": "框架梁", "L": "非框架梁", "WKL": "屋面框架梁", "XL": "悬挑梁",
        "KZ": "框架柱", "Z": "非框架柱",
        "QZ": "墙上柱", "LZ": "梁上柱",
        "ZH": "转换柱", "XZ": "芯柱",
    }
    component_name = name_map.get(component_type, component_type)

    parsed = ParsedAnnotation(
        component_type=component_type,
        component_name=component_name,
        number=number if number > 0 else None,  # 无编号时设为 None
        span_count=partial.get("span_count"),
        width=partial.get("width"),
        height=partial.get("height"),
    )

    # 获取基础释义 - 根据构件类型加载对应的 glossary
    glossary_id_map = {
        "KL": "glossary-KL", "L": "glossary-L", "WKL": "glossary-WKL", "XL": "glossary-XL",
        "KZ": "glossary-KZ", "Z": "glossary-Z",
        "QZ": "glossary-QZ", "LZ": "glossary-LZ",
        "ZH": "glossary-ZH", "XZ": "glossary-XZ",
    }
    glossary_id = glossary_id_map.get(component_type, "glossary-KZ")
    glossary = load_glossary([glossary_id])

    # 生成友好的提示信息
    suggestion = generate_suggestion(partial, component_type)

    return AnnotationParseResult(
        success=True,  # 部分匹配也视为成功
        parsed=parsed,
        glossary=glossary,
        related_spec_id="spec-beam-notation" if component_type in ["KL", "L", "WKL", "XL"] else "spec-column-notation",
        related_calc_params={"rebar_type": "HRB400", "diameter": None},
        partial=partial,
        suggestion=suggestion,
    )


def generate_suggestion(partial: Dict[str, Any], component_type: str) -> str:
    """根据已识别的信息生成友好的补充提示"""
    suggestions = []

    if component_type in ["KL", "L", "WKL", "XL"]:
        if partial.get("number", 0) == 0:
            suggestions.append("建议补充编号，如 KL7")
        if "span_count" not in partial:
            suggestions.append("可补充跨数，如 KL7(3)")
        if "width" not in partial or "height" not in partial:
            suggestions.append("可补充截面尺寸，如 300×650")

    elif component_type in ["KZ", "Z", "QZ", "LZ", "ZH", "XZ"]:
        if partial.get("number", 0) == 0:
            suggestions.append("建议补充编号，如 KZ1")
        if "width" not in partial or "height" not in partial:
            suggestions.append("可补充截面尺寸，如 500×500")

    if suggestions:
        return "提示：" + "; ".join(suggestions)

    return "已成功识别标注"


def get_help_suggestion() -> str:
    """获取帮助提示"""
    return """支持的标注格式：
- 梁：KL/L/WKL/XL 编号 [跨数] 宽×高
  示例：KL7(3) 300×650、L2、WKL6(5A)、KL7、KL
- 柱：KZ/Z/QZ/LZ/ZH/XZ 编号 [宽×高]
  示例：KZ1 500×500、Z2、QZ3

注意：支持中英文括号混用，如 KL4（5）、KL4(5)"""


def get_examples() -> List[str]:
    """获取常用标注示例"""
    return [
        "KL7(3) 300×650",
        "L2(1A) 250×500",
        "WKL6(5B) 400×800",
        "KZ1 500×500",
        "Z2 400×600",
        "KL",
        "L3",
        "WKL6(5)",
        "KL4（5）",  # 中文括号示例
    ]


def get_types() -> List[Dict[str, str]]:
    """获取支持的标注类型"""
    return [
        {"type": "beam", "name": "梁标注 (KL/L/WKL/XL)"},
        {"type": "column", "name": "柱标注 (KZ/Z/QZ/LZ/ZH/XZ)"},
    ]


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
    test_cases = [
        "KL7(3) 300×650",     # 完全匹配 - 梁
        "L2(1A) 250×500",     # 完全匹配 - 悬挑梁
        "WKL6(5B) 400×800",   # 完全匹配 - 两端悬挑
        "KZ1 500×500",        # 完全匹配 - 柱
        "Z2 400×600",         # 完全匹配 - 柱
        "KL",                 # 仅类型
        "L3",                 # 类型 + 编号
        "WKL6(5)",            # 类型 + 编号 + 跨数
        "KL7 300×650",        # 类型 + 编号 + 截面
        "KL7(3)",             # 类型 + 编号 + 跨数
        "KL4（5）",           # 中文括号
        "KL4(5)",             # 英文括号
        "KL4（5）300×650",    # 中文括号 + 截面
        "KL4(5) 300x650",     # 英文括号 + 小写 x
        "KL4（5）300x650",    # 中英文混合
        "INVALID",            # 无法识别
    ]

    print("=" * 70)
    for text in test_cases:
        result = parse_annotation(text)
        print(f"\n【{text}】")
        status = "OK" if result.success else "FAIL"
        print(f"  Status: {status}")
        if result.parsed:
            print(f"  Type: {result.parsed.component_name} ({result.parsed.component_type})")
            if result.parsed.number:
                print(f"  Number: {result.parsed.number}")
            if result.parsed.span_count:
                print(f"  Spans: {result.parsed.span_count}")
            if result.parsed.width and result.parsed.height:
                print(f"  Section: {result.parsed.width}x{result.parsed.height}")
        if result.suggestion:
            print(f"  Suggestion: {result.suggestion}")
        if result.error:
            print(f"  Error: {result.error}")
