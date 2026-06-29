"""
图集速查 API 测试 - /api/v1/specification/

测试覆盖：
- GET /search - 关键字搜索
- GET /categories - 分类列表
- GET /by-category - 按分类查询
- GET /detail/{id} - 条文详情
- GET /related/{id} - 关联内容
"""
import pytest
from fastapi.testclient import TestClient

# 确保 backend 模块可导入
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.main import app


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


class TestSpecificationAPI:
    """图集速查 API 测试类"""

    def test_search_with_keyword(self, client):
        """测试关键字搜索 - 应返回匹配结果"""
        response = client.get("/api/v1/specification/search", params={"keyword": "锚固"})
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "count" in data
        assert data["count"] > 0, "应至少找到锚固相关条文"
        # 验证返回结构
        result = data["results"][0]
        assert "id" in result
        assert "title" in result
        assert "snippet" in result

    def test_search_empty_keyword(self, client):
        """测试空关键字搜索"""
        response = client.get("/api/v1/specification/search", params={"keyword": ""})
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "请输入搜索关键字"
        assert data["results"] == []

    def test_search_no_results(self, client):
        """测试无匹配结果的搜索"""
        response = client.get("/api/v1/specification/search", params={"keyword": "不存在的关键词 XYZ"})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_get_categories(self, client):
        """测试获取分类列表"""
        response = client.get("/api/v1/specification/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        # 验证包含已知分类
        assert "一般构造" in data["categories"]
        assert "柱" in data["categories"]
        assert "梁" in data["categories"]

    def test_get_by_category_beam(self, client):
        """测试按分类查询 - 梁"""
        response = client.get("/api/v1/specification/by-category", params={"category": "梁"})
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "梁"
        assert "specifications" in data
        assert data["count"] > 0, "梁分类下应至少有条文"
        # 验证返回结构
        spec = data["specifications"][0]
        assert "id" in spec
        assert "title" in spec
        assert "clause_number" in spec

    def test_get_by_category_column(self, client):
        """测试按分类查询 - 柱"""
        response = client.get("/api/v1/specification/by-category", params={"category": "柱"})
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "柱"
        assert data["count"] > 0

    def test_get_by_category_empty(self, client):
        """测试按分类查询 - 空参数"""
        response = client.get("/api/v1/specification/by-category", params={"category": ""})
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "请指定分类参数 category"

    def test_get_detail_existing(self, client):
        """测试获取存在的条文详情"""
        response = client.get("/api/v1/specification/detail/spec-anchor-general")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "spec-anchor-general"
        assert data["clause_number"] == "8.3"
        assert "content_html" in data
        assert len(data["content_html"]) > 0

    def test_get_detail_not_found(self, client):
        """测试获取不存在的条文"""
        response = client.get("/api/v1/specification/detail/non-existent-id")
        assert response.status_code == 404

    def test_get_related_with_calc(self, client):
        """测试获取关联内容 - 有计算关联的条文"""
        response = client.get("/api/v1/specification/related/spec-anchor-general")
        assert response.status_code == 200
        data = response.json()
        assert "calculation" in data
        assert data["calculation"] is not None, "锚固条文应有关联计算"
        assert data["calculation"]["type"] == "anchor"
        assert "url" in data["calculation"]

    def test_get_related_with_annotation(self, client):
        """测试获取关联内容 - 有标注关联的条文"""
        response = client.get("/api/v1/specification/related/spec-beam-notation")
        assert response.status_code == 200
        data = response.json()
        assert "annotation_type" in data
        assert data["annotation_type"] == "beam"
        # 应有交叉引用
        assert "cross_references" in data

    def test_get_related_not_found(self, client):
        """测试获取不存在的条文的关联"""
        response = client.get("/api/v1/specification/related/non-existent-id")
        assert response.status_code == 404

    def test_get_related_cross_references(self, client):
        """测试交叉引用 - 同一分类的其他条文"""
        response = client.get("/api/v1/specification/related/spec-column-notation")
        assert response.status_code == 200
        data = response.json()
        assert "cross_references" in data
        # 柱分类下有 2 条，扣除自身应至少 1 条交叉引用
        assert len(data["cross_references"]) >= 1
        for ref in data["cross_references"]:
            assert "id" in ref
            assert "title" in ref
