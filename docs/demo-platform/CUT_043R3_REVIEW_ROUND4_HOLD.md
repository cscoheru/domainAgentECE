# cut-043R3 第四轮复审 — HOLD

> Date: 2026-09-22
> Reviewer: Codex（架构师）
> Base commit: `e6e1757`（cut-043 已在 origin/main）
> Review state: cut-043R/R2/R3 未 commit
> Verdict: **HOLD / 尚未通过**
> Gate: 修复完成并第五轮复审 PASS 前，不 commit / push / 进入 cut-044。

## 1. 已独立复现的通过项

| 项 | 结果 |
|----|------|
| KM 边界测试，无外部 anchor | `14 passed` |
| KM 边界 + discovery，外部 anchor `2027-01-01` | `16 passed` |
| 全量非 eval 套件 | `489 passed, 5 skipped, 3 deselected` |
| ruff | `All checks passed!` |
| mypy | `Success: no issues found in 17 source files` |
| lint-imports | `2 kept, 0 broken` |
| KM mutation | `3/3 OK` |
| KM smoke | `PASS=4 SKIP=0 FAIL=0` |

R7-B1 的强制覆盖已闭合：外部 `2027-01-01` 无法劫持测试锚点。
R7-B3 的 PRD 三列表格与 KM 计数已修正。

## 2. 剩余阻断项

### R8-B1 — anchor 校验不是严格 `YYYY-MM-DD`

`src/ece/demo/api.py` 目前只调用：

```python
date.fromisoformat(raw_anchor)
```

但 Python 3.12 的 `date.fromisoformat()` 接受多种 ISO 形式，不只是
`YYYY-MM-DD`。独立复现：

```text
ECE_SERVER_TODAY_ANCHOR=20260922
→ 200
reason = “...今日 20260922...”

ECE_SERVER_TODAY_ANCHOR=2026-W38-2
→ 200
reason = “...今日 2026-W38-2...”
```

这些值随后进入字符串比较：

```python
valid_from <= today < valid_to
```

非 canonical 字符串会使有效期判定依赖词法比较，而不是日期语义。错误信息
明确承诺 `YYYY-MM-DD`，实现却接受其它 ISO 形式，契约不一致。

必须修：

1. `date.fromisoformat(raw_anchor)` 后追加 canonical round-trip 校验：

   ```python
   parsed = date.fromisoformat(raw_anchor)
   if parsed.isoformat() != raw_anchor:
       raise HTTPException(status_code=422, ...)
   ```

2. 增加 binding tests，至少覆盖 `20260922` 和 `2026-W38-2`，断言 422。
3. 错误信息、YAML 注释、PRD 契约统一为 strict `YYYY-MM-DD`。

同时修正注释/实现不一致：API 注释写 fallback 是“today's UTC date”，但代码
使用 `date.today()`（local date）。要么改为 `datetime.now(UTC).date()`，
要么如实写 local date。

### R8-B2 — closure 报告仍有互相矛盾的统计与占位符

`reports/cut-043R3/closure.md` 内部不一致：

- Header 写当前 tracked diff `21 files / +682 / -182`。
- §4 R7-B4 证据行写 `21 files / +721 / -221`。
- 多处出现 `B904 from-err fix`，这看起来是编号/文案残缺，不是可审验的 blocker ID。
- Header 说 cut-043R3 standalone delta 是 `2 modified + 1 new`，但 R7-B4 的
  Files 列表又包含 `reports/cut-043R/closure.md` 与
  `reports/cut-043R2/closure.md` 的修改，未纳入 standalone 统计口径。

复审时当前实测为 `21 files / +721 / -221`；这说明 diff 统计会随后续 evidence
regeneration 变化。closure 必须固定测量时点与输入状态。

必须修：

1. 只保留一个当前 tracked diff 数字，并注明执行命令、时间点和是否包含 reviewer-run 后的 evidence。
2. 删除或修正 `B904` 残缺编号。
3. standalone delta 明确列出每个文件；说明未跟踪 report 文件是否计入。
4. R7-B4 的历史数字如果保留，必须放在历史段，不能作为当前验证结果。

## 3. PASS / FAIL 摘要

| 项 | 结果 |
|----|------|
| R7-B1 anchor force override | PASS |
| R7-B2 invalid anchor fail fast（`not-a-date`） | PASS |
| strict `YYYY-MM-DD` canonical form | FAIL |
| R7-B3 PRD 表格与计数 | PASS |
| R7-B4 closure 统计一致性 | FAIL |
| 全量回归 / quality gates | PASS |
| mutation / smoke | PASS |

## 4. 下一刀：cut-043R4

只修 R8-B1–R8-B2，不启动企业合规 pack，不引入 LLM、migration、新 Runtime 或
SaaS 能力。完成后 STOP，等 Codex 第五轮复审。

第五轮额外抽查：

```bash
for raw in 20260922 2026-W38-2 not-a-date; do
  ECE_SERVER_TODAY_ANCHOR="$raw" \
  DATABASE_URL=postgresql+psycopg://ece@127.0.0.1:55440/ece \
  .venv/bin/python - <<'PY'
from fastapi.testclient import TestClient
from ece.main import app
r = TestClient(app).post(
    '/api/v1/demo/scenarios/generate',
    headers={'X-User-Id': 'km-alice'},
    json={'domain': 'knowledge', 'scenario': 'default', 'params': {'policy_id': 'KM-POL-001'}},
)
assert r.status_code == 422, r.text
PY
done
```
