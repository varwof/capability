# EMILIA → CLC evidence projection probe（2026-10-17）

把 EMILIA 的证据侧对象按"投影"方式映射进 CLC，并**实际求值**，用来检验
投影模型（Observation / Fact / Requirement / Result）是否够用。

不是 conformance 套件，是一个探针：输入取自已发布草案的公开示例，输出见
`out-probe.txt`。

## 输入及其出处

| 对象 | 出处 | 检查日期 |
|---|---|---|
| `EP-AEC-REQUIREMENT-v1` 示例（`treasury-wire-evidence@7`） | `draft-schrock-ep-authorization-evidence-chain-08` §4 | 2026-10-17 |
| 证据事实的形态（verified / subject / issued_at） | `draft-schrock-action-evidence-boundary-07` §5.2、§5.6 | 2026-10-17 |
| 动作形态（`tool.call.1`，`occurrence_id` 可选；只测 CLC material projection，不解析 CAID wire identifier） | `draft-schrock-canonical-action-identifier-05` §4.7 | 2026-10-17 |

运行：

```sh
(cd ../register && go run ./cmd/emilia-projection-probe)
```

## 映射规则（探针实现的）

| AEC 字段 | CLC | 说明 |
|---|---|---|
| `expression` | `"(<expression>) AND <binding-role>…"` | 原表达式整体加括号，再与派生 binding 角色合取 |
| `freshness_sec[role]` | `constraints += {role, varwof/evidence-v1:freshness:sec:<n>}` | 每角色一条；角色必须通过 pinned RoleMap |
| `role_constraints[type=distinct-subject-quorum]` | `constraints += {role, quorum:distinct:<threshold>}` | `component_type` 必须通过 pinned RoleMap |
| `requirement_id` | `requirement_id` | 原样 |
| `@version` | `CLC-REQUIREMENT-v1` | 版本改写 |
| `purpose` | `purpose` | 保留为描述性字段，不参与求值 |
| `status_required` | `RequiredNativeChecks` + `NativeCheckResults` | AEB/载体负责状态查询，不作为证据 Fact；role 必须通过 pinned RoleMap，每一项检查、每一个分量都必须有一条显式结果记录 |
| `required_bindings` | 新角色 `clc:evidence-binding:<base64url(uint32be(len)||part…)>` | native verifier 输出派生事实；原 `ep-quorum` 和 `policy-permit` 均保留 |
| `subject_id_source` | `RequiredNativeChecks` | AEC-08 要求值为 `native-verifier`；CLC 不自行推断 |

派生 binding 角色不是哈希，而是完整有序三元组
`(from_type, relation, to_type)` 的可逆、带长度前缀编码：命名空间
`clc:evidence-binding:`，payload 为三个 `uint32be(len) || utf8` 片段，再做
无填充 base64url。三元组各段必须非空、合法 UTF-8、且落在 AEC 标识符字符集
`1*( ALPHA / DIGIT / "." / ":" / "-" / "_" )` 内；编码后超过 256 字节直接
拒绝，不截断。长度前缀保证即使 `:` 出现在分量内也不会产生歧义碰撞。

`out-probe.txt` 同时打印两个 requirement digest：

- `source requirement digest`：投影前完整 AEC 对象（严格 JSON、拒绝重复成员）
  的 JCS SHA-256；
- `projected requirement digest`：改写并验证后的最终 `CLC-REQUIREMENT-v1`
  对象的 CLC digest。

两者都是 report 字段，不是 `CLC Requirement` 或 `Satisfaction` 的成员。

## 投影本身的三语言一致性（`EMI-PROJ-*`，19/19 PASS）

`probe.py`、`probe.mjs` 现在**自己实现** AEC → CLC-REQUIREMENT-v1 的投影
（freshness/quorum 约束、binding 角色编码、JCS 摘要），并与 Go 及共享 fixture
比对：

