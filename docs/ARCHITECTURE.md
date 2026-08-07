# 架构说明

## 总体关系

~~~mermaid
flowchart LR
    K[Knowledge 知识] --> A[Agent 智能体]
    S[Skill 方法] --> A
    M[MCP 工具] --> A
    A --> R[结果与案例]
    R --> K
    R --> E[Evaluation 评估]
~~~

## 四层职责

### Skill：方法层

Skill 描述完成一类任务所需的稳定方法，包括前置检查、执行步骤、工具规范、输出格式、验证方式和安全边界。Skill 不应绑定某个具体 Agent 的临时状态。

### MCP：能力层

MCP 描述 Agent 可以调用的外部能力。一个 MCP 条目应明确 Server、Tool、Resource 或 Prompt 的接口、参数、权限、错误处理和兼容性。

### Agent：编排层

Agent 负责理解任务、选择 Skill、读取 Knowledge、调用 MCP、管理状态和生成结果。Agent 文档需要明确角色边界、工作流分支、模型策略和人工确认点。

### Knowledge：上下文层

Knowledge 保存 Agent 和 Skill 所需的领域事实、案例、标准、数据和引用。Knowledge 应尽量与执行逻辑解耦，并标记来源、时间、可信度和敏感级别。

## 推荐执行链路

1. 接收任务并判断任务类型。
2. 检索相关 Knowledge，确认事实和约束。
3. 选择一个或多个 Skill，确定执行计划。
4. 根据 Skill 所需能力选择 MCP 工具或资源。
5. Agent 按工作流执行，记录输入、调用、输出和异常。
6. 通过 Evaluation 或人工复核验证结果。
7. 将通用经验沉淀到 Knowledge、Skill 或案例目录。

## 依赖方向

- Knowledge 可以被 Skill 和 Agent 引用。
- Skill 可以声明所需的 MCP 和 Knowledge。
- MCP 提供能力，不应隐式改变 Agent 的决策逻辑。
- Agent 可以组合前三类资产，但不应把大量静态知识直接复制到 Prompt 中。
- Evaluation 结果可以反向推动 Skill、Agent 和 Knowledge 的迭代。
