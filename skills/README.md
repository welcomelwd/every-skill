# Skills 目录

所有可复用的 AI 项目技能统一放在 `skills/<skill-name>/` 下。

## 推荐结构

```text
skills/
├── README.md
├── <skill-name>/
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   ├── assets/
│   └── tests/
└── _template/
```

## 约定

- 每个技能目录必须包含 `SKILL.md`。
- `SKILL.md` 描述技能目标、输入、执行流程、输出和验证方式。
- 可执行脚本放在 `scripts/`，参考资料放在 `references/`，模板和静态资源放在 `assets/`。
- 技能应尽量自包含、可复用，并明确依赖和安全边界。
- 不要提交密码、Token、私钥、真实业务数据或其他敏感信息。
- 新技能可以从 `_template/` 复制后再按实际用途修改。
