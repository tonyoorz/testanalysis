---
title: "学术 Text-to-SQL 系统：CHESS / CHASE-SQL / XiYan-SQL"
type: knowledge
source: "research-doc"
source_file: "智能问数Agent全网深度调研-2026-08-03.md"
compiled_at: 2026-11-11
compiler: zcode-night
tags:
  - compiled-knowledge
---

# 学术 Text-to-SQL 系统：CHESS / CHASE-SQL / XiYan-SQL

> 编译自 [[智能问数Agent全网深度调研-2026-08-03]] §4（L502–545）。证据等级 A/C。

## 核心问题
学术系统的哪些机制值得吸收进 Data-Agent？哪些只适合离线/兜底场景？

## 关键结论

### CHESS：召回/剪枝/候选/单测四角色（§4.1，L507–525）
1. **Information Retriever**：关键词、实体、值召回；预处理用 minhash、LSH、向量索引。
2. **Schema Selector**：从大 schema 选表和列。
3. **Candidate Generator**：生成并迭代修复 SQL。
4. **Unit Tester**：生成自然语言测试并评价候选。
- 源码目录与模块一一对应：`src/workflow/agents/{information_retriever,schema_selector,candidate_generator,unit_tester}`。
- 直接价值（L518–523）：候选召回与最终解析**分开**；大 Ontology 只取 query-relevant 子图；value linking 不用纯子串；端到端 golden 加「期望不变量/反例」。
- 不照搬：四个在线 Agent——Ontology 规模有限，先做确定性 retrieval pipeline + 主 Agent 澄清（L525）。

### CHASE-SQL：多路径候选 + preference selector（§4.2，L527–534）
- 三种路径产生多样候选：divide-and-conquer、基于执行计划的 chain-of-thought、instance-aware synthetic demonstrations；fine-tuned binary selector 两两排序。
- 论文报告当时 BIRD execution accuracy 73.0%（ICLR 2025）。
- 使用条件（L534）：只在「复杂多跳、多个合法解释、普通解析低置信度」的小部分问题触发；平常不付 test-time compute 成本。

### XiYan-SQL：中文时间/值理解、M-Schema、专用模型（§4.3，L536–544）
- 机制：M-Schema 半结构化 schema 表示、多 generator ensemble、ICL + SFT、多候选 refiner/selector；**DateResolver 专门处理中文时间理解**，配专用 QwenCoder 模型；另有 MCP server。
- 注意（L544）：总仓库主要是论文/模型/子项目入口，**不是可直接嵌入的企业 Agent runtime**；价值在中文时间/版本/项目简称解析测试集与 schema representation。

## 操作要点
- 吸收落点（对应 [[60 Knowledge/Concepts/Data-Agent工程路线P0-P1-P2|工程路线]]）：
  - CHESS 召回/剪枝 → P1.2 Value/Schema Linking：BM25/向量只做候选召回，最终选择受类型、scope、capability 校验（L878–880）。
  - CHESS unit test / 不变量 → P0.5 golden 加反例断言。
  - CHASE 多候选 ensemble → P2：仅低置信度复杂问题，且必须由 eval 证明收益大于时延（L907）。
  - XiYan DateResolver → 中文日期窗口解析测试集（项目、OS、PU、模块、版本、phase、日期窗口优先，L880）。
- 与 [[60 Knowledge/Concepts/智能问数行业收敛方向-2026|行业收敛方向]]一致：学术多 Agent/高算力机制不进在线主链路。

## 相关页面
- [[60 Knowledge/Concepts/Agent平台工程参考-Datus-DB-GPT-Vanna|Datus（benchmark 工程）]] · [[60 Knowledge/Concepts/Data-Agent架构基线与代码断点|基线断点 H（评测层级不足）]]
