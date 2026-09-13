# Summary — Track A + Track B Spec Final Report

> **Project**: Enterprise AI Platform Kernel(双轨架构:Track A 研究 + Track B 工程)
> **Author**: Claude(Fable 5.1,Anthropic)
> **Final Updated**: 2026-09-13
> **Reviewer**: User(创始人)+ Cline 红队审查(Phase 2.5)
> **Repo**: github.com/cscoheru/domainAgentECE(branch: main,HEAD: 见 §6.3)

---

## 1. 项目背景

### 1.1 双轨架构(per ROOT `CLAUDE.md` §16)

| 轨道 | 内容 | 仓 | 状态 |
|---|---|---|---|
| **Track A** | Glean Architecture Reverse Engineering & Enterprise AI Platform Kernel | `github.com/cscoheru/domainAgentECE`(本仓) | ✅ STOPPED(Phase 6 STOP Gate 通过) |
| **Track B** | ECE v0 工程实施(Sprint 0-6) | `github.com/cscoheru/ece`(独立仓) | ⏳ Spec 已交付,代码未开始 |

**约束**:本会话不能 touch `ece/` 仓文件(per ROOT CLAUDE.md + 用户早先指令)。Track A 与 Track B 互不阻塞。

### 1.2 战略背景(RED_TEAM_REVIEW.md v3)

- v3 Red Team 确立 **主路径 D**:私有化垂直 Context+Agent(中国市场事实:Glean Partner 路径降级为期权)
- 用户 M0 输入:可达市场 = 中国大陆,无 Glean 客户;Glean Partner 申请已提交(后取消)
- 信任货币 = **数据主权**(私有化部署 + 国产开源模型),不是 Glean 式品牌信任

---

## 2. 完成清单(Track A 7 个 Phase + Track B Spec)

### 2.1 Phase 0 — Partner 会谈准备(c1dd32b)
- 2 文件:`partner-meeting-brief.md` + `questions-for-glean.md`
- 14 题必问清单;3 题 UNKNOWN 必答(C03/C11/C24)
- **当前状态**:Robin Glean Partner 路径取消(用户决定);文件保留作为历史 artifacts

### 2.2 Phase 1 — Evidence Collection(f5d4d0e)
- 1 文件:`evidence-matrix-v2.md`(初版)
- 尝试抓 12 个 URL,claude.ai WebFetch 全部 BLOCKED(工具特定限制)
- 产出 C35+ = 0(网络层屏蔽误判)

### 2.3 Phase 2 — Capability Map(9f3a5cb)
- 11 文件:9 个模块研究文档(M01-M09)+ `capability-matrix-v2.md` + README
- 16 能力 × 8 列 BBIP 决策矩阵
- 6 个 Build 高 IP 决策(Domain 三件套 + Entity Resolution + Context Assembly + Permission Engine)

### 2.4 Phase 2.5 — Cline 红队审查 + R1-R7 修复(b527574)
- 1 文件:`cline-review-phase1-2.md`(Cline 报告)
- **关键 catch**:"BLOCKED" 是 claude.ai WebFetch 工具特定限制,非网络层屏蔽
- Cline 用备用通道验证 6 URL,带回 C35-C42 八条新 CONFIRMED 证据
- R1-R7 修复:
  - R1:削弱"全网 BLOCKED"过强表述
  - R2:C35-C42 原样登记到 §4(引文未改写)
  - R3:C29 superseded by C36 / C15 re-verified by C35 / C11 partial answer by C37 / C22 tightened by C38
  - R4:M04/M05/M08 + capability-matrix 4 处更新
  - R5:README 重复行删除 / evidence-matrix §5/§7 重写 / partner-brief §11 修复
  - R6:partner/ Q6/Q10/Q12/Q14 用 C35-C42 新证据锐化
  - R7:commit + push

