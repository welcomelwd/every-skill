# MCP

MCP 目录用于整理 Model Context Protocol 相关的服务、工具、资源、Prompt、客户端和安全规范。

## 子类

- [servers](servers/README.md)：MCP Server 实现、适配和生命周期。
- [tools](tools/README.md)：Tool 名称、描述、输入 Schema、返回值和错误模型。
- [resources](resources/README.md)：文件、数据库、API、知识库等资源。
- [prompts](prompts/README.md)：MCP Prompt 定义和参数。
- [clients](clients/README.md)：客户端接入、会话和传输。
- [security](security/README.md)：认证、授权、沙箱、审计和速率限制。
- [examples](examples/README.md)：最小可运行或完整调用示例。
- [_template](_template/README.md)：新建 MCP 资产的模板。

## 登记要求

每个 MCP 资产至少说明：

- 服务或能力的用途和版本。
- 输入、输出、错误和超时行为。
- 需要的凭据、网络、文件和系统权限。
- 对外部系统的读写影响。
- 本地运行、测试和回滚方法。
