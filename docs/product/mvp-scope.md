# MVP Scope — EvidenceIQ v0.1

> Phase: Gate 4
> 硬性约束（PRD #19）：1 Persona / 1 Problem / 1 Workflow / 1–2 Agents / 1 Dataset / 1–3 Tools / 1 Output / 1 Outcome

## 1. In Scope（做）

| 项 | 内容 | 数量 |
|---|---|---|
| Persona | GRC 合规经理 | 1 |
| Problem | SOC2 Type II 续证的期间证据收集与充分性判断 | 1 |
| Workflow | Ingest→Map→Retrieve→Reason→Act→Approve→Package | 1 |
| Domain Agents | Control Intake Agent + Evidence & Gap Agent | 2 |
| Reference Dataset | NimbusWorks Mock Enterprise（含 4 个埋入缺口） | 1 |
| Tools（ContextAdapter） | search / get_record / create_task | 3（+get_person 仅用于派工查询） |
| 核心输出 | Audit-Ready Evidence Pack（Matrix + Gap List + 派工回执） | 1 |
| Business Outcome | 审计准备 3–4 周→≤3 天；缺口提前 4–6 周 | 1 |
| 本体 | SOC2 CC 域 12 个代表性控制项 | 1 套 |
| 评估 | 回归案例 10–20 个（五维评分） | 1 套 |
| UI | 单页工作台：输入审计范围 → 运行 → Reasoning 面板 / Evidence Matrix / Gap List / 派工回执 / 审批按钮 | 1 页 |
| 上下文层 | MockAdapter（角色门控）+ GleanAdapter 骨架（TODO 标注 C 编号） | 2 |

## 2. Out of Scope（不做，明确禁止）

- ❌ 多租户 / 用户系统 / 登录（actingUser 写死演示角色 + 切换开关）
- ❌ 权限系统（Mock 角色门控模拟；真权限留给 Glean 继承，C06）
- ❌ 计费 / 部署平台 / K8s / 微服务 / 消息队列
- ❌ 自研向量库 / 自研搜索（Mock 用内存过滤检索）
- ❌ ISO27001 / 多框架切换（本体留扩展点，不做）
- ❌ TPRM 双向问卷（C9，第二阶段）
- ❌ 全量 SOC2 百余控制项（只做 12 个代表性控制项）
- ❌ 真实 Glean 集成（只写骨架 + TODO）
- ❌ Agent 框架引入（LangChain 等，见 agent-runtime.md）
- ❌ 移动端 / 国际化

## 3. 技术栈（Round 2 实现依据）

| 层 | 选型 | 理由 |
|---|---|---|
| 应用 | Next.js（App Router）+ TypeScript | UI + API 单体，演示部署最简 |
| Domain | 纯 TS 模块（ontology JSON + 规则函数 + Agent prompt） | 零框架依赖，可测试 |
| LLM | OpenAI 兼容 SDK（环境变量配供应商） | 不锁定厂商；规则优先少调 LLM |
| Mock 数据 | `mock/enterprise/` 结构化 JSON | 内部关系一致（见 reference-case.md） |
| 评估 | Node 脚本 + JSON 案例 | 领域 CI |
| 部署 | 单进程本地/单容器 | Demo 用 |

## 4. 目录结构（Round 2 建立）

```text
/src
  /domain
    ontology/          # soc2-cc.json（控制项-证据类型-责任人）
    reasoning/         # sufficiency / freshness / coverage / routing
    workflows/         # audit-prep pipeline
    agents/            # control-intake / evidence-gap
    evaluation/        # runner + cases
  /adapters
    /glean             # 骨架（TODO + C 编号）
    /mock              # MockAdapter + 角色门控
  /application
    services/          # orchestration + adapter 工厂
  /ui                  # Next.js 页面与组件
/mock/enterprise       # NimbusWorks 数据
/docs                  # 本轮文档
```

## 5. 验收清单（Gate 4 完成定义）

1. `npm run demo` 一条命令跑通完整 workflow 并输出 Evidence Pack
2. `npm run eval` 输出回归报告（五维分数）
3. CI：`src/domain/**` 无 glean/mcp 字样
4. 15 分钟 Demo 走查通过（对照 demo-script.md）
5. 全部输出标注 "Reference Case / Demo Case"，无真实客户冒充
