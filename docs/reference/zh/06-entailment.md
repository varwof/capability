# 06 · 蕴含（Entailment）——授权绑定

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §6.1（Entailment）、§6.3（算法）、§6.4（Match）
> 本页是便于阅读的指南。若出现冲突，以规范为准。
> 状态：预览版——不用于生产环境。

## 速览

绑定在授权侧回答“这个 grant 是否授权这个 request？”（**蕴含（Entailment）**），在证据侧回答“这份 evidence 是否对应这个 action？”（**Match**）。蕴含决定**类覆盖**：只有标识符匹配且每个声明的参数/约束都成立时，grant G 才覆盖 operation O。Match 决定**内容绑定**：ActionId 必须等于重新计算的投影；不涉及 occurrence 声明，也不做原生验证。

## §6.1 —— Entailment：两条标识符规则

当以下两种情况之一成立时，grant G 覆盖 operation O：

1. **字面匹配**：G = O；归一化后逐字节相同。
2. **尾部通配符**：G = `scheme:prefix:*`，且 O 在 `scheme:prefix:` 后**至少有一个**尾部段——按段边界比较，**不是**词法前缀。

| 授权（Grant） | 操作（Operation） | 结果 |
|-------|-----------|--------|
| `std/database-v1:query:*` | `std/database-v1:query:SELECT` | ✅ 通配符匹配（[`entail-002`](../../../data/_vectors/clc-v1/vectors.json)） |
| `std/database-v1:query:*` | `std/database-v1:query:SELECT:deep` | ✅ 多段匹配（[`entail-003`](../../../data/_vectors/clc-v1/vectors.json)） |
| `std/database-v1:query:*` | `std/database-v1:admin:DDL` | ❌ 不同命名空间（[`entail-004`](../../../data/_vectors/clc-v1/vectors.json)） |
| `std/database-v1:query:SELECT` | `std/database-v1:query:INSERT` | ❌ 字面值不匹配（[`entail-006`](../../../data/_vectors/clc-v1/vectors.json)） |

以下两种形式**始终拒绝**（§6.3 步骤 1–2）：命名空间不匹配（`different_namespace`，layer 3），以及通配符后没有尾部段（[`entail-005`](../../../data/_vectors/clc-v1/vectors.json)，`wildcard_requires_trailing_segment`）。类位置通配符（`std/database-v1:*`）是语法缺陷，不是超集——关于 `different_namespace` 组合 `entail-007/-008`，参见 [03-identifiers.md](03-identifiers.md)。

## §6.3 —— `Entails` 算法

```
Entails(G, O) → bool:
  1. G.namespace ≠ O.namespace   → false   (namespace = scheme + action Class, §9.1 layer 3)
  2. G.id doesn't cover O.id     → false   (path coverage, §9.1 layer 4)
  3. G declares no key           → true    (no `params` and no `param_bounds` ⇒ unconstrained, absent ≡ empty object)
  4. O.params absent             → false   (bounded grant, request omits it → `params_missing`)
  5. params_subset(O.params, keys(params) ∪ keys(param_bounds), param_bounds)
                                  (declared key set, §9.1 layers 5–9)
```

逐条解释规则：

- **步骤 3——不受约束意味着接受所有参数。** 同时没有 `params` 和 `param_bounds`（或为 `"params":{}`）的 grant 覆盖 operation 的*任意*参数。缺失与 `{}` 在语义上相同（§6.2; §7 rule 6; §9.1）。
- **步骤 4——有界 grant 在字段缺失时按 fail-closed 处理。** 如果 grant 收紧了任何内容，而 operation 省略整个 `params` 字段，则为 `deny("params_missing")`——缺少一个有界键，与整个对象缺失含义相同（[`decide-007`](../../../data/_vectors/clc-v1/vectors.json)）；有界 grant 作用于携带未声明键的 operation 时，结论由 `undeclared-002` 固定为 `params_missing`，因为在 layer 7 中，**缺少键的检查优先于未声明键的检查**。
- **步骤 5——声明键集合。** 比较针对 `keys(params) ∪ keys(param_bounds)` 进行；`param_bounds` 中的键还会强制执行其 Bound（包括 `min`/`max`、`step`、枚举基数、`optional`、`nested`——§6.5）。没有 `param_bounds` 时，步骤 5 就退化为仅比较 `params`。

**如果一个以上的检查失败，报告的 reason 遵循固定的 §9.1 顺序，而不是算法文字中的步骤顺序。** 最容易混淆的是这两种顺序：

- **`params_missing` 优先于 `undeclared_param`**（§9.1 layer 7 internal order），正如 `undeclared-002` 所示。
- **Layer 6（`invalid_params_null`）先于存在性检查处理。** 即使 operation 省略整个 `params` 字段，`null` 参数值也会因 `invalid_params_null` 失败——null 检查会遮蔽步骤 4 的 `params_missing`（[`decide-008`](../../../data/_vectors/clc-v1/vectors.json) → `invalid_params_null`）。

**Scheme 默认值。** capability scheme 可以声明 `param_defaults`；根据 §6.5，实现 MUST 在第 4 步之前将其物化到 `O` 中，优先级为 **显式 operation 值 > scheme 默认值 > 缺失**。只有当默认值是满足 grant 声明键所必需时才应用默认值；`optional:true` 键绝不会被物化（该标记优先于默认值）。

## §6.4 —— Match（证据绑定）

当以下条件全部满足时，证据 E 绑定到 action A：

1. E 带有语言投影形式 `clc-action:1:…` 的有效 ActionId（§4.3）；
2. E 的 ActionId **等于重新计算的** ObservedAction 的 ActionId；
3. 该 ActionId 是在依赖方锁定的 suite 和 definition source 下计算的。

Match 仅进行**内容关联**（参见 [04-actions.md](04-actions.md)）：它不验证原生工件，不授权执行，也不标识一次 occurrence。跨格式映射（E 的原生格式 ≠ A 的规范形式）必须固定为 Action-Mapping Profile，结果为 `EQUIVALENT_UNDER_PROFILE`、`NOT_EQUIVALENT` 或 `INDETERMINATE`。

## 关联速查

| 绑定 | 侧 | 检查 | 语料示例 |
|---------|------|--------|-----------------|
| **Entailment** | 授权 | 类覆盖：标识符 + 参数 + 约束 | `entail-001…008`，`params-001/002`，`decide-007/008` |
| **Match** | 证据 | 内容同一性：重新计算的投影摘要 | 证据语料（`evidence-vectors.json`） |

## 常见误区

- **按算法文字理解层顺序。** §6.3 的编号步骤只是*展示顺序*；结果的权威顺序是 §9.1 (layers 1–9)。两个检查同时失败时，始终优先采用固定的层顺序，而不是“第一个失败的步骤”。
- **把声明键集合当成有序列表。** 步骤 5 比较的是*集合* `keys(params) ∪ keys(param_bounds)`；对这些检查而言，声明顺序和字段选择都不具有语义。
- **把 `allow_unresolved` 当作 Entailment 的终点。** 约束未求值时，Entailment 可以*成功*，但决策会是 `allow_unresolved`——这属于 §8.4 的业务，不是 Entailment 的结果。

---
← [05-grants.md](05-grants.md) · → [07-parameters.md](07-parameters.md) · 相关：[10-decisions.md](10-decisions.md)、[11-reason-codes.md](11-reason-codes.md)
