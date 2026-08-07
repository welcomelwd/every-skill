# 分类规则

## 顶层分类选择

| 内容主要回答的问题 | 放置目录 |
| --- | --- |
| 如何完成一类任务 | skill |
| 如何调用一个外部能力 | mcp |
| 如何组织角色和任务流程 | agent |
| 某个事实、概念、案例或数据是什么 | knowledge |
| 跨多个目录的设计原则或协作约定 | docs |

## Skill 子类

- analysis：诊断、对比、归因、审计和决策分析。
- development：编码、测试、重构、代码审查和工程自动化。
- security：漏洞分析、逆向、固件、模糊测试和威胁建模。
- operations：部署、运维、监控、故障处理和自动化。
- research：资料调研、实验设计、评测和基准测试。

## MCP 子类

- servers：服务端实现、协议适配和生命周期。
- tools：工具函数、参数、返回值和错误模型。
- resources：文件、数据库、API、知识库等资源访问。
- prompts：由 MCP 暴露的可复用 Prompt。
- clients：客户端接入、会话和传输方式。
- security：认证、授权、沙箱、审计和速率限制。
- examples：完整调用样例和最小可运行示例。

## Agent 子类

- roles：职责、边界、角色协作和决策权限。
- workflows：任务状态、步骤、分支、并发、重试和人工确认。
- evaluations：评测数据、指标、基线、回归和失败样例。
- memory：上下文、短期记忆、长期记忆和隐私策略。
- runtimes：模型、容器、工具镜像、资源限制和部署方式。
- prompts：System Prompt、任务 Prompt 和输出协议。

## Knowledge 子类

- security：漏洞、CVE、补丁、PoC、情报和安全机制。
- reverse-engineering：二进制、固件、文件系统、反汇编和仿真。
- protocols：协议、报文、状态机、认证和兼容性。
- products：产品、版本、组件、架构和部署形态。
- tools：工具能力、参数、版本、平台和限制。
- standards：标准、规范、指南和最佳实践。
- cases：分析过程、实验记录、验证结果和复盘。
- datasets：数据集、样本、字段、许可和质量说明。
- glossary：术语、缩写、别名和概念关系。

## 命名与元数据

- 目录和文件名使用小写英文，多个单词使用连字符。
- 每个条目应有唯一、稳定、可读的名称。
- 时间使用 ISO 8601 格式，例如 2026-08-07。
- 外部资料记录 source、source_url、version、updated_at 和 confidence。
- 高风险或敏感内容必须记录 sensitivity、访问限制和脱敏说明。
