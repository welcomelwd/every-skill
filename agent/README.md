# Agent

Agent 目录用于整理智能体的角色、工作流、评估、记忆、运行时和提示词。

## 子类

- [roles](roles/README.md)：角色职责、能力边界和决策权限。
- [workflows](workflows/README.md)：任务流、状态、分支、并发和重试。
- [evaluations](evaluations/README.md)：评测集、指标、基线和回归结果。
- [memory](memory/README.md)：短期记忆、长期记忆和上下文策略。
- [runtimes](runtimes/README.md)：模型、容器、工具镜像和资源限制。
- [prompts](prompts/README.md)：System Prompt、任务 Prompt 和输出协议。
- [_template](_template/README.md)：新建 Agent 的模板。

## Agent 设计原则

- 角色边界清晰，避免一个 Agent 承担互相冲突的权限。
- Skill、MCP 和 Knowledge 通过引用组合，不重复复制正文。
- 工作流明确成功条件、异常路径、重试策略和人工确认点。
- 高风险操作默认只读或隔离，结果必须保留证据。
- 用 evaluations 记录效果，不只依赖主观感受。