### 2.5 Phase 3 — Architecture Reconstruction(03b096e)
- 3 文件:`glean-architecture-reconstruction.md` + 2 mermaid(`glean-layers-v2.mmd` + `platform-kernel-architecture.mmd`)
- Glean 分层:**OFFICIAL / SEMI / INFERRED / UNKNOWN** 4 区
- Platform Kernel:**G/O/P/?** 5 层标注

### 2.6 Phase 4 — Build/Buy/Integrate/Partner(713c083)
- 9 文件:`build-buy-integrate-partner-matrix.md` + 8 个 ADR(ADR-003 ~ ADR-010)
- 16 能力 4 向决策详表
- **Row 13 Platform Observability 裁决**:Build 简化版 + Integrate Glean 完整版
- 8 个 Build 决策 ADR,每个含理由 + 关联 C 编号 + ECE 铁律符合性 + 备选否决

### 2.7 Phase 5 — Platform Kernel Definition(421dc06)
- 1 文件:`platform-kernel-definition.md`
- **8 Kernel(K1-K8)+ D1 Postgres + 6 外购(X1-X6)+ 3 缓建(L1-L3)**
- 与 ECE 现有架构完整映射(已覆盖 / 缺口 / 冗余)
- **真缺口识别**:K7 MCP Tool Layer(Sprint 4 需新增 S4.5)

### 2.8 Phase 6 — Reference Applications + STOP Gate(49604b0)
- 1 文件:`reference-applications.md`
- 3 个 Reference Applications:EvidenceIQ / Procurement Agent / HR Q&A
- 每个含 Kernel 依赖图(8 Kernel × 3 App = 24 依赖点)+ 验证假设(9 个 H1-H3)
- **STOP Gate §11 十问全部有证据支持答案**
- **Track A 研究阶段正式 STOP**(per PRD §11 + §13.3)

### 2.9 Track B 战略 Spec(a10c75a,POST-STOP)
- 3 文件:`docs/track_b/{README.md, execution-plan.md, track-a-decisions.md}`
- Sprint 0-6 × Phase 5 K1-K8 完整映射矩阵
- **Sprint 4 S4.5 MCP Tool Layer 详细 spec**(4 tools / 文件结构 / 集成命令 / 验收 DoD)
- Phase 4 8 ADR → ECE TASKS 审计链
- ECE 仓 ADR-001~010 与根目录 ADR-001~010 **无冲突**(两套独立编号)

---

## 3. 交付物清单(15 commits / 23 文件)

### 3.1 Track A 文档(`/docs/`)

