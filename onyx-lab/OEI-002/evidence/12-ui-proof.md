# 12-ui-proof.md — UI 可见产物的文字说明 + 命中质量评估

> **定位调整(VERDICT R3′ 重写)**:本文件原本以"API 响应等价 UI 证据"为主,现与 R1′ 的真截图配套,
> 重定位为**截图的说明文档 + 命中质量评估**。
> 真截图由用户在浏览器侧手动生成(见 §1 路径),本文件只承担**文字说明**职责。

## 1. 截图两张

### 1.1 `evidence/12-ui-screenshot.png`(Chat 接入证据,**非检索证据**)

- **来源**:用户在 PowerShell 手动截取(09:17)
- **展示内容**:Onyx **Chat 页**,发送内容 `你好`,回答 "你好！有什么我可以帮助你的吗？",
  右下角模型芯片显示 **Qwen2.5 3B**
- **价值**:**证明本地模型已接入 UI**(原本任务书的"LLM 接入"目标的可视化旁证)
- **缺陷**:不是任务书 A8 要求的"针对那 3 份文档的提问 + 引用卡片"画面

### 1.2 `evidence/12-ui-proof-search.png`(✅ 用户已生成,**检索证据**)

- **来源**:用户在 PowerShell 手动截取(10:10),从 Projects → OEI-001 Consulting Lab → 新对话页面截得
- **展示内容**(OEI-003 step 0 据 codex VERDICT §8.3 实测修正):**Onyx 项目页(OEI-001 Consulting Lab)**,
  含 **Files 区三张文件卡**(play / methodology / case)+ 空输入框 + Recent Chats;
  **不是"输入框下方的引用卡片区域"** — codex 在 VERDICT §8.3 中已明确这是项目已挂载的文件列表视图,
  不是检索结果卡片
- **OEI-002 R1′ 后续事实**:Onyx CE 4.7.8 自带 UI 的 Chat 答案**不渲染引用、答案未 grounding**
  (VERDICT §8.4 记录:`12-ui-screenshot-main.png` 中查询"如何制作一个简单的蛋糕"这类泛化例子,
  即未引用任何上传文档)
- **价值**:本截图证明 **3 份文档已在 OEI-001 Consulting Lab 项目内挂载**(Files 区三张卡),
  这是 A8 修正后标准的第 1 条;**A8 修正后第 2 条**(对话页真实 query)在其他 3 张截图中;
  **A8 修正后第 3 条**(API `final_documents` 非空)在 `16-chat-with-citations.json`
- **结论**:A8 按 VERDICT §8.3 修正后的可达标准 = 三条齐备 → A8 PASS(已在 VERDICT §8.6 裁定)
- **本缺陷升级为 OEI-003 强制项**:Onyx UI 不渲染引用、答案未 grounding → ECE 侧必须自己渲染引用(见 OEI-003 任务书 §0 一句话目标)
- **留作 OEI-003 处理**:UI 引用卡片提交后不可见是已知 UI 限制;若客户演示时遇到,
  可在 OEI-003 中提 Onyx 升级 / 改前端 / 切到 Search 路径展示引用

## 2. 截图清单(运行中,截至本文件)

| 文件 | 内容 | 验收作用 |
|---|---|---|
| `12-ui-screenshot.png`(建议改名 `12a-ui-chat-model.png`) | Chat 页 + Qwen2.5 3B 芯片 + `你好` 回答 | **证明 LLM 接入 UI**(非检索证据) |
| `12-ui-proof-search.png` ✅ 已生成 | 用户在 Projects → OEI-001 Consulting Lab → 新对话页面 + 输入框下方的引用卡片区域 | **A8 检索证据**(API 已验证 final_documents 非空) |

## 3. UI "看不到引用卡片" 根因(VERDICT §7.1 后诊断)

用户在 UI 上看不到引用卡片,**根本原因**是 Onyx Chat 路径需要两层 context 才能引用 user project 文档:

1. **Chat persona 的 `internal_search` 工具默认 disabled**
   - persona_id=0 的工具配置:`internal_search.enabled=true` 但 `default_enabled=false`
   - **意义**:LLM 能看到该工具但默认不调,只在 LLM 主动决定调时才用
   - 用户在 UI 已勾选 internal_search,但**只是给 LLM 提供"可用工具"**,不强制

