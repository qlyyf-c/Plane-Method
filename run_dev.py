"""启动脚本 - 仅用于开发验证

用法: cd pingfa_app && python run_dev.py
"""
import os
import sys

# 将 backend/ 加入 Python 路径，使 app 模块可导入
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_PATH = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_PATH)

import uvicorn  # noqa: E402

uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=False)
