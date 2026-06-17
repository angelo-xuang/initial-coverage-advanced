# initial-coverage-advanced

机构级中文**首次覆盖（深度）研报**生成 skill。对标中泰、华创、东吴、银河等券商深度报告水准，最终交付一份 DOCX（25–45 页、1.5–3 万字、40–70 个图表）。

这是一个 [Claude Code](https://claude.com/claude-code) skill，用于协作迭代研报生成的**方法论**本身。

## 仓库结构

| 文件/目录 | 作用 |
|------|------|
| `SKILL.md` | skill 入口：触发条件、五阶段总览、调用规则 |
| `references/` | 每个阶段的详细做法（阶段 1 公司研究 → 阶段 5 报告组装） |
| `assets/` | 报告模板与版式、研报写作规范、质量检查清单 |

## 五阶段流程

| 阶段 | 名称 | 前置 | 产物 |
|------|------|------|------|
| 1 | 公司研究 | 公司名 / 代码 | 公司研究稿 `.md` |
| 2 | 盈利预测建模 | 能获取财报 | 财务模型 `.xlsx` |
| 3 | 估值与目标价 | 阶段 2 模型 | 估值稿 `.md` + 估值页并入 Excel |
| 4 | 图表生成 | 阶段 1、2、3 | 图表包 `.zip`（PNG + 清单） |
| 5 | 报告组装 | 阶段 1–4 全部 | 研报 `.docx` |

## 本地安装（作为 Claude Code skill 使用）

把本仓库 clone 到 Claude Code 的 skills 目录：

```bash
git clone https://github.com/angelo-xuang/initial-coverage-advanced.git ~/.claude/skills/initial-coverage-advanced
```

之后在 Claude Code 里说"给某公司写一份首次覆盖/深度研报"即可触发。

## 协作迭代

我们迭代的是**研报生成的方法论**（`SKILL.md` + `references/` + `assets/`），不是某一份具体报告。改方法论时：

1. 改对应阶段的 `references/阶段N-*.md`，或 `assets/` 里的规范/模板
2. 用一个真实标的端到端跑一遍验收，确认产物质量
3. commit 时 message 写清改了哪个阶段、解决什么问题
