# 00-oei002-carryover.md — OEI-002 → OEI-003 收尾结论

> OEI-003 任务书 §4 步骤 0 要求本刀开头的收尾动作

## 1. OEI-002 12-ui-proof.md §1.2 修订已落

`OEI-002/evidence/12-ui-proof.md` §1.2 已按 VERDICT §8.3 实际画面修正:

- **旧描述**:"输入框下方的引用卡片区域"(误判)
- **新描述**:"Onyx 项目页(OEI-001 Consulting Lab),含 Files 区三张文件卡(play / methodology / case)+ 空输入框 + Recent Chats"
- **结论保留**:A8 按修正后标准三条齐备 → A8 PASS(VERDICT §8.6 已裁定)
- **新加内容**:Onyx UI 不渲染引用 + 答案未 grounding 的硬缺陷 + 该缺陷升级为 OEI-003 强制项

## 2. Onyx UI 答案未 grounding 的证据

- `evidence/12-ui-screenshot-main.png`:对话页 query 真实,但回答举例"如何制作一个简单的蛋糕",
  **未引用任何 OEI-001 上传的咨询文档**
- `evidence/16-chat-with-citations.json`:Chat API 层 `message_start.final_documents` 含 3 份文档完整 blurb,
  **API 召回成立**,UI 未渲染 = 前端 bug
- 结论:Onyx CE 4.7.8 的 Chat UI **不渲染引用卡片到答案区**;`/api/search` **不返回生成答案**
  —— 两条路径都不能直接给客户演示"可追溯"

## 3. OEI-003 强制项

按 VERDICT §8.4:**ECE 侧必须自己渲染引用**(拿引擎返回的文档结构,由 ECE 自己的界面展示
query → 召回文档 → 片段),不得依赖 Onyx UI。该项为 OEI-003 的硬验收(A4),不是可选项。

## 4. 遗留风险(从 OEI-002 转出,OEI-003 知情)

| 项 | 状态 | OEI-003 处理 |
|---|---|---|
| 资源紧张(swap 7.7/8.0 GiB) | ⚠️ 持续 | OEI-003 状态页运行时若再触发 LLM,会进一步推高 swap |
| 3b 召回质量不足(q2 漏召 play、MECE 召回 methodology) | ⚠️ 已知 | OEI-003 mock 模式不依赖 LLM;onyx 模式如实展示召回结果(由 ECE 渲染,不掩盖) |
| Onyx UI 引用渲染缺陷 | 🔴 已转出 | OEI-003 A4 强制项 |

## 5. OEI-002 验收状态

- VERDICT §8 第三轮裁定:**PASS**(全部 A1–A12)
- 任务书 §5 收口完成:`DONE` 已建(2026-09-24T10:12:54)
- 28 个 evidence 文件
- codex 已签发 OEI-003 TASK.md v1(2026-09-24)
