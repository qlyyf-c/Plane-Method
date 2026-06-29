# 平法辅助学习 App - 开发任务清单

> 创建日期：2026-06-26  
> 预计周期：7-8周

---
## 当前状态

✅ **Week 1-6 完成**

- ✅ FastAPI 后端骨架搭建完成
- ✅ SQLModel 数据模型定义完成（9 张表）
- ✅ init_db.py 数据导入脚本完成
- ✅ Vue3 + Vite 前端搭建完成
- ✅ Vuetify + Router + Pinia 配置完成
- ✅ pytest 测试基础设施（69 个测试全部通过）
- ✅ 22G101-1 数据录入完成（79 条记录）
- ✅ 锚固计算引擎完成（查表法 + 公式法双策略）
- ✅ 锚固计算 API 完成（POST /api/v1/anchor/calculate）
- ✅ 数据选项 API 完成（GET /api/v1/data/*, GET /api/v1/anchor/options）
- ✅ 标注解析引擎完成（正则匹配 + glossary 关联）
- ✅ 标注解析 API 完成（POST /api/v1/annotation/parse）
- ✅ 锚固计算器前端完成（Vue3 + Vuetify + API 联调）
- ✅ 标注解析器前端完成（Parser.vue）
- ✅ 图集速查 API 完成（5 个路由）
- ✅ 图集速查前端完成（Reference.vue）
- ✅ 条文数据骨架完成（8 条，待用户填原文）
- ✅ 三模块闭环功能完成（最近查询、关联跳转）
- ✅ PWA 配置完成（manifest、Service Worker、离线缓存、8 尺寸图标）
- ✅ 标注解析增强（悬挑规则 A=一端/B=两端，支持 x/X/×三种乘号）

**里程碑 M1 完全达成**：环境就绪 + 数据完整
**里程碑 M2 完全达成**：锚固计算可演示（后端 API）
**里程碑 M3 完全达成**：锚固计算可演示（手机浏览器）
**里程碑 M4 完全达成**：三模块完整可用 + 模块间关联跳转
**Week 6 里程碑达成**：PWA 可用 + 核心功能验证通过（69 测试全过）

---

## 任务总览

### Week 1: 环境搭建 + 数据准备 ✅ (已完成)

- [x] Day 1-2: FastAPI 项目骨架、SQLModel 模型、init_db 脚本
- [x] Day 3-4: Vue3 + Vite 项目搭建、Vuetify 配置、路由框架
- [x] Day 5-7: 22G101 数据提取（锚固表、强度值、系数）→ JSON

**里程碑 M1**: ✅ 环境就绪 + 数据完整（数据库 74 条记录）

---

### Week 2: 数据层 + 锚固计算核心 ✅ (已完成)

- [x] Day 1-3: 数据导入脚本验证、数据库 API 完善
- [x] Day 4-5: 锚固计算引擎（查表 + 公式双策略）
- [x] Day 6-7: 锚固计算 API 实现 + 单元测试

**里程碑 M2**: ✅ 锚固计算可演示（后端 API）

---

### Week 3: 标注解析 + 锚固计算器前端 ✅ (已完成)

- [x] Day 1-3: 标注解析引擎（正则匹配 + glossary 关联）
- [x] Day 4-5: 锚固计算器页面（Vue3 + Vuetify）
- [x] Day 6-7: API 联调 + 测试（6 个新测试）

**里程碑 M3**: ✅ 锚固计算可演示（手机浏览器）

---

### Week 4: 图集速查 API + 标注解析器前端 ✅ (已完成)

- [x] Day 1-3: 22G101 条文转写 HTML 骨架（一般构造 3 条、柱 2 条、梁 3 条，共 8 条）
- [x] Day 4-5: 标注解析器页面 Parser.vue（输入/示例/解析结果/符号释义）
- [x] Day 6-7: 图集速查 API + 搜索功能（5 个路由完整实现 + 13 个测试）

**里程碑 M4**: ✅ 完全达成（API+ 前端完成，三模块关联跳转）

---

### Week 5: 图集速查 + 三模块闭环 ✅ (已完成)

- [x] Day 1-3: 图集速查页面、分类浏览、搜索 UI（已有基础，补充路由参数支持）
- [x] Day 4-5: 模块间关联跳转（相关计算/条文/标注）
- [x] Day 6-7: 首页（最近查询 localStorage）、关于页面（联系方式、条文依据）

**里程碑 M4**: 三模块完整可用 + 模块间关联跳转

---

### Week 6: PWA + 测试修正 ✅ (已完成)

- [x] Day 1-3: PWA 配置（manifest、Service Worker、离线缓存、图标生成）
- [x] Day 4-5: 对照 22G101 验证计算结果（21 个锚固计算测试全部通过）
- [x] Day 6-7: 标注解析测试用例覆盖（18 个标注解析测试全部通过）
- [x] 修正：int() 截断改为 int(×+0.001) 避免浮点精度导致的偏小误差
- [x] 修正：标注解析输入自动转大写、兼容 x/X/×三种乘号
- [x] 原 47 个测试 → 69 个测试，全部通过

**Week 6 里程碑** ✅: PWA 可用 + 核心功能验证通过（69 测试全过）

---

### Week 7: 整合优化 ⏳

- [ ] Day 1-3: UI 响应式优化（手机端适配）、交互细节打磨
- [ ] Day 4-5: 性能优化、加载速度、错误边界处理
- [ ] Day 6-7: 最近查询功能、localStorage 持久化

**里程碑 M5**: PWA 上线（公网 HTTPS + 二维码）

---

### Week 8: 部署上线 ⏳

- [ ] Day 1-3: Docker 打包、服务器部署、域名配置
- [ ] Day 4-5: PWA 验证、二维码生成、分享测试
- [ ] Day 6-7: 用户测试（3 名学生）、反馈收集、问题修复

**里程碑 M6**: MVP 完成（3 名学生独立使用 + 反馈≥5 条）

---

## 会话交接记录

### 2026-06-26 - 设计阶段完成

- ✅ 完成完整设计方案（Vue3 + FastAPI）
- ✅ 创建 pingfa_app/ 目录结构
- ✅ 更新 development/CLAUDE.md
- ✅ 撰写 README.md 和 tasks.md
- ⏳ 待开始：撰写 docs/design.md（完整设计规格）

**下次会话入口**: 继续撰写设计规格文档，或开始 Week 1 开发

---

### 2026-06-27 - Week 1 环境搭建完成

**完成项**:
- ✅ `backend/app/` 目录结构 + `__init__.py` + `requirements.txt`
- ✅ `backend/app/main.py` - FastAPI 入口 + 4 个空壳 API 路由
- ✅ `backend/app/models/database.py` - 7 张 SQLModel 表定义
- ✅ `backend/app/api/` - data/anchor/annotation/specification 空壳路由
- ✅ `data/init_db.py` - 数据导入脚本（支持 Optional 字段 null，非 Optional 字段 null 则跳过整条）
- ✅ `data/anchor/` - 4 个 JSON 占位文件（concrete_strength/rebar_strength/seismic_modifiers/lab_table）
- ✅ `data/annotation/` - 3 个 JSON 文件（beam_rules/column_rules/glossary）
- ✅ `data/specifications/` - 3 个 JSON 占位文件（条文 HTML 待转写）
- ✅ `frontend/` - Vue3 + Vite 项目创建
- ✅ `frontend/src/router/index.ts` - 5 路由配置（hash 模式）
- ✅ `frontend/src/views/` - 5 个空壳页面组件
- ✅ `frontend/src/main.ts` - Vuetify + Pinia + Router 配置
- ✅ `frontend/src/App.vue` - 底部导航栏框架
- ✅ `backend/tests/` - pytest 测试（24 个测试全部通过）
  - `test_backend_startup.py` - FastAPI 启动、根路径、OpenAPI 文档
  - `test_api_empty.py` - 所有 API 路由空壳响应结构验证
  - `test_database.py` - SQLModel 模型、数据库创建、数据插入
- ✅ 后端启动验证：`python run_dev.py` → localhost:8001 可访问
- ✅ 前端启动验证：`npm run dev` → localhost:5173 可访问

**数据库状态**:
- `pingfa.db` 已创建，导入 19 条记录
- `seismicmodifier`: 5 条（完整）
- `annotationrule`: 2 条（梁 + 柱规则）
- `glossary`: 9 条（符号释义）
- `concretegrade/rebartype/anchortable/specification`: 0 条（数值待用户提供）

**测试状态**:
- ✅ 24 个 pytest 测试全部通过
- 覆盖率：后端启动、API 结构、数据库模型
- 运行命令：`cd backend && pytest tests/ -v`

**阻塞项**:
- ⏳ 22G101-1 锚固表、混凝土/钢筋强度值 → 待用户提供真实数值后填入 JSON
- ⏳ 图集条文 HTML 转写 → 待用户提供条文原文

**下次会话入口**:
1. 用户提供 22G101-1 数值数据 → 填入 JSON → 运行 init_db.py → 开始 Week 2 锚固计算引擎
2. 或：直接进入 Week 2 后端开发（锚固计算引擎先实现公式法，锚固表查表法等数据到位后再补充）

---

### 2026-06-28 - 数据录入完成 + 测试更新

**完成项**:
- ✅ 用户提供 22G101-1 第 58 页锚固表（24 条 lab_d 数据）
- ✅ 用户提供 GB50010 混凝土/钢筋强度值（ft: 8 条，fy: 3 条）
- ✅ 用户提供抗震修正系数（5 条，一/二级 1.15、三级 1.05、四级 1.0）
- ✅ 用户提供其他修正系数（5 条：直径>25mm、环氧涂层、施工扰动、保护层 3d/5d）
- ✅ 用户校对图集条文 HTML（锚固规定、梁平法、柱平法）
- ✅ 添加钢筋直径表（15 条：6-50mm）
- ✅ 更新 SQLModel 模型（新增 `RebarDiameter`、更新 `AnchorModifier`）
- ✅ 更新 `data.py` API 实现数据库查询
- ✅ 更新测试文件：`test_api_empty.py` → `test_api_data.py`
- ✅ 数据库总记录数：74 条

**数据表状态**:
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
| **总计** | **74** | ✅ |

**测试状态**:
- ✅ 17 个 pytest 测试全部通过
- 新增测试：`test_api_data.py`（8 个测试，含数据库查询验证）
- 运行命令：`cd backend && pytest tests/ -v`

**修正系数设计**:
- 叠加逻辑：连乘（ζa = ζ1 × ζ2 × ...）
- 可勾选选项：前端传递选中的 `modifier_id` 列表
- 5 种修正：直径 (>25mm, 1.10)、环氧涂层 (1.25)、施工扰动 (1.10)、保护层 3d(0.80)、保护层 5d(0.70)

**下次会话入口**:
- 开始 Week 2：锚固计算引擎开发（查表 + 公式双策略）

---

### 2026-06-29 - Week 2 锚固计算核心完成

**完成项**:
- ✅ `app/core/anchor_calc.py` - 锚固计算引擎（查表法 + 公式法双策略）
- ✅ `app/api/anchor.py` - 锚固计算 API（POST /calculate, GET /options）
- ✅ `app/api/data.py` - 数据选项 API 完善（modifiers 改用数据库查询）
- ✅ `tests/test_anchor_calc.py` - 锚固计算单元测试（11 个测试全部通过）
- ✅ 总测试数：28 个全部通过

**API 验证**:
- POST `/api/v1/anchor/calculate` - C30/HRB400/25mm/二级 → laE = 1006mm ✓
- GET `/api/v1/anchor/options` - 返回所有下拉选项数据 ✓
- GET `/api/v1/data/*` - 所有数据查询接口正常 ✓

**计算结果验证** (对照 22G101-1 p.58):
| 测试用例 | lab | la | laE | 状态 |
|---------|-----|-----|-----|------|
| C30/HRB400/25mm/二级 | 35d=875mm | 35d=875mm | 40.25d=1006mm | ✓ |
| C25/HPB300/20mm/非抗震 | 34d=680mm | 34d=680mm | 34d=680mm | ✓ |
| C30/HRB400/28mm/二级 | 35d | 38.5d (直径修正) | 44.27d | ✓ |
| C50/HRB500/32mm/一级 | 32d | 35.2d (直径修正) | 40.48d | ✓ |

**里程碑 M2 达成**：锚固计算后端 API 完整可用

---

### 2026-06-30 - Week 3 标注解析 + 前端完成

**完成项**:
- ✅ `app/core/annotation_parser.py` - 标注解析引擎（正则匹配 + glossary 关联）
- ✅ `app/api/annotation.py` - 标注解析 API（POST /parse, GET /examples, /types, /glossary）
- ✅ `frontend/src/views/Calculator.vue` - 锚固计算器前端（Vue3 + Vuetify）
- ✅ `tests/test_api_annotation.py` - 标注解析 API 测试（6 个测试全部通过）
- ✅ 总测试数：34 个全部通过

**API 验证**:
- POST `/api/v1/annotation/parse` - KL7(3) 300x650 → 框架梁，编号7，3跨，300×650 ✓
- POST `/api/v1/annotation/parse` - KZ1 500x500 → 框架柱，编号1，500×500 ✓
- GET `/api/v1/annotation/examples` - 返回示例列表 ✓
- GET `/api/v1/annotation/glossary` - 返回符号释义 ✓

**前端验证**:
- Calculator.vue - 表单下拉选项正常加载
- 计算按钮调用 API 成功
- 结果显示 lab, la, laE 值

**解析结果验证**:
| 输入 | 类型 | 编号 | 跨数 | 截面 | 状态 |
|------|------|------|------|------|------|
| KL7(3) 300x650 | 框架梁 | 7 | 3 | 300×650 | ✓ |
| L2(1A) 250x500 | 非框架梁 | 2 | 1A | 250×500 | ✓ |
| KZ1 500x500 | 框架柱 | 1 | - | 500×500 | ✓ |
| Z2 400x600 | 柱 | 2 | - | 400×600 | ✓ |

**里程碑 M3 达成**：锚固计算可通过浏览器访问（http://localhost:5173）

---

### 2026-06-28 - Week 4 图集速查 API + 标注解析器前端完成

**完成项**:
- ✅ 修复 annotation.py ParseResponse 缺少 partial 字段的 bug（解析失败时不再返回 500 错误）
- ✅ 修复 annotation_rule field_map 索引问题（从 1-based 改为 0-based，解析逻辑已修正）
- ✅ 扩展 specification JSON 条文骨架（一般构造 3 条、柱 2 条、梁 3 条，共 8 条）
- ✅ 实现图集速查 API（5 个路由：search/categories/by-category/detail/related）
- ✅ 新增 13 个 specification API 测试
- ✅ 实现标注解析器前端页面 Parser.vue（输入框、示例快捷按钮、解析结果、符号释义）
- ✅ 实现图集速查前端页面 Reference.vue（搜索、分类浏览、详情对话框、关联跳转、交叉引用）
- ✅ 数据库总记录数：79 条（specification 表 8 条）
- ✅ 总测试数：47 个全部通过

**API 验证**:
- GET `/api/v1/specification/search?keyword=锚固` - 返回匹配结果 ✓
- GET `/api/v1/specification/categories` - 返回 ["一般构造", "柱", "梁"] ✓
- GET `/api/v1/specification/by-category?category=梁` - 返回 3 条梁条文 ✓
- GET `/api/v1/specification/detail/spec-anchor-general` - 返回条文详情（含 HTML）✓
- GET `/api/v1/specification/related/spec-beam-notation` - 返回关联标注类型和交叉引用 ✓
- POST `/api/v1/annotation/parse` - KL7(3) 300x650 → 框架梁，编号 7，3 跨，300×650 ✓

**前端验证**:
- Parser.vue - 加载示例列表、解析 API 调用成功、结果显示正常
- Reference.vue - 分类加载、搜索、详情对话框、v-html 渲染正常

**条文数据状态**:
- 一般构造：3 条（锚固长度、修正系数、保护层 - 后 2 条为骨架占位）
- 柱：2 条（标注规则、截面注写 - 后 1 条为骨架占位）
- 梁：3 条（标注规则、集中标注、原位标注 - 后 2 条为骨架占位）
- 占位条目已用 `[待用户提供原文后补充]` 标注，用户填入真实规范原文后可直接使用

**里程碑 M4 部分达成**：图集速查 API 完整可用，前端页面已完成，条文数据骨架就绪（待填原文）

---

### 2026-06-28 - Week 5 图集速查 + 三模块闭环完成

**完成项**:
- ✅ Home.vue - 实现最近查询功能（localStorage 持久化，最多保存 5 条）
- ✅ About.vue - 完善反馈联系方式、条文依据声明、技术栈展示
- ✅ Calculator.vue - 添加"查看相关条文"跳转按钮，支持路由参数预填，保存最近查询
- ✅ Parser.vue - 添加"查看条文"和"计算锚固"跳转按钮，支持路由参数预填，保存最近查询
- ✅ Reference.vue - 支持路由参数搜索/分类，添加最近查询保存，优化关联跳转逻辑

**模块间跳转映射**:
| 从 | 动作 | 到 | 携带参数 |
|----|------|----|---------|
| 锚固计算器 | 查看相关条文 | 图集速查 | ?keyword=锚固长度 |
| 标注解析器 | 查看相关条文 | 图集速查 | ?keyword=梁平法/柱平法 |
| 标注解析器 | 计算锚固 | 锚固计算器 | /calculator |
| 图集速查 | 试试锚固计算 | 锚固计算器 | /calculator |
| 图集速查 | 解析相关标注 | 标注解析器 | ?text=示例标注 |
| 首页 | 点击最近查询 | 对应页面 | 带参数的跳转 |

**最近查询功能**:
- 三个模块统一使用 localStorage 存储最近查询
- 数据类型：anchor_calc, annotation_parse, spec_search
- 最多保存 5 条，自动去重
- 首页显示查询类型、内容、时间（刚刚/X 分钟前/X 小时前/月/日）
- 点击历史项可直接跳转到对应页面并预填参数

**里程碑 M4 完全达成**: 三模块完整可用 + 模块间关联跳转

---

### 2026-06-28 - Week 6 PWA + 测试修正完成

**完成项**:
- ✅ vite-plugin-pwa 集成，配置 manifest 和 Service Worker
- ✅ 生成 8 尺寸 PWA 图标（72x72 ~ 512x512）
- ✅ Workbox 缓存策略配置（API 数据 7 天、条文 30 天）
- ✅ PWA 更新提示组件（PWAPrompt.vue）
- ✅ 锚固计算验证：新增 10 组对照 22G101 测试用例（共 21 个锚固测试）
- ✅ 浮点精度修正：int(x) → int(x+0.001) 避免截断误差
- ✅ 标注解析增强：
  - 悬挑规则修正：(3)=3 跨、(3A)=3 跨一端悬挑、(3B)=3 跨两端悬挑
  - 支持 x/X/×三种乘号输入
  - 输入自动转大写、兼容多余空格
- ✅ 测试总数从 47→69，全部通过

**关键修正**:
- 平法悬挑规则理解错误已纠正（用户指正）
- 大写 X 替代乘号的支持（用户测试发现）

**Week 6 里程碑达成**: PWA 可用 + 核心功能验证通过（69 测试全过）

---

### 2026-06-28 - Week 7 UI 响应式优化完成 (Day 1-3)

**完成项**:
- ✅ App.vue 底部导航栏优化 (增加触摸区域、调整字体大小)
- ✅ App.vue 添加全局样式优化 (移动端导航栏、输入框防缩放、按钮触摸区域)
- ✅ Home.vue 功能卡片优化 (固定高度、增大图标、过渡动画)
- ✅ Calculator.vue 错误边界处理 (选项加载失败提示 + 重试按钮)
- ✅ Parser.vue textarea 替换 input (多行输入、auto-grow、字数限制)
- ✅ Reference.vue 搜索框布局优化 (手机端堆叠布局)
- ✅ Reference.vue 错误边界处理 (分类加载失败 + 重试)
- ✅ 所有页面统一错误提示样式和恢复机制

**优化要点**:
- 底部导航栏 min-height: 56px，字体 11px，适合单手操作
- 主内容区 padding-bottom: 72px，防止被导航栏遮挡
- 输入框 font-size: 16px，防止 iOS 自动放大
- 卡片 hover 效果 (桌面端) 和 active 反馈 (移动端)
- 错误提示包含重试按钮，提升用户体验

**UI 响应式状态**: ✅ 手机端适配完成

---

### 2026-06-28 - Week 7 性能优化完成 (Day 4-5)

**完成项**:
- ✅ 创建 useOptionsStore Pinia Store（缓存锚固计算选项数据）
- ✅ 创建 useSpecificationStore Pinia Store（缓存图集条文数据）
- ✅ Calculator.vue 改用 Store 读取选项数据
- ✅ Reference.vue 改用 Store 读取条文数据
- ✅ 缓存有效期：选项数据 30 分钟、条文数据 10 分钟
- ✅ 修复 vite.config.ts esbuild 配置错误
- ✅ 前端构建成功 (dist/目录生成)

**性能优化要点**:
- 避免重复 API 调用，提升首次访问速度
- Store 缓存减少服务器压力
- 前端代码分割优化打包体积

**构建状态**: ✅ dist/目录已生成，PWA 预缓存 35 个资源

**UI 响应式状态**: ✅ 手机端适配完成 + 性能优化完成

---

## 风险跟踪

| 风险 | 概率 | 影响 | 应对措施 | 状态 |
|------|------|------|---------|------|
| Vue3 学习曲线超预期 | 中 | 高 | Week1 增加 1 天 Vue3 速成 | ✅ 已缓解 |
| 22G101 数据提取耗时过长 | 中 | 高 | 先提取核心数据 | ✅ 已完成 |
| 标注解析准确率不足 | 中 | 高 | Week3 预留 1 天规则调优 | ✅ 已缓解 (field_map 修正后测试通过) |
| 手机端性能问题 | 低 | 中 | Week6-7 重点优化 | ✅ 已优化 |
| 部署受阻 | 低 | 中 | Railway 为主，Vercel 备用 | ⏳ 监控中 |