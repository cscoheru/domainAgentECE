# 演示数据清理记录（Onyx project `id=1`）

> 执行：codex ｜ 日期：2026-09-25 ｜ 授权：用户（"同时清理演示文件"）
> 目的：OEI-006/007/008 三刀的测试把演示项目塞满了探针文档；叠加 Onyx `top-k≈2`，Library 的"引擎召回"分组打开就是一堆 `oei007-xx-probe` 噪声，直接影响演示观感。

## 1. 清理前

`GET /api/user/projects/files/1` → **19 份**：

- **保留 3 份（真文档）**：`case-management-consulting.md`（chunk 3）、`methodology-framework.md`（chunk 4）、`play-sales-delivery.md`（chunk 4）
- **删除 16 份（测试产物）**：`o8-test.md`×4、`o7-en.txt`、`verify-doc.md`、`probe.txt`、`oei007-binary-oei007docx*.docx`×2、`oei007-closed-loop-probe.txt`×2、`oei007-08-repeat.txt`×2、`oei007-port-probe.txt`×2、`oei007-probe.md`

## 2. 操作与一个值得记住的坑

**第一次尝试失败且"静默"**：直接 `DELETE /api/user/projects/file/{user_file_id}` 对**有项目关联**的文件**不会删除**，只返回

```json
{"has_associations": true, "project_names": ["OEI-001 Consulting Lab"], "assistant_names": []}
```

HTTP 状态是 **200**——也就是说"看起来成功，实际没删"。（读容器内 `/app/onyx/server/features/projects/api.py:517-575` 确认：这是**确认预览**语义，不是错误。）

**正确顺序是两步**（每份文件都要走）：

```bash
# 1) 先解绑项目关联 → 204
curl -X DELETE -b "$CK" "http://127.0.0.1:8080/api/user/projects/1/files/<user_file_id>"
# 2) 再删用户文件 → 200（触发异步向量清理）
curl -X DELETE -b "$CK" "http://127.0.0.1:8080/api/user/projects/file/<user_file_id>"
```

16 份全部 `unlink=204 / delete=200`。

> **给后续刀的提示**：如果 ECE 将来要做"删除知识"的能力，必须按这个两步语义实现，否则会出现"接口 200 但内容还在"的假成功。这条建议登记给 OEI-009 之后的相关刀。

## 3. 清理后验证

| 检查 | 结果 |
|---|---|
| `GET /api/user/projects/files/1` | **3 份**，且全部 `status=COMPLETED`（`play-sales-delivery.md` / `methodology-framework.md` / `case-management-consulting.md`） |
| `POST /api/search`「oei007 probe」 | 只返回那 3 份真文档（探针已从检索面消失） |
| `POST /api/search`「OEI-007 Closed-Loop Probe」 | 同上 |
| `POST /api/search`「问题树怎么用」 | `methodology-framework.md`（原演示行为恢复） |

## 4. 防复发（转出给 OEI-009）

测试上传应使用**独立的 scratch project**（`POST /api/v1/consulting/documents` 已支持 `project_id`），而不是共用演示项目。**这条要写进 OEI-009 的任务书**，否则下次跑测试又会把演示项目塞满。