| 子目录 | 文件 | 阶段 | Commit |
|---|---|---|---|
| `/docs/partner/` | `partner-meeting-brief.md` | Phase 0 | c1dd32b |
| `/docs/partner/` | `questions-for-glean.md` | Phase 0 | c1dd32b |
| `/docs/research_v2/` | `evidence-matrix-v2.md` | Phase 1 | f5d4d0e + b527574 |
| `/docs/research_v2/` | `01-data-connector.md` | Phase 2 | 9f3a5cb |
| `/docs/research_v2/` | `02-enterprise-context.md` | Phase 2 | 9f3a5cb |
| `/docs/research_v2/` | `03-search-retrieval.md` | Phase 2 | 9f3a5cb |
| `/docs/research_v2/` | `04-permission-security.md` | Phase 2 | 9f3a5cb + b527574 |
| `/docs/research_v2/` | `05-agent-runtime.md` | Phase 2 | 9f3a5cb + b527574 |
| `/docs/research_v2/` | `06-action-tool.md` | Phase 2 | 9f3a5cb + b527574 |
| `/docs/research_v2/` | `07-governance-evaluation.md` | Phase 2 | 9f3a5cb + b527574 |
| `/docs/research_v2/` | `08-platform-developer.md` | Phase 2 | 9f3a5cb + b527574 |
| `/docs/research_v2/` | `09-partner-boundary.md` | Phase 2 | 9f3a5cb + b527574 |
| `/docs/research_v2/` | `capability-matrix-v2.md` | Phase 2 | 9f3a5cb + b527574 |
| `/docs/research_v2/` | `README.md` | 进度看板 | 多个 commit |
| `/docs/research_v2/` | `cline-review-brief.md` | 红队自审 | b166061 |
| `/docs/research_v2/` | `cline-review-phase1-2.md` | 红队报告 | 040c04e |
| `/docs/architecture_v2/` | `glean-architecture-reconstruction.md` | Phase 3 | 03b096e |
| `/docs/architecture_v2/` | `build-buy-integrate-partner-matrix.md` | Phase 4 | 713c083 |
| `/docs/architecture_v2/` | `platform-kernel-definition.md` | Phase 5 | 421dc06 |
| `/docs/diagrams/` | `glean-layers-v2.mmd` | Phase 3 | 03b096e |
| `/docs/diagrams/` | `platform-kernel-architecture.mmd` | Phase 3 | 03b096e |
| `/docs/product_v2/` | `reference-applications.md` | Phase 6 | 49604b0 |
| `/docs/adr/` | `ADR-001.md` ~ `ADR-010.md` | 治理(001/002 既存) + Phase 4(003-010) | 713c083 |
| `/docs/track_b/` | `README.md` | Track B 概述 | a10c75a |
| `/docs/track_b/` | `execution-plan.md` | Sprint × Kernel + S4.5 | a10c75a |
| `/docs/track_b/` | `track-a-decisions.md` | ADR → TASKS 审计链 | a10c75a |

### 3.2 根目录与 v1 文档(未修改)

| 文件 | 状态 |
|---|---|
| `CLAUDE.md`(根) | 未修改(项目治理文件) |
| `RESEARCH_PRD_V2.md`(根) | 未修改(Master PRD) |
| `RED_TEAM_REVIEW.md`(根,v3) | 未修改(战略基线) |
| `Enterprise Context Engine.md`(根) | 未修改 |
| `RESEARCH_PRD.md`(根,v1) | 未修改 |
| `Glean_x_Domain_Product_Architecture_PRD_v0.1-作废.md` | 未修改(已作废) |
| `/docs/research/`(v1,8 文件) | **未修改**(PRD §13.5 强约束) |
| `/docs/architecture/`(v1,5 文件) | **未修改** |
| `/docs/product/`(v1,5 文件) | **未修改** |
| `/docs/cases/`(v1,2 文件) | **未修改** |
| `/docs/customer/`(v1,3 文件) | **未修改** |
| `/docs/diagrams/`(v1,5 文件) | **未修改**(新增 2 个 v2 mermaid 在同目录) |
| `/docs/adr/ADR-001.md` + `ADR-002.md`(根目录,既存) | **未修改**(继续从 003 编号) |

---

## 4. 审验范围(Verification Scope)

### 4.1 可由用户直接审验

| 项 | 验证方式 | 时间 |
|---|---|---|
| **15 commits 历史** | `git log --oneline` | < 1 分钟 |
| **v1 文档未修改** | `git diff f28472e..HEAD -- docs/research docs/architecture docs/product docs/cases docs/customer docs/diagrams` 应为空 | < 1 分钟 |
| **ECE 子目录未触碰** | `ls /Users/kjonekong/projects/domainAgentECE/ece/` 应为空 | < 1 分钟 |
| **42 条证据一致性** | 抽查 `docs/research_v2/evidence-matrix-v2.md` §2-4 的 C 编号 | < 10 分钟 |
| **STOP Gate §11 十问** | 读 `docs/product_v2/reference-applications.md` §6,每问可回溯到证据 | < 30 分钟 |
| **ADR 决策链** | `docs/adr/ADR-003.md` ~ `ADR-010.md` 逐读,每条都有 C 编号 + ECE TASKS 引用 | < 30 分钟 |

### 4.2 可由 Cline 红队审计

