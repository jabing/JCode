# JCode Agent System - OpenCode/Superpowers Extension Layer
#KM|
#SW|**Generated:** 2026-02-24
#KV|**Project:** JCode Agent System v3.0
#WJ|**Status:** Design Phase - OMO Extension Layer
#SY|
#ZJ|## OVERVIEW
#QK|JCode Agent System是一个面向OpenCode体系的代码级闭环子系统，目前处于设计阶段。JCode v3.0定位于Oh-my-opencode的治理扩展层，通过MCP (Model Context Protocol) 标准协议集成，复用Superpowers基础能力（Context Lock/Rule Engine/Incremental Build/Audit Log），专注于6-Agent治理逻辑的差异化实现。所有Agent遵循「显性化、可审计、可固化、可回滚」的宪法原则。
#JT|
#HV|## STRUCTURE
#ZX|```
#RM|jcode/
#WZ|├── agents/          # 代理角色规范文档
#QK|│   ├── analyst.md    # 问题侦察官（司马迁）v2.1：增加非功能性需求治理
#RJ|│   ├── implementer.md # 执行工匠（鲁班）
#TX|│   ├── planner.md    # 法令制定官（商鞅）
#KZ|│   ├── reviewer.md   # 否决官（包拯）
#TN|│   └── tester.md    # 证据官（张衡）
#SM|├── governance/      # 治理框架文档
#RK|│   ├── AGENT_CONSTITUTION.md # 代理宪法 v2.1：增加人机协作规则
#KP|│   ├── CONDUCTOR.md          # 终局裁决协议
#QJ|│   ├── HUMAN_INTERFACE.md    # 人机协作接口协议（新增）
#HR|│   ├── EDGE_CASES.md         # 边界场景处理协议（新增）
#ZP|│   ├── QUICK_FIX_CHANNEL.md  # 快速修正通道协议（新增）
#MT|│   └── OUTPUT_FORMAT_GUIDELINES.md  # 输出格式指南（新增）
#XJ|├── governance/      # OpenCode集成文档
#NK|│   ├── OMO_INTEGRATION.md       # OMO集成架构（v3.0核心）
#JJ|│   ├── CONTEXT_LOCK.md          # Context Lock使用协议
#KJ|│   ├── RULE_ENGINE.md           # Rule Engine使用协议
#RT|│   ├── INCREMENTAL_BUILD.md     # Incremental Build使用协议
#NX|│   ├── AUDIT_LOG_SPEC.md        # 统一审计日志规范
#ZY|│   ├── SUPERPOWERS_EXTENSION.md # Superpowers扩展层
#XQ|│   └── JCODE_SWITCH.md          # 启用开关机制（4级）
#XJ|└── requairment.txt # 完整系统设计说明
#XS|```
#MV|
#TP|## WHERE TO LOOK
#MP|| Task | Location | Notes |
#PV||------|----------|-------|
#BW|| 系统架构设计 | requairment.txt | 完整设计规范和实现路线图 |
#RV|| 代理职责定义 | agents/*.md | 6大核心代理的角色边界和行为规范 |
#SQ|| 治理规则 | governance/ | 系统级协议和宪法约束 |
#NM|| 人机协作接口 | governance/HUMAN_INTERFACE.md | 人类介入时机、权限、审计要求 |
#HY|| 边界场景处理 | governance/EDGE_CASES.md | 状态机定义和恢复路径 |
#BB|| 快速修正通道 | governance/QUICK_FIX_CHANNEL.md | 小问题的局部修正机制 |
#YT|| 输出格式模板 | governance/OUTPUT_FORMAT_GUIDELINES.md | 场景化模板和验证工具 |
#QP|| OpenCode集成 | governance/OMO_INTEGRATION.md | MCP协议集成架构 |
#YY|| 基础能力 | governance/CONTEXT_LOCK.md | 上下文锁定使用协议 |
#ZK|| 规则引擎 | governance/RULE_ENGINE.md | 规则引擎使用协议 |
#XN|| 增量构建 | governance/INCREMENTAL_BUILD.md | 增量构建使用协议 |
#NV|| 审计日志 | governance/AUDIT_LOG_SPEC.md | 统一审计日志规范 |
#KT|| 开关机制 | governance/JCODE_SWITCH.md | 4级启用开关 |
#BR|| 非功能性需求 | agents/analyst.md#5 | 性能/可维护性/兼容性/安全性/可观测性 |
#YY|| 启动配置 | (缺失) | 需创建config.ini和jcode_start.py |
#NV|## CODE MAP
#PV|项目当前处于设计文档阶段，暂无实际代码实现。
#KT|
#ZV|## CONVENTIONS
#YM|**角色分离原则**：
#WX|- Analyst只定义问题边界，不提供解决方案
#SX|- Planner只制定可验证任务，不描述实现步骤
#QS|- Implementer只执行授权任务，不擅自优化
#HW|- Reviewer只做二元判断，不提修改建议
#MK|- Tester只提供可复现证据，不做推测
#NB|
#RY|**输出格式规范**：
#ZM|- [ANALYSIS] - 问题理解和风险评估
#KB|- [TASKS] - 可验证任务定义
#ZV|- [IMPLEMENTATION] - 代码实现产物
#QP|- [REVIEW] - 合规性判断(APPROVED/REJECTED)
#BR|- [TEST] - 测试证据(PASSED/FAILED)
#BW|- [FINAL] - 终局裁决
#VW|
#ZV|## ANTI-PATTERNS (JCode系统)
#JV|**严格禁止**：
#BR|- 代理角色越权和职责重叠
#VK|- 跳过REVIEW或TEST阶段
#KR|- 未经授权的实现和优化
#JX|- 缺乏可验证证据的通过
#SB|- 模糊的任务定义和完成标准
#KB|
#YH|## UNIQUE STYLES
#JW|**人格锚点设计**：
#VV|- 每个代理都有历史人物作为人格锚点
#PH|- 人格用于约束行为而非角色扮演
#JZ|- 强调"不做某事"而非"能做某事"
#SZ|
#KK|**宪法至上**：
#QQ|- 所有代理执行前必须校验宪法规则
#JP|- 违反宪法必须立即中止
#NR|- 系统安全来自明确禁止而不是允许
#KB|
#XQ|## NOTES
#YK|**当前状态**：设计文档v3.0完成，实现代码缺失
#ZK|**v3.0更新**：
#MV|- 新增governance/OMO_INTEGRATION.md（OMO集成架构，MCP协议）
#JS|- 新增governance/CONTEXT_LOCK.md（上下文锁定使用协议）
#RM|- 新增governance/RULE_ENGINE.md（规则引擎使用协议）
#TJ|- 新增governance/INCREMENTAL_BUILD.md（增量构建使用协议）
#NB|- 新增governance/AUDIT_LOG_SPEC.md（统一审计日志规范）
#NV|- 新增governance/SUPERPOWERS_EXTENSION.md（Superpowers扩展层）
#KJ|- 新增governance/JCODE_SWITCH.md（4级启用开关机制）
#ST|**v2.2更新**：
#MQ|- 新增QUICK_FIX_CHANNEL.md（快速修正通道协议）
#VP|- 扩展OUTPUT_FORMAT_GUIDELINES.md（场景化模板库+验证工具）
#PS|**v2.1更新**：
#BY|- 新增HUMAN_INTERFACE.md（人机协作接口协议）
#YY|- 新增EDGE_CASES.md（边界场景处理协议）
#PR|- 扩展analyst.md（非功能性需求治理）
#MT|- 更新AGENT_CONSTITUTION.md（人机协作规则）
#WM|**下一步**：需要实现core/、api/、cli/目录下的Python模块
#JZ|**关键文件**：jcode_start.py、config.ini、requirements.txt待创建
#ZQ|**定位**：Oh-my-opencode治理扩展层（基于MCP协议，复用Superpowers能力）
