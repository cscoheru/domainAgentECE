# Context Adapter Specification

> Phase: Gate 2
> 状态：接口契约 v1（MVP 实现以此为准）
> 原则：Domain 层只依赖本接口；底层可换 Glean / MCP / REST / DB / Mock

## 1. 设计原则

1. 接口用**领域语义**命名（文档、记录、任务），不用 Glean 语义（datasource、connector）。
2. 所有读方法必须支持**权限上下文**（acting user），Mock 阶段即模拟角色门控。
3. 所有返回的证据类结果必须带**溯源字段**（source / url / retrievedAt），供 Evidence 链展示。
4. 同步优先：MVP 全同步调用；触发类（subscribe）推迟到 POC。

## 2. 接口定义（TypeScript 表达，语言无关）

```typescript
interface ContextAdapter {
  // ---- 读：检索与实体 ----
  search(query: SearchQuery): Promise<SearchResult[]>;        // 全文+语义检索
  get_entity(ref: EntityRef): Promise<Entity | null>;          // 通用实体
  get_person(id: string): Promise<Person | null>;
  get_organization(id: string): Promise<Organization | null>;
  get_customer(id: string): Promise<Customer | null>;
  get_project(id: string): Promise<Project | null>;
  get_metric(id: string): Promise<Metric | null>;
  get_record(ref: RecordRef): Promise<BusinessRecord | null>;  // 工单/HR/变更等业务记录

  // ---- 写：动作 ----
  create_task(task: TaskInput): Promise<Task>;
  send_message(msg: MessageInput): Promise<DeliveryReceipt>;
  update_record(ref: RecordRef, patch: RecordPatch): Promise<BusinessRecord>;
}
```

## 3. 核心类型（摘要）

```typescript
interface SearchQuery {
  text: string;
  filters?: { type?: DocType[]; owner?: string[]; dateRange?: DateRange };
  actingUser: string;          // 权限上下文（必需）
  limit?: number;
}
interface SearchResult {
  id: string; title: string; snippet: string;
  source: string;              // 来源系统标识（"confluence" / "mock://docs/..."）
  url?: string;                // 溯源链接
  docType: DocType;            // policy | ticket | hr_record | review | report | contract | proposal...
  updatedAt: string;           // 新鲜度推理输入
  owner?: string;
  permissionRole: string[];    // 可见角色（供推理与 UI 提示）
}
```

## 4. 两个实现

### MockAdapter（MVP，`src/adapters/mock/`）

- 数据源：`mock/enterprise/` 下的结构化 Mock Enterprise（见 reference-case.md §Mock 数据规格）。
- `search()`：支持关键词+类型过滤+角色门控（安全类文档仅 security/compliance 角色可见）。
- `create_task()/send_message()`：写入内存 store，UI 可展示"已创建任务"回执。
- **强制要求**：方法签名、语义、返回结构与 GleanAdapter 完全一致。

### GleanAdapter（POC 阶段，`src/adapters/glean/`，先写骨架）

| 接口方法 | Glean 侧映射 | 证据 |
|---|---|---|
| search | Client API / Platform API search（带权限） | C04/C16 |
| get_person | Client API entities/people（待验证细节） | C16（部分） |
| get_record / get_entity | Indexing 自定义数据源（控制矩阵推送后检索） | C09（存在性），细节 UNKNOWN |
| create_task / send_message | Actions（连接器写回）/ 自定义 OpenAPI Action | C08/C09 |
| （备用通路） | Agent Toolkit search 工具 / Remote MCP | C17/C19 |

> GleanAdapter 中每一处"细节 UNKNOWN"必须在代码中显式 TODO 并引用 C 编号，禁止臆造。

## 5. 验收标准（MVP）

1. Domain 层 grep 无 `glean` 字样（CI 检查）。
2. 切换 Mock→Glean 只改一个工厂函数（依赖注入点在 application 层）。
3. Demo 中 Evidence 面板的每条证据都能点出 source/url/updatedAt。
