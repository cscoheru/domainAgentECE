# cut-043R2 第三轮复审 — HOLD

> Date: 2026-09-22
> Reviewer: Codex（架构师）
> Base commit: `e6e1757`（cut-043 已在 origin/main）
> Review state: cut-043R/R2 未 commit
> Verdict: **HOLD / 尚未通过**
> Gate: 修复完成并第四轮复审 PASS 前，不 commit / push / 进入 cut-044。

## 1. 已独立复现的通过项

| 项 | 结果 |
|----|------|
| 全量非 eval 套件，移除外部 anchor | `487 passed, 5 skipped, 3 deselected` |
| ruff | `All checks passed!` |
| mypy | `Success: no issues found in 17 source files` |
| lint-imports | `2 kept, 0 broken` |
| KM mutation | `3/3 OK` |
| KM smoke | `PASS=4 SKIP=0 FAIL=0` |
| KM permission contrast | `km-eve + KM-POL-001 → no_permission / 0 evidence` |
| R5-B2 zero evidence | `km-eve + KM-POL-002 → needs_valid_policy / 0 evidence` |

R6-B3 的功能目标已闭合：permission contrast 与 zero-evidence 两条路径都已保留并实测通过。

## 2. 剩余阻断项

### R7-B1 — 时间锚仍受 ambient env 支配，非法 anchor 不 fail fast

`tests/conftest.py` 使用：

```python
os.environ.setdefault("ECE_SERVER_TODAY_ANCHOR", "2026-09-22")
```

`setdefault` 无法覆盖外部环境。实测：

```bash
ECE_SERVER_TODAY_ANCHOR=2027-01-01 \
  .venv/bin/python -m pytest \
  'tests/integration/test_knowledge_boundary.py::test_knowledge_boundary_truth_table[validity_pass_perm_pass_answerable]'
```

结果：

```text
decision_value='needs_valid_policy' != expected='answerable'
1 failed
```

因此测试仍依赖调用者的 ambient env，不具备可重复性。

同时，`src/ece/demo/api.py` 仍直接读取并使用：

```python
server_today = os.environ.get("ECE_SERVER_TODAY_ANCHOR") or date.today().isoformat()
```

没有 `date.fromisoformat()` 校验。实测：

```text
ECE_SERVER_TODAY_ANCHOR=not-a-date
→ 200 / needs_valid_policy
reason 含“今日 not-a-date”
```

这不是 fail fast，而是把非法配置静默带入业务判定。

必须修：

1. conftest 强制设置 `os.environ["ECE_SERVER_TODAY_ANCHOR"] = "2026-09-22"`，
   或使用 autouse fixture / monkeypatch 强制覆盖；不能 `setdefault`。
2. API 校验 anchor 为严格的 `YYYY-MM-DD` ISO date；建议校验
   `parsed.isoformat() == raw_value`。非法值返回明确 422，不进入规则。
3. 增加 binding tests：
   - ambient `2027-01-01` 不影响测试；
   - ambient `not-a-date` 返回 422；
   - 合法 anchor 正常注入。
4. `date.today()` 注释若声称 UTC，应改用 UTC date；否则如实写 local date。

### R7-B2 — canonical PRD 已更新但结构/轨迹仍不真实

[DEMO_PLATFORM_PRD.md](../../docs/demo-platform/DEMO_PLATFORM_PRD.md:107)
的 cut-043 行变成 4 列：

```markdown
| **cut-043** | ... | ... | ✅ 闭合 (043R) |
```

但 §8 表头只有 3 列。这会破坏 Markdown 表格渲染。

§11 轨迹也不符合实际变更史：

1. `cut-043R` 行声称该刀把 PRD 更新为 `486 passed`，但 cut-043R 实际未改 PRD；
   PRD 更新发生在 cut-043R2。
2. `cut-043R2` 行没有记录本刀实际完成的关键收敛：knowledge 状态、487 基线、
   smoke 4 项、报告口径修正。
3. cut-043R2 当前状态写“⏳ R6 复审中”，但本刀实际处于第三轮/第四轮复审状态；
   若本刀 PASS，commit 前应改为已闭合。