| 项 | 验证方式 | 报告位置 |
|---|---|---|
| **§4 证据纪律(PRD §4)合规性** | 每条 Claim / Source / Evidence / Confidence / Last Verified 五要素 | evidence-matrix-v2.md |
| **Cline 红队审查后续影响** | R1-R7 修复完整性 | cline-review-phase1-2.md §3 |
| **架构 OFFICIAL/INFERRED 区分** | 每个 Glean 声明是否标证据 | glean-layers-v2.mmd + reconstruction.md §1-2 |
| **ECE 铁律符合性** | Permission Before / 领域包隔离 / LLM 不可知 / 垂直纪律 | 每个 ADR 末段 |

### 4.3 可由未来审计者/同事审验

| 项 | 验证方式 |
|---|---|
| **Track A → Track B 决策可追溯** | `docs/track_b/track-a-decisions.md` 提供 ADR → TASKS 完整映射 |
| **ECE 仓 vs Track A 一致性** | `docs/track_b/track-a-decisions.md` §9 验证 ADR 编号独立无冲突 |
| **证据基线持久化** | git tag 可加 `git tag v1.0-stop-gate a10c75a` 标记最终状态 |
| **文件完整性** | 23 个新增/修改文件 + 0 个 v1 修改 + 0 个 ECE 触碰(可在 git log 中验证) |

### 4.4 关键自审点(诚实声明)

| 局限 | 详情 | 缓解 |
|---|---|---|
| **claude.ai WebFetch 屏蔽 glean.com** | 工具特定限制,非网络层屏蔽;Cline 用备用通道绕过 | Phase 1 BLOCKED 后改 Cline 备用通道,带回 C35-C42 |
| **C22/C23 STRONGLY_INFERRED** | "Glean 无业务正确性评估" / "Domain 层是 Glean 未覆盖的空白" 均为推断,无官方反证 | Robin Q10/Q11 必问;Phase 5 已标 INFERENCE_TIGHTENED |
| **ECE 仓 ADR-001~010 未深度读取** | 仅通过 `ls` 确认存在,内容未深审 | track-a-decisions.md §9.2 仅做主题级交叉验证 |
| **Glean 分层堆叠图(INFERRED)** | 9 层堆叠为我方基于 C02/C04/C06/C07/C18 综合推导,Glean 官方未公开 | Phase 3 §2.1 明确标 INFERRED + 推理依据 |
| **Track A 全程未实施 ECE 代码** | 本会话不写产品代码;Track B 由 ECE session 独立实施 | ROOT CLAUDE.md 双轨架构约束 |

### 4.5 不在审验范围(NOT DONE)

| 项 | 原因 | 后续路径 |
|---|---|---|
| **Robin Glean Partner 会谈** | 用户取消 | (不进行) |
| **ECE v0 代码实现** | 独立仓;本会话不能 touch | Track B session 实施 |
| **Glean C03/C11/C24/C25 直接验证** | Robin 会谈取消 | (不进行,除非 Glean 路径重新激活) |
| **Track A 新证据补强(网络抓取)** | claude.ai WebFetch 屏蔽;Cline 备用通道不可持续调用 | 暂缓,除非 Glean 路径重新激活 |

---

## 5. 关键发现与战略决策

### 5.1 Track A 核心发现

1. **Glean 真正壁垒** = 不是功能清单,是 **7 年企业信任阶梯 + 数据主权**(RED_TEAM v3 §0.2)
2. **可达市场约束** = **中国大陆 + 私有化部署 + 国产开源模型**(v3 主路径 D)
3. **Glean Enterprise Context ≠ 仅 KG** = KG + Search Index + Entity System + Permission + Context Assembly 之综合(Phase 2 §M02)
4. **我方最高 IP 价值** = **Domain 三件套**(Ontology / Reasoning / Evaluation)+ Entity Resolution(Glean 未覆盖纵深,C22/C23)
5. **Phase 2 §M07 关键论断**(C38 收紧):Glean 官方 "evaluations" 语义指向 execution-path,**≠ domain correctness**

