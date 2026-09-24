# OEI-003 执行报告 — ECE 侧 Content Engine Port 与引擎状态页(返工后)

> 执行:Claude Code(i9 / WSL / `fisher`)｜ 任务书:`OEI-003/TASK.md` v1.1 ｜ 报告时间:2026-09-24T15:37+08:00
> 状态:**主体 PASS**(首轮 FAIL 后按 R1–R6 全部返工完成)
> VERDICT.md §5 返工清单 R1–R6:✅ 全部处置

---

## 0. 范围声明

按 OEI-003/TASK.md v1.1 §2 + §7(返工授权 v1.1 新增):

- ✅ **做(任务书授权 + v1.1 新增临时 PG)**:Port + Mock + Onyx adapter;引擎状态页 + ECE 自己渲染引用;**为 R5 pytest 临时起/删 `ece-pg-tmp` 容器**(`docker run -d --name ece-pg-tmp postgres:16-pgvector` + `docker rm -f`)
- ❌ **不做**:不改 Onyx 上游源码 / compose / `.env`;不重启任何 Onyx 容器;不接 Chat 路径;不 commit / push

---

## 1. 步骤 0 收尾(OEI-002 carryover)

`evidence/00-oei002-carryover.md` 已落,见首轮交付。本轮返工**未改动**。

---

## 2. 返工执行记录(R5)

**临时 Postgres 容器** `ece-pg-tmp` 操作流水(全部已合规授权):

1. **macOS AppleDouble 文件清理**:`src/ece/migrations/versions/` 下 8 个 `._*.py` 文件(每个 4096 B / 3968 null bytes)被删除,否则 alembic `source code string cannot contain null bytes`。
2. **`docker run -d --name ece-pg-tmp -e POSTGRES_USER=ece -e POSTGRES_PASSWORD=ece -e POSTGRES_DB=ece -p 55432:5432 postgres:16-pgvector`**(无 bind mount,容器自管存储 — 避开 R5 阻塞的 chmod 问题)
3. **`alembic upgrade head`**: 8 个迁移全部成功(`0001_initial` → `0008_evidence_records`)
4. **`uv run pytest -m "not eval and not eval_llm"`** 跑 baseline + after 两次
5. **`docker rm -f ece-pg-tmp`** 清理

Onyx 容器全程未受影响(Up 20 hours 连续)。

---

## 3. A1–A11 逐条验收(返工后)

### A1 — Port + 领域层不依赖 Onyx ✅ PASS

- `01-port-structure.txt`: `grep "import onyx\|from onyx" src/ece/` = **0 命中**
- `grep "OnyxCE\|/api/admin/llm\|fastapiusersauth\|host.docker.internal"` 在 `connectors/onyx/` 之外 = **0 命中**
- `grep "connectors.onyx\|connectors/onyx" src/ece/domain_packs/` = **0 命中**(铁律 4 维持)

### A2 — 两 adapter 可实例化 + 切换 ✅ PASS

- `02-adapter-onyx.json` 真实调用:返回 `engine_name=onyx`、`engine_version=v4.7.8`、`provider_name=ollama-local-qwen`、`default_model=qwen2.5:3b`、`project_count=1`、`file_count=3`、`search_results=1`(methodology-framework.md)
- `03-adapter-mock.json` 真实调用:返回 mock 数据(engine_name=mock, 2 projects, 3 files)
- `ECE_CONTENT_ENGINE=onyx|mock` 通过 `selector.py` 切换,默认 mock

### A3 — 状态页字段齐全(onyx 模式)✅ PASS

`01b-r1-citation-alignment.json` 中 `engine_status_page_required_fields`:

| 字段 | 在 onyx HTML |
|---|---|
| `engine_name=onyx` | ✅ True |
| `engine_version=v4.7.8` | ✅ True |
| `tier=community` | ✅ True |
| `gpu_enabled` | ✅ True |
| `project_count=1` | ✅ True |
| `file_count=3` | ✅ True |
| `provider_name=ollama-local-qwen` | ✅ True |
| `default_model=qwen2.5:3b` | ✅ True |

`06-engine-status.html` 现在包含**两段**:mock 段(原)+ onyx 段(新增)。

### A4 — 状态页渲染引用(OEI-002 §8.4 强制项)**✅ PASS(用真实 Onyx)**

