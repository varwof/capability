# 13 · 一致性

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §12（12.1 Language Revision）、附录 B
> 本页是便于阅读的指南。如有冲突，以规范为准。
> 状态：Preview — 不供生产环境使用。

## 速览

CLC-v1 定义了**三个一致性类别**。**CLC-A**（授权侧）是基线；**CLC-D**（委派包含）是可选类别，叠加在 CLC-A 上；**CLC-E**（证据侧）**已实现并由语料库锁定，但未声明**。诚实原则是：由同一作者维护的实现之间结果一致，只能算回归测试，不能算独立验证。

## 1. 三个类别（§12）

| 类别 | 包含内容 | 状态 |
|-------|------------------|--------|
| **CLC-A** | §3 文法、§6.1 entailment、§7 intersection、§9 decision、`unknown_constraint`/`invalid_constraint`、`allow_unresolved` + 增量式 `unresolved` 通道（§8.4）、多授权聚合（§9.1）、稳定原因代码（§9.2）；必须通过 `vectors.json`（123）和 `property-cases.json`（1184） | **已声明 — v1 基线** |
| **CLC-D** | 带有序各层的 `Contains(parent, child)`、两个稳定关系代码（`child_exceeds_parent`、`params_not_narrower`）、配置契约（§13.8.1）、`AuthorizeWithChain`（修订 CLC-1.13）；必须通过 `containment-vectors.json`（64）和 `authorize-chain-vectors.json`（15）。第三个代码 `delegation_mode_not_narrower` 属于绑定配置预检，绝不属于 `Contains` | **已声明** |
| **CLC-E** | §6.4 match、§10 satisfaction、证据侧约束文法、`evidence-vectors.json`（32） | **已实现，未声明** |

**为何暂不声明 CLC-E**（§12）：不是材料不足，而是出于**原则**——一致是最低门槛，而门槛是两个*独立*实现（P12）。同一作者实现的一致性达不到门槛；证据侧语义还在与 EMILIA 联合审查，因此审查完成前不作声明。未来如要声明，所需义务已在 §12 中逐项列出：采用三值求值，`unknown` 绝不能视为满足；资格只能来自完整性受保护的原生结果；`ActionId` 是所声明材料投影的摘要；采用封闭的 `CLC-REQUIREMENT-v1`；根据依赖方配置生成要求；通过 `evidence-vectors.json`。

仅实现 CLC-A 的实现不得声明 CLC-E。

## 2. 一致性语料库（§12、附录 B）

位于 `capability/data/_vectors/clc-v1/` 的两个机器可读测试套件用于检验 CLC-A：

- **`vectors.json`** — 123 个向量，对应附录 B（机器可读的 `kind` 分组不同于附录的语义 B.1–B.6 分组；两种计数都可从语料库复现）：`kind=entail`（47）、`kind=decide`（50）、`kind=intersect`（17）、`kind=syntax`（9）。CLC-1.15 的三个跨型审计向量（`intersect-011/-012/-013`）是 B.4 表之外对 intersect 组的增量。
- **`property-cases.json`** — 1184 个用例，锁定 §7 meet 定律、标识符收窄和来源顺序无关性。

CLC-D 增加 `capability/data/_vectors/clc-d/containment-vectors.json`（64）、`containment-property-cases.json`（784 个用例 × 39 个共享操作，前向闭包：`Contains(P,C) ∧ Entails(C,o) ⟹ Entails(P,o)`）、`containment-crosswalk-vectors.json`（44）和 `authorize-chain-vectors.json`（15）。证据侧提供 `evidence-vectors.json`（32）。

其他生成并锁定的语料库：`param-bounds-vectors.json`（43）、`param-bounds-meet-vectors.json`、`constraint-union-vectors.json`（12）、`constraint-union-collation-vectors.json`（2）、`resolve-vectors.json`（26）、`crosswalk-vectors.json`（13，双向：AEB crossing 成员及 OAuth RAR、AIC-JWT DA、AEG、UCAN、delegation chain → CLC grants 五种外部表示）。

**通用性经过检验，而非仅作声明**（§12）：配置只是外部格式所有者编写的少量映射代码；核心不为其中任何一种而修改。实现不得重新定义语义、接受 v1 禁止的通配符，或在规范化过程中放宽边界。

## 3. 实现独立性（诚实的范围，§12/§13.7）

仓库 README 中列出的三个实现（Go、Python、TypeScript）**不是独立证据**：它们由同一作者维护，其一致性是对规范的回归测试，不是第三方验证。在出现独立实现之前，一致性声明的范围仅限于**“同一作者、三种语言、一套语料库”**。审查者应把单一作者的一致性视为规范*可以实现*的证据，而不是规范已被独立*解释*的证据。