### 5.2 ECE v0 决策(8 个 Build ADR)

| ADR | 决策 | 关键证据 |
|---|---|---|
| ADR-003 Permission Engine | Build + Integrate(语义) | C06/C07/C16/C19/C36 |
| ADR-004 MCP Tool Layer | Build + Integrate | C19/C37/C39(MCP 是事实标准) |
| ADR-005 Enterprise Graph | Build(简化版)+ Integrate | C02/C03/C18;Phase 5+ 接 Glean |
| ADR-006 Context Assembly | Build(12 步流水线) | C02/C18 |
| ADR-007 Entity Resolution | Build(渐进流水线) | C18/C23(高 IP) |
| ADR-008 Domain Evaluation | Build(业务正确性评估) | C22/C38(最高 IP) |
| ADR-009 Domain Ontology | Build(YAML spec) | C23(框架无关性) |
| ADR-010 Domain Reasoning | Build(规则优先 + LLM 轻量) | C23 + ADR-006(国产开源友好) |

### 5.3 Platform Kernel 最小集(Phase 5)

| 类别 | 内容 |
|---|---|
| **核心 8 Kernel(K1-K8)** | Permission Engine / Context Assembly / Entity Resolution / Domain Ontology / Domain Reasoning / Domain Evaluation / MCP Tool Layer / Query Planner |
| **数据底座(D1)** | PostgreSQL + pgvector + FTS |
| **6 外购(X1-X6)** | Connector 275+(Glean)/ Search(砍掉)/ Actions(关闭)/ Glean Enterprise Context / Agent Builder(砍掉)/ Glean Protect |
| **3 缓建(L1-L3)** | Agent Identity / Glean Partner ext / 完整 Platform Observability |

### 5.4 真缺口(Phase 5 §3.1 识别)

**K7 MCP Tool Layer** — Sprint 4 需新增 S4.5 任务(详见 `docs/track_b/execution-plan.md` §4)。

---

## 6. 完整 git 历史(16 commits,HEAD = a10c75a)

```
a10c75a  Track B 战略 spec(POST-STOP, for ECE session) ← HEAD
49604b0  Phase 6 — Reference Applications + STOP Gate ✅
421dc06  Phase 5 — Platform Kernel Definition
713c083  Phase 4 — BBIP 矩阵 + 8 ADRs
03b096e  Phase 3 — Architecture Reconstruction
b527574  R1-R7 fixes (Cline review)
040c04e  Cline 红队审阅报告
b166061  Cline review brief
9f3a5cb  Phase 2 — Capability Map
f5d4d0e  Phase 1 — Evidence Collection
c1dd32b  Phase 0 — Partner meeting prep
f28472e  (initial)
```

### 6.1 提交规范

所有 commits 遵循:
- Conventional Commits 格式(`docs(research-v2): <description>`)
- 详细 commit message 含 Phase 标识 + 关键发现
- `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` attribution

---

## 7. 残留项与已知限制

### 7.1 残留项(未完成 / 主动推迟)

| 项 | 状态 | 影响 |
|---|---|---|
| Robin Glean Partner 会谈 | **取消**(用户决定) | Glean 路径降级为期权;partner/ 文档保留作为历史 |
| Glean C03/C11/C24/C25 直接验证 | **不进行**(Robin 取消) | UNKNOWN 维持 INFERENCE_HOLDS / STILL_UNKNOWN |
| Track B 工程代码实施 | **待 ECE session** | 本会话不写代码;Track B spec 已交付 |

### 7.2 已知限制(诚实声明)

