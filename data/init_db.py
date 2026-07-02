"""
数据库初始化脚本 - 平法辅助学习 App

功能：
1. 读取 data/ 下所有 JSON 数据文件
2. 创建 SQLModel 表结构
3. 将数据导入 SQLite 数据库

设计要点：
- 数据中有 null 值的字段（如 ft_value、lab_d）表示"待用户提供"，导入时跳过这些条目
- 数据中有 _note 字段用于注释说明，导入时忽略（模型无此字段）
- 重复运行时先删除旧数据库再重建，确保干净状态

使用方式：
  cd pingfa_app
  python data/init_db.py
"""
import json
import os
import sys

from sqlmodel import Session, create_engine

# 确保 backend 模块可导入
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_PATH)

from app.models.database import (  # noqa: E402
    AnchorModifier,
    AnchorTable,
    AnnotationRule,
    ConcreteGrade,
    Glossary,
    RebarDiameter,
    RebarType,
    SeismicModifier,
    Specification,
    SQLModel,
)

# 数据库文件路径
DB_PATH = os.path.join(PROJECT_ROOT, "data", "pingfa.db")
DB_URL = f"sqlite:///{DB_PATH}"

# JSON 数据文件目录
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# 条文数据文件目录（使用 build/ 目录下的新格式文件）
SPECIFICATIONS_DIR = os.path.join(PROJECT_ROOT, "data", "specifications", "build")


def load_json(filename: str) -> list:
    """加载 JSON 数据文件，返回列表"""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  [WARN] 文件不存在：{filepath}, 跳过")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print(f"  [WARN] 文件格式错误：{filepath}, 期望列表，跳过")
        return []
    return data


def load_spec_json(filename: str) -> list:
    """加载条文 JSON 数据文件（从 SPECIFICATIONS_DIR 目录）"""
    filepath = os.path.join(SPECIFICATIONS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  [WARN] 文件不存在：{filepath}, 跳过")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print(f"  [WARN] 文件格式错误：{filepath}, 期望列表，跳过")
        return []
    return data


def clean_record(record: dict, model_class) -> dict:
    """清理单条记录：
    - 移除 _note 注释字段（模型不包含）
    - Optional 字段允许 null（转为 Python None）
    - 非 Optional 字段出现 null 时，整条跳过（数据未就绪）
    """
    cleaned = {}

    # 收集模型中 Optional 字段名（字段类型包含 Optional/None）
    optional_fields = set()
    for name, field_info in model_class.model_fields.items():
        # SQLModel 字段的 is_required() 返回 False 表示 Optional
        if not field_info.is_required():
            optional_fields.add(name)

    for key, value in record.items():
        if key.startswith("_"):
            continue  # 跳过注释字段
        if value is None:
            if key in optional_fields:
                cleaned[key] = None  # Optional 字段允许 null
            else:
                # 非 Optional 字段为 null -> 数据未就绪，整条跳过
                return None
        else:
            cleaned[key] = value

    return cleaned


def import_data(session: Session, model_class, filename: str) -> int:
    """导入一个 JSON 文件的数据到对应表"""
    data = load_json(filename)
    if not data:
        return 0

    count = 0
    skipped = 0
    for record in data:
        cleaned = clean_record(record, model_class)
        if cleaned is None:
            skipped += 1
            continue
        try:
            instance = model_class(**cleaned)
            session.add(instance)
            count += 1
        except Exception as e:
            print(f"  [WARN] 导入失败：{record} -> {e}")
            skipped += 1

    session.commit()
    print(f"  [OK] {model_class.__name__}: 导入 {count} 条，跳过 {skipped} 条 (数据待填入)")
    return count


def import_spec_data(session: Session, model_class, filename: str) -> int:
    """导入一个 JSON 文件的数据到对应表（从 SPECIFICATIONS_DIR 目录）"""
    data = load_spec_json(filename)
    if not data:
        return 0

    count = 0
    skipped = 0
    for record in data:
        cleaned = clean_record(record, model_class)
        if cleaned is None:
            skipped += 1
            continue
        try:
            instance = model_class(**cleaned)
            session.add(instance)
            count += 1
        except Exception as e:
            print(f"  [WARN] 导入失败：{record} -> {e}")
            skipped += 1

    session.commit()
    print(f"  [OK] {model_class.__name__}: 导入 {count} 条，跳过 {skipped} 条 (数据待填入)")
    return count


def main():
    """主函数：建表 + 导入数据"""
    # 删除旧数据库（确保干净重建）
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"已删除旧数据库：{DB_PATH}")

    # 创建引擎和表
    engine = create_engine(DB_URL, echo=False)
    SQLModel.metadata.create_all(engine)
    print("[OK] 表结构创建完成")

    # 导入数据
    with Session(engine) as session:
        total = 0

        print("\n--- 导入锚固数据 ---")
        total += import_data(session, ConcreteGrade, "anchor/concrete_strength.json")
        total += import_data(session, RebarType, "anchor/rebar_strength.json")
        total += import_data(session, RebarDiameter, "anchor/rebar_diameters.json")
        total += import_data(session, SeismicModifier, "anchor/seismic_modifiers.json")
        total += import_data(session, AnchorModifier, "anchor/anchor_modifiers.json")
        total += import_data(session, AnchorTable, "anchor/lab_table.json")

        print("\n--- 导入标注数据 ---")
        # annotation_rules: beam_rules + column_rules
        total += import_data(session, AnnotationRule, "annotation/beam_rules.json")
        total += import_data(session, AnnotationRule, "annotation/column_rules.json")
        total += import_data(session, Glossary, "annotation/glossary.json")

        print("\n--- 导入条文数据 ---")
        # 使用 build/ 目录下的新格式文件（由 Markdown 源文件构建生成）
        total += import_spec_data(session, Specification, "general_rules.json")
        total += import_spec_data(session, Specification, "column_rules.json")
        total += import_spec_data(session, Specification, "beam_rules.json")

    print(f"\n[OK] 数据库初始化完成，共导入 {total} 条记录")
    print(f"  数据库文件：{DB_PATH}")

    # 验证：查看各表记录数
    from sqlalchemy import text

    with Session(engine) as session:
        for table_name in [
            "concretegrade",
            "rebartype",
            "rebardiameter",
            "seismicmodifier",
            "anchormodifier",
            "anchortable",
            "annotationrule",
            "glossary",
            "specification",
        ]:
            result = session.exec(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.one()
            print(f"  {table_name}: {count} 条记录")


if __name__ == "__main__":
    main()
