# 平法辅助学习 App - 实施计划

> 基于设计规格 `docs/design.md`  
> 创建日期：2026-06-26  
> 工期：7-8周（56天）

---

## 计划概览

| 项目 | 内容 |
|------|------|
| 工期 | 7-8周（56天） |
| 人力 | 1人（全栈开发） |
| 技术栈 | Vue3 + FastAPI + SQLite |
| 里程碑 | 5个（M1-M5） |
| 交付物 | PWA应用 + 公网部署 |

---

## 阶段划分

```
Week 1-2: 基础设施 → 数据层 → 核心引擎
Week 3-4: 前端框架 → 页面实现 → API联调
Week 5:   功能闭环 → 整合优化
Week 6-7: PWA → 测试 → 性能优化
Week 8:   部署 → 用户测试 → 上线
```

---

## Week 1: 环境搭建 + 数据准备

### 任务 1.1: FastAPI项目骨架 (Day 1-2)

**目标**: 可运行的后端服务框架

**具体步骤**:
1. 创建目录结构
   ```
   backend/
   ├── app/
   │   ├── __init__.py
   │   ├── api/
   │   ├── core/
   │   ├── models/
   │   └── services/
   ├── data/
   └── tests/
   ```

2. 创建 `requirements.txt`
   ```txt
   fastapi>=0.100.0
   uvicorn[standard]>=0.23.0
   sqlmodel>=0.0.14
   aiosqlite>=0.19.0
   pydantic>=2.0.0
   pytest>=7.4.0
   pytest-asyncio>=0.21.0
   httpx>=0.24.0
   ```

3. 创建 `main.py` - FastAPI入口
   - 初始化FastAPI应用
   - 配置CORS（开发环境）
   - 注册API路由（空壳）
   - 数据库连接初始化

