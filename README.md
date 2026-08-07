# every-skill

面向 AI 项目的能力与资料库，用于沉淀可复用的 Skill、MCP、Agent、Knowledge，以及它们之间的组合方式。

## 项目定位

这个仓库不只是保存提示词或代码片段，而是把 AI 项目中可复用的四类资产统一管理：

- Skill：解决某类问题的方法、步骤、工具规范和输出格式。
- MCP：可被 Agent 调用的工具、资源、Prompt 和服务适配。
- Agent：角色定义、任务流程、模型策略、记忆和评估方案。
- Knowledge：产品、协议、安全、工具、案例和数据等领域知识。

四类资产的关系是：

Knowledge 提供上下文，Skill 规定方法，MCP 提供执行能力，Agent 负责按任务组合并运行它们。

## 目录结构

~~~text
every-skill/
├── skill/                         # 可复用的任务方法与执行规范
│   ├── analysis/                  # 分析、诊断、对比和决策
│   ├── development/               # 编程、测试、重构和工程实践
│   ├── security/                  # 网络安全、逆向、漏洞和模糊测试
│   ├── operations/                # 部署、运维、自动化和故障处理
│   ├── research/                  # 调研、实验、评估和基准测试
│   └── _template/                 # 新建 Skill 的标准模板
├── mcp/                           # MCP 服务、工具、资源和协议资料
│   ├── servers/                   # MCP Server 实现与适配
│   ├── tools/                     # Tool 定义和输入输出 Schema
│   ├── resources/                 # Resource 数据源和读取规范
│   ├── prompts/                   # MCP Prompt 定义
│   ├── clients/                   # MCP Client 接入方式
│   ├── security/                  # 权限、隔离、审计和安全边界
│   ├── examples/                  # 可运行或可参考的示例
│   └── _template/                 # 新建 MCP 资产的模板
├── agent/                         # Agent 角色、编排、运行时和评估
│   ├── roles/                     # 角色职责和能力边界
│   ├── workflows/                 # 多步骤任务流和编排图
│   ├── evaluations/               # 评测集、指标和回归结果
│   ├── memory/                    # 会话记忆、长期记忆和上下文策略
│   ├── runtimes/                  # 模型、容器、资源和运行环境
│   ├── prompts/                   # System Prompt 和提示词片段
│   └── _template/                 # 新建 Agent 的模板
├── knowledge/                     # 可检索、可引用的领域知识
│   ├── security/                  # CVE、漏洞、补丁、PoC 和威胁情报
│   ├── reverse-engineering/       # 固件、二进制和逆向分析
│   ├── protocols/                 # 协议、报文和状态机
│   ├── products/                  # 产品、版本和组件信息
│   ├── tools/                     # 工具能力、参数和兼容性
│   ├── standards/                 # 标准、规范和最佳实践
│   ├── cases/                     # 分析案例、复盘和验证记录
│   ├── datasets/                  # 数据集、样例和数据说明
│   ├── glossary/                  # 术语、缩写和概念索引
│   └── _template/                 # 新建 Knowledge 条目的模板
├── docs/                          # 项目架构、分类和协作说明
├── PROJECT.md                     # 项目目标、边界和生命周期
└── .gitignore
~~~

## 推荐使用流程

1. 在 knowledge 中补充任务所需的事实、背景和引用来源。
2. 在 skill 中描述稳定、可复用的分析或执行方法。
3. 在 mcp 中登记 Agent 需要调用的工具和资源。
4. 在 agent 中组合角色、Skill、MCP 和 Knowledge。
5. 在 agent/evaluations 和 knowledge/cases 中记录验证结果与经验。
6. 将成熟内容从模板或实验目录移动到正式分类下。

## 目录入口

- [Skill 目录说明](skill/README.md)
- [MCP 目录说明](mcp/README.md)
- [Agent 目录说明](agent/README.md)
- [Knowledge 目录说明](knowledge/README.md)
- [项目说明](PROJECT.md)
- [架构说明](docs/ARCHITECTURE.md)
- [分类规则](docs/TAXONOMY.md)
- [协作规范](docs/CONTRIBUTING.md)

## 基本约定

- 目录名使用小写英文和连字符，例如 reverse-engineering。
- 每个正式分类目录至少包含一个 README.md，说明内容边界和使用方式。
- 技能入口文件统一使用 SKILL.md；Agent、MCP 和 Knowledge 使用对应模板中的元数据格式。
- 资料必须标明来源、更新时间、可信度和敏感级别；不能提交密码、Token、私钥或真实业务敏感数据。
- 能被复用的内容优先写成结构化条目，避免只保存无法验证的零散结论。
- 任何外部写入、命令执行、网络访问或高风险操作，都要在文档中明确权限和安全边界。
