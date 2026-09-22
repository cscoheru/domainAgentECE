# cut-043R 第二轮复审 — HOLD

> Date: 2026-09-22
> Reviewer: Codex（架构师）
> Base commit: `e6e1757`（cut-043 已在 origin/main）
> Review state: cut-043R 当前未 commit，工作区 `21 files changed, +497 / -186`
> Verdict: **HOLD / 尚未通过**
> Gate: 修复完成并第三轮复审 PASS 前，不 commit / push / 进入 cut-044。

## 1. 已确认闭合的功能 blocker

### R5-B1 — server-owned temporal anchor：功能闭合

独立黑盒结果：

```text
X-User-Id=km-alice
policy_id=KM-POL-002
today=2024-06-01
→ 422
```

不携带 `today` 时，`ECE_SERVER_TODAY_ANCHOR=2026-09-22` 下：

```text
KM-POL-002 + km-alice → needs_valid_policy / 1 evidence
```

客户端无法再用请求参数回溯日期。

### R5-B2 — 双失败零证据路径：功能闭合

独立黑盒结果：

```text
X-User-Id=km-eve
policy_id=KM-POL-002
→ 200 / needs_valid_policy / 0 evidence
```

不再 500。

### R5-B3 — ontology resolver 注册方向：架构闭合

`src/ece/entities/ontology_resolver.py` 已无 `ece.domain_packs.*` import；
procurement / knowledge 改为在 pack 侧注册；unknown prefix fail-closed。

严格 mypy 已通过：

```text
Success: no issues found in 17 source files
```

`lint-imports`：

```text
Domain pack isolation KEPT
Engine core isolation KEPT
Contracts: 2 kept, 0 broken
```

### R5-B4 — root / identity 参数契约：功能闭合

独立黑盒结果：

```text
policy_id + root_source_id override → 422
X-User-Id=km-eve + employee_id=km-bob → 仍按 km-eve 判定，不提权
```

## 2. 本轮独立实跑结果

| 项 | 结果 |
|----|------|
| 全量非 eval 套件，`ECE_SERVER_TODAY_ANCHOR=2026-09-22` | `486 passed, 5 skipped, 3 deselected` |
| KM 关键集合 | `23 passed` |
| ruff | `All checks passed!` |
| mypy | `Success: no issues found in 17 source files` |
| lint-imports | `2 kept, 0 broken` |
| KM mutation | `3/3 OK` |
| KM smoke | `PASS=3 SKIP=0 FAIL=0` |

## 3. 剩余阻断项

### R6-B1 — R5-B5 仍未闭合：canonical PRD 没有更新

根仓 [DEMO_PLATFORM_PRD.md](../../docs/demo-platform/DEMO_PLATFORM_PRD.md) 仍写：

```text
Domain Packs: procurement ✅ · knowledge ⬜(043) · compliance ⬜(044)
```

§9 仍把 `463 passed` 当作当前验收计数。cut-043R 报告声称把 PRD 更新推迟到
cut-044 启动前，但这正是第一轮 R5-B5 明确要求本刀收敛的内容。

必须修：

1. `knowledge` 状态改为已实现，且与实际代码一致。
2. 当前基线更新为 cut-043R 修完后的可复现计数。
3. 补充 server-owned temporal anchor 与 zero-evidence allowlist 两个已生效契约。
4. 修订记录写入 §11，不新增与正文冲突的旧契约。

### R6-B2 — KM 时间锚测试会随时间漂移；anchor 未校验

测试定义了：

```python
SERVER_TODAY = "2026-09-22"
```

但没有把该值注入 `ECE_SERVER_TODAY_ANCHOR`。API 实际 fallback 到
`date.today()`。我用未来锚点复现：

```bash
DATABASE_URL=... ECE_SERVER_TODAY_ANCHOR=2027-01-01 \
  .venv/bin/python -m pytest \
  'tests/integration/test_knowledge_boundary.py::test_knowledge_boundary_truth_table[validity_pass_perm_pass_answerable]'
```

结果：

```text
decision_value='needs_valid_policy' != expected='answerable'
1 failed
```

也就是说，KM fixture 在 2026-12-31 后，不加显式环境变量的常规测试会自然变红。
这违反可重复验证要求。

另外，`ECE_SERVER_TODAY_ANCHOR` 直接进入字符串比较，未校验 ISO date。错误配置
不会越权放行，但会静默把所有制度判为无效。