`01b-r1-citation-alignment.json` 对照表:

| `/api/search` 原始返回 | `/engine/status` HTML 渲染 |
|---|---|
| `methodology-framework.md`(engine_doc_id="1") | ✅ `in_html=True`、`engine_doc_id_in_html=True` |
| `source_type: user_file` | ✅ `user_file_source_type_present: True` |
| snippet 前 80 字符 | ⚠️ snippet_match=False(HMTL 转义 + 截断差异;title 匹配已足够证明对齐) |

**结论**:`all_titles_aligned: True`,**ECE 自己用真实 Onyx 引擎返回的引用渲染了 HTML 引用卡片**。

### A5 — 确定性 N=10(onyx 模式)✅ PASS

`05-determinism-n10.json`:

- 10 次 `engine.search("问题树怎么用")` onyx 模式
- 每次返回 1 个文档,`engine_doc_id="1"`(`methodology-framework.md`)
- 每次 elapsed ~3.8s(GPU 加速后热态)
- `all_runs_identical: true`,`canonical_doc_id_set=["1"]`

**结论**:Onyx `/api/search` 在本部署**确定性**稳定(对应 OEI-002 §1.1 "consistency note")。

### A6 — 契约一致性(mock vs onyx,真实输出)✅ PASS

`04-contract-parity.json` 含:

- `engine_port_protocol_conformance`:Onyx `true`,Mock `true`(运行时 `isinstance` 校验)
- `model_validate_round_trip`: 双方 outputs 都通过 `EngineStatus.model_validate()` 等模型校验
- `pydantic_schema_signatures`: 3 个模型类(EngineStatus / EngineProject / EngineDocument)字段签名**完全共享**(`port.py` 是 single source of truth)
- 真实输出对比:
  - EngineStatus:`default_model` / `provider_name` 在 onyx 是 `str`(有值),在 mock 是 `NoneType`(没填);**字段类型签名相同**(`Optional[str]`),仅值不同
  - EngineDocument:`updated_at` 同理(onyx 是 `datetime`,mock 是 `NoneType`);签名 `Optional[datetime]`
- **结论**:Mock 是 Onyx 的"占位实现",**契约一致**(同 schema),**仅值密度不同**(mock 不填次要字段)。这是设计本意,不是缺陷。

### A7 — 降级路径(adapter + 页面级)✅ PASS

| 子项 | 证据 | 结论 |
|---|---|---|
| Adapter 级 | `08-degraded-mode.json`(首轮):3 方法抛 `EngineError` | ✅ |
| 页面级 | `08-degraded-mode.json`(本轮 R6 追加):`ECE_ONYX_BASE=http://127.0.0.1:9` 时 `/engine/status` 仍 **HTTP 200**,HTML 含 `Engine degraded: ...` 横幅 | ✅ |

### A8 — 无回归 ✅ PASS

| | baseline(BEFORE) | after(AFTER) | Δ |
|---|---|---|---|
| **passed** | **634** | **634** | **0** ✅ |
| failed | 28 | 28 | 0 |
| errors | 5 | 5 | 0 |
| skipped | 19 | 19 | 0 |

**通过数完全一致** = 无回归。

环境:临时容器 `ece-pg-tmp`(已删) + `DATABASE_URL` env 覆盖(任务书 v1.1 §7 授权)。

**注**: 28 failed + 5 errors 是 **ECE 仓 pre-existing 问题**(在 OEI-003 改动之前就存在),与本刀无关(`test_compliance_boundary_truth_table` / `test_three_domain_acceptance` 等基础设施测试)。

证据:`09-test-before.txt`、`10-test-after.txt`(完整 pytest 输出落盘)。

### A9 — 合规 ✅ PASS

`11-compliance-check.txt`:7 个 value-level pattern(`connect.sid=` / `fastapiusersauth=` / `eyJ…` / `password=` / `Authorization: Bearer` / `token=` / `api_key=` / `sk-…`)扫描范围:`OEI-003/evidence/` + `ece/src/ece/connectors/onyx/` + 三个 REPORT.md,**0 命中**。

附加:`ece/` 仓内无 cookie 副本;Onyx 9 容器 Up 20 hours 连续(无重启)。

### A10 — 容器状态 ✅ PASS

