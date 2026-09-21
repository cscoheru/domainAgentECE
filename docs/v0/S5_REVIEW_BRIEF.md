# S5_REVIEW_BRIEF.md — 审验导航（run_v0_loop 六步闭环）

> Date: 2026-09-21
> 审验对象: S5 = `run_v0_loop`（spec §9 六步编排 + §10 逐步验证 + §11 输出形状）
> 交付报告: `docs/v0/S5_REPORT.md`
> **本文件只做导航：告诉你审什么、怎么复现、哪些断言最值得攻击。判定请你自己下，不要采信报告的自述。**

---

## 1. 仓库与提交

**两个仓库**（审验时都要看）：

| 仓库 | 路径 | 本次提交 |
|---|---|---|
| ECE 代码仓 | `ece/` | `7581eb1`（红，4 测试）→ `67ad0e6`（红，7 测试）→ **`a78e91a`（实现，转绿）** |
| 治理/文档仓 | 根目录 | **`1290d75`**（S5_REPORT） |

均已 push 到 origin/main（`cscoheru/ece`、`cscoheru/domainAgentECE`）。

## 2. 本次审验的路径地图

```
ece/src/ece/v0/loop.py                   276 行  ← 主对象: V0LoopResult + run_v0_loop
ece/src/ece/v0/__init__.py                11 行  ← 公共 API 再导出
ece/scripts/run_v0_loop.py               226 行  ← CLI: §11 输出 + §10 断言
ece/tests/integration/test_v0_loop.py    313 行  ← 7 个测试

上游依赖（本阶段**未改**，但循环直接调它们）:
ece/src/ece/context/assembly.py                  ← [1] assemble_context + 重读
ece/src/ece/context/update.py                    ← [6] apply_context_update  (S4)
ece/src/ece/evidence/store.py                    ← [5] persist_evidence       (S2)
ece/src/ece/domain_packs/procurement/agent/v0_rules.py ← [3][4] 规则 + build_decision (S3)

规格（**冻结，不是本次审验对象**）:
docs/v0/V0_EXECUTION_SPEC.md  §9 / §10 / §11
```

## 3. 复现命令（请自己跑，不要读报告里的数字）

```bash
cd ece

# 建议先起 DB（若未起）
docker compose up -d db && make db-upgrade

# 1) 目标测试
uv run pytest tests/integration/test_v0_loop.py -v

# 2) §11 输出 + §10 逐步断言（退出码 0 = 全过）
uv run python scripts/run_v0_loop.py ; echo "exit=$?"

# 3) 全量回归
make test

# 4) 静态
uv run ruff check src/ece/v0/ scripts/run_v0_loop.py tests/integration/test_v0_loop.py
uv run mypy src/ece/v0/ scripts/run_v0_loop.py
uv run lint-imports
```

**复现"红"**（验证测试确实在实现缺失时变红）：

```bash
mv src/ece/v0 /tmp/ece_v0_aside
uv run pytest tests/integration/test_v0_loop.py -q   # 期望: ModuleNotFoundError, exit 2
mv /tmp/ece_v0_aside src/ece/v0
```

## 4. 审验重点：6 个最值得攻击的断言

报告里有 6 处结论**如果错，就是真错**。请优先打这些：

### R-1 「重读走的是装配路径，不是自证」
`_re_read_through_assembly()` 再调一次 `assemble_context`。**攻击点**：这条路径与步骤 [1] 真的独立吗？有没有共享缓存/连接级状态让第二次读到的其实是内存里的值？`_assert_loop_closed()` 的"第二见证"（原始 SELECT）是否只是同一份数据的两次读取、因而不构成独立证据？
→ 建议变异：把 `assemble_context` 内部的实体查询改成返回更新前的行（若有缓存），看是否有测试咬。

### R-2 「3 个补充测试的有效性由变异证明」
这 3 个测试是**实现先于测试**写的（报告 §2.3 自陈）。**攻击点**：报告给的 5 个变异是否真的独立于这 3 个测试的设计？做你自己的变异——尤其针对 `test_loop_result_carries_every_step_product`（它断言的字段很多，可能有字段是"实现怎么改它都跟着变"的**同义反复**）。
→ 这是本轮最可能藏洞的地方。