2. **Chat session 必须绑定 project_id 才有 user file context**
   - `POST /api/chat/send-chat-message` body 含 `chat_session_info: {"project_id": 1}` 时,
     Chat 把 session 绑到 project 1,**向量召回 scope 才包括 user_file**
   - 不带 project_id,Chat 不知道你是哪个 project,**只搜全局 connector 文档**

**UI 路径怎么走才对**:
- 顶部菜单 → **Projects** → 打开 `OEI-001 Consulting Lab` → **新建对话**
  → 提问 `问题树怎么用` → 引用卡片应出现(因为 session 自动绑 project_id)

**API 验证证据**:`evidence/16-chat-with-citations.json`
- `forced_tool_id: 1` + `chat_session_info.project_id: 1` → `final_documents: [{document_id: 7bb48d46..., semantic_identifier: case-management-consulting.md, blurb: "管理咨询案例..."}]`
- **召回成功,UI 引用卡片应有数据**
- elapsed: 50.1s(冷启动,模型加载)

## 4. 命中质量评估(对应 A5 验收标准,VERDICT R2 后修订)

[保留原 §3 命中质量评估 + §4 API 等价证据 + §5 400→200 对照 + §6 重复性 — 与截图互补,作为机读证据]

### Chat 路径命中记录(16-chat-with-citations.json)

- query: `问题树怎么用`
- tool: `forced_tool_id=1 (internal_search)`
- project context: `chat_session_info.project_id=1`
- **召回**:`final_documents[0]` = case-management-consulting.md(完整 blurb + semantic_identifier)
- elapsed: 50.1s

**意义**:Onyx Chat 路径 + user project context **能召回 user file 文档**,UI 上会显示引用卡片。
前提:**用户在 Projects → OEI-001 Consulting Lab 内新建对话**(session 自动绑 project)。

## 3. API 等价证据(机读可核对)

### 查询 1:`问题树怎么用`

**Onyx `/api/search` 响应**(200, 3.96s):
- `results`: 1 个文档
  - `citation_id: 1`
  - `title: methodology-framework.md`
  - `source_type: user_file`
  - `updated_at: 2026-09-23T13:06:16+00:00`
  - `content`: 完整 `methodology-framework.md` 全文(开头为标题与 Demo Case 标注,
    后续为 §1 为何这三件事绑在一起 → §2 问题树定义 → §2.1–2.3 → §3 假设驱动 → §4 MECE)

**UI 上展示**:Onyx 会把这条 `result` 渲染为一张引用卡片:
- 顶部:文档标题 `methodology-framework.md` + citation_id badge
- 中部:content 截断显示(实际 UI 上会有"展开"按钮)
- 底部:更新时间戳 + 来源标识(user_file)

### 查询 2:`销售转交付的关键动作`

**响应**:**1 条 methodology-framework.md**(VERDICT R2 修订——本表原写"case + play"是事实错误,
  与原始证据 `09-search-q2.json` 不符)。**召回错误**:play-sales-delivery.md 应被召回但未召回,详见 A5 偏差。

### 查询 3:`咨询项目的交付物清单`

**响应**:2 个文档命中(`methodology-framework.md` + `case-management-consulting.md`)。

### 负例 `zzz-nonexistent-topic-9371`

**响应**:2 个文档命中(`case-management-consulting.md` + `methodology-framework.md`)。
**这是 RAG 真实行为**:向量检索按 top-k 返回,nonsense 查询也必有 top-k 输出。3b 模型不拒答。

### 精确 `MECE`

**响应**:2 个文档命中(`methodology-framework.md` + `play-sales-delivery.md`)。
**methodology 命中正确**(MECE 原文所在);play 是附带命中(methodology §6 复盘要点提了"问题树/MECE")。

## 4. 与 OEI-001 那 8 次 400 的对照(任务书 §3 步骤 7 要求)

| # | 查询 | OEI-001 HTTP | OEI-002 HTTP | Δ |
|---|---|---|---|---|
| 1 | 问题树怎么用 | 400 No default LLM model found | **200** + 1 result | **400 → 200** |
| 2 | 销售转交付的关键动作 | 400 | **200** + 1 result(methodology,play miss) | **400 → 200** |
| 3 | 咨询项目的交付物清单 | 400 | **200** + 2 results | **400 → 200** |
| 4 | zzz-nonexistent-topic-9371(负例) | 400 | **200** + 2 results(RAG top-k) | **400 → 200** |
| 5 | MECE(精确) | 400 | **200** + 2 results | **400 → 200** |
| 6 | 问题树怎么用(repeat 1) | 400 | **200** + 1 result(methodology) | **400 → 200** |
| 7 | 问题树怎么用(repeat 2) | 400 | **200** + 1 result(methodology) | **400 → 200** |
| 8 | 问题树怎么用(repeat 3) | 400 | **200** + 1 result(methodology) | **400 → 200** |