必须修：

1. 修正 §8 为标准 3 列表；状态并入“内容”或“关键产物”列。
2. §11 按实际文件变更史记录：cut-043R 不应声明 PRD 更新；cut-043R2 应完整记录实际收敛。
3. 当前基线、anchor 契约、smoke 数量、cut-043R2 状态彼此一致。
4. 若本轮 PASS，commit 前将 cut-043R2 状态从“复审中”改为“已闭合”。

### R7-B3 — 报告 delta 与实测不符，KM 测试计数口径仍乱

`reports/cut-043R/closure.md` 写 cut-043R delta：

```text
21 files modified, +597 / -221
```

当前可实测 diff 为：

```text
git diff：21 files, +558 / -182
tests/conftest.py 新增 33 行
```

即便计入 conftest，也是约 `22 files, +591 / -182`，不是 `+597 / -221`。
报告声称 R6-B4 已校正，但数字仍不真实。

PRD §9 写：

```text
含 22 KM boundary + 4 个 cut-043R binding test + 1 个 cut-043R2 permission-contrast 恢复
```

这个拆分也与实际测试结构不一致。实际 KM 相关测试是 24 个：

```text
boundary file：12 个
domain discovery：2 个
KM unit：10 个
```

相对 cut-043 closure 的净增是 4 个，不是上述三段相加。

必须修：

1. 用 `git diff --shortstat` / `git diff --numstat` 的真实输出写报告。
2. 明确统计口径：working-tree delta、commit delta、是否含 conftest/report。
3. PRD §9 改成可核对的 KM 测试计数，不使用无法复现的拆分。
4. R2 closure 中所有 PASS 数字必须与实跑输出一致。

## 3. PASS / FAIL 摘要

| 项 | 结果 |
|----|------|
| 全量回归 | PASS |
| ruff / mypy / lint-imports | PASS |
| KM mutation | PASS |
| smoke 4 项 | PASS |
| R6-B3 permission contrast | PASS |
| R6-B2 anchor 固定与校验 | FAIL |
| R6-B1 canonical PRD 收敛 | FAIL |
| R6-B4 报告口径 | FAIL |

## 4. 下一刀：cut-043R3

只修 R7-B1–R7-B3，不启动企业合规 pack，不引入 LLM、migration、新 Runtime 或
SaaS 能力。完成后 STOP，等 Codex 第四轮复审。

最低复审命令：

```bash
export DATABASE_URL=postgresql+psycopg://ece@127.0.0.1:55440/ece
unset ECE_SERVER_TODAY_ANCHOR

.venv/bin/python scripts/seed_knowledge_fixture.py
.venv/bin/python -m pytest -m "not eval and not eval_llm"
.venv/bin/ruff check src/ece/v0 src/ece/demo src/ece/domain_packs src/ece/entities src/ece/main.py src/ece/context/update.py src/ece/evidence
.venv/bin/mypy src/ece/v0/loop.py src/ece/demo src/ece/domain_packs/procurement/agent/materializer.py src/ece/domain_packs/procurement/agent/v0_rules.py src/ece/domain_packs/knowledge src/ece/entities/ontology_resolver.py src/ece/entities/pipeline.py src/ece/main.py
.venv/bin/lint-imports
DATABASE_URL="$DATABASE_URL" .venv/bin/python scripts/cut_043_mutation_runner.py
```

第四轮额外抽查：

```bash
ECE_SERVER_TODAY_ANCHOR=2027-01-01 .venv/bin/python -m pytest \
  tests/integration/test_knowledge_boundary.py

ECE_SERVER_TODAY_ANCHOR=not-a-date .venv/bin/python - <<'PY'
from fastapi.testclient import TestClient
from ece.main import app
r = TestClient(app).post(
    '/api/v1/demo/scenarios/generate',
    headers={'X-User-Id': 'km-alice'},
    json={'domain': 'knowledge', 'scenario': 'default', 'params': {'policy_id': 'KM-POL-001'}},
)
assert r.status_code == 422, r.text
PY
```