**实验性相邻工作不属于 CLC**（§12）：WIT/WPT 互操作研究（`varwof/aic-jwt`）实现了本修订拒绝的更宽通配符语法（`**`、`{a,b}`、`[a-z]`），以 `unsupported_wildcard` 处理；它不是 CLC-A，也不得被如此引用。

## 4. Language Revision（§12.1）

每个实现都声明语言修订 `CLC-<major>.<minor>`；**本文档声明 `CLC-1.15`**。输入（授权、操作、OCM）应当携带其编写时所依据的修订；**未携带修订的输入视为 `CLC-1.0`**。

- **兼容读取：** 输入声明的 major 与实现相同，且 minor ≤ 实现自身的 minor 时，实现可以求值（CLC-1.3 实现读取 1.0–1.3，不读取 1.4 或 2.0）。
- **不兼容读取必须失败关闭** → `deny("unsupported_language_revision")`，并在任何 §9.1 层**之前**解析；不降级，也不先警告再放行（[`revision-002`](../../../data/_vectors/clc-v1/vectors.json)；正向示例见 [`revision-001`](../../../data/_vectors/clc-v1/vectors.json)）。
- **CLC-A 一致性与 minor 门禁是同一规则的两面**（§12.1）：声明 CLC-A 意味着实现所声明修订的语义——宣传 `CLC-1.15` 就必须实现 `param_bounds`（文法 + §6.6 meet）、`Resolve`、`ConstraintUnion` 和 §6.2 规范化，而不只是接受它们的输入。落后的实现应声明旧修订，并通过门禁拒绝更新输入；它不得声明高于自身实现能力的修订，也不得在拒绝自身所声明修订的格式正确输入时，仍声明 CLC-A。

**逐修订摘要**（完整文本见 §12.1；各项对判定的影响均在该处说明）：

| 修订 | 性质 | 主要新增／变更 |
|-----|--------|----------------------|
| 1.2 | 增量 | decision 的 `unresolved` 字段 + `invalid_constraint` |
| 1.3 | 增量，一处重新划定范围 | `allow_unresolved` 判定值；`allow` = “完全执行” |
| 1.9 | 增量 | 包含关系 + CLC-D（§13） |
| 1.10 | 增量，minor 门禁 | `param_bounds` + 四个原因代码 |
| 1.11 | 增量 | `Resolve`（§8.5）+ `invalid_resolution`/`invalid_timestamp` |
| 1.12 | 增量 | `ConstraintUnion`（§7.1） |
| 1.13 | 增量，限于 CLC-D | `AuthorizeWithChain`（§13.11） |
| 1.14 | 增量 | `BoundMeet` §6.6（`param_bounds` 交集） |
| 1.15 | **纠正性** | 跨族 meet 拒绝 `invalid_params_binding`（该子集由 allow→deny）；JSON 类型敏感的 enum `equal`；UTF-8 字节序排序；`delegation_mode_not_narrower` 重新归属配置预检 |

**判定稳定性的诚实说明**（§12.1）：兼容读取控制的是*可读性*，不是判定稳定性。在 §6.6 meet 子集上，CLC-1.10→1.14 将 `invalid_params_binding` 改为正确 meet（deny→allow），1.15 又将跨族子情况改回 `invalid_params_binding`（allow→deny）。所有不含 `param_bounds` 的输入在整个 1.x 范围内判定稳定；使用者不得假设 `param_bounds` meet 子集也稳定。

## 总结：一致性审查检查什么

- [ ] CLC-A：`vectors.json`（123）+ `property-cases.json`（1184）通过；不得丢弃 §8.4 的 `allow_unresolved`/`unresolved`。
- [ ] CLC-D：`containment-vectors.json`（64）+ `authorize-chain-vectors.json`（15）通过；`Contains` 始终只比较声明集合。
- [ ] CLC-E：未声明（未达到独立性门槛，等待 EMILIA 审查）。
- [ ] minor 门禁：不静默降级；输入不兼容时，在任何层之前报告 `unsupported_language_revision`。
- [ ] 诚实的范围：同一作者的一致性属于回归测试，不属于独立验证。

## 常见误区

- **沿用 1.15 之前的旧计数**——CLC-1.15 跨型审计之前的文本写 120 个向量 / `kind=intersect`（14）；审计新增 `intersect-011/-012/-013` 后为 123 /（17）。修订历史 CLC-1.8 行的"114 to 120"是当时事实，保留不改。
- **声明 CLC-E**——语料库已经存在，但该类别出于原则暂不声明（§12、P12）。
- **假设各 minor 的 `param_bounds` meet 输入判定稳定**——规范明确不保证（§12.1）。

---
← [12-containment.md](12-containment.md) · → [14-cookbook.md](14-cookbook.md) · 相关：[02-overview.md](02-overview.md)、[11-reason-codes.md](11-reason-codes.md)
