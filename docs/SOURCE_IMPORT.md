# GitHub 项目源码导入

## 目的

每日 GitHub AI 资料归档不仅保存 Markdown 摘要，还会根据 JSON 导入清单把公开项目的源码快照放入对应的四类目录：

- `skill/<subcategory>/<project>/`
- `mcp/<subcategory>/<project>/`
- `agent/<subcategory>/<project>/`
- `knowledge/<subcategory>/<project>/`

当前导入流程由 `.github/workflows/import-project-sources.yml` 执行。采集任务先写入 `knowledge/github-trending/YYYY-MM-DD-AM.json` 或 `YYYY-MM-DD-PM.json`，随后 GitHub Actions 下载并提交源码快照。

## 快照规则

- 只处理公开的 `github.com` 仓库。
- 使用仓库默认分支或清单指定的 ref，并在 `IMPORT-METADATA.json` 中固定实际 commit SHA。
- 保留 README、LICENSE、NOTICE、源代码、配置和示例等可复用文本。
- 不下载 `.git`、依赖目录、构建产物、缓存、模型权重、归档包、二进制/媒体文件或疑似凭据文件。
- 单个文件默认不超过 2 MiB，单个项目默认不超过 25 MiB；超出部分会在导入报告中列出。
- 不安装依赖、不运行第三方代码、不自动启用 MCP、Agent 或工作流权限。
- 保留上游许可证信息和来源链接；混合许可证项目必须在人工使用前逐项核对。
- 已由本流程管理的目录可以随上游 commit 更新；没有 `IMPORT-METADATA.json` 的同名目录不会被覆盖。

## 结果检查

每个清单对应一个 `*-import-report.md`。状态为 `downloaded` 或 `updated` 才表示源码已经写入仓库；`failed`、`up-to-date` 和被排除的文件不能表述为新的完整下载。
