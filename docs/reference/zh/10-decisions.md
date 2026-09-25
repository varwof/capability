# 10 · 决策与满足

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §9（9.1 reason ordering）、§10、Appendix A
> 本页是便于阅读的指南。若出现冲突，以规范为准。
> 状态：预览版——不用于生产环境。

## 速览

`Authorize(grants, operation) → Decision` 产生三值 verdict：`allow` / `deny` / `allow_unresolved`。`Satisfy(evidence_set, requirement)`（§10）产生证据侧的二值报告：`SATISFIED` / `UNSATISFIED`。两者都是确定性、fail-closed 的，并携带稳定的 reason code。Appendix A 展示了消费者如何绑定这套共享词汇。

## 1. `Authorize`——授权侧（§9）

```
Decision = { verdict: "allow"|"deny"|"allow_unresolved",
             reason: string|null,
             unresolved: string[] }   // additive, §8.4
```

算法（后续内容沿用 §9.1's layer order，但**不代表优先级**）：

| 步骤 | 检查 | 解析为 |
|------|-------|-------------|
| 0. **预检查** | grant 集合缺失或为空 → `capability_not_authorized`（§9.1 layer 10），**早于**任何 operation 检查，即使 operation 也缺失 | [`decide-016`](../../../data/_vectors/clc-v1/vectors.json)：`{}` grants + `{}` op → `capability_not_authorized`，而不是 `missing_capability_id` |
| 1. **Operation 验证** | id 缺失或无效——报告**具体的 layer 1 代码**，绝不合并 | `missing_capability_id` [`decide-017`](../../../data/_vectors/clc-v1/vectors.json)；`unsupported_wildcard` [`decide-018`](../../../data/_vectors/clc-v1/vectors.json)；`invalid_capability_id` [`decide-025`](../../../data/_vectors/clc-v1/vectors.json) |
| 2. **查找覆盖 grant** | 通过 `Entails`（§6.1）；没有覆盖项 → `capability_not_authorized`（§9.1 layer 10） | [`decide-002`](../../../data/_vectors/clc-v1/vectors.json) |
| 3. **求值约束** | 按覆盖 grant 逐个处理，依据 §8.1 | `unknown_constraint` / `invalid_constraint` / `{type}:violated` / 遗留义务（§8.4） |
| 4. **聚合**（多 grant，§9.1） | 任一覆盖并允许即可 → allow；合并判定为 allow 的覆盖 grant 的 residual union；全部拒绝 → 取规范顺序中第一个覆盖 grant（§9.1），结果确定 | [`decide-029`](../../../data/_vectors/clc-v1/vectors.json)、[`decide-030`](../../../data/_vectors/clc-v1/vectors.json)、[`decide-035`](../../../data/_vectors/clc-v1/vectors.json) |
| 5. **Verdict** | 有非空 residual 的 allow → `allow_unresolved`；无 residual 的 allow → `allow` | [`decide-020`](../../../data/_vectors/clc-v1/vectors.json) |

预检查是唯一的优先级规则：缺失或为空的 grant 集合会以 `capability_not_authorized`（layer 10）拒绝——调用方如果两个输入都未传入，得到的就是这个 reason，而不是 `missing_capability_id`。operation 缺失则解析为 `missing_capability_id`（layer 1）。语言修订不匹配（§12.1）会在每一层之前解析为 `unsupported_language_revision`。

## 2. 多 grant 聚合（§9.1）

`Authorize` 处理的是**有序 grant 列表**；授权结果与顺序无关，只有 reason 的选择使用输入顺序：

1. **任一覆盖并允许的 grant 都允许**（窄 grant 绝不能 deny 宽 grant 允许的 operation）——[`decide-029`](../../../data/_vectors/clc-v1/vectors.json)。
2. 遗留义务 = **同时覆盖、判定为 allow 的 grant 之间**的 `unresolved` **并集**（规范化后排序）。在 params/约束层被拒绝的覆盖 grant 不贡献任何内容——它没有授权，因此其遗留义务也不会被携带（[`decide-035`](../../../data/_vectors/clc-v1/vectors.json)：两个 grant，network + time，都为 allow → 以 `allow_unresolved` 携带并集）。
3. 没有 grant 覆盖 → `capability_not_authorized`；operation 的第 1 层错误始终先于任何覆盖/聚合处理。
4. 所有覆盖 grant 都在 params/约束层被拒绝 → deny，reason = **规范顺序中第一个覆盖 grant** 的 layer 5–11 拒绝结果（输入列表顺序；MUST NOT 按哈希/迭代顺序选择）——[`decide-030`](../../../data/_vectors/clc-v1/vectors.json)。

**Op-ID 验证错误会传播其具体的 layer 1 代码**（`missing_capability_id` / `unsupported_wildcard` / `invalid_capability_id`），绝不使用笼统代码，也绝不变成 `capability_not_authorized`；只有**覆盖**失败（layers 3–4 and 10）才归并为 `capability_not_authorized`。grant 中出现格式错误的 id，会使该 grant 无法匹配：`Entails` 会将它的 layer 1 代码作为 false 的 reason 报告，但 `Authorize` 会把不匹配归并到覆盖失败（`capability_not_authorized`）——不会暴露 grant 自身的代码。

