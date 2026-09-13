# Cline 红队审验 Cycle 001 — track_b spec R1-R4 修复

> **模板声明**: 本文件是 **Cline 红队审验 刀报告的格式模板**。后续 刀请按此结构产出 `docs/track_b/clines-review-cycle-NNN.md`(NNN 递增)。详见 §6 模板说明。

---

## 0. 元数据

| 项 | 值 |
|---|---|
| **Cycle** | 001 |
| **触发** | 用户提交首刀 track_b spec 审验(基于 `docs/track_b/cline-review-trackb-spec.md` 红队报告 §4 Sign-off 条件) |
| **上游 Cline 报告** | `docs/track_b/cline-review-trackb-spec.md`(commit `040c04e` 同期产物) |
| **审验者** | Cline(红队角色,目标推翻不维护) |
| **修复者** | Claude(Fable 5.1,Anthropic) |
| **日期** | 2026-09-13 |
| **涉及文件** | `docs/track_b/{README.md, execution-plan.md, track-a-decisions.md}` |
| **HEAD** | `c2625db`(本 刀 commit) |

---

## 1. 完成情况(改动清单)

### 1.1 改动统计

| 维度 | 数值 |
|---|---|
| 修改文件数 | 3 |
| 修复项总数 | 11(R1=5, R2=2, R3=4 包含 README §6.1 + track-a-decisions §3.1 + §3.5 + 注记同一句话) |
| 新增行 | +12 |
| 删除行 | -10 |
| Commit | `c2625db` |
| Pushed | `3d58477..c2625db main -> main` ✅ |

### 1.2 逐条修复(file:line + 修复前后)

> 表头: 修复 ID | 文件:行号 | 关联 Cline Finding | 修复前 | 修复后

#### R1 — 5 处 ADR 编号错位(F1【MEDIUM】)

| # | 文件:行号 | 关联 | 修复前 | 修复后 |
|---|---|---|---|---|
| **R1a** | `README.md:72` | F1 错位 #1 | `ADR-006(根)+ ece/ADR-006 + Phase 6 §3 Procurement H1` | `ece/ADR-006 + 根 ADR-010(仅"规则优先"维度) + Phase 6 §3 Procurement H1` |
| **R1b** | `README.md:71` | F1 错位 #2 | `ADR-010(根) + ece/ADR-010(独立)` | `ece/ADR-010` |
| **R1c** | `track-a-decisions.md:317` | F1 错位 #3 | `根 ADR-010(根域包隔离,ECE ADR-010 也是域包隔离,视角略不同)` | `(根目录无对应——领域包隔离是 ECE 工程决策)` |
| **R1d** | `track-a-decisions.md:327` | F1 错位 #4 | `LLM 不可知 + 规则优先(根 ADR-010)` | `规则优先(根 ADR-010);LLM 不可知由 ece/ADR-006 承担` |
| **R1e** | `track-a-decisions.md:328` | F1 错位 #5 | `O Build 决策(根 ADR-009 + ADR-010)` | `(根目录无对应,ece/ADR-010 独立承担)` |

#### R2 — MCP 接入命令修正 + 依赖注记(F2【MEDIUM】)

| # | 文件:行号 | 关联 | 修复前 | 修复后 |
|---|---|---|---|---|
| **R2a** | `execution-plan.md:278-280` | F2 | `**Claude Code 接入**:\n\`\`\`bash\nclaude mcp add ece-context -- stdio -C /path/to/ece python -m ece.mcp.server\n\`\`\`` | `**Claude Code 接入**(在 ece 仓库根目录执行;如需全局再加 \`-s user\`):\n\`\`\`bash\nclaude mcp add ece-context -- python -m ece.mcp.server\n\`\`\``(删除错误 `-C`) |
| **R2b** | `execution-plan.md:269` | F2 延伸 | (新增引用块) | `> **依赖注记**: \`mcp\` SDK 在 **S4.5 动工时** 才引入 pyproject(Sprint 0 不加,S0.1 依赖列表保持最小地基 ...)` |

#### R3 — Robin 路径取消注记(F4【LOW】,3 处)

> 注记内容(各处相同):`「（Robin 路径已取消 2026-09-13；触发改为 Glean 期权重启或 Phase 5+ POC 客户已有 Glean）」`

| # | 文件:行号 | 上下文 | 修复前 | 修复后 |
|---|---|---|---|---|
| **R3-1** | `README.md:108` | §6.1 风险表 Robin Q9 行 | `Phase 5 §3 路径已设计,Robin Q9 决定` | `Phase 5 §3 路径已设计「（Robin 路径已取消 2026-09-13；触发改为 Glean 期权重启或 Phase 5+ POC 客户已有 Glean）」` |
| **R3-2** | `track-a-decisions.md:97` | §3.1 ADR-005 摘要 | `Phase 5+ 视 Robin Q9(C03)决定是否接 GleanAdapter。` | 末尾追加注记 |
| **R3-3** | `track-a-decisions.md:123` | §3.5 ADR-005 风险/备注 | `若 Robin Q9 确认 Glean schema 自定义 → 写 \`src/ece/adapters/glean/graph_adapter.py\`` | 末尾追加注记 |

#### R4 — commit + push(自动化收尾)

| # | 项 | 值 |
|---|---|---|
| Commit | hash | `c2625db` |
| Commit | message | `docs(track_b): spec fixes R1-R4 per cline-review-trackb-spec.md` |
| Push | range | `3d58477..c2625db main -> main` ✅ |

---

## 2. 审验范围

### 2.1 自检 grep(本仓)

> 验证 R1 + R2 修复完整性的唯一 grep 命令。后续 刀 请按此模式构造。