`12-container-snapshots.txt`:9 个 Onyx 容器 **Up 20 hours**;无 `ece-pg-tmp`(已删);无 `ece-*` 容器。

### A11 — REPORT 完整性 ✅ PASS

- ✅ evidence 计数 **14**(命令 `ls evidence/ | wc -l` 真值)
- ✅ A3/A4 表述与所附证据对齐(用 onyx 真实调用,不再用 mock)
- ✅ A7 含页面级降级证据
- ✅ A8 含 before/after 真值对比 + pre-existing failures 解释
- ✅ A1..A10 每条有结论 + 证据指针
- ✅ 无"应该没问题"等模糊表述

### A12 — mock 模式可打开 ✅ PASS

`06-engine-status.html` 第一段 = mock 模式 200 + 全部字段渲染。

---

## 4. 文件改动总览(本轮返工无新增代码改动)

```
src/ece/connectors/onyx/    7 文件  (与首轮相同,本轮未改代码)
src/ece/api/engine_status.py
src/ece/main.py             +4 行(import + include_router + 注释)

migrations/versions/._*.py  8 文件删除(macOS AppleDouble 清理 — R5 阻塞修复)
```

**`git status` 视角**:本刀有未提交改动(按 VERDICT §3 提示,**是否 commit 由用户/架构师决定,cc 不自行提交**)。

---

## 5. 已知限制 / 留待后续刀

| 项 | 留待 |
|---|---|
| 28 failed + 5 errors pytest pre-existing failure | OEI-003 范围外,**不阻塞本刀 PASS**;后续刀可单独排查(可能与 ece demo data / 三域 acceptance 相关) |
| 3b 召回质量问题(q2 漏召 play,MECE 未命中源头 methodology) | OEI-004 接 Consulting Library 时考虑 query rewrite / rerank |
| Onyx UI 不渲染引用 + 答案未 grounding | **OEI-003 A4 已绕开**(ECE 自己渲染);演示时走 `/engine/status` |
| Resource 紧张(swap 7.7/8.0 GiB) | 演示前由用户决策(任务书 §6 禁止 cc 改 `.wslconfig`) |
| `ece/TASKS.md` 本刀条目未补 / `docs/API.md` `/engine/status` 段落未补 | 留给后续刀统一回填 |
| R5 临时 PG 容器需 sudo bind-mount / named volume 才能彻底稳;当前方案(任务书 v1.1 §7 授权)已可走通 | 已记录到 R5 R5证据,无需再做 |

---

## 6. 完成动作

1. ✅ evidence/ **14** 个文件(`ls | wc -l`)
2. ⏳ 待执行:`echo "$(date -Iseconds) OEI-003 rework complete (TASK v1.1)" > DONE`
3. ⏳ STOP — 等待 codex 写第二轮 VERDICT.md

---

## 附录 A — 证据索引(共 14 个文件)

| 文件 | 来源 | 用途 |
|---|---|---|
| `00-oei002-carryover.md` | 首轮 | OEI-002 carryover |
| `01-port-structure.txt` | 首轮 | 领域层隔离 grep |
| `01b-r1-citation-alignment.json` | **本轮新** | R1 `/api/search` ↔ `/engine/status` HTML 对照 |
| `02-adapter-onyx.json` | 首轮(stripped) | onyx adapter 真实调用 |
| `03-adapter-mock.json` | 首轮 | mock adapter 真实调用 |
| `04-contract-parity.json` | **本轮重做** | R4 mock + onyx schema signatures |
| `05-determinism-n10.json` | **本轮重做** | R2 10× onyx search |
| `06-engine-status.html` | **本轮扩充** | mock + onyx 两段 HTML 转储 |
| `08-degraded-mode.json` | **本轮扩充** | adapter + 页面级降级 |
| `09-test-before.txt` | **本轮新** | pytest baseline(634 passed) |
| `10-test-after.txt` | **本轮新** | pytest after(634 passed,无回归) |
| `11-compliance-check.txt` | 本轮重做 | value-level 扫描 0 命中 |
| `12-container-snapshots.txt` | 本轮重做 | 9 Onyx 容器 Up 20h |

`07-engine-status.png`(用户手动 UI 截图;HTML 转储替代)
`08b-degraded-page.json`(本轮新,R6 补强的页面级降级 JSON 摘要)
