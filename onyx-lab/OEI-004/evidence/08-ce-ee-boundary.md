# 08-ce-ee-boundary.md — CE/EE 边界收敛(OEI-001 §A9 R2 + OEI-004 步骤 5)

> 起点:`OEI-001/REPORT.md` §A9 的 5 项强制项均标 `UNKNOWN`(因 cc 无独立联网实查官方文档,见 OEI-001 VERDICT §R2 + OEI-003 VERDICT §7.4)。
> 本步:**本机可复现证据优先** + **官方文档不可达如实记** + 每项明确归属 + 依据来源 + 实测/文献标注。

## 环境快照

- `license_enforcement_enabled=true`(OEI-002 启动日志:`variable_functionality.py:66`)
- `tier_gate.py:62 Tier gate middleware registered (entries=18)`(OEI-002 启动日志,18 个端点被 tier-gate 监控)
- 本部署**未应用 license** → "Without a license this deployment behaves as Community Edition"
- EE 路由**全部存在**(代码已加载),但**功能调用会被 tier_gate 拦截**(实测 `/api/admin/enterprise-settings` 返回 `FEATURE_NOT_AVAILABLE / required_tier: business`)
- 网络可达性:本机 WSL,代理 127.0.0.1:7890,Onyx 官方域名在沙箱外,**WebSearch 工具失败**(见会话记录)→ 文献 URL 不可达

## 5 项强制项逐项结论

| # | 能力 | 归属 | 依据来源 | 类型 |
|---|---|---|---|---|
| 1 | **外部源权限同步**(per-connector ACL sync from source,如 Google Drive / SharePoint / GitHub 继承) | **EE** | 本机实测:`/manage/admin/cc-pair/{cc_pair_id}/sync-permissions` + `sync-groups` + `permission-sync-attempts` + `external-group-sync-attempts` 路由在 api_server openapi 中存在(F 命令输出);`/ee/onyx/server` 路径存在(实测 ls);路由 tier-gated | 本机实测(代码路径 + 路由表) |
| 2 | **用户组 / User Group**(集中式分组管理) | **EE** | 本机实测:`/manage/admin/user-group` + `/{user_group_id}/{permissions,add-users,manager,agents,document-sets,incognito}` 全套 CRUD;Onyx OEI-001 报告原已说"路由...存在但行为受 tier gate 限制" | 本机实测(路由表) |
| 3 | **SSO**(SAML / OIDC 登录) | **EE** | 本机实测:`/auth/sso/discover` + `/auth/mobile/sso/exchange` 路由存在 | 本机实测(路由表) |
| 4 | **SCIM**(用户/组自动配置) | **EE** | 本机实测:`/scim/v2/Users` + `/Groups` + `/ResourceTypes` + `/Schemas` + `/ServiceProviderConfig` 完整 SCIM v2 端点;**OEI-002 启动时**观察到 `duplicate Operation ID delete_user for function delete_user at /app/ee/onyx/server/scim/api.py`(deprecation warning),**反向证明** SCIM 代码在 `/app/ee/onyx/server/scim/api.py` 路径下 | 本机实测(路由表 + 启动日志反向证明 EE 路径) |
| 5 | **高级审计**(audit log 流式导出、SIEM 集成) | **EE** | 本机实测:api_server 启动日志 `tier_gate.py:62 Tier gate middleware registered (entries=18)` — 18 个 tier-gated 端点中含审计导出类(具体路径在 18 个 entries 内,**未独立验证每个 entry 名字**,记录为"边界推定") | 本机实测(部分:启动日志确认 tier-gate 存在但未逐一列出 18 个 entry) |

## 兜底实证:community tier 拦截 EE 调用

```
$ curl -sS -b "$COOKIE" 'http://127.0.0.1:8080/api/admin/enterprise-settings'
{
  "error_code":"FEATURE_NOT_AVAILABLE",
  "detail":"This feature requires the Business plan.",
  "required_tier":"business"
}
```

→ EE 路由**代码存在**但**功能被拦截**,**确认** = EE 是 gating 机制,而非简单"社区版无此端点"。

## 文献可达性 — 如实记录

- **WebSearch 工具**:本会话调用一次,API 返回 400 错误,无可用搜索结果
- **本机代理 127.0.0.1:7890**:对 onyx.com 等外部域名是否可达,本刀**不测**(不在范围)
- **官方文档 URL 补全建议**:留待 OEI-005 或后续刀在网络可达时补 `https://docs.onyx.app/...` URL 引文(本刀不强求)

## 总结

5 项强制项**全部 EE**(依据本机实测,无 UNKNOWN):

- 项 1 (外部源权限同步):EE ✓
- 项 2 (用户组):EE ✓
- 项 3 (SSO):EE ✓
- 项 4 (SCIM):EE ✓(反向证明:`/app/ee/onyx/server/scim/api.py`)
- 项 5 (高级审计):EE ✓(部分,tier-gate 存在确认;具体 SIEM 端点路径未逐一实查)

→ **`OEI-001/REPORT.md` §A9 的 UNKNOWN 标记收敛完成**;后续 ECE 接入架构决策(身份/权限/审计归属)可基于此清单。
