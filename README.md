# PreAnalysis - 汽车测试数据分析系统

<p align="center">
  <img src="pic/bmw-21976-removebg-preview.png" alt="项目标志" width="200">
</p>

## 📋 项目概述

PreAnalysis 是一个用于汽车行业测试数据和缺陷管理的综合分析平台。该系统集成了多种数据可视化工具，能够帮助测试团队和管理人员深入理解测试覆盖率、缺陷分布、风险评估等关键指标，从而优化测试策略和提高产品质量。

## ✨ 主要功能

### 1. 缺陷分析与可视化

- **缺陷矩阵分析 (defect_matrix.py)**  
  提供直观的缺陷矩阵视图，帮助团队识别高风险区域。

- **缺陷地图分布 (defect_map.py)**  
  基于地理位置展示缺陷分布，支持按测试人员和地区分析。

- **缺陷覆盖率分析 (defect_coverage.py)**  
  评估各功能区域的测试覆盖情况，识别测试盲点。

### 2. 🎯 风险分析与预测

- **风险评估 (risk_analysis.py)**  
  综合分析缺陷严重性、测试覆盖率等因素进行风险评估，支持动态时间轴分析。

- **改进版Risk Score算法**  
  采用非线性算法优化，提供更精确的风险评估：
  
  - **Matrix严重度指数衰减**: 使用指数函数替代线性递减，高危等级分数差距更大
  - **缺陷时间双峰分布**: 新票峰(0-3天)和长期峰(30+天)设计，更符合实际业务逻辑
  - **子票数量对数增长**: 体现边际递减效应，避免子票过多导致分数失真
  - **智能组合算法**: 高分项加强影响，低分项降低影响，突出关键风险因素

- **测试覆盖分析 (test_coverage.py)**  
  分析测试用例覆盖情况，评估测试完整性。

### 3. 数据管理与处理

- **数据处理器 (data_processor.py)**  
  核心数据预处理模块，处理数据清洗、转换和聚合。

- **数据库存储 (db_storage.py)**  
  管理数据的持久化存储和检索。

- **数据探索分析 (defect_explore.py)**  
  提供数据探索分析功能，支持数据趋势分析。

### 4. 数据收集工具

- **SSO会话管理 (sso_session.py)**  
  处理单点登录和API接口认证。

- **数据下载工具 (Downloader.ipynb)**  
  自动化数据下载和更新。

### 5. 🤖 AI智能分析

- **统一AI聊天管理器 (ai_chat_manager.py)**  
  提供统一的AI聊天管理架构，支持所有看板的AI功能集成。

- **DeepSeek AI对话助手**  
  集成先进的AI对话功能，提供智能数据分析和建议。

- **智能数据分析**  
  支持多种看板类型，AI助手能够：
  - 智能总结各类数据概况（缺陷、测试、趋势等）
  - 识别和分析高风险问题和异常模式
  - 提供项目分布洞察和优化建议
  - 生成趋势分析和改进建议
  - 回答自定义数据分析问题

- **多看板类型支持**  
  - 缺陷分析看板：专注于缺陷数据分析
  - 测试覆盖率看板：提供测试相关分析
  - 趋势分析看板：专注于时间序列分析
  - 通用看板：适用于任何数据分析场景
L
- **即插即用设计**  
  只需几行代码即可在任何看板中集成完整的AI对话功能。

- **实时上下文感知**  
  AI助手会根据当前筛选的数据提供相关分析，确保建议的准确性和相关性。

## 🛠️ 技术栈

- **Web框架**: Dash, Flask
- **数据分析**: Pandas, NumPy
- **可视化**: Plotly, Dash Bootstrap Components
- **数据存储**: SQLite/JSON
- **AI集成**: DeepSeek API, 流式对话处理
- **智能分析**: 自然语言处理, 上下文感知

## 📊 关键仪表盘

1. **缺陷矩阵仪表盘**  
   直观展示不同矩阵区域的缺陷分布情况。

2. **风险分析仪表盘**  
   通过散点图展示各AIDA(功能区域)的风险状况，支持实时筛选和动态更新。

3. **缺陷地图仪表盘**  
   通过地图展示全球范围内的缺陷分布，支持时间轴动画展示。

4. **覆盖率仪表盘**  
   展示测试覆盖情况与缺陷分布的对比分析。

## 🚀 开始使用

### 安装依赖

```bash
pip install -r requirements.txt
```

### 🤖 AI功能配置（可选）

要使用AI对话功能，请先配置DeepSeek API：

