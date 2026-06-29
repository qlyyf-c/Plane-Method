# 平法辅助学习 App - 设计规格文档

> 版本：v2.0  
> 日期：2026-06-26  
> 技术栈：Vue3 + FastAPI + SQLModel + SQLite  
> 工期：7-8周

---

## 1. 设计概览

### 1.1 项目定位

土木工程专业学生平法识图学习工具，同时为培训线获客入口。

### 1.2 核心功能

| 功能模块 | 描述 | 优先级 |
|---------|------|--------|
| 锚固长度计算器 | 输入混凝土等级、钢筋类型、直径、抗震等级，计算 lab/la/laE | P0 |
| 平法标注解析器 | 拆解 KL/KZ 标注并给出符号释义 | P0 |
| 图集条文速查 | 22G101 条文搜索、分类浏览 | P0 |
| 三模块关联跳转 | 模块间互相关联，形成学习闭环 | P1 |
| 最近查询记录 | localStorage 持久化，快速复用 | P1 |

### 1.3 技术架构

```
┌─────────────────────────────────────────────────┐
│                   用户浏览器                       │
│              Vue3 SPA + Vite 构建                  │
│  ┌──────────┬──────────────┬───────────────┐     │
│  │锚固计算器 │ 标注解析器    │ 图集速查      │     │
│  │ calculator │ parser      │ reference     │     │
│  └──────────┴──────────────┴───────────────┘     │
│         Vue Router 路由 / Pinia 状态              │
└──────────────────────┬──────────────────────────┘
                       │ HTTP (REST API)
                       │ JSON 请求/响应
┌──────────────────────┴──────────────────────────┐
│              FastAPI 后端服务                      │
│  ┌───────────────────────────────────────┐       │
│  │  /api/v1/anchor     锚固计算           │       │
│  │  /api/v1/annotation 标注解析           │       │
│  │  /api/v1/spec       图集条文查询       │       │
│  │  /api/v1/data       参数选项数据       │       │
│  └───────────────────────────────────────┘       │
│         SQLModel ORM + Pydantic 验证             │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────┐
│              SQLite 数据库                        │
│  anchor_tables / seismic_factors /               │
│  concrete_grades / specifications                │
└─────────────────────────────────────────────────┘
```

---

## 2. 技术栈

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| 前端框架 | Vue3 + Vite | Vue ≥3.4, Vite ≥5.0 | SPA标准方案，生态成熟 |
| 前端路由 | Vue Router | ≥4.0 | 支持hash模式，PWA兼容 |
| 状态管理 | Pinia | ≥2.1 | Vue3官方推荐，轻量 |
| UI组件库 | Vuetify 3 | ≥3.5 | Material Design，移动端友好 |
| 后端框架 | FastAPI | ≥0.100 | 异步高性能，OpenAPI自动文档 |
| ORM | SQLModel | ≥0.0.14 | Pydantic + SQLAlchemy融合 |
| 数据库 | SQLite | - | 单文件部署，MVP够用 |
| HTTP客户端 | axios | ≥1.6 | Vue3标准HTTP库 |
| 部署 | Uvicorn + Docker | - | 生产级ASGI服务器 |

---

## 3. 页面设计

### 3.1 导航结构

底部导航（5个tab）：
- 🏠 **首页** - 功能入口卡片 + 最近查询
- 📐 **计算** - 锚固长度计算器
- 🔍 **解析** - 平法标注解析器
- 📖 **查阅** - 图集条文速查
- ℹ️  **关于** - 应用说明 + 反馈入口

### 3.2 首页布局

```
┌─────────────────────────┐
│    平法助手 PingFa      │
├─────────────────────────┤
│                         │
│  ┌─ 锚固计算 ──┐        │
│  │ 快查锚固长度 │        │
│  └───────────┘         │
│                         │
│  ┌─ 标注解析 ──┐        │
│  │ 拆解平法标注 │        │
│  └───────────┘         │
│                         │
│  ┌─ 图集速查 ──┐        │
│  │ 22G101条文  │        │
│  └───────────┘         │
│                         │
│  ─── 最近查询 ──         │
│  C30/HRB400/25mm        │
│  KL7(3) 300×650         │
│                         │
├───┬───┬───┬───┬───┤
│ 🏠│ 📐│ 🔍│ 📖│ ℹ️ │
│首页│计算│解析│查阅│关于│
└───┴───┴───┴───┴───┘
```

### 3.3 锚固计算器页面

