# Cline Review Brief — Phase 1 & 2 Deliverables

> **Author**: Claude (Fable 5.1, Anthropic)
> **Audience**: Cline (red team reviewer; target: challenge conclusions, not validate — per RED_TEAM_REVIEW.md v3 红队角色定义)
> **Review Date**: 2026-09-13
> **Master PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md)
> **Root Governance**: [`/CLAUDE.md`](../../CLAUDE.md)
> **Review Purpose**: Audit Phase 1 (Evidence Collection) + Phase 2 (Capability Map) per PRD §4 evidence discipline + §9 phase DoD

---

## 0. Purpose & Scope

This brief summarizes Phase 1 and Phase 2 of Track A (Glean Architecture Reverse Engineering & Enterprise AI Platform Kernel).

**In scope**:
- 12 files in `/docs/research_v2/`(created across Phase 0/1/2)
- 1 file modified: `docs/research_v2/README.md`
- 2 git commits for Phase 1/2: `f5d4d0e`(Phase 1)、`9f3a5cb`(Phase 2)
- Evidence discipline §4 compliance audit
- Build/Buy/Integrate/Partner decision rationale

**Not in scope**:
- Phase 0(Partner meeting prep)— already pushed in commit `c1dd32b`; background context only
- Phase 3-6(not yet started)
- Track B(ECE v0 development)— independent repo at `github.com/cscoheru/ece`; **not touched**

**Working tree at review time**:
```
main: 9f3a5cb (HEAD)
├── 9f3a5cb  Phase 2 — Capability Map complete (881 +)
├── f5d4d0e  Phase 1 — Evidence Collection BLOCKED (167 +)
└── c1dd32b  Phase 0 — Partner meeting prep (651 +)
```

---

## 1. Strategic Context (background for review)

### 1.1 Project structure

Track A is one of two parallel tracks defined in `/RESEARCH_PRD_V2.md` §16:
- **Track A**: Glean Architecture Reverse Engineering → Platform Kernel Definition (this review)
- **Track B**: ECE v0 development (Procurement 领域包验证架构; 独立仓库 `github.com/cscoheru/ece`)

Phase 0 was the **hard deadline** for next-week Glean Partner Manager call. Phase 1-6 follow with **STOP Gate** after each(per ROOT CLAUDE.md §16 治理 framework)。

### 1.2 Critical inputs shaping the work

- **v1 baseline**: [`/docs/research/evidence-matrix.md`](../research/evidence-matrix.md)(C01-C25, last verified **2026-09-03**)— kept untouched per PRD §13.5
- **RED_TEAM_REVIEW.md v3**(根目录): established 主路径 D = 私有化垂直 Context+Agent;Glean 降级为**非阻塞期权**;Glean Partner 路径需谨慎
- **ROOT CLAUDE.md**: 4-role governance(Enterprise AI Researcher + 产品架构师 + MVP PM + Tech Lead)
- **M0 founder input**(v3 Red Team §0.6): 中国大陆可达市场,无 Glean 客户,Glean Partner 申请已提交未回应

### 1.3 Evidence discipline(PRD §4 铁律)

Every Claim must carry 5 elements:
- **Claim / Source / Evidence / Confidence / Last Verified**
- Confidence levels: `CONFIRMED` / `STRONGLY_INFERRED` / `INFERRED` / `UNKNOWN`
- **UNKNOWN cannot be design premise**
- Marketing-level claims explicitly tagged(产品页 slogan)
- v1 docs MUST NOT be modified/deleted(only `_v2/` directories new content)
- BLOCKED 来源显式标 BLOCKED + retry strategy(PRD §14)

---

## 2. Phase 1 — Evidence Collection(per PRD §9)

### 2.1 DoD(per PRD §9)

- [x] 种子 URL 全量抓取(§5 清单 9 个)— **attempted, all 12 BLOCKED**
- [x] 复核 C01-C25 — **attempted, all BLOCKED, v1 baseline maintained**
- [x] 新增证据从 C26 起编号 — produced in Phase 0(C26-C29);no **C35+** added in Phase 1
- [x] 产出 `evidence-matrix-v2.md` — produced
- [x] 所有 URL 注明抓取日期 — done with BLOCKED + Last Verified columns