```bash
# 1. 获取API密钥：访问 https://platform.deepseek.com/api_keys
# 2. 设置环境变量
export DEEPSEEK_API_KEY="your-api-key-here"

# 3. 测试配置
python test_deepseek_api.py
```

### 启动应用

#### 方式一：使用启动器（推荐）
```bash
# 快速启动主应用（自动打开浏览器）
python app_launcher.py --quick-start

# 启动完整平台（包含所有子模块）
python app_launcher.py --with-submodules

# 仅启动主应用
python app_launcher.py --main-only

# 显示所有应用状态
python app_launcher.py --status

# 启动指定子模块
python app_launcher.py --module defect_coverage
```

#### 方式二：直接启动
```bash
# 直接启动主应用
python defect_explore.py

# 启动风险分析仪表盘
python risk_analysis.py

# 启动缺陷矩阵仪表盘（包含AI对话功能）
python defect_matrix.py

# 启动缺陷地图仪表盘
python defect_map.py

# 启动覆盖率仪表盘
python defect_coverage.py
```

### 🔍 AI对话功能使用

在缺陷矩阵看板中，您可以：

1. **使用快捷按钮**：
   - "总结当前数据" - 获取数据概览
   - "分析高风险问题" - 识别关键风险
   - "项目分布分析" - 查看项目情况
   - "趋势分析建议" - 获取优化建议

2. **自由对话**：
   - 在输入框中提问任何关于数据的问题
   - AI会根据当前筛选的数据提供智能分析
   - 支持中文对话，易于理解

3. **示例问题**：
   - "当前矩阵1A区域有多少个缺陷？"
   - "哪个项目需要优先关注？"
   - "如何优化测试策略？"

### 集成运行

```bash
# 启动集成仪表盘
python integrated_dashboards.py
```

## 📂 项目结构

```
preanalysis/
├── data_processor.py      # 核心数据处理模块（含改进版Risk Score算法）
├── risk_analysis.py       # 风险分析仪表盘
├── defect_matrix.py       # 缺陷矩阵仪表盘（集成AI对话）
├── defect_map.py          # 缺陷地图仪表盘
├── defect_coverage.py     # 覆盖率分析仪表盘
├── test_coverage.py       # 测试覆盖分析模块
├── db_storage.py          # 数据库存储模块
├── defect_explore.py      # 缺陷探索性分析
├── integrated_dashboards.py # 集成仪表盘
├── test_improved_risk_algorithm.py # 🎯 改进版Risk Score算法测试脚本
├── ai_chat_manager.py     # 🤖 统一AI聊天管理器
├── deepseek_config.py     # 🤖 DeepSeek API配置
├── deepseek_streaming.py  # 🤖 DeepSeek流式对话处理
├── test_deepseek_api.py   # 🤖 API配置测试脚本
├── example_dashboard_with_ai.py # 🤖 AI集成示例看板
├── AI_CHAT_SETUP.md       # 🤖 AI功能设置指南
├── AI_CHAT_INTEGRATION_GUIDE.md # 🤖 AI集成指南
├── scripts/               # 辅助脚本和工具
├── aida/aida_mapping_updater.py # AIDA映射更新工具
├── requirements.txt       # 项目依赖
├── README.md              # 项目说明文档
├── assets/                # 静态资源文件
├── pic/                   # 图像资源
├── defect/                # 缺陷数据目录
├── aida/                  # AIDA相关数据
├── mr/                    # 测试需求数据
└── history/               # 历史数据文件
```

## 🗂️ 缓存管理

项目集成了智能缓存管理系统，帮助优化性能和控制磁盘使用：

### 缓存管理功能

- **自动清理**: 根据文件年龄、大小和使用频率自动清理缓存
- **智能监控**: 实时监控缓存大小和状态
- **定时任务**: 支持设置定时清理任务
- **手动管理**: 提供命令行工具进行手动管理

### 缓存管理工具

```bash
# 查看缓存状态
python scripts/performance/cache/cache_management.py info

# 查看详细文件信息
python scripts/performance/cache/cache_management.py info --details

# 智能清理缓存
python scripts/performance/cache/cache_management.py clean --type smart

# 清理7天以上的旧文件
python scripts/performance/cache/cache_management.py clean --type old --age 7

# 清理到指定大小
python scripts/performance/cache/cache_management.py clean --type large --size 5.0

# 监控缓存状态
python scripts/performance/cache/cache_management.py monitor --check
```

### 设置定时清理

```bash
# 设置每天凌晨2点自动清理
bash scripts/utilities/setup_cache_cron.sh

# 手动运行清理
python scripts/performance/cache/scheduled_cleanup.py
```