```
┌─────────────────────────┐
│  锚固长度计算器          │
├─────────────────────────┤
│                         │
│  混凝土等级             │
│  ┌─[ C30 ▼ ]────────┐ │
│                         │
│  钢筋类型               │
│  ┌─[ HRB400 ▼ ]─────┐ │
│                         │
│  钢筋直径               │
│  ┌─[ 25 mm ▼ ]──────┐ │
│                         │
│  抗震等级               │
│  ┌─[ 二级 ▼ ]───────┐ │
│                         │
│  ┌──────────────────┐ │
│  │    计 算          │ │
│  └──────────────────┘ │
│                         │
│  ─── 计算结果 ───       │
│  ┌──────────────────┐ │
│  │  基本锚固 lab     │ │
│  │   35d = 875 mm   │ │
│  │                  │ │
│  │  受拉锚固 la      │ │
│  │   35d = 875 mm   │ │
│  │                  │ │
│  │  抗震锚固 laE     │ │
│  │   1.15×la        │ │
│  │   = 1006 mm      │ │
│  │                  │ │
│  │  [查看相关条文→] │ │
│  └──────────────────┘ │
└─────────────────────────┘
```

### 3.4 标注解析器页面

```
┌─────────────────────────┐
│  平法标注解析器          │
├─────────────────────────┤
│                         │
│  输入标注               │
│  ┌──────────────────┐ │
│  │ KL7(3) 300×650   │ │
│  └──────────────────┘ │
│                         │
│  常用示例：[KL7(3)]     │
│  [KZ1] [WKL2(2A)]      │
│                         │
│  ┌──────────────────┐ │
│  │    解 析          │ │
│  └──────────────────┘ │
│                         │
│  ─── 解析结果 ───       │
│  ┌──────────────────┐ │
│  │ 构件类型：框架梁   │ │
│  │ 编号    ：7       │ │
│  │ 跨数    ：3       │ │
│  │ 截面尺寸：300×650 │ │
│  │                  │ │
│  │ ── 释义说明 ──   │ │
│  │ KL = 框架梁      │ │
│  │ 7  = 第7号梁     │ │
│  │ (3) = 3跨        │ │
│  │ 300 = 梁宽(mm)   │ │
│  │ 650 = 梁高(mm)   │ │
│  │                  │ │
│  │ [查看相关条文→]  │ │
│  │ [计算锚固长度→]  │ │
│  └──────────────────┘ │
└─────────────────────────┘
```

### 3.5 图集速查页面

```
┌─────────────────────────┐
│  22G101 图集速查        │
├─────────────────────────┤
│  ┌─[ 🔍 搜索锚固... ]─┐ │
│                         │
│  [柱] [梁] [墙] [一般]  │
│                         │
│  ─── 条文列表 ───       │
│  ┌──────────────────┐ │
│  │ 4.2.1 梁平法标注  │ │
│  │ 表示方法          │ │
│  └──────────────────┘ │
│  ┌──────────────────┐ │
│  │ 2.2.1 锚固长度   │ │
│  │ 一般规定          │ │
│  └──────────────────┘ │
│                         │
│  ─── 条文详情 ───       │
│  ┌──────────────────┐ │
│  │ 4.2.1 梁平法...  │ │
│  │ [正文内容...]     │ │
│  │                  │ │
│  │ [试试锚固计算→]  │ │
│  │ [解析相关标注→]  │ │
│  └──────────────────┘ │
└─────────────────────────┘
```

---

## 4. 后端API设计

### 4.1 API路由总览

```
/api/v1/
├── /anchor/
│   ├── POST /calculate       # 计算锚固长度
│   ├── GET  /options         # 获取输入选项
│   └── GET  /detail/{id}     # 获取某次计算详情
│
├── /annotation/
│   ├── POST /parse           # 解析标注字符串
│   ├── GET  /examples        # 获取常用标注示例
│   ├── GET  /types           # 获取支持的标注类型
│   └── GET  /glossary        # 获取符号释义表
│
├── /specification/
│   ├── GET  /search          # 关键字搜索条文
│   ├── GET  /categories      # 获取章节分类
│   ├── GET  /by-category     # 按分类获取条文
│   ├── GET  /detail/{id}     # 获取单条条文
│   └── GET  /related/{id}    # 获取关联接口
│
└── /data/
    ├── GET  /concrete-grades # 混凝土等级
    ├── GET  /rebar-types     # 钢筋类型
    ├── GET  /seismic-grades  # 抗震等级
    └── GET  /diameters       # 钢筋直径
```

### 4.2 核心接口详细设计

#### POST /api/v1/anchor/calculate

**请求体：**
```json
{
  "concrete_grade": "C30",
  "rebar_type": "HRB400",
  "diameter": 25,
  "seismic_grade": "二级",
  "rebar_surface": "带肋"
}
```