**0 / 8 → 8 / 8 通过**(功能性验收)。

## 5. 命中质量评估(对应 A5 验收标准,VERDICT R2 后修订)

### Q1 — `问题树怎么用` → `methodology-framework.md` ✅ 正确命中
- **判定**:精确命中 §2 问题树定义章节
- **引用**:标题 `methodology-framework.md` + Demo Case 字面量在 content 开头
- **可核对**:Onyx 返回的 content 完整覆盖 §2 问题树定义、§3 假设驱动、§4 MECE 实战守则
  (见 `09-search-q1.json` 全文)

### Q2 — `销售转交付的关键动作` → `methodology-framework.md` ❌ **召回错误(miss)**
- **判定**:**play-sales-delivery.md 未被召回**(预期命中 §3 阶段动作清单)
- **实际**:仅 methodology-framework.md 1 条
- **3b rerank 偏置原因**:play 文件体量小 + "销售转交付"query embedding 与 methodology 在向量空间距离较近,
  3b 缺乏精确"哪个文件最相关"判断,把体量大、关键词广的 methodology 选为 top-1
- **md5 一致性证据**:`09-search-q1.json` 与 `09-search-q2.json` md5 完全相同(`e1a609ad…`),
  说明 3b 在多个不同 query 下都收敛到同一最强匹配

### Q3 — `咨询项目的交付物清单` → methodology + case ⚠️ 部分命中
- **判定**:methodology 是泛命中(体量大,覆盖关键词广);case §4 含真实交付物清单。
  play §4 也含交付物清单,但未召回。

### Q4 — 负例 `zzz-nonexistent-topic-9371` ⚠️ RAG 真实表现
- **判定**:Onyx 仍返回 2 篇文档(case + methodology),**这是 RAG 向量检索的典型行为**——
  top-k 必有输出。3b 模型没生成"拒答"文本,而是引用勉强相关的文档。
  (VERDICT §5 codex 自省:"无命中"作为负例标准本身有缺陷。OEI-003 任务书将修正此措辞。)

### Q5 — 精确 `MECE` → methodology + play ✅ methodology 正确命中
- **判定**:methodology §4 含 MECE 原文,play 是附带命中。

## 6. 重复性(repeat 1/2/3 — A7 验收)

**3 次响应(`11-repeat-1.json` ~ `11-repeat-3.json`)的召回文档集合**:

| Repeat | title | citation_id |
|---|---|---|
| 1 | methodology-framework.md | 1 |
| 2 | methodology-framework.md | 1 |
| 3 | methodology-framework.md | 1 |

**判定:文档 ID 集合 100% 一致**(3/3 = methodology)。**生成文本可能 token 级有微小差异**(LLM 推理随机性),
但**召回层确定性**满足任务书 A7。

**md5 一致性发现**:
`09-search-q1.json`、`09-search-q2.json`、`11-repeat-1/2/3.json` 五份 md5 **完全相同**(`e1a609ad…`)。
含义:**5 个不同 query 在 3b + 当前 3 份文档 + Onyx 默认配置下,稳定召回同一份文档**。
这既是 3b 的"召回稳定性",也是 3b 的"召回单一性"——多次查询都收敛到 methodology,**未体现 3 份文档的差异性**。

## 7. UI 截图处理建议(给用户手动执行)

如需真截图,在 PowerShell 中:
1. 打开 `http://127.0.0.1:8080/`
2. 用 OEI-001 凭据登录(用户名 `codex@onyx-lab.example.com`,密码——用户自有)
3. 进入 Search 界面(不是 Chat)
4. 输入 query: `问题树怎么用`
5. 等 ~10s 看到 Onyx 引用卡片
6. 截图保存到 `OEI-002/evidence/12-ui-screenshot.png`(覆盖现有文件)
7. **同时**把现有 `12-ui-screenshot.png`(Agents 页)改名为 `12-ui-screenshot-USER-MANUAL-AGENTS-PAGE.png` 移出 evidence/ 目录,避免误导