4. 运行验证
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   # 访问 http://localhost:8000/docs 看到OpenAPI文档
   ```

**验收标准**:
- [ ] `python main.py` 启动成功，无报错
- [ ] 访问 `/docs` 看到FastAPI自动生成的API文档页面
- [ ] 项目目录结构符合设计规范

---

### 任务 1.2: SQLModel数据模型 (Day 2-3)

**目标**: 定义所有数据表结构

**具体步骤**:
1. 创建 `app/models/database.py`
   - ConcreteGrade 表
   - RebarType 表
   - SeismicModifier 表
   - AnchorTable 表
   - Specification 表
   - AnnotationRule 表
   - Glossary 表

2. 创建 `data/init_db.py` - 数据库初始化脚本
   - 读取JSON数据文件
   - 创建表结构
   - 导入初始数据

3. 运行验证
   ```bash
   python data/init_db.py
   # 生成 SQLite 数据库文件
   ```

**验收标准**:
- [ ] 所有SQLModel类定义完成，无语法错误
- [ ] `init_db.py` 可成功创建SQLite数据库
- [ ] 数据库文件可正常打开，表结构正确

---

### 任务 1.3: Vue3 + Vite项目搭建 (Day 3-4)

**目标**: 可运行的前端开发环境

**具体步骤**:
1. 使用Vite创建Vue3项目
   ```bash
   cd pingfa_app
   npm create vite@latest frontend -- --template vue-ts
   cd frontend
   npm install
   ```

2. 安装依赖
   ```bash
   npm install vue-router@4 pinia axios vuetify@3
   ```

3. 配置Vuetify
   - 修改 `main.ts` 引入Vuetify
   - 配置主题（Material Design）

4. 配置Vue Router
   - 创建 `src/router/index.ts`
   - 定义5个路由：Home, Calculator, Parser, Reference, About

5. 配置Pinia
   - 创建 `src/stores/` 目录
   - 创建空的状态文件

6. 运行验证
   ```bash
   npm run dev
   # 访问 http://localhost:5173 看到Vue默认页面
   ```

**验收标准**:
- [ ] `npm run dev` 启动成功
- [ ] 浏览器访问看到Vue3 + Vuetify界面
- [ ] 项目目录结构符合设计规范

---

### 任务 1.4: 22G101核心数据提取 (Day 5-7)

**目标**: 提取锚固计算所需的数值数据

**数据来源**: 22G101-1 第57-58页

**提取内容**:

1. **锚固长度表** (`data/anchor/lab_table.json`)
   - 混凝土等级: C20, C25, C30, C35, C40, C45, C50, C55, C60
   - 钢筋类型: HRB300, HRB400, HRB500
   - lab值: d的倍数

2. **抗震修正系数** (`data/anchor/seismic_modifiers.json`)
   - 一级抗震: 1.15
   - 二级抗震: 1.15
   - 三级抗震: 1.05
   - 四级抗震: 1.00
   - 非抗震: 1.00

3. **混凝土强度值** (`data/anchor/concrete_strength.json`)
   - 各等级的 ft 值（抗拉强度设计值）

4. **钢筋参数** (`data/anchor/rebar_strength.json`)
   - 各钢筋类型的 fy 值（抗拉强度设计值）
   - 外形系数 α（光圆0.16，带肋0.14）

**数据验证**:
- 手工核对10组数据与图集一致
- 创建验证脚本 `tests/test_data.py`

**验收标准**:
- [ ] 4个JSON文件创建完成
- [ ] 数据通过验证脚本检查
- [ ] `init_db.py` 可成功导入这些数据

---

**Week 1 里程碑 M1**: 环境就绪
- FastAPI可访问 (`/docs`)
- Vue3可访问 (开发服务器)
- 数据库有数据 (SQLite文件存在且有数据)

---

## Week 2: 数据层 + 锚固计算核心

### 任务 2.1: 数据导入与API基础 (Day 1-3)

**目标**: 数据服务层 + 基础API框架

**具体步骤**:
1. 完善 `init_db.py`
   - 加载所有JSON数据
   - 插入数据库
   - 添加日志输出

2. 创建 `app/services/data_service.py`
   - 查询混凝土等级列表
   - 查询钢筋类型列表
   - 查询抗震等级列表
   - 查询锚固长度（查表）

3. 创建 `app/api/data.py`
   - GET /api/v1/data/concrete-grades
   - GET /api/v1/data/rebar-types
   - GET /api/v1/data/seismic-grades
   - GET /api/v1/data/diameters

4. 在 `main.py` 中注册路由

5. API测试
   ```bash
   curl http://localhost:8000/api/v1/data/concrete-grades
   ```

**验收标准**:
- [ ] 所有数据查询API可正常访问
- [ ] 返回JSON格式正确
- [ ] API文档中可见这些接口

---

### 任务 2.2: 锚固计算引擎 (Day 4-5)

**目标**: 实现查表+公式双策略

**具体步骤**:
1. 创建 `app/core/anchor_calc.py`

2. 实现查表法
   ```python
   def get_lab_from_table(concrete_grade, rebar_type) -> int:
       # 查询 anchor_tables 表
       # 返回 lab_d (d的倍数)
   ```

3. 实现公式法
   ```python
   def calculate_lab_formula(concrete_grade, rebar_type, diameter, surface) -> float:
       # lab = α × (fy/ft) × d
       # 查询 ft, fy, α
       # 计算 lab
   ```

4. 实现双策略验证
   ```python
   def calculate_anchor(concrete_grade, rebar_type, diameter, 
                        seismic_grade, surface) -> AnchorResult:
       # 1. 查表得到 lab_d
       # 2. 公式计算 lab
       # 3. 对比验证（误差<1%）
       # 4. 计算 la, laE
       # 5. 返回完整结果
   ```

5. 单元测试
   - 创建 `tests/test_anchor_calc.py`
   - 10组测试用例对照22G101验证
   - 覆盖C20-C60 × HRB300/400/500

**验收标准**:
- [ ] 计算引擎可正确计算lab/la/laE
- [ ] 10组测试用例全部通过
- [ ] 查表值与公式计算值一致（误差<1%）

---

### 任务 2.3: 锚固计算API (Day 6-7)

**目标**: POST /api/v1/anchor/calculate 接口

**具体步骤**:
1. 创建 `app/api/anchor.py`
   - POST /api/v1/anchor/calculate
   - GET /api/v1/anchor/options

2. 定义Pydantic模型
   - AnchorCalculateRequest
   - AnchorCalculateResponse

3. 实现API逻辑
   - 接收请求参数
   - 调用计算引擎
   - 返回完整结果

4. API测试
   ```bash
   curl -X POST http://localhost:8000/api/v1/anchor/calculate \
     -H "Content-Type: application/json" \
     -d '{"concrete_grade":"C30","rebar_type":"HRB400",
          "diameter":25,"seismic_grade":"二级","rebar_surface":"带肋"}'
   ```

**验收标准**:
- [ ] API可正常接收请求并返回结果
- [ ] 返回格式符合设计规格
- [ ] 错误参数返回400错误

---

**Week 2 里程碑 M2**: 锚固计算可演示（后端）
- 锚固计算API可用
- 可通过curl或API文档测试

---

## Week 3: 标注解析 + 锚固计算器前端

### 任务 3.1: 标注解析规则与引擎 (Day 1-3)

**目标**: 实现梁/柱标注解析

**具体步骤**:
1. 创建标注规则数据 (`data/annotation/`)
   - beam_rules.json
   - column_rules.json
   - glossary.json

2. 创建 `app/core/annotation_parser.py`
   - load_rules() - 从数据库加载规则
   - parse_annotation(text) - 解析主函数
   - match_rule(text, rules) - 规则匹配
   - extract_fields(match, field_map) - 字段提取
   - build_glossary(symbols) - 释义组装

3. 实现解析逻辑
   - 遍历所有规则尝试匹配
   - 正则捕获组提取字段
   - 组装parsed结果
   - 查询glossary组装释义

4. 错误处理
   - 部分匹配处理
   - 完全失败处理（返回suggestion）

5. 单元测试
   - 梁标注测试: KL7(3) 300×650, L2(1A) 250×500等
   - 柱标注测试: KZ1 500×500, Z2 400×600等
   - 失败case测试

**验收标准**:
- [ ] 可正确解析KL/L/WKL/KZ/Z/QZ标注
- [ ] 返回包含parsed、glossary、related_spec_id的完整结果
- [ ] 失败时返回有用的suggestion

---

### 任务 3.2: 标注解析API (Day 3)

**目标**: POST /api/v1/annotation/parse 接口

**具体步骤**:
1. 创建 `app/api/annotation.py`
   - POST /api/v1/annotation/parse
   - GET /api/v1/annotation/examples
   - GET /api/v1/annotation/types
   - GET /api/v1/annotation/glossary

2. 定义Pydantic模型
   - AnnotationParseRequest
   - AnnotationParseResponse

3. API测试

**验收标准**:
- [ ] 标注解析API可用
- [ ] 返回格式符合设计规格

---

### 任务 3.3: 锚固计算器页面 (Day 4-5)

**目标**: Vue3实现锚固计算器UI

**具体步骤**:
1. 创建 `src/views/Calculator.vue`

2. 组件结构
   - 页面标题
   - 输入表单（4个v-select）
   - 计算按钮
   - 结果展示卡片

3. 数据绑定
   - 使用Pinia store存储选择状态
   - 调用API获取选项列表
   - 提交计算请求

4. 样式调整
   - Vuetify卡片布局
   - 移动端适配
   - 结果数值突出显示

5. 交互优化
   - 加载状态
   - 错误提示
   - 计算历史（临时）

**验收标准**:
- [ ] 页面可在浏览器正常显示
- [ ] 可选择参数并点击计算
- [ ] 结果正确显示
- [ ] 样式符合设计稿

---

### 任务 3.4: API联调 (Day 6-7)

**目标**: 前后端联调，锚固计算完整可用

**具体步骤**:
1. 配置axios
   - 创建 `src/api/index.ts`
   - 配置baseURL
   - 添加错误处理

2. 实现API调用
   - fetchOptions() - 获取选项列表
   - calculateAnchor() - 提交计算

3. 联调测试
   - 前端调用后端API
   - 数据流转验证
   - 错误处理验证

4. 路由配置
   - 确保 `/calculator` 路由可用

**验收标准**:
- [ ] 从前端到后端完整流程可用
- [ ] 选择参数→计算→显示结果
- [ ] Week 3里程碑达成

---

**Week 3 里程碑 M3**: 锚固计算可演示（完整）
- 访问 `/calculator` 可进行完整计算
- 结果与22G101一致

---

## Week 4: 图集数据 + 标注解析器前端

### 任务 4.1: 图集条文转写 (Day 1-3)

**目标**: 将22G101核心条文转写为HTML

**提取范围**:
- 第1-2章：一般构造规定（节选）
- 第2章：柱平法规则（节选）
- 第4章：梁平法规则（节选）

**具体步骤**:
1. 创建 `data/specifications/`
   - general_rules.json
   - column_rules.json
   - beam_rules.json

2. 每条条文格式
   ```json
   {
     "id": "spec-anchor-general",
     "clause_number": "2.2.1",
     "title": "受拉钢筋锚固长度一般规定",
     "category": "一般构造",
     "content_html": "<h3>2.2.1 受拉钢筋锚固长度</h3><p>当...</p><table>...</table>",
     "related_calc": "anchor",
     "related_ann_type": null
   }
   ```

3. 内容转写
   - 保留条文编号
   - 表格用HTML table
   - 公式用纯文本描述（MVP阶段）

4. 数据验证
   - 人工核对关键数值

**验收标准**:
- [ ] 3个JSON文件创建完成
- [ ] 覆盖核心条文（锚固、梁标注、柱标注）
- [ ] init_db.py可成功导入

---

### 任务 4.2: 图集速查API (Day 3-4)

**目标**: 实现图集搜索和查询API

**具体步骤**:
1. 创建 `app/api/specification.py`
   - GET /api/v1/specification/search
   - GET /api/v1/specification/categories
   - GET /api/v1/specification/by-category
   - GET /api/v1/specification/detail/{id}
   - GET /api/v1/specification/related/{id}

2. 实现搜索功能
   - 关键词匹配title和content_html
   - 支持分类筛选
   - 分页返回

3. 定义Pydantic模型

4. API测试

**验收标准**:
- [ ] 搜索API可用
- [ ] 可按分类浏览
- [ ] 可获取单条条文详情

---

### 任务 4.3: 标注解析器页面 (Day 4-5)

**目标**: Vue3实现标注解析器UI

**具体步骤**:
1. 创建 `src/views/Parser.vue`

2. 组件结构
   - 页面标题
   - 输入框（v-text-field）
   - 常用示例快捷按钮
   - 解析按钮
   - 结果展示（parsed + glossary）
   - 相关链接（查看条文、计算锚固）

3. 数据绑定
   - 输入文本
   - 调用parse API
   - 展示结果

4. 样式调整
   - glossary释义卡片样式
   - 链接按钮样式

**验收标准**:
- [ ] 可输入标注并解析
- [ ] 显示parsed字段和释义
- [ ] 相关链接可点击跳转

---

### 任务 4.4: 图集速查页面 (Day 6-7)

**目标**: Vue3实现图集速查UI

**具体步骤**:
1. 创建 `src/views/Reference.vue`

2. 组件结构
   - 搜索栏（v-text-field + 搜索图标）
   - 分类标签（v-chip-group）
   - 条文列表（v-list）
   - 条文详情（v-card）

3. 功能实现
   - 搜索关键词
   - 点击分类筛选
   - 点击列表项展开详情
   - 详情中显示关联链接

4. 样式调整
   - 列表简洁显示
   - 详情区域突出

**验收标准**:
- [ ] 可搜索条文
- [ ] 可按分类浏览
- [ ] 可查看条文详情
- [ ] 关联链接可点击跳转

---

**Week 4 里程碑**: 三模块前端可用
- 锚固计算器、标注解析器、图集速查三页面可用
- 各自独立功能完整

---

## Week 5: 功能闭环 + 整合优化

### 任务 5.1: 模块间关联跳转 (Day 1-3)

**目标**: 实现三模块间的关联跳转

**跳转映射**:

| 从 | 动作 | 到 | 携带参数 |
|----|------|----|---------|
| 锚固计算器 | 查看相关条文 | 图集速查 | spec_id |
| 标注解析器 | 查看相关条文 | 图集速查 | spec_id |
| 标注解析器 | 计算锚固长度 | 锚固计算器 | rebar_type |
| 图集速查 | 试试锚固计算 | 锚固计算器 | category暗示的默认值 |
| 图集速查 | 解析相关标注 | 标注解析器 | ann_example |

**具体步骤**:
1. 实现路由跳转
   - Vue Router编程式导航
   - query参数传递

2. 实现参数预填
   - 锚固计算器读取query参数预填表单
   - 标注解析器读取query预填输入框

3. 添加跳转按钮
   - 锚固计算器结果卡片添加"查看相关条文"
   - 标注解析器结果添加"查看条文"和"计算锚固"
   - 图集详情添加"试试计算"和"解析标注"

**验收标准**:
- [ ] 所有跳转路径可用
- [ ] 参数正确传递和预填

---

### 任务 5.2: 首页 (Day 4)

**目标**: 实现首页功能入口

**具体步骤**:
1. 创建 `src/views/Home.vue`

2. 组件结构
   - 应用标题和简介
   - 3个功能入口卡片（计算/解析/查阅）
   - 最近查询记录（5条）

3. 最近查询功能
   - Pinia store存储历史
   - localStorage持久化
   - 点击历史项快速跳转

**验收标准**:
- [ ] 首页显示3个功能入口
- [ ] 最近查询记录可点击复用

---

### 任务 5.3: 关于页面 (Day 5)

**目标**: 实现关于页面

**具体步骤**:
1. 创建 `src/views/About.vue`

2. 内容
   - 应用说明
   - 版本信息
   - 反馈联系方式（微信/邮箱）
   - 条文依据声明

**验收标准**:
- [ ] 关于页面可用
- [ ] 包含反馈入口

---

### 任务 5.4: UI整合优化 (Day 6-7)

**目标**: 统一风格，完善细节

**具体步骤**:
1. 统一主题色（建议土木工程蓝 #1976d2）
2. 统一按钮样式
3. 统一卡片样式
4. 添加页面过渡动画
5. 添加加载状态
6. 添加错误提示（toast/snackbar）

**验收标准**:
- [ ] 三页面风格统一
- [ ] 交互流畅
- [ ] Week 5里程碑达成

---

**Week 5 里程碑 M4**: 三模块完整可用
- 首页 + 三功能模块 + 关于
- 模块间可关联跳转
- 最近查询功能可用

---

## Week 6: PWA + 测试修正

### 任务 6.1: PWA配置 (Day 1-3)

**目标**: 配置PWA，支持离线访问

**具体步骤**:
1. 安装vite-plugin-pwa
   ```bash
   npm install vite-plugin-pwa -D
   ```

2. 配置 `vite.config.ts`
   - 引入PWA插件
   - 配置manifest
   - 配置workbox

3. 创建 `public/manifest.json`
   - 应用名称：平法助手
   - 图标（192x192, 512x512）
   - 主题色
   - 启动方式

4. 创建图标
   - 使用在线工具生成多尺寸图标
   - 放入public/icons/

5. 测试PWA
   - Chrome DevTools Lighthouse测试
   - 验证可"添加到桌面"
   - 验证离线可用

**验收标准**:
- [ ] Lighthouse PWA测试通过
- [ ] Android Chrome可"添加到桌面"
- [ ] 离线可访问基础功能

---

### 任务 6.2: 计算结果验证 (Day 4-5)

**目标**: 对照22G101验证计算结果

**验证清单**:
| 测试项 | 数据 | 来源 |
|--------|------|------|
| C30/HRB400/25mm/二级 | laE = 1.15×35d = 1006mm | 22G101-1 p.58 |
| C40/HRB500/20mm/一级 | laE = 1.15×32d = 736mm | 22G101-1 p.58 |
| ...共10组 | 手工验算 | 图集附表 |

**具体步骤**:
1. 手工计算10组测试用例
2. 与App结果对比
3. 发现偏差立即修正算法
4. 补充测试用例

**验收标准**:
- [ ] 10组测试全部通过
- [ ] 误差<1%

---

### 任务 6.3: 标注解析测试 (Day 6-7)

**目标**: 提高标注解析准确率

**测试用例**:
- 标准格式：KL7(3) 300×650
- 变体格式：KL7(3A) 300×650（悬挑）
- 边界格式：L1 250×500（简单梁）
- 失败格式：错误格式测试失败处理

**具体步骤**:
1. 收集更多标注示例
2. 调整正则规则
3. 测试覆盖率>80%

**验收标准**:
- [ ] 标准标注解析成功率>95%
- [ ] 失败处理给出有用提示

---

**Week 6 里程碑**: PWA可用 + 核心功能验证通过

---

## Week 7: 整合优化

### 任务 7.1: 手机端适配 (Day 1-3)

**目标**: 优化移动端体验

**检查清单**:
- [ ] 底部导航栏在手机上可见且可点击
- [ ] 输入框在手机上可正常输入
- [ ] 结果卡片在手机上可读
- [ ] 字体大小合适（不小于14px）
- [ ] 按钮大小合适（不小于44px触摸区域）
- [ ] 页面无横向滚动

**具体步骤**:
1. Chrome DevTools手机模拟测试
2. 调整响应式布局
3. 测试真机（如有）

---

### 任务 7.2: 性能优化 (Day 4-5)

**目标**: 提高加载速度

**优化项**:
- [ ] 路由懒加载
- [ ] 图片/图标压缩
- [ ] API响应缓存
- [ ] 首屏加载<3秒

**Lighthouse目标**:
- Performance > 80
- Accessibility > 90
- Best Practices > 90
- SEO > 80

---

### 任务 7.3: 错误边界处理 (Day 6-7)

**目标**: 完善错误处理

**检查项**:
- [ ] API错误显示友好提示
- [ ] 网络错误处理
- [ ] 解析失败处理
- [ ] 全局错误捕获

---

**Week 7 里程碑 M5**: PWA上线准备完成

---

## Week 8: 部署上线

### 任务 8.1: Docker打包 (Day 1-2)

**目标**: 创建Docker镜像

**具体步骤**:
1. 创建 `docker/Dockerfile`
   - 多阶段构建（前端build + 后端run）
   - 或分离部署（前端CDN + 后端Docker）

2. 创建 `docker/docker-compose.yml`

3. 本地测试
   ```bash
   docker-compose up -d
   ```

**验收标准**:
- [ ] Docker镜像构建成功
- [ ] 本地docker-compose可运行

---

### 任务 8.2: 服务器部署 (Day 3-4)

**目标**: 部署到公网

**推荐方案**: Railway（免费额度足够）

**具体步骤**:
1. 注册Railway账号
2. 关联GitHub仓库
3. 配置环境变量
4. 部署

**备选方案**: Vercel（前端）+ Railway（后端）

**验收标准**:
- [ ] 公网HTTPS链接可访问
- [ ] 所有功能正常

---

### 任务 8.3: PWA验证 (Day 5)

**目标**: 验证PWA功能

**检查项**:
- [ ] 公网链接可"添加到桌面"
- [ ] 离线模式可用
- [ ] 二维码生成（使用在线工具）

---

### 任务 8.4: 用户测试 (Day 6-7)

**目标**: 收集用户反馈

**测试任务**:
1. 找3名土木专业学生
2. 不指导，让用户自己打开链接
3. 完成一次锚固计算
4. 尝试搜索"梁上部钢筋"
5. 收集反馈

**反馈收集**:
- 哪里卡住了
- 哪里看不懂
- 觉得有用吗
- 改进建议

**验收标准**:
- [ ] 3名学生可独立完成查询
- [ ] 收集≥5条反馈
- [ ] Week 8里程碑达成

---

**Week 8 里程碑 M6**: MVP完成

---

## 风险应对计划

| 风险 | 应对预案 | 触发条件 |
|------|---------|---------|
| Vue3学习困难 | 增加2天学习缓冲，简化UI | Week1任务延期>2天 |
| 22G101数据提取耗时 | 仅提取核心数据，后续追加 | Week1数据任务延期>1天 |
| 标注解析准确率低 | 减少覆盖类型，仅保梁标注 | Week3测试成功率<80% |
| 手机端性能差 | 降级为在线优先，弱离线 | Week6 Lighthouse < 60 |
| 部署受阻 | 使用Vercel+Railway分离部署 | Railway部署失败 |

---

## 每日时间分配建议

| 时段 | 活动 | 时长 |
|------|------|------|
| 上午 | 核心开发（难任务） | 3-4小时 |
| 下午 | 联调/测试/文档 | 2-3小时 |
| 晚上 | 复盘/计划次日 | 1小时 |

**每日产出检查**:
- 今天完成了什么？
- 是否有阻塞？
- 明天优先级最高的任务是什么？

---

## 交付物清单

### 代码
- [ ] `pingfa_app/` 完整代码
- [ ] `README.md` 部署说明
- [ ] `requirements.txt` + `package.json`

### 文档
- [ ] `docs/design.md` 设计规格
- [ ] API文档（FastAPI自动生成）
- [ ] 部署文档

### 运营
- [ ] 公网访问链接
- [ ] 二维码图片
- [ ] 用户反馈记录

---

**下次会话入口**:
1. 读 `tasks.md` 了解当前任务状态
2. 读 `docs/design.md` 了解设计细节
3. 读 `docs/implementation-plan.md` 了解实施计划
4. 从 Week 1 任务开始执行
