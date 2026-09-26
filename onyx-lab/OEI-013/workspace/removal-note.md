# 对照文档移除说明（OEI-013）—— **状态：用户决定暂缓，未执行**

> 记录时间：2026-09-26 ｜ 记录人：cc ｜ 决策人：用户

## 1. 结论先行：**本次不删除**

TASK.md §3.1 写「用户已拍板：移除该对照文档」，但用户在本刀执行期间
（2026-09-26，cc 就"是否执行这次不可逆删除"当面征询时）明确选择了
**「先不删，只做只读取证」**。

因此：
- **未执行**两步删除；Onyx 项目 1 仍是 **4 份**文件；
- 本刀的检索重测在**当前语料**上做，并**如实报告**（对照文档仍在霸榜）；
- 演示 UI / 演示脚本 / 常驻起链**照做**（它们不依赖这次删除）；
- 删除与否留待用户看过重测数字后再决定。

## 2. 待删对象（用户点头后可执行）

| 项 | 值 |
|---|---|
| 文件名 | `ece-df16d19c9e7b-oei009-comparison-restricted.md` |
| Onyx project | `id=1`（OEI-001 Consulting Lab） |
| `user_file_id`（两步删除用它） | `6138305b-0f40-468f-a1c8-bdea6f68d424` |
| `file_id` | `1d3c880a-91fd-4069-9133-4bc0b9d2292a` |
| 内容 | 「员工报销政策与发票审核流程」——与咨询域**无关**的合成对照文档 |
| 原用途 | OEI-009 的**权限反差演示材料**（`restricted` 档，用来演示"同一 query、两个身份、不同召回"） |

**为什么要删**（OEI-012 实测，`OEI-012/evidence/04-retrieval-matrix.json`）：
72 次运行里它 **61 次进 top-3、54 次是唯一结果**，把三份真咨询文档全部挤出召回；
9 条 hit query 的目标文档**一次都没进前 3**（hit@1 = hit@3 = 0%）。

## 3. 执行两步删除的确切命令（**仅供用户决定后使用**）

> 语义来自 `onyx-lab/重启必读/DEMO-DATA-CLEANUP-2026-09-25.md` §2：
> 直接 `DELETE .../file/<id>` 对**有项目关联**的文件**不会删除**，只回 `has_associations: true`
> 而 HTTP 仍是 **200**（"看起来成功，其实没删"）。**必须先解绑再删。**

```bash
CK=/home/fisher/.onyx-lab/.secrets/admin-cookies.txt
UFID=6138305b-0f40-468f-a1c8-bdea6f68d424
# 1) 先解绑项目关联 → 期望 204
curl -s -b "$CK" -X DELETE "http://127.0.0.1:8080/api/user/projects/1/files/$UFID" -w 'unlink=%{http_code}\n'
# 2) 再删用户文件 → 期望 200（触发异步向量清理）
curl -s -b "$CK" -X DELETE "http://127.0.0.1:8080/api/user/projects/file/$UFID" -w 'delete=%{http_code}\n'
# 3) 验证 → 期望 3 份
curl -s -b "$CK" "http://127.0.0.1:8080/api/user/projects/files/1" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))"
```

**如何恢复**：`onyx-lab/OEI-009/workspace/step26_demo_falsifiable.py` 会重建它
（连同 ACL 行）。**注意**：该脚本是 OEI-009 的**历史证据工具**，**不在本刀授权改动范围内**，
所以它今天仍能重建这份文档——这是一处**已知残留风险**，已写进 REPORT 的建议段。

## 4. 本刀实际做了什么（替代动作）

没有删文件，但把"删了会怎样"变成了数字：
- 在**当前语料**上重跑 012 的口径（原始引擎层 + 过滤后路径，各 N=3 × 两档）；
- 过滤后路径尤其关键：对照文档是 `restricted` 档，**在真实 consulting library 路径会被权限过滤滤掉**
  → 可以量化"产品可见层"到底是"露出真文档"还是"啥都没有"。
- 见 `evidence/02-retrieval-rematrix.json`、`evidence/03-retrieval-filtered.json`。
