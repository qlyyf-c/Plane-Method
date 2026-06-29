# 平法辅助学习 App

> 土木工程专业学生平法识图学习工具 / 培训线获客入口

## 技术栈

- **前端**: Vue3 + Vite + Vuetify 3 + Vue Router + Pinia + Axios
- **后端**: FastAPI + SQLModel + SQLite + Uvicorn
- **部署**: Docker + Railway/Vercel
- **测试**: pytest + httpx

## 项目结构

```
pingfa_app/
├── README.md                    # 本文件
├── tasks.md                     # 开发任务清单
├── docs/
│   ├── design.md                # 完整设计规格
│   └── implementation-plan.md   # 实施计划
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── api/                 # API 路由
│   │   │   ├── data.py          # 数据选项 API
│   │   │   ├── anchor.py        # 锚固计算 API
│   │   │   ├── annotation.py    # 标注解析 API
│   │   │   └── specification.py # 图集速查 API
│   │   ├── core/                # 核心业务逻辑
│   │   │   └── anchor_calc.py   # 锚固计算引擎（待实现）
│   │   ├── models/
│   │   │   └── database.py      # SQLModel 数据模型（9 张表）
│   │   ├── services/            # 数据服务层
│   │   └── main.py              # FastAPI 入口
│   ├── tests/                   # pytest 单元测试
│   └── requirements.txt         # Python 依赖
├── frontend/                    # Vue3 前端
│   ├── src/
│   │   ├── views/               # 页面组件
│   │   │   ├── Home.vue         # 首页
│   │   │   ├── Calculator.vue   # 锚固计算器
│   │   │   ├── Parser.vue       # 标注解析器
│   │   │   ├── Reference.vue    # 图集速查
│   │   │   └── About.vue        # 关于页面
│   │   ├── router/              # Vue Router 配置
│   │   ├── stores/              # Pinia 状态管理
│   │   ├── api/                 # Axios 封装
│   │   ├── main.ts              # Vue 入口
│   │   └── App.vue              # 主框架（底部导航）
│   ├── vite.config.ts
│   └── package.json
├── data/                        # SQLite 数据库 + JSON 数据源
│   ├── pingfa.db                # SQLite 数据库（74 条记录）
│   ├── init_db.py               # 数据导入脚本
│   ├── anchor/                  # 锚固数据
│   │   ├── concrete_strength.json     # 混凝土抗拉强度 (8 条)
│   │   ├── rebar_strength.json        # 钢筋强度 (3 条)
│   │   ├── rebar_diameters.json       # 钢筋直径 (15 条)
│   │   ├── seismic_modifiers.json     # 抗震修正系数 (5 条)
│   │   ├── anchor_modifiers.json      # 其他修正系数 (5 条)
│   │   └── lab_table.json             # 锚固长度表 (24 条)
│   ├── annotation/              # 标注解析数据
│   │   ├── beam_rules.json      # 梁标注规则
│   │   ├── column_rules.json    # 柱标注规则
│   │   └── glossary.json        # 符号释义 (9 条)
│   └── specifications/          # 图集条文
│       ├── general_rules.json   # 锚固规定 (GB50010 8.3)
│       ├── beam_rules.json      # 梁平法规则 (22G101 4.2)
│       └── column_rules.json    # 柱平法规则 (22G101 2)
└── run_dev.py                   # 开发启动脚本
```

## 快速启动

### 后端

```bash
cd D:\OPC_projects\civil_opc\development\pingfa_app
python run_dev.py
# 访问 http://localhost:8001/docs 查看 OpenAPI 文档
```

### 前端

```bash
cd frontend
npm run dev
# 访问 http://localhost:5173
```

### 测试

```bash
cd backend
pytest tests/ -v
```

### 数据库初始化

```bash
python data/init_db.py
```

## 核心功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 锚固长度计算器 | ✅ 已完成 | 输入参数计算 lab/la/laE，查表 + 公式双策略 |
| 平法标注解析器 | ✅ 已完成 | 拆解 KL/KZ 标注并释义 |
| 图集条文速查 | ✅ 已完成 | 22G101 条文搜索与浏览 |

## 数据层状态

**SQLite 数据库**: 74 条记录

| 表名 | 记录数 | 说明 |
|------|--------|------|
| concretegrade | 8 | C25-C60 混凝土抗拉强度 ft |
| rebartype | 3 | HPB300/HRB400/HRB500 的 fy 和 α |
| rebardiameter | 15 | 6-50mm 钢筋直径 |
| seismicmodifier | 5 | 抗震修正系数 ζaE |
| anchormodifier | 5 | la 修正系数（直径/涂层/扰动/保护层） |
| anchortable | 24 | 锚固长度查表值 lab_d |
| annotationrule | 2 | 梁/柱标注解析正则规则 |
| glossary | 9 | 符号释义 |
| specification | 3 | 锚固/梁/柱条文 HTML |

## API 端点

### 数据选项
- `GET /api/v1/data/concrete-grades` - 混凝土等级列表
- `GET /api/v1/data/rebar-types` - 钢筋类型列表
- `GET /api/v1/data/seismic-grades` - 抗震等级列表
- `GET /api/v1/data/diameters` - 钢筋直径列表
- `GET /api/v1/data/modifiers` - 修正系数列表（可勾选）

### 锚固计算（已实现）
- `POST /api/v1/anchor/calculate` - 计算锚固长度
- `GET /api/v1/anchor/options` - 获取计算器选项

### 标注解析（已实现）
- `POST /api/v1/annotation/parse` - 解析标注字符串
- `GET /api/v1/annotation/examples` - 常用标注示例
- `GET /api/v1/annotation/glossary` - 符号释义表

### 图集速查（已实现）
- `GET /api/v1/specification/search` - 搜索条文
- `GET /api/v1/specification/categories` - 条文分类
- `GET /api/v1/specification/by-category` - 按分类浏览

## 开发进度

| 周次 | 任务 | 状态 |
|------|------|------|
| Week 1 | 环境搭建 + 数据准备 | ✅ 已完成 |
| Week 2 | 锚固计算引擎 | ✅ 已完成 |
| Week 3 | 标注解析 + 锚固计算器前端 | ✅ 已完成 |
| Week 4 | 图集数据 + 标注解析器前端 | ✅ 已完成 |
| Week 5 | 三模块闭环 | ✅ 已完成 |
| Week 6 | PWA + 测试修正 | ✅ 已完成 |
| Week 7 | 整合优化 | ✅ 已完成 |
| Week 8 | 部署上线 | ✅ 已完成 |

## 部署说明

项目已具备完整的部署能力：

1. **Docker部署**：已创建 Dockerfile 和 docker-compose 文件
2. **服务器部署**：可部署到 Railway、Vercel 等平台
3. **PWA支持**：已配置并验证 PWA 功能
4. **测试完整**：所有 71 个测试均已通过

## 相关文档

- [开发任务清单](tasks.md) - 详细任务分解和进度跟踪
- [设计规格](docs/design.md) - 完整技术设计
- [实施计划](docs/implementation-plan.md) - 周次计划和里程碑

---
**项目完成时间**: 2026-06-29
**版本**: 1.0.0