| case | 内容 |
|---|---|
| `EMI-PROJ-001` | 投影出的 CLC requirement 与 fixture 逐字节 JCS 一致 |
| `EMI-PROJ-002` | source requirement digest 一致 |
| `EMI-PROJ-003` | projected requirement digest 一致 |
| `EMI-PROJ-004` | 未知 AEC 成员被拒绝 |
| `EMI-PROJ-005` | 未 pin 的 role 被拒绝 |
| `EMI-PROJ-006` | 投影后表达式超过 CLC 512 字节被拒绝 |
| `EMI-PROJ-007` | 未知 role constraint 类型被拒绝 |
| `EMI-PROJ-008` | `subject_id_source=presenter` 被拒绝 |
| `EMI-PROJ-009` | binding 分量为空被拒绝 |
| `EMI-PROJ-010` | quorum 阈值 < 2 被拒绝 |
| `EMI-PROJ-011` | 非法表达式语法被拒绝 |
| `EMI-PROJ-012` | role_constraints 内未知成员被拒绝 |
| `EMI-PROJ-013` | 负 freshness 被拒绝 |
| `EMI-PROJ-014` | 未知 AEC `@version` 被拒绝 |
| `EMI-PROJ-015` | 缺少 `requirement_id` 被拒绝 |
| `EMI-PROJ-016` | binding 标识符含非法字符被拒绝 |
| `EMI-PROJ-017` | binding 编码后角色超过 256 字节被拒绝 |
| `EMI-PROJ-018` | `required_bindings` 内未知成员被拒绝 |
| `EMI-PROJ-019` | 未 pin 的 `status_required` role 被拒绝 |

这是“投影规则”而不是“求值结果”的跨语言证据：三份实现独立生成同一个
canonical requirement 与两个 digest，并对未知成员、未 pin role、超长表达式
做出相同的拒绝。Python/TS 的实现也做了 AEC 成员闭合检查、标识符字符集检查和
UTF-8 字节序排序。

## 实际求值结果（`out-probe.txt`，36/36 PASS）

| # | 事实 | 期望 | 实际 |
|---|---|---|---|
| 1 | 两名已验证批准 + 一份许可 + 派生 binding 事实 | SATISFIED | SATISFIED |
| 2 | 其中一名批准 `verified=false` | UNSATISFIED | UNSATISFIED（`quorum:distinct_subjects=1<threshold=2`） |
| 3 | binding 事实很新，但一条批准已超过 300s | UNSATISFIED | UNSATISFIED（`freshness:stale`） |
| 4 | 原 quorum/permit 都在，但没有派生 binding 事实 | UNSATISFIED | UNSATISFIED（`requirement:expression_false`） |
| 5 | 事实按 `component_type` 字面标注为 `ep-human-authorization` | UNSATISFIED | UNSATISFIED（`requirement:expression_false`） |

CLC 动作身份（CAID 的 `tool.call.1` 形态 → CLC §4.2；不解析 CAID wire identifier）：

| 场景 | 期望 | 实际 |
|---|---|---|
| 同 tool+args，观测里多一个 `occurrence_id` | MATCH | MATCH（非 material 字段不携带身份） |
| args 的 amount 改成 3001 | NOT_EQUIVALENT | NOT_EQUIVALENT |

## 探针暴露的跨层义务

1. **角色命名不一致**：表达式用的是 `ep-quorum`，而 `role_constraints.component_type`
   写的是 `ep-human-authorization`。草案没有说明"哪个事实类型填充 `ep-quorum`
   这个表达式角色"；探针把 quorum 约束挂到 `ep-quorum` 上，并把这一假设列出来。
   ⇒ binding profile 必须给出角色映射表，不能留给实现猜。
2. **`status_required`**：要求"新鲜的状态结果"，CLC 没有对应约束类型；只能由
   AEB/载体执行，并作为 `RequiredNativeChecks` 返回。该检查不能由证据 Fact
   代替。`RequiredNativeChecks` 只说明**应该跑什么**，不说明跑过没有；report
   必须为每项必需检查、每个分量给出一条显式 `NativeCheckResult`，成功的检查
   也要有记录。空的不可用列表不构成任何证明。结果使用封闭的四种 outcome：

   | outcome | 含义 |
   |---|---|
   | `success` | 检查已执行且通过；只有它可能先于 eligible Fact |
   | `failed` | 检查已执行且该构件不合格；**已核实的 revoked 状态是 `failed`** |
   | `unavailable` | 必需的来源或结果无法取得或求值 |
   | `not_applicable` | profile 明确认定该检查不适用 |

   四者必须保持区分。每条记录都绑定 check ID、native component type、构件证据
   摘要（同一类型有多个构件时用于区分）、verifier 与其 profile 摘要、核验
   时间；即使检查不可用或不适用，也不能丢掉构件身份。`success` 和 `failed`
   还必须绑定 trust snapshot 摘要、status snapshot 摘要与 freshness 决策。
   `unavailable` 或 `not_applicable` 必须给出稳定原因；实际取得的 trust、status
   或 freshness 材料应保留，但不得为不存在的快照编造摘要。记录可用时还携带
   AEC replay 摘要。report 级的 `NativeChecksComplete` 只在 `status_required`
   的每项检查都有可归属结果时为 true；它是 report 元数据，不是 CLC verdict，
   且只证明调用方提交的构件结果完整，native profile 仍须对未提交的漏项负责。
   CLC 不做任何状态查询或刷新。