**响应体：**
```json
{
  "lab": {"d_value": 35, "mm_value": 875},
  "la": {"d_value": 35, "mm_value": 875, "modifier": 1.0, "modifier_note": "默认值"},
  "laE": {"d_value": 40, "mm_value": 1006, "seismic_modifier": 1.15, "seismic_note": "二级抗震"},
  "reference": {"standard": "22G101-1", "page": 58, "clause": "表2.2.1"},
  "related_spec_id": "spec-anchor-general"
}
```

#### POST /api/v1/annotation/parse

**请求体：**
```json
{"annotation": "KL7(3) 300×650"}
```

**成功响应：**
```json
{
  "success": true,
  "parsed": {
    "component_type": "KL",
    "component_name": "框架梁",
    "number": 7,
    "span_count": 3,
    "span_type": "等跨",
    "width": 300,
    "height": 650
  },
  "glossary": [
    {"symbol": "KL", "meaning": "框架梁", "description": "框架结构中的主梁"},
    {"symbol": "(3)", "meaning": "3跨", "description": "该梁跨越3个支座"},
    {"symbol": "300×650", "meaning": "截面尺寸", "description": "梁宽300mm，梁高650mm"}
  ],
  "related_calc_params": {"rebar_type": "HRB400", "diameter": null},
  "related_spec_id": "spec-beam-notation"
}
```

**失败响应：**
```json
{
  "success": false,
  "error": "无法识别标注格式",
  "suggestion": "支持的梁标注格式：KL/L/WKL 编号(跨数) 宽×高",
  "partial": {"component_type": "KL", "number": 7}
}
```

---

## 5. 数据模型

### 5.1 SQLModel表结构

```python
# concrete_grades - 混凝土等级
class ConcreteGrade(SQLModel, table=True):
    id: int = Field(primary_key=True)
    grade: str  # C20, C25, C30...
    ft_value: float  # 混凝土抗拉强度设计值

# rebar_types - 钢筋类型
class RebarType(SQLModel, table=True):
    id: int = Field(primary_key=True)
    type: str  # HRB300, HRB400, HRB500
    fy_value: int  # 钢筋抗拉强度设计值
    alpha: float  # 外形系数（光圆0.16，带肋0.14）

# seismic_modifiers - 抗震修正系数
class SeismicModifier(SQLModel, table=True):
    id: int = Field(primary_key=True)
    grade: str  # 一级, 二级, 三级, 四级, 非抗震
    factor: float  # ζaE 系数
    note: str

# anchor_tables - 预置锚固表（查表法）
class AnchorTable(SQLModel, table=True):
    id: int = Field(primary_key=True)
    concrete_grade: str
    rebar_type: str
    lab_d: int  # lab 的 d 倍数

# specifications - 图集条文
class Specification(SQLModel, table=True):
    id: str = Field(primary_key=True)
    clause_number: str
    title: str
    category: str  # 柱, 梁, 墙, 一般构造
    content_html: str
    related_calc: str  # 关联计算类型
    related_ann_type: str  # 关联标注类型

# annotation_rules - 标注解析规则
class AnnotationRule(SQLModel, table=True):
    id: int = Field(primary_key=True)
    type: str  # beam, column
    pattern: str  # 正则表达式
    name: str
    examples: str  # JSON数组
    field_map: str  # JSON映射
    glossary_entries: str  # JSON数组
    related_spec_id: str
    default_rebar_type: str

# glossary - 符号释义表
class Glossary(SQLModel, table=True):
    id: str = Field(primary_key=True)
    symbol: str
    meaning: str
    description: str
```

---

## 6. 标注解析器工作机制

### 6.1 两层架构

```
用户输入 "KL7(3) 300×650"
         │
         ▼
  ┌─ 规则匹配层 ──────────────────────┐
  │ 1. 读取 annotation_rules 表        │
  │ 2. 按类型（梁/柱）逐条匹配 pattern │
  │ 3. KL→匹配梁规则，命中             │
  │ 4. 正则捕获组提取各字段             │
  └──────────┬──────────────────────────┘
             │
             ▼
  ┌─ 结果构建层 ──────────────────────┐
  │ 1. field_map 映射捕获组到字段名     │
  │ 2. 关联 glossary_entries           │
  │ 3. 推断 related_calc_params        │
  │ 4. 关联 related_spec_id            │
  └──────────────────────────────────┘
```

### 6.2 规则示例

