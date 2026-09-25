# 09 · 交集与 `ConstraintUnion` 投影

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §7（7.1 `ConstraintUnion`）
> 本页是便于阅读的指南。若出现冲突，以规范为准。
> 状态：预览版——不用于生产环境。

## 速览

`Intersect` 组合委托来源：`P_effective = P_principal ∩ C_agent ∩ P_gateway`。它**只会收窄**——结果必须被每个来源覆盖，且与顺序无关；当来源无法求交时，以稳定的 reason code 拒绝。`ConstraintUnion`（§7.1）是另一种投影：表示整条链的*全部约束负担*，但不计算有效 grant。

## 1. 授权集合上的 meet（§7）

把“JSON 值的交集”当作正确图景是错误的。每个 param 值都**表示一个授权集合**——数字表示 `(-∞, v]`，数组表示成员集合，字符串/布尔值表示 `{v}`，对象表示其各键所表示集合的乘积——而 meet 就是在这些语义表示上求集合交集：

- `{"limit":100} ∩ {"limit":50} = {"limit":50}`——更紧的边界胜出，也就是取**最小值**，不是空集（[`intersect-004`](../../../data/_vectors/clc-v1/vectors.json)）。
- `{"tables":["a","b"]} ∩ {"tables":["a"]} = {"tables":["a"]}`——allowlist 取交集（[`intersect-001`](../../../data/_vectors/clc-v1/vectors.json)）。
- 两个不相交的 allowlist（`{"tables":["a"]}` 对 `{"tables":["b"]}`）→ `deny("no_overlap")`；**零个来源** → `deny("absent_source")`（[`intersect-007`](../../../data/_vectors/clc-v1/vectors.json)）。

只有当这些语义表示确实不相交时，meet 才为空（`no_overlap`）——例如两个没有共同成员的枚举集合，或彼此不同的键集合。数值 `params` 的 meet 始终是最小值（params 没有下界）。

## 2. 规则（§7）

| # | 规则 | 固定依据 |
|---|------|-----------|
| 1 | 每个来源提供一个 grant 集合 | — |
| 2 | 有效 grant MUST 被每个来源中的至少一个 grant 覆盖 | [`intersect-010`](../../../data/_vectors/clc-v1/vectors.json) |
| 3 | 同一 capability 的约束通过**并集**合并（每个约束都保留——约束是合取的，丢弃某个来源的约束就丢弃了它的限制） | [`cu-008`](../../../data/_vectors/clc-v1/constraint-union-vectors.json)（反转 hop 顺序，并集不变） |
| 4 | 任一来源缺少该 capability → 有效集合中不含该 capability | 无专属向量；最接近的钉桩 [`combined-008`](../../../data/_vectors/clc-v1/vectors.json) |
| 5 | **零个/缺失来源按 fail-closed 处理** → `deny("absent_source")`（存在但没有该 capability 的 grant 的来源属于 rule 4，不是 rule 5） | [`intersect-007`](../../../data/_vectors/clc-v1/vectors.json) |
| 6 | **空 params 不声明约束**：存在但为空的 `params` 不贡献限制；先有界后为空与先空后有界的结果相同——来源顺序 MUST NOT 改变结果 | [`intersect-008`](../../../data/_vectors/clc-v1/vectors.json) `{limit:50} ∩ {} = {limit:50}` |

**标识符比较不涉及 params（rule 2）。** 有效标识符是被每个来源覆盖的**最窄**标识符，只依据 §6.1 的标识符规则选择——如果带 params 通过 `Entails` 路由 grant，有界 grant 会与没有 params 的兄弟 grant 求交，并错误地触发缺失处理（§6.3 step 4）（[`intersect-010`](../../../data/_vectors/clc-v1/vectors.json)：`query:SELECT` ∩ `query:*` → `{}`，较窄的标识符胜出）。

**声明后的拒绝行为与 rule 6 的关系：** 明确为空的 `[]`/`{}` param 值会拒绝该类——`{"tables":[]}` 是限制，`params:{}` 不是。委托链中某个中间 hop 声明空边界时，会传播 `empty_bound_denies_class`（[`combined-011`](../../../data/_vectors/clc-v1/vectors.json)）；三来源交集中有一个来源缺失时，则落到 `no_overlap`（[`combined-008`](../../../data/_vectors/clc-v1/vectors.json)）。