3. **`required_bindings`**（`policy-permit -permits-> ep-quorum`）：CLC
   不直接比较事实间关系，因此由 native verifier 把它归一化为
   一个由三元组稳定派生的角色。requirement 改写为
   `(ep-quorum AND policy-permit) AND <binding-role>`；关系事实只补充，
   不替代 quorum。若 verifier 不输出该事实，表达式为假。
   - 派生事实绑定 source/target artifact 摘要、action、verifier/profile 与
     trust 结果、trust-snapshot 摘要、distinct subjects、原始证据时间、完整原始
     requirement digest、policy generation 和 status 快照；verifier/profile 与
     trust context 直接绑定。closed tuple 的成员与编码以 profile §5.1 为准。
   - freshness 取原始证据和状态，而不是关系重算时间；重算关系不能刷新旧批准。
4. **`subject_id_source`**：AEC-08 要求主体标识来自 `native-verifier`；CLC
   只消费受保护事实中的 `subject`，不自行推断。

### binding identity 派生检查

`out-probe.txt` 还检查 canonical relation tuple 的 base64url SHA-256 与固定
subject 一致，并分别修改 source artifact、target artifact、action 和 status
快照，确认四种修改都会改变 subject。

目标工件集合按成员各自的 JCS 字节升序编码；到达顺序不属于编码，重复成员
拒绝。元组只有一个 `to.type`，因此集合成员的类型必须一致——混类型集合会被
拒绝，否则 `to.type` 只能取自某个成员，subject 又会依赖顺序。`EMI-BIND-007`
用相反顺序重算元组，确认 subject 不变；`EMI-BIND-008` 拒绝重复成员；
`EMI-BIND-009` 拒绝混类型集合；`EMI-BIND-010` 拒绝空集合。缺少 `type` 的成员
同样被拒绝。三个探针实现同一规则。

CLC core 把 binding subject 当作不透明值：只要 native verifier 给出
`verified=true` 的 `clc:evidence-binding:…` fact，CLC 就接受该 role。因此
source/target/action/status 的实际绑定由 native verifier 负责，不由 CLC
重新计算。probe 用 `EMI-BIND-006` 明确记录这条边界，避免把 role 在场误写成
CLC 已验证关系内容。

`failed`、`unavailable` 与 `not_applicable` 在报告中保持区分，且不会因为某个
`OR` 分支已满足而消失：不合格的分量不产生 eligible Fact，其 native 原因保留在
report 中；在 `A OR B` 下，若 B 可用且满足表达式，结果仍可为 `SATISFIED`，但 A
的结果（不可用，或已核实的 revoked 记为 `failed`）不会消失。显式声明的 role
constraint 失败或 required binding 无法建立时，整个 requirement 仍为
`UNSATISFIED`。若 `status_required` 的某项检查没有结果，report 表达式仍可能由
其余 eligible facts 满足，但该 `Satisfaction` 不得表述为最终 native 校验，
且 `NativeChecksComplete` 为 false。证据侧不产生 `allow_unresolved`；该 verdict
只属于授权侧。

Python 和 TypeScript runner（`probe.py`、`probe.mjs`）读取 register 仓库中的
同一 `emilia-binding-fixture-v1.json`，输出同样的 45 个 case ID、
`want` 和 `got`。schema 与完备性的 9 个用例（`EMI-BIND-011`、
`EMI-SCHEMA-001..005`、`EMI-COMP-001..003`）读 `emilia-binding-fixture-v2.json`：
载体必须钉住状态 schema 的摘要，结果不能声明与载体不同的 schema，且
`SATISFIED` 只有在 native 检查完整且全部成功时才成立。Go 通过 `go:embed` 读取该 fixture；求值事实也来自
fixture 的 `evidence_cases`，三份实现不再各留一份。每个 case 行都满足
`want == got`（`want` 是完整期望，而不是只写 verdict 前缀）。

## 结论

投影模型对 **freshness / quorum / 表达式组合** 是够用的。关系型证据绑定
（`required_bindings`）通过 native-verifier 派生事实处理，且不删除或替代原始
quorum。status、revocation、subject resolution 和关系重算不得刷新旧证据的规则
仍是 binding profile 的显式义务。CLC 验证 role、`verified` 和约束；relation
tuple 的身份及来源由 native verifier 和 binding profile 验证。
