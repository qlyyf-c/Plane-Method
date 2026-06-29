"""
测试数据选项 API - /api/v1/data/

验证：
- 混凝土等级、钢筋类型、抗震等级、钢筋直径列表正确返回
- 修正系数列表可正常获取
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestDataAPI:
    """测试 /api/v1/data/ 基础路由 - 验证响应结构"""

    def test_concrete_grades(self):
        """测试混凝土等级接口返回正确结构"""
        response = client.get("/api/v1/data/concrete-grades")
        assert response.status_code == 200
        data = response.json()
        assert "grades" in data
        assert isinstance(data["grades"], list)

    def test_rebar_types(self):
        """测试钢筋类型接口返回正确结构"""
        response = client.get("/api/v1/data/rebar-types")
        assert response.status_code == 200
        data = response.json()
        assert "types" in data
        assert isinstance(data["types"], list)

    def test_seismic_grades(self):
        """测试抗震等级接口返回正确结构"""
        response = client.get("/api/v1/data/seismic-grades")
        assert response.status_code == 200
        data = response.json()
        assert "grades" in data
        assert isinstance(data["grades"], list)

    def test_diameters(self):
        """测试钢筋直径列表 - 应返回 15 个直径（6-50mm）"""
        response = client.get("/api/v1/data/diameters")
        assert response.status_code == 200
        data = response.json()
        assert "diameters" in data
        assert isinstance(data["diameters"], list)
        assert len(data["diameters"]) == 15


class TestDataAPIWithDatabase:
    """测试 /api/v1/data/ 数据库查询功能"""

    def test_concrete_grades_from_db(self):
        """测试混凝土等级从数据库返回（8 个等级：C25-C60）"""
        response = client.get("/api/v1/data/concrete-grades")
        assert response.status_code == 200
        data = response.json()
        assert len(data["grades"]) == 8

    def test_rebar_types_from_db(self):
        """测试钢筋类型从数据库返回（3 种：HPB300/HRB400/HRB500）"""
        response = client.get("/api/v1/data/rebar-types")
        assert response.status_code == 200
        data = response.json()
        assert len(data["types"]) == 3

    def test_seismic_grades_from_db(self):
        """测试抗震等级从数据库返回（5 个等级）"""
        response = client.get("/api/v1/data/seismic-grades")
        assert response.status_code == 200
        data = response.json()
        assert len(data["grades"]) == 5

    def test_modifiers(self):
        """测试修正系数列表（5 种可勾选修正）"""
        response = client.get("/api/v1/data/modifiers")
        assert response.status_code == 200
        data = response.json()
        assert "modifiers" in data
        assert isinstance(data["modifiers"], list)
        assert len(data["modifiers"]) == 5
        # 验证 modifier_id 存在
        modifier_ids = [m["modifier_id"] for m in data["modifiers"]]
        assert "diameter" in modifier_ids
        assert "coating" in modifier_ids
        assert "cover_3d" in modifier_ids
        assert "cover_5d" in modifier_ids
