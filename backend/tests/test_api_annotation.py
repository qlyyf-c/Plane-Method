"""标注解析 API 测试

覆盖目标：
- 标准格式：梁/柱标注解析
- 变体格式：悬挑标注、简单梁、屋面板梁
- 边界格式：柱无截面、最小有效输入
- 失败格式：无效标注、部分匹配
- API 元数据：示例/类型/释义
"""
import sys
sys.path.insert(0, '.')

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestAnnotationAPI:
    """标注解析 API 测试"""

    # ==================== 标准格式 ====================

    def test_parse_beam_standard(self, client):
        """标准梁标注：KL7(3) 300x650"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "KL7(3) 300x650"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['component_type'] == 'KL'
        assert data['parsed']['component_name'] == '框架梁'
        assert data['parsed']['number'] == 7
        assert data['parsed']['span_count'] == '3跨'
        assert data['parsed']['width'] == 300
        assert data['parsed']['height'] == 650
        assert len(data['glossary']) >= 4

    def test_parse_column_standard(self, client):
        """标准柱标注：KZ1 500x500"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "KZ1 500x500"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['component_type'] == 'KZ'
        assert data['parsed']['component_name'] == '框架柱'
        assert data['parsed']['number'] == 1
        assert data['parsed']['width'] == 500
        assert data['parsed']['height'] == 500
        assert data['parsed']['span_count'] is None

    # ==================== 变体格式 ====================

    def test_parse_beam_with_cantilever(self, client):
        """悬挑变体：L2(1A) 250x500（一端悬挑）"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "L2(1A) 250x500"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['component_type'] == 'L'
        assert data['parsed']['component_name'] == '非框架梁'
        assert data['parsed']['number'] == 2
        assert data['parsed']['span_count'] == '1跨，一端有悬挑'
        assert data['parsed']['width'] == 250
        assert data['parsed']['height'] == 500

    def test_parse_beam_simple(self, client):
        """简单梁标注：L1 250x500"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "L1 250x500"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['component_type'] == 'L'
        assert data['parsed']['component_name'] == '非框架梁'
        assert data['parsed']['number'] == 1
        # span_count 可能是空字符串或 None，取决于正则捕获
        assert data['parsed']['width'] == 250
        assert data['parsed']['height'] == 500

    def test_parse_roof_beam(self, client):
        """屋面框架梁：WKL3(2) 300x700"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "WKL3(2) 300x700"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['component_type'] == 'WKL'
        assert data['parsed']['component_name'] == '屋面框架梁'
        assert data['parsed']['number'] == 3
        assert data['parsed']['span_count'] == '2跨'
        assert data['parsed']['width'] == 300
        assert data['parsed']['height'] == 700

    # ==================== 边界格式 ====================

    def test_parse_column_without_section(self, client):
        """柱无截面：QZ1"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "QZ1"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['component_type'] == 'QZ'
        assert data['parsed']['component_name'] == '剪力墙上柱'
        assert data['parsed']['number'] == 1
        assert data['parsed']['width'] is None
        assert data['parsed']['height'] is None

    def test_parse_generic_column(self, client):
        """通用柱：Z2 400x600"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "Z2 400x600"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['component_type'] == 'Z'
        assert data['parsed']['component_name'] == '柱'
        assert data['parsed']['number'] == 2
        assert data['parsed']['width'] == 400
        assert data['parsed']['height'] == 600

    def test_parse_beam_x_multiply(self, client):
        """梁标注使用×号：KL7(3) 300×650"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "KL7(3) 300×650"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['component_type'] == 'KL'
        assert data['parsed']['number'] == 7
        assert data['parsed']['width'] == 300
        assert data['parsed']['height'] == 650

    # ==================== 失败格式 ====================

    def test_parse_invalid(self, client):
        """完全无法识别的输入"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "INVALID_TEXT"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert data['error'] is not None
        assert data['suggestion'] is not None
        # 失败时不应有 parsed
        assert data['parsed'] is None

    def test_parse_partial_match(self, client):
        """部分匹配：KL后面缺少截面尺寸"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "KL7"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        # 应识别出 KL 和 7
        assert data['partial'] is not None
        assert data['partial']['component_type'] == 'KL'
        assert data['partial']['number'] == 7

    # ==================== API 元数据 ====================

    def test_get_examples(self, client):
        """测试获取示例列表"""
        response = client.get('/api/v1/annotation/examples')
        assert response.status_code == 200
        data = response.json()
        assert 'examples' in data
        assert len(data['examples']) > 0

    def test_get_types(self, client):
        """测试获取标注类型"""
        response = client.get('/api/v1/annotation/types')
        assert response.status_code == 200
        data = response.json()
        assert 'types' in data
        types = {t['type'] for t in data['types']}
        assert 'beam' in types
        assert 'column' in types

    def test_get_glossary(self, client):
        """测试获取完整释义表"""
        response = client.get('/api/v1/annotation/glossary')
        assert response.status_code == 200
        data = response.json()
        assert 'glossary' in data
        assert len(data['glossary']) > 0


class TestAnnotationEngine:
    """标注解析引擎直接测试"""

    def test_kuake_format_lowercase(self, client):
        """小写 x 也可识别"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "kl7(3) 300x650"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['component_type'] == 'KL'
        assert data['parsed']['number'] == 7

    def test_extra_spaces(self, client):
        """多余空格处理"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "  KL7(3)   300x650  "
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['component_type'] == 'KL'

    def test_cantilever_both_ends(self, client):
        """两端悬挑 (3B)"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "KL5(3B) 300x700"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['span_count'] == '3跨，两端有悬挑'
        assert data['parsed']['width'] == 300
        assert data['parsed']['height'] == 700

    def test_kl12_3b_user_case(self, client):
        """用户用例：KL12(3B) 500×700 → 3跨，两端有悬挑"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "KL12(3B) 500×700"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['component_type'] == 'KL'
        assert data['parsed']['component_name'] == '框架梁'
        assert data['parsed']['number'] == 12
        assert data['parsed']['span_count'] == '3跨，两端有悬挑'
        assert data['parsed']['width'] == 500
        assert data['parsed']['height'] == 700

    def test_kl12_3b_lowercase_x(self, client):
        """小写x替代乘号：KL12(3B) 500x700"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "KL12(3B) 500x700"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['span_count'] == '3跨，两端有悬挑'
        assert data['parsed']['width'] == 500
        assert data['parsed']['height'] == 700

    def test_kl12_3b_uppercase_x(self, client):
        """大写X替代乘号：KL12(3B) 500X700"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": "KL12(3B) 500X700"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['parsed']['span_count'] == '3跨，两端有悬挑'
        assert data['parsed']['width'] == 500
        assert data['parsed']['height'] == 700

    def test_empty_text(self, client):
        """空字符串输入"""
        response = client.post('/api/v1/annotation/parse', json={
            "text": ""
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert data['error'] is not None
