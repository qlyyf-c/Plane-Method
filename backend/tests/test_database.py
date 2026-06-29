"""
测试 SQLModel 数据库模型定义

验证：
1. 所有模型类定义正确
2. 数据库可以创建
3. 表结构符合预期
"""
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from sqlmodel import Session, create_engine, SQLModel

from app.models.database import (
    ConcreteGrade,
    RebarType,
    SeismicModifier,
    AnchorTable,
    Specification,
    AnnotationRule,
    Glossary,
)


def test_model_classes_exist():
    """测试所有模型类定义存在"""
    assert ConcreteGrade is not None
    assert RebarType is not None
    assert SeismicModifier is not None
    assert AnchorTable is not None
    assert Specification is not None
    assert AnnotationRule is not None
    assert Glossary is not None


def test_model_fields():
    """测试模型字段定义"""
    # ConcreteGrade
    cg_fields = ConcreteGrade.model_fields
    assert "id" in cg_fields
    assert "grade" in cg_fields
    assert "ft_value" in cg_fields

    # RebarType
    rt_fields = RebarType.model_fields
    assert "id" in rt_fields
    assert "type" in rt_fields
    assert "fy_value" in rt_fields
    assert "alpha" in rt_fields

    # SeismicModifier
    sm_fields = SeismicModifier.model_fields
    assert "id" in sm_fields
    assert "grade" in sm_fields
    assert "factor" in sm_fields

    # Specification
    spec_fields = Specification.model_fields
    assert "id" in spec_fields
    assert "clause_number" in spec_fields
    assert "title" in spec_fields
    assert "category" in spec_fields
    assert "content_html" in spec_fields


def test_database_creation():
    """测试数据库可以创建"""
    # 使用临时文件
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)

    # 创建所有表
    SQLModel.metadata.create_all(engine)

    # 验证表存在
    from sqlalchemy import text

    with Session(engine) as session:
        # 查询各表是否存在（通过查询 count）
        for table_name in [
            "concretegrade",
            "rebartype",
            "seismicmodifier",
            "anchortable",
            "specification",
            "annotationrule",
            "glossary",
        ]:
            result = session.exec(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.one()[0]  # result.one() 返回元组
            assert count == 0  # 空表

    # 清理：先关闭 engine 再删除文件
    engine.dispose()
    os.unlink(db_path)


def test_seismic_modifier_insert():
    """测试 SeismicModifier 数据插入（这条表有完整数据）"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # 插入一条测试数据
        sm = SeismicModifier(grade="一级", factor=1.15, note="测试")
        session.add(sm)
        session.commit()

        # 验证插入成功
        from sqlalchemy import text

        result = session.exec(text("SELECT COUNT(*) FROM seismicmodifier"))
        count = result.one()[0]  # result.one() 返回元组
        assert count == 1

    engine.dispose()
    os.unlink(db_path)


def test_annotation_rule_json_fields():
    """测试 AnnotationRule 的 JSON 字段存储"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        rule = AnnotationRule(
            type="beam",
            pattern="^(KL|L)(\\d+)$",
            name="梁标注",
            examples='["KL7(3) 300x650"]',
            field_map='{"1":"component_type"}',
            glossary_entries='["glossary-KL"]',
        )
        session.add(rule)
        session.commit()

        # 验证 JSON 字段存储正确
        from sqlalchemy import text

        result = session.exec(text("SELECT examples FROM annotationrule WHERE id=1"))
        examples = result.one()[0]  # result.one() 返回元组
        assert examples == '["KL7(3) 300x650"]'

    engine.dispose()
    os.unlink(db_path)