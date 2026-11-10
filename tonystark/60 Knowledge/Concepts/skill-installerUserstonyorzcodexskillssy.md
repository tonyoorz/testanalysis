---
title: "skill-installerUserstonyorzcodexskillssy"
type: knowledge
source: "Codex"
source_file: "10 Sources/raw/conversations/Codex/skill-installer-Users-tonyorz-codex-skills-system-.md"
compiled_at: 2026-07-15
compiler: claude-sonnet-5
tags:
  - compiled-knowledge
---

# skill-installerUserstonyorzcodexskillssy

> 编译自 [[10 Sources/raw/conversations/Codex/skill-installer-Users-tonyorz-codex-skills-system-.md]] 的完整对话。

## 核心问题

针对项目中的 Duplicate Search Agent（查重业务智能体），制作一份"少 AI 味"的技术分享 PPT，面向测试、产品、技术、管理层四类混合听众，需要讲透彻该 agent 的原理、技术架构和工作流程，同时兼顾不同角色的理解门槛。

## 关键结论

- **技能选型**：通过 `skill-installer` 对比官方精选库与 GitHub 高热度技能，最终选定 [anthropics/skills](https://github.com/anthropics/skills) 仓库下的 `pptx` 技能（约 16.1 万 Star），安装于 `/Users/tonyorz/.codex/skills/pptx/SKILL.md`，采用专有许可。该技能覆盖创建/编辑 `.pptx`、模板套用、讲者备注、内容提取、渲染与视觉 QA 全流程。
- **技术定位**：代码分析确认 Duplicate Search Agent 不是简单的"LLM + 向量库"，而是由检索、融合、渐进式重排、证据解释和反馈闭环共同组成的系统。
- **分享结构确定**：
  - 时长：30 分钟正文 + 10 分钟问答
  - 目标：A（建立跨角色共同认知，讲清现状、价值与边界），结尾自然过渡到"争取下一阶段资源"
  - 内容抽象层级：不展示代码与模块清单、不点名具体 embedding 模型名等技术细节，只讲原理与功能（为什么需要两路检索、为什么要融合与重排、反馈如何改变结果、为什么当前规模不需要重型向量数据库），确保非技术听众能跟上
  - 叙事方案：A"问题 → 机制 →闭环"（讲清语义召回、字面召回、RRF 融合、结构化约束、反馈重排、结果解释，最后落到业务价值、边界与资源路线图），并用一个匿名的"蓝牙连接失败"案例贯穿全程作为理解锚点
- **视觉方向确定**：方案 A「工程手记」风格——暖灰底、炭黑正文、青绿表示检索链路、橙色标出关键判断；不使用渐变、发光、口号堆砌、满屏卡片
- **视觉内容清单**（共 16 页）：3 张真实产品 UI 截图、3 张原理信息图（含检索内部原理图、Embedding 语义空间图等）、3 张流程图（业务泳道流程图、反馈学习闭环等）、1 张四层技术架构图、2 张数据图（匿名缺陷对比图、候选结果界面解剖等），每章节至少配一张"视觉主角"而非装饰性 AI 插画
- **设计说明已固化并提交**：[/Users/tonyorz/Data-Agent/docs/superpowers/specs/2026-07-14-duplicate-search-agent-tech-share-deck-design.md](/Users/tonyorz/Data-Agent/docs/superpowers/specs/2026-07-14-duplicate-search-agent-tech-share-deck-design.md)
- 用户批准规格后，助手用 `writing-plans` 技能将制作过程拆解为可验证执行计划（截图采集、16 页生成、讲者备注、内容校验、视觉复验分步进行），再用 `executing-plans` 技能进入实际执行阶段

## 操作要点

- 使用 `skill-installer` 时优先对比 GitHub Star 数与功能完整度（专用生成 `.pptx`、是否含渲染/检查/修复完整工作流）来决策安装哪个技能
- 创意梳理（brainstorm）技能要求先加载可视化协作指南，仅在架构图/流程图/版式对比等"看图更清楚"的节点才打开本地浏览器预览（如 `http://localhost:59282`），文字型需求仍直接文字确认
- 可视化协作流程：每次修改会刷新同一预览地址，用户查看后选择方案或提出调整意见（如"缺少架构图/业务流程图/UI-UX"→"缺少更多图而非文字"→"要更像真实材料的视觉证据而非更多框"）
- 内部信息展示尺度需与用户协商确定（真实模块名/模型/阈值/数据规模 vs. 完全匿名化），最终选择更保守的抽象层级以保证跨角色可理解性
- 设计规格固化为独立文档并单独 git commit，与 PPT 生成解耦，便于用户审阅确认后再进入生产阶段
- 执行阶段需先确认工作区隔离策略（是否用独立 worktree），因为当前分支非 main/master 且存在大量未提交文件；最终产物固定输出到项目 `outputs/` 目录，不影响现有改动

## 踩过的坑

- 安装脚本 ZIP 下载过程中出现 TLS 中断，改用该技能支持的 Git 稀疏检出方式重试，避免影响当前项目
- 生成的设计说明文档存在 Markdown 行尾多余空格，通过修正刚创建文件并 amend 单文件提交处理，不影响用户其他改动
- 生成的计划文件末尾多出一个空行，同样通过修正单文件提交处理
- 第一版视觉方案确认了"讲什么"（叙事顺序），但漏了"用什么图讲清楚"，需要回退一步补充三组核心视觉（业务泳道流程、技术分层架构、UI/UX 操作与结果界面）
- 补充视觉后用户仍反馈"文字为主、缺少图"，说明单靠增加图表数量（"更多框"）不足以解决问题，需要转向"视觉优先"的真实材料型证据（真实 UI 截图、匿名缺陷对比、语义空间示意等）

## 待解决问题

- 是否允许创建隔离 worktree 进行 PPT 制作（因当前分支非 main/master 且工作区有大量未提交文件），对话结束时该问题尚未得到用户确认答复
- PPT 最终生成、真实 UI 截图采集、渲染检查及视觉复验的具体执行结果（对话中未涉及，流程在最后一轮仍处于"进入执行阶段"节点）