```bash
# 排除 cline-review-trackb-spec.md 自身(它合法引用旧文本作为红队审查证据)
grep -rn 'ADR-006(根)\|根 ADR-010(根域包隔离\|根 ADR-009 + ADR-010\|-C /path/to/ece' \
  docs/track_b/ | grep -v cline-review-trackb-spec.md
```

**期望输出**: 空
**实际输出**: 空 ✅
**退出码**: 1(grep 无匹配 = PASS)

### 2.2 git 二次审计(任何人可复现)

```bash
# 1. 看 commit 详情
git show c2625db --stat

# 2. 看改动 diff
git diff 3d58477..c2625db -- docs/track_b/

# 3. 验证 R2a 命令修复
git show c2625db:docs/track_b/execution-plan.md | grep -n 'claude mcp add'

# 4. 验证 R1 R2 R3 全部就位
git show c2625db:docs/track_b/README.md | grep -n 'ece/ADR-010 |$\|ece/ADR-006 + 根 ADR-010\|Robin 路径已取消'
git show c2625db:docs/track_b/track-a-decisions.md | grep -n '根目录无对应——领域包隔离\|规则优先(根 ADR-010);LLM 不可知\|根目录无对应,ece/ADR-010\|Robin 路径已取消'
```

### 2.3 排除项(本刀明确不动)

| 排除范围 | 理由 |
|---|---|
| `/docs/research/` 等 v1 文档 | ROOT CLAUDE.md 治理 + PRD §13.5 强约束;全程零修改 |
| `/docs/architecture_v2/platform-kernel-definition.md` | Phase 5 历史交付物,Track A 已 STOP,保持历史原貌(红队审查 §3 F4 明确) |
| `/docs/product_v2/reference-applications.md` | Phase 6 历史交付物,同 F4 |
| `/docs/adr/ADR-001~010.md` | Phase 4 根目录 ADR,本刀不修订战略决策 |
| `ece/` 子目录 | 独立仓,本会话不能 touch |
| `docs/SUMMARY.md` | Track A 收尾文件,本刀不修改总结 |

### 2.4 不在本仓范围的 Cline Finding(移交 ECE session)

| Finding | 内容 | 修复位置 |
|---|---|---|
| **F3【MEDIUM】** | ece/TASKS.md S4.2 "权限后置过滤" 措辞违反 ADR-003 SQL 子查询层强制铁律 | ECE session kickoff 指令(已附 cline-review-trackb-spec.md §5.2 任务 b) |

---

## 3. Commit 信息

```
[main c2625db] docs(track_b): spec fixes R1-R4 per cline-review-trackb-spec.md
 3 files changed, 12 insertions(+), 10 deletions(-)
```

**Pushed**: `3d58477..c2625db main -> main` ✅

---

## 4. 本刀特有的非典型项(给后续 刀的特例参考)

| 项 | 说明 |
|---|---|
| 排除项增加 `cline-review-trackb-spec.md` 自身 | 红队审查报告合法引用旧文本作为证据;grep 自检必须排除该文件 |
| 部分修复需合并相邻行(R1a+R1b,R1d+R1e) | 若同一表格内多行同一改动,可合并为 1 个 Edit |
| R2a 涉及多行改动(命令 + 行首补说明) | 跨行修改可一个 Edit 完成,old_string 覆盖完整 |
| R3 在已有文本后追加 | 找 unique 子串,append 注记;无需重新构造整段 |

---

## 5. 经验教训(给后续 刀)

1. **grep -F + bash 单引号 + `**` 转义有异常**:R2b grep 用 `grep -F 'mcp SDK 在 **S4.5 动工时**'` 首次未匹配;改用 Read 验证文件内容确认 Edit 已生效。后续 刀如遇类似 grep 异常,先用 Read 验证内容,不要反复试 grep 模式
2. **`&&` 链 grep 易断**:grep 返回 1(无匹配)会中断 `&&` 链,导致后续命令不执行。后续 刀用 `;` 串行,或显式 `|| true` 兜底
3. **同文件多个 Edit 应 unique old_string**:合并相邻行改动可减少 Edit 次数,但 old_string 必须严格匹配

---

## 6. 模板说明(给后续 Cline 红队审验 刀)

### 6.1 文件命名

| 本 刀 | 后续 刀 |
|---|---|
| `docs/track_b/clines-review-cycle-001.md` | `docs/track_b/clines-review-cycle-NNN.md`(NNN 递增) |

### 6.2 必填项

后续 刀请保留以下章节,内容可空但需存在:

- §0 元数据(cycle / 上游报告 / 涉及文件 / HEAD)
- §1 完成情况(改动清单 + file:line + 修复前后)
- §2 审验范围(自检 grep + git 命令 + 排除项)
- §3 Commit 信息
- §4 本刀非典型项(可选)
- §5 经验教训(可选)
- §6 模板说明(可引用本文件作为样板)

### 6.3 必做的最小验证

每个 刀 commit 后必须做:

```bash
# 1. 自检 grep(根据本刀 Cline Finding 构造)
grep -rn '<forbidden patterns>' docs/<scope> | grep -v <excluded files>

# 2. 行号定位 grep(为报告提供 file:line)
grep -n '<new content unique substrings>' docs/<scope>

# 3. git diff 范围
git diff <prev>..<this> -- docs/<scope>
```

退出码 1 = PASS(无匹配);退出码 0 = FAIL(有匹配 → 不能 commit)。

### 6.4 范围声明模板

后续 刀首段固定写:

```
**Scope**: 仅 docs/<scope>/ [N] 文件,不动 v1 / ece/ / [其他排除范围]。
```

---

**Cycle 001 报告结束。** 后续 刀 模板示范完成。