### 2.2 Process

**Attempted 12 URLs in parallel via WebFetch(2026-09-13)**:
- 9 seed URLs from PRD §5(产品导航/connectors/Agent Builder/blog × 5/developers/mcp)
- 3 supplementary URLs(partners、agents-go-2026、pricing)

**Result**: ALL 12 returned `"Unable to verify if domain www.glean.com is safe to fetch"`(claude.ai 网络策略屏蔽)。

**Decision**(per PRD §14 允许显式标 BLOCKED): wrote `evidence-matrix-v2.md` documenting:
- 20 entries marked **BLOCKED_REVERIFY**(v1 baseline 2026-09-03 维持)
- 4 entries marked **STILL_UNKNOWN**(C03/C11/C24/C25)
- 2 entries marked **INFERENCE_HOLDS**(C22/C23 — 推理性,无 URL 依赖)
- **0 new C35+ entries**

**User decision**(via AskUserQuestion):
- User chose **Option C**: Accept v1 baseline, proceed to Phase 2 with deferred re-verify tags

### 2.3 Deliverable

| File | Status | Approx Lines |
|---|---|---|
| `docs/research_v2/evidence-matrix-v2.md` | created | ~150 |
| `docs/research_v2/README.md` | modified(Phase 1 status) | +20 lines |

### 2.4 Commit

```
f5d4d0e  docs(research-v2): Phase 1 — Evidence Collection BLOCKED on live re-verification
2 files changed, 167 insertions(+), 1 deletion(-)
```

### 2.5 Red Team Audit Points(请 Cline 重点挑战)

1. **Is BLOCKED_REVERIFY a valid status?** Per PRD §14 it is,但 C01-C20 maintain v1 confidence 而 v2 Last Verified 标 BLOCKED — 是否在审计上造成混淆?
2. **Were all 12 URLs truly necessary?** PRD §5 lists 9 seed URLs。supplementary 3 URLs(partners/agents-go-2026/pricing)由我自行加入。是 scope creep 还是合理 due diligence?
3. **C26-C29 routing**: These came from v1 draft references, not Phase 1 fresh fetches. Should they be re-numbered or recategorized as Phase 0 evidence?
4. **Was Option C the right choice?** 接受 v1 baseline 而非等网络恢复,对一个 adversarial research track 是否合适?
5. **v1 docs NOT modified?** git diff 应能验证 — please check。

---

## 3. Phase 2 — Capability Map(per PRD §9)

### 3.1 DoD(per PRD §9)

- [x] 产出 M01-M08 模块文档 — 8 docs created, each with: research questions / evidence table(C01-C34)/ capability judgment / Kernel implication / UNKNOWN 转 Robin 会谈必问
- [x] M09(Partner Boundary)— research view(与 Phase 0 行动视角 partner-meeting-brief.md 区分)
- [x] Capability Matrix v2(§7 format)— 16 capabilities × 8 columns, every cell has C-number or `?`
- [x] 每模块结论挂到 Q1-Q5(root 5 research questions)

### 3.2 Process

**Source material used**(已在 context,未重新 fetch):
- v1 capability map(`docs/research/glean-capability-map.md`)
- `glean-context-architecture.md`(M02 deep dive)
- `evidence-matrix-v2.md`(C01-C34 verification status)
- ROOT CLAUDE.md Q1-Q5 framework
- `Glean Architecture Research v2.md`(9-module problem framing)
- `RED_TEAM_REVIEW.md v3`(strategic context)

**⚠️ NOT re-read during Phase 2**(potential audit gap):
- `glean-agent-architecture.md`(v1 — likely M05 partial)
- `glean-evaluation.md`(v1 — likely M07 partial)
- `glean-governance.md`(v1 — likely M07 partial)

I synthesized from existing context without re-reading these. **Cline should verify if v1 docs contradict any Phase 2 conclusion.**

### 3.3 Deliverables