| 字段 | 梁标注规则 |
|------|-----------|
| type | beam |
| pattern | `^(KL|L|WKL|XL)(\d+)(\(([0-9]+[AB]?)\))?\s*(\d+)×(\d+)$` |
| name | 框架梁标注 |
| examples | `["KL7(3) 300×650", "L2(1A) 250×500", "WKL3(2) 300×700"]` |
| field_map | `{"1":"component_type","2":"number","3":"span_count","4":"width","5":"height"}` |
| glossary_entries | `["glossary-KL","glossary-L","glossary-span","glossary-section"]` |
| related_spec_id | spec-beam-notation |
| default_rebar_type | HRB400 |

---

## 7. 22G101数据提取策略

### 7.1 数据来源与范围

| 数据项 | 来源 | 提取方式 | 工作量 |
|--------|------|---------|--------|
| 锚固长度表 (lab) | 22G101-1 p.58 | 手工提取JSON | 2天 |
| 抗震修正系数 | 22G101-1 p.57 | 手工提取 | 0.5天 |
| 混凝土强度值 | 22G101-1 / GB50010 | 手工提取 | 1天 |
| 钢筋强度值 | GB50010 | 手工提取 | 0.5天 |
| 图集条文（梁章节） | 22G101-1 第4章 | 转写HTML | 3天 |
| 图集条文（柱章节） | 22G101-1 第2章 | 转写HTML | 2天 |
| 图集条文（一般构造） | 22G101-1 第1-2章 | 转写HTML | 2天 |
| 标注解析规则 | 条文归纳 | 编写正则 | 2天 |
| 释义表 | 术语+常识 | 编写JSON | 1天 |

**总计约14天**（与代码开发并行）

### 7.2 数据文件结构

```
data/
├── anchor/
│   ├── lab_table.json           # 受拉钢筋基本锚固长度表
│   ├── seismic_modifiers.json   # 抗震修正系数
│   ├── concrete_strength.json   # 混凝土强度值
│   └── rebar_strength.json      # 钢筋强度值 + 外形系数
├── specifications/
│   ├── general_rules.json       # 一般构造条文
│   ├── column_rules.json        # 柱平法规则
│   └── beam_rules.json          # 梁平法规则
├── annotation/
│   ├── beam_rules.json          # 梁标注解析规则
│   ├── column_rules.json        # 柱标注解析规则
│   └── glossary.json            # 符号释义表
└── init_db.py                   # 数据导入脚本
```

### 7.3 数据验证机制

- **锚固计算**：查表值 vs 公式计算值，10组交叉验证，误差 < 1%
- **条文内容**：与原图集逐字核对关键公式和数值
- **标注规则**：每组规则至少5个测试用例覆盖

---

## 8. 三模块关联闭环

```
首页 ──入口卡片──→ 锚固计算器
                ──入口卡片──→ 标注解析器
                ──入口卡片──→ 图集速查
                ──最近查询──→ 快速复用

锚固计算器 ──"查看相关条文"──→ 图集速查（锚固条文）

标注解析器 ──"查看相关条文"──→ 图集速查（梁/柱标注规则）
          ──"计算锚固长度"──→ 锚固计算器（带参数预填）

图集速查   ──"试试锚固计算"──→ 锚固计算器
          ──"解析相关标注"──→ 标注解析器（带标注示例预填）
```

跳转时携带参数预填是关键体验——能推断的参数自动填入，减少用户操作。

---

## 9. PWA配置

### 9.1 配置清单

- `manifest.json`：应用名称、图标、启动画面、主题色
- `Service Worker`：静态资源缓存、离线回退策略
- `icons/`：多尺寸图标（192x192, 512x512）

### 9.2 离线策略

- **在线优先**：联网时始终获取最新数据
- **静态缓存**：JS/CSS/HTML离线可用
- **数据缓存**：图集条文、计算结果缓存24小时
- **离线回退**：提示用户联网获取最新数据

---

## 10. 风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| Vue3学习曲线超预期 | 中 | 高 | Week1增加1天Vue3速成 |
| 22G101数据提取耗时过长 | 中 | 高 | 先提取核心数据，柱/梁条文可后续追加 |
| 标注解析准确率不足 | 中 | 高 | Week3预留1天规则调优，Week6专项测试 |
| 手机端性能问题 | 低 | 中 | Week6-7重点优化 |
| 部署受阻 | 低 | 中 | Railway为主，Vercel备用 |

---

## 11. 相关文档

- 本设计规格：`docs/design.md`
- 开发任务清单：`tasks.md`
- 项目README：`README.md`
- 开发板块指导：`../CLAUDE.md`
- 历史方案：`../实施方案_v1.md`（已废止）、`../实施方案_v1_保守.md`（已废止）

---

**设计完成日期**: 2026-06-26  
**待开始**: Week 1 开发