必须修：

1. KM integration tests 使用 autouse fixture / monkeypatch 固定
   `ECE_SERVER_TODAY_ANCHOR=2026-09-22`。
2. 不依赖测试机器当前日期。
3. API 读取 anchor 时用 `date.fromisoformat()` 校验；非法值返回明确启动/请求错误，
   不得静默参与字符串比较。
4. 注释如写 UTC，应使用 UTC date；否则改为 local date，保证说明与实现一致。

### R6-B3 — KM permission 反差 smoke 被替换，而不是扩展

原 cut-043 smoke 覆盖：

```text
km-eve + KM-POL-001 → no_permission / 0 evidence
```

cut-043R 把该用例改成：

```text
km-eve + KM-POL-002 → needs_valid_policy / 0 evidence
```

这覆盖了新的 R5-B2 路径，但丢掉了 PRD §7 要求的 Permission Before Intelligence
黑盒反差路径。功能仍存在——我实测 `km-eve + KM-POL-001` 仍返回
`no_permission`——但 smoke 证据不再锁住它。

必须修：

1. smoke 恢复 `no_permission` 检查。
2. 保留 `needs_valid_policy / 0 evidence` 检查。
3. smoke 变为 `PASS=4 SKIP=0 FAIL=0`。
4. 报告同步更新为 4 项。

### R6-B4 — 报告口径仍有错误

closure 报告 §5.4 写：

```text
cut-043: 12 新 + 3 改 = 15 文件
累计: 12 新 + 24 改 = 25 文件
```

但 `e6e1757` 实际是：

```text
19 files added
6 files modified
25 files changed
```

虽然累计总数 25 对上，但构成仍不真实。报告还把当前 smoke 描述为 3 项；
按 R6-B3 修复后应为 4 项。

必须修：

1. 报告改用 `git diff --name-status` 的真实 added/modified 计数。
2. smoke 预期和实测更新为 4 项。
3. 所有“PASS”结论只在证据生成后写。

## 4. PASS / FAIL 摘要

| 项 | 结果 |
|----|------|
| R5-B1 temporal authority 功能 | PASS |
| R5-B2 double-failure zero evidence 功能 | PASS |
| R5-B3 resolver isolation + mypy | PASS |
| R5-B4 route / identity contract 功能 | PASS |
| R5-B5 canonical PRD / reporting | FAIL |
| 测试时间稳定性 | FAIL |
| permission 反差 smoke 覆盖 | FAIL |
| 功能回归 / mutation | PASS |

## 5. 下一刀：cut-043R2

只修 R6-B1–R6-B4，不启动企业合规 pack，不引入 LLM、migration、新 Runtime 或
SaaS 能力。完成后 STOP，等 Codex 第三轮复审。

最低复审命令：

```bash
export DATABASE_URL=postgresql+psycopg://ece@127.0.0.1:55440/ece
export ECE_SERVER_TODAY_ANCHOR=2026-09-22

.venv/bin/python scripts/seed_knowledge_fixture.py
.venv/bin/python -m pytest -m "not eval and not eval_llm"
.venv/bin/ruff check src/ece/v0 src/ece/demo src/ece/domain_packs src/ece/entities src/ece/main.py src/ece/context/update.py src/ece/evidence
.venv/bin/mypy src/ece/v0/loop.py src/ece/demo src/ece/domain_packs/procurement/agent/materializer.py src/ece/domain_packs/procurement/agent/v0_rules.py src/ece/domain_packs/knowledge src/ece/entities/ontology_resolver.py src/ece/entities/pipeline.py src/ece/main.py
.venv/bin/lint-imports
DATABASE_URL="$DATABASE_URL" ECE_SERVER_TODAY_ANCHOR="$ECE_SERVER_TODAY_ANCHOR" .venv/bin/python scripts/cut_043_mutation_runner.py
```

第三轮额外抽查：

1. 不设置外部 anchor 时，KM 测试仍必须固定通过。
2. `ECE_SERVER_TODAY_ANCHOR=not-a-date` 必须 fail fast / 422，不能静默比较。
3. smoke 必须同时覆盖 `no_permission` 与 `needs_valid_policy / 0 evidence`。
4. canonical PRD 的 KM 状态与测试基线必须和实跑一致。