### 性能优化启动

```bash
# 使用优化模式启动应用
python scripts/performance/startup/run_optimized.py

# 查看性能分析报告
python scripts/performance/tools/refactor_helper.py
```

### 配置说明

缓存管理器内置了智能配置：

- 最大缓存大小: 10GB（可通过参数调整）
- 文件最大保留天数: 30天（可通过参数调整）
- 自动清理阈值: 当超过80%限制时触发
- 智能清理策略: 结合文件年龄、使用频率和大小控制

## 📝 注意事项

1. 首次运行前请确保配置正确的数据源路径
2. 若使用SSO认证，需在`login_info.txt`中配置凭据信息
3. 对于大型数据集，建议先运行数据预处理脚本提高仪表盘响应速度
4. **缓存管理**: 建议定期检查缓存大小，设置定时清理任务以避免磁盘空间不足
5. **🤖 AI功能**: 
   - AI对话功能需要配置DeepSeek API密钥才能使用
   - 如果没有配置API密钥，系统会自动降级到基础分析模式
   - 建议先运行 `python test_deepseek_api.py` 验证配置
   - 详细配置说明请参考 `AI_CHAT_SETUP.md` 文档

## 📈 使用场景

- **测试覆盖率分析**: 识别测试覆盖不足的功能领域
- **风险评估**: 基于多维度数据评估产品风险
- **🤖 智能数据分析**: 通过AI助手快速获得数据洞察
- **决策支持**: AI提供基于数据的优化建议和趋势分析
- **缺陷管理优化**: 智能识别高风险区域和优先级排序
- **缺陷趋势分析**: 监控和预测缺陷发展趋势
- **团队协作**: 提高测试和开发团队间的沟通效率

## 🔧 架构优化和模块化

### 模块化架构
- ✅ **统一导航管理** - 通过 `navigation_manager.py` 统一管理导航栏
- ✅ **配置驱动开发** - 通过 `config.py` 集中管理所有配置
- ✅ **页面组件管理** - 通过 `page_components.py` 统一管理页面组件
- ✅ **自动化启动器** - 通过 `app_launcher.py` 智能管理应用启动

### 开发效率提升
- 🚀 **快速添加模块** - 只需修改配置文件即可添加新模块
- 🔄 **热插拔支持** - 通过配置控制模块启用/禁用
- 🎨 **统一样式管理** - 自动主题适配和样式统一
- 📊 **组件复用** - 减少重复代码，提高开发速度

### 如何添加新模块

1. **更新配置** (`config.py`)：
   ```python
   # 在 NAVIGATION_CONFIG 中添加导航项
   {
       'id': 'tab-your-new-module',
       'label': '您的新模块',
       'icon': 'fas fa-chart-bar',
       'component': 'your_new_module_page',
       'enabled': True
   }
   ```

2. **创建页面组件** (`page_components.py`)：
   ```python
   def create_your_new_module_page(self) -> html.Div:
       """创建您的新模块页面"""
       return html.Div([
           nav_manager.create_breadcrumb('tab-your-new-module'),
           html.H2("您的新模块"),
           # 添加您的页面内容
       ])
   ```

3. **重启应用**：
   ```bash
   python app_launcher.py --quick-start
   ```

## 🚀 Master缺陷下载优化

### 优化内容
针对Master票据下载失败问题，进行了全面优化：

- **批量重试功能** - 将失败ID分组批量处理，不再一个一个重试
- **智能失败分析** - 区分可重试和不可重试的失败原因
- **灵活的重试配置** - 支持自定义重试参数
- **失败报告文件重试** - 从失败报告文件中批量重试

### 使用方法
```bash
# 基本使用（自动优化）
python downloader3.py --defect-years 2024 --auth-method cookie

# 自定义重试参数
python downloader3.py --defect-years 2024 --auth-method cookie \
  --retry-batch-size 5 \
  --retry-max-attempts 3 \
  --retry-delay 1.0

# 从失败报告重试
python downloader3.py --retry-from-failure-report defect/2024_master_download_failures.json --auth-method cookie
```

## 📱 AI集成指南

### 功能特性
- **统一的AI接口** - 封装DeepSeek API调用和错误处理
- **智能数据上下文** - 自动分析当前数据并生成上下文信息
- **多种看板类型支持** - 预设了缺陷、测试、通用等不同类型的问题模板
- **即插即用** - 只需几行代码即可在任何看板中添加AI功能

