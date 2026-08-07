# 协作规范

## 新增内容

1. 先根据 docs/TAXONOMY.md 选择顶层目录和子类。
2. 从对应的 _template 复制模板。
3. 填写目标、输入、依赖、来源、输出和验证方式。
4. 在同级 README 中补充必要的导航信息。
5. 检查是否包含敏感信息、失效链接或未说明的外部写入。
6. 提交前执行格式检查和最小可复现验证。

## 命名规范

- Skill 目录：动词或任务名，例如 firmware-unpack、cve-triage。
- MCP 目录：服务或能力名，例如 gh-repository、binary-analysis。
- Agent 目录：角色或场景名，例如 vuln-researcher、firmware-auditor。
- Knowledge 条目：主题名加必要的版本或日期，例如 fortios-7-4、modbus-tcp。
- 不使用空格、中文路径、无意义的 final、new、test2 等名称。

## 文档规范

- README 负责导航和边界，不替代正式条目。
- 正式条目记录来源和更新时间。
- 实验性内容标记状态、环境、样本和已知限制。
- 代码示例保持最小可运行，避免提交真实地址、账号或密钥。
- 结论与推测分开书写；不确定内容必须标注置信度。

## 提交规范

建议使用 Conventional Commits：

- docs：文档和知识整理。
- feat：新增 Skill、MCP、Agent 或 Knowledge。
- fix：修正错误内容或示例。
- refactor：目录和结构调整。
- test：新增评估或验证样例。
- chore：工具和项目配置变更。

## 合并检查清单

- [ ] 目录归类正确。
- [ ] 模板字段已经填写。
- [ ] 来源、版本和更新时间完整。
- [ ] 无敏感信息和无授权数据。
- [ ] 示例可以运行或已说明不能运行的原因。
- [ ] 结果有验证方式或失败边界。