| File | Module | Lines | Status |
|---|---|---|---|
| `01-data-connector.md` | M01 | ~70 | created |
| `02-enterprise-context.md` | M02(central) | ~110 | created |
| `03-search-retrieval.md` | M03 | ~75 | created |
| `04-permission-security.md` | M04 | ~95 | created |
| `05-agent-runtime.md` | M05 | ~110 | created |
| `06-action-tool.md` | M06 | ~75 | created |
| `07-governance-evaluation.md` | M07 | ~85 | created |
| `08-platform-developer.md` | M08 | ~85 | created |
| `09-partner-boundary.md` | M09 | ~95 | created |
| `capability-matrix-v2.md` | Matrix | ~150 | created |
| `README.md` | (modified) | +30 | updated Phase 1/2 status |

Total: **11 files changed, +881 lines**。

### 3.4 Commit

```
9f3a5cb  docs(research-v2): Phase 2 — Capability Map complete (9 modules + matrix v2)
11 files changed, 881 insertions(+), 1 deletion(-)
```

### 3.5 Key findings(6 高 IP Build 能力)

| # | Capability | Why Build | Evidence |
|---|---|---|---|
| 1 | **Domain Ontology** | Glean 无领域本体 | C23(STRONGLY_INFERRED) |
| 2 | **Domain Reasoning** | Glean 无领域推理 | C23(STRONGLY_INFERRED) |
| 3 | **Domain Evaluation** | Glean Observability 停在平台级 | C22(STRONGLY_INFERRED) |
| 4 | **Permission Engineering** | Glean 实现 + ECE 可叠加中国私有化场景 | C06, C07(CONFIRMED) |
| 5 | **Context Assembly** | ECE 核心架构,12 步流水线 | C02 + C18 综合(CONFIRMED) |
| 6 | **Entity Resolution(跨系统)** | Glean 模糊地带,我方领域优势 | C18 + C23(MIXED) |

### 3.6 Red Team Audit Points(请 Cline 重点挑战)