### 快速集成
```python
# 导入AI聊天管理器
from ai_chat_manager import ai_chat_manager, get_chat_css_styles

# 在布局中添加聊天界面
ai_chat_manager.create_chat_interface(
    chat_id_prefix='your-dashboard-chat',
    dashboard_type='defect'  # 'defect', 'test', 'trend', 'general'
)

# 注册回调函数
ai_chat_manager.register_chat_callbacks(
    app=app,
    chat_id_prefix='your-dashboard-chat',
    data_store_id='filtered-data',
    dashboard_type='defect'
)
```

## 🔍 未来规划

### 短期目标（1-2周）
1. **完善现有模块** - 将独立 `.py` 文件功能集成到页面组件
2. **数据接口优化** - 创建统一的数据访问层
3. **用户体验提升** - 添加更多交互功能和错误处理

### 中期目标（1-2个月）
1. **API化改造** - 将数据处理逻辑抽象为RESTful API
2. **实时数据支持** - 支持WebSocket实时数据更新
3. **权限管理** - 添加用户认证和权限控制

### 长期目标（3个月以上）
1. **微服务架构** - 各模块独立部署和扩展
2. **容器化部署** - Docker和Kubernetes支持
3. **AI智能分析** - 集成机器学习模型

## 🎨 界面特性

- **响应式设计**: 适配不同屏幕尺寸
- **主题切换**: 支持明暗主题切换
- **交互式图表**: 可点击查看详细数据
- **数据导出**: 支持Excel格式导出
- **全局搜索**: 快速查找特定缺陷信息

## 📱 部署指南

### 本地部署

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境**:
   ```bash
   cp .env.example .env
   vim .env
   ```

3. **启动应用**:
   ```bash
   # 生产模式
   python deploy.py start
   
   # 开发模式
   python deploy.py dev
   ```

### 访问方式
- **本机访问**: http://localhost:8051
- **局域网访问**: http://YOUR_IP:8051

### 性能监控
- 访问日志: `logs/access.log`
- 错误日志: `logs/error.log`
- 进程状态: `ps aux | grep defect_explore`

## 🛠️ 开发指南

### 添加新功能

1. 在 `defect_explore.py` 中添加新的页面组件
2. 在 `data_processor.py` 中添加数据处理逻辑
3. 更新 `dash_common_styles.py` 中的样式定义
4. 添加相应的回调函数

### 样式自定义

项目支持主题切换，在 `dash_common_styles.py` 中定义了：
- 明亮主题样式
- 暗色主题样式
- 通用组件样式
- 响应式布局

## 📝 注意事项

1. 首次运行前请确保配置正确的数据源路径
2. 若使用SSO认证，需在`login_info.txt`中配置凭据信息
3. 对于大型数据集，建议先运行数据预处理脚本提高仪表盘响应速度
4. **缓存管理**: 建议定期检查缓存大小，设置定时清理任务以避免磁盘空间不足
5. **🤖 AI功能**: 
   - AI对话功能需要配置DeepSeek API密钥才能使用
   - 如果没有配置API密钥，系统会自动降级到基础分析模式
   - 建议先运行 `python test_deepseek_api.py` 验证配置

### 数据文件要求

确保以下数据文件存在并可访问：
- `defect/2025_defect.json` - 主要缺陷数据
- `defect/2025_defect_master.json` - 主缺陷关联数据
- `aida/top_aida_project_fv_mapping.xlsx` - AIDA项目映射
- `project/vin_project_mapping.xlsx` - 项目VIN映射
- `history/` - 历史数据目录（可选）

### 缓存管理建议

```bash
# 查看缓存状态
python cache_helper.py

# 清理缓存
find . -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null

# 清理7天以上的缓存文件
find cache/ -name "*.pkl" -mtime +7 -delete 2>/dev/null
```

## 🎯 改进版Risk Score算法详解

### 算法概述

改进版Risk Score算法采用非线性数学模型，相比传统线性算法提供更精确的风险评估。算法基于8个维度进行综合评估，总分可达200+分，支持智能组合和非线性调整。

### 核心改进点

#### 1. **Matrix严重度 - 指数衰减** 📊
```
旧算法: 线性递减
Matrix-1a: 30分 → Matrix-1b: 28分 → Matrix-1c: 26分

新算法: 指数衰减
Matrix-1a: 30分 → Matrix-1b: 24分 → Matrix-1c: 19分
```

**数学公式**: `score = 30 × e^(-0.25 × order)`

**优势**: 高危等级分数差距更大，更好区分严重性层级