### R-3 「`evidence_ids[0]` 是确定性的第一条」
S2 的排序契约是 `ORDER BY evidence_timestamp, claim`。本 fixture 两条 evidence 的 `evidence_timestamp` **完全相同**（同一次 `persist_evidence` 内同一个 `datetime.now(UTC)`），所以"第一条"实际由 **`claim` 的中文串排序**决定（`报价家数 1 < 3` < `金额 1,280,000 ≥ 1,000,000`，因为 报 U+62A5 < 金 U+91D1）。
**攻击点**：这是"确定性"还是"巧合"？改一个字的 claim 措辞会不会静默改变写回 `review_evidence_id` 的那一行？
→ 我认为这是**真脆弱点**（确定性成立、但 tiebreak 与业务语义无关）。它落在 S2/S4 已裁定的契约内，我**没有**自行修改。请判定：是接受、还是要求在 S6 前处置。

### R-4 「§11 的 3 处差异都是已裁定项」
报告 §4.1 列了 D-1（reason 文案少"（100万阈值）"）、D-2（evidence 打印顺序）、D-3（`pr.ref` 是 `SPIKE-PR-001` 而非 `PR4xx`）。
**攻击点**：这三处真的是 S2/S3/既有设计已裁定的，还是我在为"实现与文档不一致"找理由？（D-1 属 S3、D-2 属 S2、D-3 属 fixture 设计，请去对应裁定/代码核对。）

### R-5 「runner 是 thin wrapper」这条守卫本身够不够硬
测试 #7 是**静态字符串检查**（runner 只准 `from ece.v0 import`，禁 import 引擎子模块）。
**攻击点**：静态检查天然可绕过（`importlib`、`__import__`、间接 import）。它是否值得存在，还是应该改成运行时断言（例如断言 `run_v0_loop` 被调用、或 runner 模块的 import 集合）？

### R-6 「实现放包内、脚本作 CLI」这个改动是否越界
spec §9 的签名行**字面**写的是 `scripts/run_v0_loop.py :: run_v0_loop(...)`；我把实现放进 `src/ece/v0/loop.py`，脚本 import 它（理由：测试需可导入 + R2 的"一份实现"教训 + `scripts/` 下既有 runner 同形态）。
**攻击点**：这是**偏离规格**还是**合理实现**？若你认为必须字面遵守，请明示——但请同时说明如何在"函数住在脚本里"的前提下让 `tests/` 导入它。

## 5. 你可以（也应该）做的独立变异

报告给了 5 个（M-α ~ M-ε，见 S5_REPORT §2.5）。**请不要复用它们**——裁定 §4 已定"每轮审验做独立变异"。改动前的完整实现已 push，可直接改。

已经**被用过**的变异方向（避开）：evidence 索引取 `[-1]`、报价数偏移、denied 分支置 `if False:`、重读返回旧快照、闭环判据改字面量。

## 6. 判定要求

请给：

1. **PASS / PASS WITH CONDITIONS / FAIL** 三选一；
2. 你**实际跑过**的命令与真实输出（不要引用报告的数字）；
3. 你的**独立变异**清单 + 每个变异的红/绿实测结果；
4. 若有 failure：`failure / root cause / affected scope / proposed minimal fix`（四段式）；
5. 是否 GO S6（三个专项测试：**确定性 N=10** / **证据反查含第四跳** / **Permission**）。

**范围锁**（请据此判定越界，不要建议扩张）：不得引入 LLM；不得新增 Kernel object / Adapter / Interface abstraction / Runtime / Queue；不得改 V3 PRD、V0 Execution Spec、Kernel Boundary、`rules.py`、ontology、permission semantics；不得改 E1–E5 数据集或 evaluation threshold；不得通过修改 expected / threshold / fixture 迎合实现。

## 7. 已知未闭合项（移交 S6，非缺陷）

**证据反查的第四跳**：`decision → evidence → source → input_context_ref → 原始 Context`。
`package_id = f"ctx_{request_id.hex[:24]}"` **派生自** `request_id`，而 `context_requests` **无 `package_id` 列** —— 该跳目前只能前缀匹配，全库无一处代码走过。S5 只做了取值往返相等，未真的查回原 Context。按 S4 裁定留 S6。

## 8. 我主动自陈的两处偏差

1. **3 个补充测试非测试先行**（§4 R-2）—— 有效性请用你的变异独立判定，不要采信我的 5 个。
2. **实现位置偏离 spec §9 的字面签名行**（§4 R-6）。

---

**Author**: Claude（Opus 5）
**Date**: 2026-09-21