| 限制 | 来源 | 影响 |
|---|---|---|
| **claude.ai WebFetch 屏蔽 glean.com** | 工具特定限制 | C01-C25 仅 v1 baseline 验证;C35-C42 由 Cline 备用通道 |
| **C22/C23 STRONGLY_INFERRED** | 推断性证据,无 Glean 官方反证 | M07 高 IP 论断基于此;Robin Q10/Q11 必问(已取消) |
| **ECE 仓 ADR-001~010 未深度审** | 仅主题级验证 | track-a-decisions.md §9.2 交叉验证仅覆盖主题 |
| **Track A 全程未实施 ECE 代码** | ROOT CLAUDE.md 双轨架构 | Track B 由 ECE session 独立实施 |

### 7.3 不在 Track A 范围

- **不修改 v1 文档**(`/docs/research/`、`/docs/architecture/`、`/docs/product/` 等):per PRD §13.5 强约束,全程零修改
- **不修改根目录治理文件**(CLAUDE.md / RESEARCH_PRD_V2.md / RED_TEAM_REVIEW.md / Enterprise Context Engine.md)
- **不操作 `ece/` 子目录**:独立仓库,本会话不能 touch

---

## 8. 给 Track B Session 的接口

### 8.1 Track B session 启动流程

1. **打开 `github.com/cscoheru/ece`**(独立仓),初始 commit 状态
2. **读取本仓 3 个 Track B spec 文档**作为输入:
   - `docs/track_b/README.md` — 概述 + 状态
   - `docs/track_b/execution-plan.md` — Sprint × Kernel 映射 + K7 S4.5 详细 spec
   - `docs/track_b/track-a-decisions.md` — ADR → TASKS 审计链
3. **按 `ece/CLAUDE.md` + `ece/TASKS.md` + 新增 S4.5 任务** 启动 Sprint 0
4. **每 Sprint 完成后跑对应 E 套件**(EVALUATION.md §1)
5. **每 Sprint commit + 汇报**(ECE 仓,不回本仓)

### 8.2 Track B 关键提醒

1. **优先 Sprint 0 + Sprint 2**:基础设施 + K1/K3 权限与消歧
2. **新增 Sprint 4 S4.5 MCP Tool Layer**(`docs/track_b/execution-plan.md` §4 详细 spec)
3. **CI 必须含 import-linter**:强制 `src/ece/` 不 import `src/domain_packs/`(ADR-010 铁律)
4. **私有化验收 S6.5**:断网 + 本地 Ollama + 国产模型 + Demo 数据集(v3 §0.8 技术要求)
5. **ECE 仓 ADR-001~010 与根目录 ADR-003~010 无冲突**:两套独立编号,互补

---

## 9. 总结

**Track A — Glean Architecture Reverse Engineering & Enterprise AI Platform Kernel ✅ COMPLETE**

- 7 个 Phase(0-6)全部完成
- 16 commits 推送到 main
- 23 个新增/修改文件(无 v1 修改,无 ECE 触碰)
- 42 条证据(C01-C42)
- 10 个 ADR(根目录 ADR-001 ~ ADR-010)
- Cline 红队审查通过(R1-R7 全部修复)
- **STOP Gate §11 十问全部有证据支持答案**

**Track B Spec — ECE v0 Engineering Execution ✅ READY FOR ECE SESSION**

- 3 个战略 spec 文档就绪(README + execution-plan + track-a-decisions)
- Sprint 0-6 × Phase 5 K1-K8 完整映射矩阵
- **真缺口 K7 MCP Tool Layer** 已识别,新增 S4.5 详细 spec

**NEXT**:
1. **用户切换到 `ece/` 仓 session** 启动 Sprint 0
2. 本会话暂停,等待用户后续指示(可能:Track A 修订 / Track B 反馈澄清 / 其他)

**Track A STOP. Track B Spec READY. ECE Session GO.**

---

**Author**: Claude(Fable 5.1)
**Reviewer**: User(创始人)+ Cline(红队)
**Date**: 2026-09-13
**Repo HEAD**: `a10c75a`