#### 2. **缺陷时间 - 双峰分布** ⏰
```
旧算法: 单调递增，越久越高分

新算法: 双峰分布
- 新票峰(0-3天): 24-18分 - 需要快速响应
- 低谷期(4-20天): 5-15分 - 正常处理中  
- 长期峰(21-30天): 15-20分 - 开始进入Long Runner
- 高峰期(30+天): 20-25分 - 严重Long Runner问题
```

**数学公式**: 
- 新票峰: `score = max(18, 24 - days × 2)`
- 低谷期: `score = 5 + 10 × (1 - ((days-12)/12)²)`
- 长期峰: `score = 15 + (days-21) × 0.5`
- 高峰期: `score = min(25, 20 + (extra_days÷10) × 2)`

**优势**: 更符合实际业务逻辑，避免"越久越重要"的误区

#### 3. **子票数量 - 对数增长** 📈
```
旧算法: 线性阶梯
1个子票: 10分 → 3个子票: 20分 → 5个子票: 30分

新算法: 对数增长
1个子票: 17分 → 3个子票: 25分 → 10个子票: 30分
```

**数学公式**: `score = min(30, 10 × log(count + 1) × 2.5)`

**优势**: 体现边际递减效应，避免子票过多导致分数失真

#### 4. **智能组合算法** 🧮
```
旧算法: 简单相加
总分 = 维度1 + 维度2 + ... + 维度8

新算法: 智能组合
- 高分项(>15分): 算术平均 × 1.2 × 项数 (加强影响)
- 低分项(≤15分): 几何平均 × 0.8 × 项数 (降低影响)
```

**数学公式**: 
- 高分项贡献: `Σ(高分项) ÷ 项数 × 1.2 × 项数`
- 低分项贡献: `∏(低分项)^(1/项数) × 0.8 × 项数`

**优势**: 突出关键风险因素，避免被大量低分项稀释

### 完整算法流程

#### 第一步: 基础维度评分
1. **Matrix严重度** (指数衰减) - 最高30分
2. **分类标签** (原有逻辑) - 最高30分
3. **ECU转移次数** (原有逻辑) - 最高30分
4. **域转移次数** (原有逻辑) - 最高20分
5. **父票复杂度** (对数增长) - 最高30分
6. **子票复杂度** (对数增长) - 最高30分
7. **处理时间** (双峰分布) - 最高25分
8. **Shift PU状态** (原有逻辑) - 最高10分

#### 第二步: 智能组合计算
```python
# 分离高分项和低分项
high_score_items = [score for score in dimension_scores if score > 15]
low_score_items = [score for score in dimension_scores if score <= 15]

# 计算组合分数
combined_score = 0
if high_score_items:
    combined_score += mean(high_score_items) × 1.2 × len(high_score_items)
if low_score_items:
    combined_score += geometric_mean(low_score_items) × 0.8 × len(low_score_items)
```

#### 第三步: 非线性调整
保留原有的维度交互效应、时间加速、复杂度阈值等非线性调整机制。

### 风险等级划分

| 分数范围 | 风险等级 | 说明 |
|---------|---------|------|
| ≥140分 | 极高风险 | 需要立即处理的关键问题 |
| ≥100分 | 高风险 | 高优先级处理 |
| ≥60分 | 中风险 | TopIssue阈值，需要重点关注 |
| ≥30分 | 低风险 | 正常跟踪处理 |
| <30分 | 无风险 | 常规处理 |

### 算法测试验证

#### 测试用例对比
```bash
# 运行算法测试
python test_improved_risk_algorithm.py
```

**测试结果示例**:
- 高严重性新票: 98分 (中风险) - 新票峰效应体现
- 中等严重性长期票: 70分 (中风险) - 长期峰效应体现  
- 复杂父票: 118分 (高风险) - 对数增长和智能组合效果明显
- 普通处理中票: 8分 (无风险) - 低谷期效应体现

### 关键优势

1. **更精确的风险识别**: 指数衰减让高危Matrix问题更突出
2. **更合理的时间评估**: 双峰分布符合实际业务流程
3. **更平衡的复杂度计算**: 对数增长避免极值失真
4. **更智能的综合评分**: 高分项加强，低分项降权
5. **更符合业务逻辑**: 算法设计贴合实际工作场景

### 实际应用效果

通过改进版算法，系统能够：
- 更准确地识别高风险缺陷
- 避免被大量低分维度稀释关键风险
- 提供更符合业务逻辑的时间评估
- 优化资源分配和优先级排序

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📞 支持

如有问题或建议，请通过以下方式联系：
- 创建 Issue
- 发送邮件到项目维护者
- 参与项目讨论 