**对象值要求键集合完全相同。** `{"a":1} ∩ {"b":1}` → `deny("no_overlap")`（合并“共享键”会丢掉另一个来源所约束的键，破坏“组合只会收窄”的性质）；键集合相同时，值递归比较——`{"a":1} ∩ {"a":2} = {"a":1}`。这两种情况都说明：在委托各跳之间应保持统一的参数形状。

**`param_bounds` 按 §6.6 的 meet 合并，而不是按 §7 的值规则：数值 `min`/`max`/`step`、枚举成员交集和基数、`nested` 递归，以及通过合取处理的 `optional`。空 meet 是 `no_overlap`；无法表示的 meet（任一顺序的跨值族数字 × 枚举、标量 × 嵌套、不可通约的 step，或某个键在一个来源的 `params` 中、却在另一个来源的 `param_bounds` 中）是 `invalid_params_binding`（§7；[07-parameters](07-parameters.md) §3）。

## 3. `ConstraintUnion`——整条链的约束负担（§7.1）

```
ConstraintUnion(chain) → string[]        // chain = ordered Grant[]
```

返回 `chain` 中每个约束字符串的**规范化并集**——重复项折叠，结果按确定性顺序排列。它是**投影，不是 meet**：不比较标识符或参数，不读取或验证约束值，也不检查包含关系（[`cu-001`](../../../data/_vectors/clc-v1/constraint-union-vectors.json) 单个 grant：并集就是它自己的集合，经过规范化并排序；[`cu-008`](../../../data/_vectors/clc-v1/constraint-union-vectors.json) 反转 hop 顺序 → 相同的排序并集）。

- **空链按 fail-closed 处理** → `deny("absent_source")`（[`cu-007`](../../../data/_vectors/clc-v1/constraint-union-vectors.json)）——丢失链的调用方不能把“没有可合并的项”误认为“没有约束”。
- **顺序采用 UTF-8 字节序**（§7.1，修订 CLC-1.15）：规范化字符串按其 UTF-8 编码逐字节比较——所有实现都得到相同结果；*不是* UTF-16 码元顺序（后者会把 emoji 放在 U+E000–U+FFFF 字符之前，尽管它的码点更高）。由 [`constraint-union-collation-vectors.json`](../../../data/_vectors/clc-v1/constraint-union-collation-vectors.json) 固定。同样的 collation 也适用于 §8.4 的 `unresolved` 列表和 §8.5 的 `Resolve` 输出。
- 序列化对象中的 JCS 成员顺序与这个列表 collation 可以共存：一个管理对象**成员**，另一个管理约束字符串**列表**；二者不会重新排序对方（§7.1）。

`ConstraintUnion` 不对权限作任何断言：每一跳的 `Contains`（§13）以及 `Authorize`/`Resolve`（§9、§8.5）仍然是独立步骤。这正是 `Contains` 保持纯粹的原因——把并集合并进去，会使该关系不再是声明元组上的子集关系。

## 防混用清单

- [ ] 交集是在**语义表示**上求交，而不是在 JSON 值上求交：数值 meet = 最小值，不是空集。
- [ ] 只有语义表示不相交时才是 `no_overlap`（枚举/键集合）；只有零个或缺失来源时才是 `absent_source`。
- [ ] 空的 `[]`/`{}`**值** = deny 该类；`params:{}` 则**不**施加限制。绝不能混淆两者。
- [ ] 标识符比较不涉及 params；绝不要带 params 将 `Intersect` 路由到 `Entails`。
- [ ] `param_bounds` 的 meet 走 §6.6 代数，而不是 §7 值规则（跨值族 → `invalid_params_binding`）。
- [ ] `ConstraintUnion` 按 **UTF-8 字节序**排序，折叠重复项，并在空链时 fail-closed。

## 常见误区

- **把空的 `Intersect` 来源理解为“没有约束”**——rule 4 把缺失 grant 视为缺少该 capability；只有*存在的*空 `params` 才表示没有约束。
- **以为 `Intersect` 会验证约束值**——它只合并约束字符串；§8.1 的值语法在决策边界（§9）执行，而不在这里执行。

---
← [08-constraints.md](08-constraints.md) · → [10-decisions.md](10-decisions.md) · 相关：[06-entailment.md](06-entailment.md)、[07-parameters.md](07-parameters.md)