## 3. `Resolved Reason Ordering`（§9.1，规范）

单一报告的 reason 是固定顺序中**第一个适用的层**（适用于 `Entails`、`Intersect`、`Authorize`）：

| # | 层 | Reason code |
|---|-------|----------------|
| 1 | CapabilityId 有效性 | `invalid_capability_id`、`missing_capability_id`、`unsupported_wildcard` |
| 2 | Params 归一化 | `invalid_params_duplicate_key`、`invalid_params_number`、`invalid_params_size`、`invalid_params_binding` |
| 3 | 命名空间（scheme + action Class） | `different_namespace` |
| 4 | 路径覆盖（同一命名空间） | `literal_mismatch`、`wildcard_requires_trailing_segment` |
| 5 | 显式空边界 | `empty_bound_denies_class` |
| 6 | null 值 | `invalid_params_null` |
| 7 | 参数存在性（双向） | `params_missing`、`undeclared_param` |
| 8 | 枚举成员资格与基数 | `not_in_enum`、`params_cardinality` |
| 9 | 边界比较 | `params_exceed_grant`、`params_out_of_range`、`params_not_multiple` |
| 10 | 覆盖为空 | `no_overlap`、`absent_source`、`capability_not_authorized` |
| 11 | 约束求值 | `unknown_constraint`、`invalid_constraint`、`{type}:violated` |

`Resolve`（§8.5）是**决策之后的处理，不是某一层**：它消费一个 `Decision`，绝不重新运行 `Authorize`；它只引入 `invalid_resolution` / `invalid_timestamp` 以及已履行的 `{type}:violated`，并且只在 `allow_unresolved` 输入上引入。

## 4. `Satisfy`——证据侧（§10）

```
Satisfy(evidence_set, requirement) → Satisfaction
Satisfaction = { verdict: "SATISFIED"|"UNSATISFIED", reason: string|null }
```

算法：**(1)** 按各自的原生规则验证每个 evidence 工件；**(2)** 每个所需 evidence 角色都已填写；**(3)** 通过 `Match`（§6.4）将每个工件精确绑定到 action；**(4)** 求值 freshness、consumption 和 role 约束（§8.2 evidence-side grammar：`varwof/evidence-v1:freshness:sec:<n>`）。如果某个已识别约束的求值属于 enforcement point（consumption），其结果为 `unknown`，在顶层产生 `UNSATISFIED`；**(5)** 所有角色都已填写并绑定 → `SATISFIED`；**(6)** 任一角色未填写、未绑定或被违反 → `UNSATISFIED`。

**三态求值，二值报告。** 已识别的证据侧约束以三态求值（`satisfied` / `violated` / `unknown`），但报告是二值的：顶层的 `unknown` **MUST 产生 `UNSATISFIED`**，绝不产生 `SATISFIED`。证据侧**没有 `allow_unresolved`**；`unresolved` 只用于授权侧（§8.4、§11）。结果确定性、fail-closed，并具有稳定的 reason code（§10）。

## 5. 消费映射（Appendix A）

Appendix A 是**信息性**内容——符合 CLC-A 不依赖任何 consumer profile：

| Consumer | 语法 | 绑定 | Verdict |
|----------|---------|---------|---------|
| AIC-JWT DA | `capability[].id` | Entailment（§6.1） | Decision（§9） |
| EMILIA AEB | AEG capability_class | Match（§6.4）+ Entailment（§6.1） | SATISFIED（§10）+ Decision（§9） |
| RAR authorization_details | `type="capability"`（RFC 9396） | Entailment（§6.1） | Decision（§9） |
| 委托链 | 每个 hop 声明的集合 | Intersection（§7） | Decision（§9） |
| 委托包含关系 | 父级和子级边界 | `Contains`（§13） | Containment verdict（§13） |

委托链和包含关系这两行绝不能混淆：交集回答整条链的有效权限，包含关系回答每一跳的 `child ⊆ parent`；必须留在父级范围内的 hop 要用 `Contains`（§13）检查——参见 [12-containment](12-containment.md)。

## 防混用清单

- [ ] grant 侧预检查（layer 10）先于 operation 验证（layer 1）：grant 缺失 + operation 缺失 → `capability_not_authorized`。
- [ ] Op-ID 的第 1 层代码具体传播；grant 侧代码则归并为 `capability_not_authorized`。
- [ ] 多 grant 采用任一覆盖原则：窄 grant 不能 deny 宽 grant 的 operation。
- [ ] 遗留义务只对同时覆盖并允许的 grant 取并集；被拒绝的 grant 不贡献任何内容。
- [ ] `allow_unresolved` 绝不是 `allow`；`unknown` 是内部状态，在证据侧绝不是第三种顶层 verdict。

## 常见误区

- **只测试 `verdict == "allow"`**——遗留义务会作为未经确认的 allow 溜过去（§8.4）。
- **期待证据侧报告 `unknown`**——它报告的是二值 `UNSATISFIED`，并带有稳定的 reason。

---
← [09-intersection.md](09-intersection.md) · → [11-reason-codes.md](11-reason-codes.md) · 相关：[08-constraints.md](08-constraints.md)、[11-reason-codes.md](11-reason-codes.md)
