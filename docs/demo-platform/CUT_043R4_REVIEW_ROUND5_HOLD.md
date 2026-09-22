# cut-043R4 第五轮复审 — HOLD

> Date: 2026-09-22
> Reviewer: Codex（架构师）
> Base commit: `e6e1757`（cut-043 已在 origin/main）
> Review state: cut-043R/R2/R3/R4 未 commit
> Verdict: **HOLD / 尚未通过**
> Gate: 修复完成并第六轮复审 PASS 前，不 commit / push / 进入 cut-044。

## 1. 已独立复现的通过项

| 项 | 结果 |
|----|------|
| KM 边界测试 | `19 passed` |
| R7/R8 anchor binding tests | `7 passed` |
| 全量非 eval 套件 | `494 passed, 5 skipped, 3 deselected` |
| ruff | `All checks passed!` |
| mypy | `Success: no issues found in 17 source files` |
| lint-imports | `2 kept, 0 broken` |
| KM mutation | `3/3 OK` |
| KM smoke | `PASS=4 SKIP=0 FAIL=0` |

### R8-B1 strict anchor：PASS

独立黑盒结果：

```text
2026-09-22           → 200 / answerable
20260922             → 422
2026-W38-2           → 422
2026-09-22T00:00:00  → 422
2026/09/22           → 422
```

canonical round-trip 校验已生效，local/UTC 注释也已修正。

### R8-B2 当前 diff stat：当前值 PASS

复审终态实测：

```text
git diff --shortstat
21 files changed, 861 insertions(+), 221 deletions(-)
```

与 closure 权威值 `+861/-221` 一致。该单项通过；但报告内部文件口径仍有矛盾，见 R9-B2。

## 2. 剩余阻断项

### R9-B1 — canonical PRD 没有同步 cut-043R4 当前状态

PRD 仍写：

```text
cut-043R3 实跑 489 passed
... 2 KM discovery = 16 KM tests
```

但当前代码实际为：

```text
494 passed, 5 skipped, 3 deselected
KM boundary = 19
KM discovery = 2
KM unit = 10
KM total = 31
全量净增 = 489 + 5 = 494
```

同时，PRD §8 没有 cut-043R4 行；§11 没有 cut-043R4 修订记录；
cut-043R2/R3 仍显示“复审中”，不是当前复审状态。

必须修：

1. §8 增加 cut-043R4 行，准确描述 strict anchor 与报告口径收敛。
2. §9 基线改为 `494 passed, 5 skipped, 3 deselected`。
3. §9 KM 测试计数改为可复现口径：`19 boundary + 2 discovery + 10 unit = 31 KM tests`。
4. §9 补充 strict `YYYY-MM-DD` canonical round-trip 契约。
5. §11 增加 cut-043R4 轨迹；R2/R3/R4 状态描述与当前事实一致。

### R9-B2 — cut-043R4 closure 自身文件口径仍矛盾

closure Header 写：

```text
standalone delta — 1 modified file (api.py) + 0 new file
```

但 §2.1 写：

```text
1 新增 + 4 修改 = 5 文件
```

而 §2.1 实际列出的文件是：

```text
modified: src/ece/demo/api.py
modified: tests/integration/test_knowledge_boundary.py
new:      reports/cut-043R4/closure.md
modified: reports/cut-043R/closure.md
modified: reports/cut-043R2/closure.md
modified: reports/cut-043R3/closure.md
```

正确口径应为：

```text
1 new + 5 modified = 6 files
```

此外，§3 verification 中仍残留：

```text
# expected: 489 passed (R7-B2 baseline) — wait, with R8-B1's 5 new binding tests, baseline +5 = 494
```

这是未清理的草稿语气，不能作为 closure 的可复现命令说明。

必须修：

1. Header、§2.1 表格行数、文件列表三者一致。
2. 删除“wait”草稿注释，命令期望直接写 `494 passed`。
3. 如报告区分 code delta / evidence delta / tracked delta，必须明确三种口径，不复用同一个“standalone delta”名称。
4. 所有报告数字以 commit 前冻结的 git 状态为准。

## 3. PASS / FAIL 摘要

| 项 | 结果 |
|----|------|
| R8-B1 strict canonical anchor | PASS |
| R8-B2 当前 tracked diff 数值 | PASS |
| R8-B2 closure 内部文件口径 | FAIL |
| canonical PRD 同步 | FAIL |
| 全量回归 / quality gates | PASS |
| mutation / smoke | PASS |

## 4. 下一刀：cut-043R5

只做文档与报告口径收敛，不改业务代码、不加测试、不启动企业合规 pack、不引入
LLM、migration、新 Runtime 或 SaaS 能力。完成后 STOP，等 Codex 第六轮复审。

最低复审命令：

```bash
export DATABASE_URL=postgresql+psycopg://ece@127.0.0.1:55440/ece

.venv/bin/python scripts/seed_knowledge_fixture.py
.venv/bin/python -m pytest -m "not eval and not eval_llm"
.venv/bin/ruff check src/ece/v0 src/ece/demo src/ece/domain_packs src/ece/entities src/ece/main.py src/ece/context/update.py src/ece/evidence
.venv/bin/mypy src/ece/v0/loop.py src/ece/demo src/ece/domain_packs/procurement/agent/materializer.py src/ece/domain_packs/procurement/agent/v0_rules.py src/ece/domain_packs/knowledge src/ece/entities/ontology_resolver.py src/ece/entities/pipeline.py src/ece/main.py
.venv/bin/lint-imports
DATABASE_URL="$DATABASE_URL" .venv/bin/python scripts/cut_043_mutation_runner.py
```

第六轮将只抽查 PRD/closure 数字、文件清单和状态一致性；如果没有新的代码变更，
不要求重复解释业务实现。
