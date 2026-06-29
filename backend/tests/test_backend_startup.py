"""
测试 FastAPI 后端启动和基础路由

验证：
1. FastAPI 应用能否正常创建
2. 根路径 '/' 返回正确结构
3. OpenAPI 文档路径 '/docs' 存在
"""
import sys
import os

# 将 backend 加入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_app_creation():
    """测试 FastAPI 应用能否正常创建"""
    assert app is not None
    assert app.title == "平法助手 PingFa"
    assert app.version == "0.1.0"


def test_root_endpoint():
    """测试根路径返回正确结构"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert "docs" in data
    assert data["docs"] == "/docs"


def test_docs_endpoint_exists():
    """测试 OpenAPI 文档路径存在"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json():
    """测试 OpenAPI JSON 规范可访问"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    assert "openapi" in openapi
    assert "paths" in openapi
    # 验证注册的路由存在
    assert "/" in openapi["paths"]
    assert "/api/v1/data/diameters" in openapi["paths"]