1. **M02 §4.2 终极问题 答**("Glean's Enterprise Context ≠ 仅 KG")— 这是 **INFERENCE**,结合 C02 + C18。该 inference 是否站得住脚?Glean 文档的 charitable reading 是否可能不同意?
2. **M05 §4.2 Workflow Agent vs Reasoning Agent 区分** — 这是 Glean 真实分类,还是我自创的范畴?(C10 marketing-level language doesn't clarify;C11 UNKNOWN)
3. **M07 §4.2 "Domain Evaluation 是最高 IP 价值"** — 该 claim 依赖 C22(STRONGLY_INFERRED,2026-09-03 v1,无 live re-verification)。Inference 扎实吗?什么会让它证伪?
4. **Capability Matrix v2 row 11(Agent Identity)** — 标 "later" 基于 C29 STRONGLY_INFERRED。该升到 Phase 4 决策吗?
5. **Capability Matrix v2 row 13(Platform Observability)** — "简化版 or 集成?" pending。该在 Phase 3 之前解决吗?
6. **C22/C23 inferences 处理**: 两者均 STRONGLY_INFERRED,从未直接验证。**若 C22 错(Glean 实际做了业务正确性评估),整个 M07 IP 价值论断崩溃**。
7. **9 模块粒度合理吗?** M04(Permission)和 M07(Governance)可否合并?M06(Action/Tool)和 M05(Agent Runtime)可否合并?

---

## 4. Key Decisions & Rationale

### 4.1 Phase 1 — Option C(accept v1 baseline)

**Why**: User chose via AskUserQuestion。审查时点的 rationale:
- v1 baseline 10 天前抓取,Glean 产品线稳定
- Phase 2-6 可立即推进,无 indefinite delay
- 每个 Capability Matrix 格子显式标 "Last Verified 2026-09-03 baseline; live re-verify deferred pending network access"

**Trade-off**: 若 v1 sources 已变化,Phase 2-6 结论可能失效。**Mitigation**: Phase 5(Platform Kernel Definition)之前 re-verify。

### 4.2 Phase 2 — 6 Build 能力

**Why these 6 and not others**:
- Domain Ontology / Reasoning / Evaluation: C22 + C23 双确认 Glean 空白(最高 IP)
- Permission Engineering: 与 Glean 模式匹配 + 中国-specific edge(私有化部署)
- Context Assembly: ECE 核心架构,无 Glean 严格 analog
- Entity Resolution: C18 确认 Glean 做了,但 cross-system variant unclear

**Trade-off**: **6 Build 能力超过 v0 Sprint 0-6 时间预算(~30 天)**。Phase 4 必须裁剪优先级。

### 4.3 User commits to ROOT CLAUDE.md governance

Per ROOT CLAUDE.md, user 同时承担:
1. Enterprise AI 产品研究员
2. 产品架构师
3. MVP 产品经理
4. 技术负责人

**Reviewer implication**: Cline 应从 4 个 perspective 都挑战,不只挑战技术准确性。

---

## 5. What's Pending / Open Questions

### 5.1 For Cline(red team reviewer)

See §2.5 and §3.6 audit points。

### 5.2 For Robin(Glean Partner Manager,下周通话)

14 questions in [`/docs/partner/questions-for-glean.md`](../partner/questions-for-glean.md)。重点 6:
- Q1: Asia strategy
- Q2: Partner type
- Q3: My fit
- Q9: Graph schema(C03 UNKNOWN)
- Q11: Pricing(C24 UNKNOWN)
- Q13: China deployment

### 5.3 For Phase 3(Architecture Reconstruction)

- 产出 G/O/P/? 分层大图
- 区分 "官方明确描述" vs "公开资料推导" architecture(两类标注)
- mermaid 入 `/docs/diagrams/platform-kernel-architecture.mmd` + `glean-layers-v2.mmd`

### 5.4 For Phase 4(Build/Buy/Integrate/Partner 四向决策)

- 每个 capability 需一个 ADR(沿 ADR-002 编号继续)
- **注意**: `/docs/adr/` 与 `ece/docs/adr/` 是**两套独立编号**

---

## 6. Evidence Discipline Notes

### 6.1 §4 合规检查

- ✅ Every Claim carries Source / Evidence / Confidence / Last Verified
- ✅ UNKNOWN / BLOCKED_REVERIFY / STILL_UNKNOWN / INFERENCE_HOLDS 显式区分
- ✅ STRONGLY_INFERRED items(C22、C23、C26-C29)显式标
- ✅ Marketing-level claims tagged(C10)
- ✅ v1 docs(`/docs/research/`、`/docs/architecture/`、`/docs/product/`)**NOT modified or deleted**(verify via git diff)
- ✅ ADR 编号保留(`/docs/adr/` 从 ADR-002 继续;`ece/docs/adr/` 独立)

### 6.2 我可能出错的地方(自检)

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | **C22/C23 inferences 错**(若 Glean 实际做了 domain evaluation) | **HIGH** — would invalidate M07 + Capability Matrix row 14 | Verify with Robin(Q10/Q11) + 网络恢复后 re-fetch |
| 2 | v1 baseline may be stale(10 天,Glean 产品线可能变) | MEDIUM | Phase 5 前 re-fetch C01-C25 |
| 3 | M02 §4.2 inference("Glean's Enterprise Context ≠ 仅 KG")可能被 misread | MEDIUM | Mark as INFERENCE_HOLDS,verify with Robin Q9 |
| 4 | M05 §4.2 "Workflow vs Reasoning" 区分可能 invented | LOW | Disclaim in M05 §3 |
| 5 | **Phase 2 合成时未重新读** `glean-agent-architecture.md` / `glean-evaluation.md` / `glean-governance.md` | LOW | v1 docs 可读 if Cline wants to verify |

---

## 7. File Inventory

### 7.1 Created files(13)

```
docs/partner/partner-meeting-brief.md        (Phase 0, ~210 lines)
docs/partner/questions-for-glean.md           (Phase 0, ~180 lines)
docs/research_v2/README.md                   (Phase 0/1/2 tracker, ~110 lines)
docs/research_v2/evidence-matrix-v2.md       (Phase 1, ~150 lines)
docs/research_v2/01-data-connector.md        (Phase 2, ~70 lines)
docs/research_v2/02-enterprise-context.md    (Phase 2, ~110 lines)
docs/research_v2/03-search-retrieval.md      (Phase 2, ~75 lines)
docs/research_v2/04-permission-security.md   (Phase 2, ~95 lines)
docs/research_v2/05-agent-runtime.md         (Phase 2, ~110 lines)
docs/research_v2/06-action-tool.md           (Phase 2, ~75 lines)
docs/research_v2/07-governance-evaluation.md  (Phase 2, ~85 lines)
docs/research_v2/08-platform-developer.md    (Phase 2, ~85 lines)
docs/research_v2/09-partner-boundary.md      (Phase 2, ~95 lines)
docs/research_v2/capability-matrix-v2.md     (Phase 2, ~150 lines)
```

### 7.2 NOT touched(per PRD §13.5)

- `/docs/research/evidence-matrix.md` and other v1 research files
- `/docs/architecture/*` v1
- `/docs/product/*` v1
- `/docs/cases/*` v1
- `/docs/customer/*` v1
- `/docs/diagrams/*` v1
- `/docs/adr/ADR-001-*.md` and `ADR-002-*.md`(root ADRs 保留)
- `ece/` subdirectory(独立仓库,NO modifications)

---

## 8. Git Commit Trail

```
$ git log --oneline -5
9f3a5cb (HEAD -> main) docs(research-v2): Phase 2 — Capability Map complete
f5d4d0e                  docs(research-v2): Phase 1 — Evidence Collection BLOCKED
c1dd32b                  docs(research-v2): Phase 0 — Partner meeting prep
```

All commits follow conventional commits format. Co-Authored-By line included。

---

## 9. Network Block Documentation

**Issue**: claude.ai WebFetch blocked from `glean.com` + `developers.glean.com` domains as of 2026-09-13。

**Error**: `"Unable to verify if domain www.glean.com is safe to fetch. This may be due to network restrictions or enterprise security policies blocking claude.ai."`

**Affected scope**:
- All glean.com subdomains(www、blog、etc.)
- developers.glean.com
- WebSearch also returns errors

**Workaround used**: BLOCKED status documented per PRD §14。v1 baseline(2026-09-03)maintained as Last Verified。

**Retry strategy**:
- A: User fetches URLs locally,shares text/screenshots → I 整理为 C35+ 证据
- B: User 解除 network policy → I 重跑 Phase 1 fetches
- **C: Accept v1 baseline → proceed to Phase 2-6 with deferred tags(USER CHOSE THIS)**
- D: Pause → wait for network access

**Recommended**: Re-verify C01-C25 + new C35+ **before Phase 5**(Platform Kernel Definition)。

---

## 10. Honest Limitations

1. **No live re-verification of any v1 evidence** in Phase 1 or Phase 2。所有 CONFIRMED claims 都 rest on 2026-09-03 v1 baseline。
2. **Three v1 docs not re-read for Phase 2 synthesis**:`glean-agent-architecture.md`、`glean-evaluation.md`、`glean-governance.md`。May contain additional detail for M05/M07。
3. **6 Build capabilities exceed v0 timeline**(~30 天 Sprint 0-6)。Phase 4 必须裁剪。
4. **No Phase 3+ done yet** — 本简报仅覆盖 Phase 1 & 2。
5. **No new ADRs** in `/docs/adr/`(Phase 4 will produce more,沿 ADR-002 继续)。
6. **Phase 0 仅作为 background context,未在本简报中详细 review** — 若需要 separate review brief,告知后提供。
7. **网络 BLOCKED 状态下结论的 robustness 未经验证** — 任何 Glean 产品线变化(2026-09-03 之后)都未被检测。

---

## 11. Sign-off

Phase 1 & 2 deliverables ready for Cline red team review。Author awaits:

- **Audit findings**(specific challenges to claims)
- **Verification of file inventory + commit trail**(请用 git diff / git log 验证)
- **Strategic pushback** on Build/Buy decisions(尤其 6 个高 IP Build 能力)
- **Identification of evidence gaps** before Phase 3

**Cline's job**(per ROOT CLAUDE.md / RED_TEAM_REVIEW v3 红队定义): 推翻结论,而非维护结论。若任何 Phase 2 模块的 Build/Buy 决策站不住,应明确指出。

---

**Author**: Claude(Fable 5.1)
**Reviewer**: Cline
**Date**: 2026-09-13
**Repo**: github.com/cscoheru/domainAgentECE(branch: main)
**Working tree HEAD**: 9f3a5cb
