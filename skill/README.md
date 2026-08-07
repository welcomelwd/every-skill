# Skill

Skill 是可复用的任务方法和执行规范。它描述如何完成一类任务，而不是某一次会话中的临时指令。

## 子类

- [analysis](analysis/README.md)：分析、诊断、对比、审计和决策。
- [development](development/README.md)：编程、测试、重构、代码审查和工程实践。
- [security](security/README.md)：网络安全、逆向、漏洞、固件和模糊测试。
- [operations](operations/README.md)：部署、运维、自动化和故障处理。
- [research](research/README.md)：调研、实验、评估和基准测试。
- [_template](_template/README.md)：新建 Skill 的标准模板。

## Skill 最小结构

~~~text
skill-name/
├── SKILL.md          # 必选：目标、输入、流程、输出和安全边界
├── scripts/          # 可执行脚本
├── config/           # 配置和参数样例
├── references/       # 参考资料、协议或规范
├── assets/           # 模板、静态资源和样例文件
└── tests/            # 测试、评估和回归样例
~~~

## 编写要求

- SKILL.md 必须说明适用范围和不负责的内容。
- 流程要能被另一个 Agent 或开发者复现。
- 工具调用和外部写入必须明确权限、失败处理和回滚方式。
- 需要领域事实时引用 knowledge，不要把大量事实硬编码进步骤。
- 将可运行内容放在 scripts，将验证内容放在 tests。
