# 07 · 参数、参数边界与 BoundMeet

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §6.2（Parameters）、§6.5（Extended parameter bounds）、§6.6（Intersection of bounds）
> 本页是便于阅读的指南。若出现冲突，以规范为准。
> 状态：预览版——不用于生产环境。

## 速览

参数约束来自两个**绝不混用**的字段：`params`（v1.1 值规则）和 `param_bounds`（CLC-1.10：有符号边界、枚举基数、嵌套、可选键）。现有 `params` 输入保持原义。§6.6 边界 meet 使用独立封闭代数；不能表示为单一值族就拒绝。

## 1. `params`：值规则（§6.2）

| 类型 | 规则 | 示例 |
|------|------|---------|
| number | op ≤ grant（上界） | `50 ≤ 100` ✅ [`params-001`](../../../data/_vectors/clc-v1/vectors.json)；`150` ❌ `params-002` |
| string | 精确匹配 | `"a"="a"` ✅ |
| boolean | 仅精确匹配，禁止数值比较（`true` ≠ `1`） | — |
| array | **允许值的集合**（enum）：标量须等于某个成员；数组的每个元素都须是成员 | `{"station":[1,2,3]}` |
| object | op 中每个 grant 键都存在，值递归比较 | `{"t":["id"]} ⊆ {"t":["id","name"]}` ✅ |

**数组的枚举语义——v1.1 规则。** grant 数组参数是允许值的**集合**，不是顺序或范围：分类参数（station、cell、tool id）SHOULD 使用数组；`params` 中的标量数字保持上界语义。`["a"] ⊉ ["a","b"]` → `not_in_enum`（[`params-004`](../../../data/_vectors/clc-v1/vectors.json)）。

**空数组 / 空集合。** `{"tables":[]}` 拒绝该类——`empty_bound_denies_class`（[`params-007`](../../../data/_vectors/clc-v1/vectors.json)）。无 `params` 的 grant，或值为 `"params":{}` 的 grant，均**不受约束**（覆盖任意 params）。

**v1 中 null 无效**——grant 或 request params 中出现 `null` → `invalid_params_null`（[`params-008`](../../../data/_vectors/clc-v1/vectors.json)、[`decide-008`](../../../data/_vectors/clc-v1/vectors.json)）。

### 输入归一化（修订 CLC-1.1/1.4/1.8）

`params` 在输入边界按固定顺序归一化和检查，**早于任何 §9.1 layer**：**(1)** JCS 规范序列化（RFC 8785：键排序，采用 ECMAScript-`Number::toString` 数字）；**(2)** 重复 JSON 键 → `invalid_params_duplicate_key`（[`params-016`](../../../data/_vectors/clc-v1/vectors.json)）；**(3)** 数字形状——非有限、超出 IEEE-754 范围或有效数字超过 17 位 → `invalid_params_number`（[`params-017`](../../../data/_vectors/clc-v1/vectors.json) `1e400`），依据**收到的原始 token**；**(4)** 大小/深度——≤ 512 个 **UTF-8 八位字节**，深度 ≤ 32（最外层 = 第 1 层）→ `invalid_params_size`（[`params-018`/`params-020`](../../../data/_vectors/clc-v1/vectors.json)，上限两侧；[`params-033`](../../../data/_vectors/clc-v1/vectors.json)，JCS 测量形式）；**(5)** 第一个失败的检查胜出，且早于第 1 层；**(6)** 规范序列化限制解码值条目，两条路径都拒绝；**(7)** 格式错误 Unicode（孤立代理项/无效 UTF-8 八位字节）无 JCS 形式 → **原始文本直接拒绝为 `invalid_params_number`**（解码前；解码器崩溃后无法恢复）。

## 2. `param_bounds`：扩展边界（§6.5）

`param_bounds` 是**独立的可选 grant 字段**，规则：**每个键只有一个权威表示**——键只能在 `params` 或 `param_bounds` 中出现，不能同时出现；否则 grant 为 `invalid_params_binding`（[`pb-031`](../../../data/_vectors/clc-v1/param-bounds-vectors.json)）。声明键集合为 `keys(params) ∪ keys(param_bounds)`。

### 边界语法（封闭）

```
Bound = {   // at most one value family + the orthogonal "optional"
  min/max, step             →  numeric
  enum, min_items/max_items →  enum
  nested                    →  nested
  optional                  →  orthogonal (default false)
}
```

成员均可选；对象**封闭**（未知成员拒绝），值族不可混用。`min > max`、`step ≤ 0`、`min_items > max_items` → `invalid_params_binding`。**空的** Bound `{}` 声明该键但不施加值约束——它*仍用于键闭合并默认必需*（[`pb-038`](../../../data/_vectors/clc-v1/param-bounds-vectors.json)：空边界、请求省略参数 → `params_missing`）。

### 四个“{}”——绝不可混淆

| 层 | 对 `{}` 的理解 |
|-------|----------------|
| 容器存在性 | `params` 缺失 ≡ `params:{}` → **不受约束** |
| 声明位置 | 键只能出现在 `params` **或** `param_bounds` 中，绝不能同时出现 |
| 值约束 | `params:{"k":[]}` **是**限制；`param_bounds:{"k":{}}` **不是**限制（仅用于键闭合） |
| 请求值 | `O` 提供的值，按该键所属的值族判断 |

### 按值族看 Entailment 语义（grant 对 operation）

- **存在性（layer 7）：** `optional:true` → MAY 缺失；否则 MUST 存在（`params_missing`，[`pb-025`](../../../data/_vectors/clc-v1/param-bounds-vectors.json)）。声明集合外的请求键 → `undeclared_param`。
- **枚举值族（layer 8）：** 请求值须为成员：标量等于成员，或数组每项都是成员（[`pb-015`](../../../data/_vectors/clc-v1/param-bounds-vectors.json)：`enum:["a","b"]` 对 `["a","c"]` → `not_in_enum`）。成员相等判断对 **JSON 类型敏感**：`true` ≠ `1` ≠ `"1"`；数字经 JCS 规范序列化后比较（`1` ≡ `1.0`）。`min_items`/`max_items` 限制请求基数（数组长度；标量计 1）→ `params_cardinality`（[`pb-017`](../../../data/_vectors/clc-v1/param-bounds-vectors.json)：3 > 2）。
- **数值值族（layer 9）：** `min ≤ v ≤ max`（含端点）→ `params_out_of_range`（[`pb-004`](../../../data/_vectors/clc-v1/param-bounds-vectors.json)：`limit:9` 对 `min:10`）。`step`：`q = v/step; q==floor(q) && q*step==v`（binary64）→ `params_not_multiple`（[`pb-011`](../../../data/_vectors/clc-v1/param-bounds-vectors.json)：`step:0.5` 配 `1.3`）。数值边界应用于**非数字**请求值 → fail-closed 为 `params_exceed_grant`（[`pb-037`](../../../data/_vectors/clc-v1/param-bounds-vectors.json)：`limit:"x"`）。
- **嵌套值族：** 对对象值键递归应用同一规则；各层键闭合并对称，optional 逐层适用。将 `nested` 边界应用到**非对象** → fail-closed 为 `params_exceed_grant`（[`pb-030`](../../../data/_vectors/clc-v1/param-bounds-vectors.json)：`columns:5`）。
- **Scheme 默认值（`param_defaults`）：** 第 4 步前物化到 `O`；优先级为 **显式 operation 值 > scheme 默认值 > 缺失**（[`pb-042`](../../../data/_vectors/clc-v1/param-bounds-vectors.json)：显式 `50` 胜过默认值 `10` → `allow`）。默认值不添加未声明键；`optional:true` 键不设默认值。

## 3. `BoundMeet`——边界求交（§6.6，CLC-1.14 新增/1.15 修订）

`Intersect` 组合由**两个或更多来源**在 `param_bounds` 中声明的每个键，使 meet 留在同一值族：

| 规则 | 结果 |
|------|--------|
| `optional` | **来源之间取 AND**：只有*每个*来源都标为 optional，结果才是 optional |
| 数值 `min`/`max` | 取最大的 min、最小的 max（未声明 = 无界）；合并后 `min > max` → **空 meet** → `no_overlap` |
| 数值 `step` | 一方是另一方的精确倍数 → 保留较粗步长；否则 `invalid_params_binding`——不合成未声明网格 |
| 枚举 | 成员集合取**交集**（相等判断区分类型）；为空 → `no_overlap`；`min_items` = 最大值，`max_items` = 最小值；`max_items < min_items` → `no_overlap`（[`bm-010`,`bm-011`](../../../data/_vectors/clc-v1/param-bounds-meet-vectors.json)） |
| 嵌套 | 要求**完全相同的键集合**，否则 `no_overlap`；逐键递归 |
| 数值 ∩ 枚举（任一顺序） | **拒绝** `invalid_params_binding`——CLC-1.14 的“筛选成员”规则已移除（它比任一来源都宽）；规则对称，先于数学运算决定 |
| 标量 ∩ 嵌套（任一顺序） | **拒绝** `invalid_params_binding`（CLC-1.15：`no_overlap` → `invalid_params_binding`） |
| 空 Bound `{}` | 值族的单位元；其 `optional` 仍参与合并 |

结果至多含**一个**值族，因而是有效 §6.5 Bound；reason code 限于 §9.2：同值族空 meet 用 `no_overlap`，无法表示用 `invalid_params_binding`。

**键的声明位置必须在各来源间一致：** 对某个 `Intersect` 来源，键在 `params` 中，而对另一个来源却在 `param_bounds` 中 → `invalid_params_binding`（委托链不会出现这种情况——§13.4.3 要求每跳声明位置匹配）。

## 防混用清单（两次修订的增量）

- [ ] `params` 中标量数字的值代数**只有上界**——`params` 内没有下界、step、基数或 optional 标记。
- [ ] min/max/step/enum/min_items/max_items/nested/optional **只存在于** `param_bounds`。
- [ ] CLC-1.14 的枚举筛选 meet **已消失**：数字 × 枚举是 `invalid_params_binding`，不会筛选枚举；`no_overlap` 只留给同一值族内的空 meet（包括标量∩嵌套 → `invalid_params_binding`）。
- [ ] 成员相等处处对 **JSON 类型敏感**（枚举 `params`、§6.5、§6.6、§13.4.3 收窄）；宿主语言中的 `true==1` 是一致性 bug。

## 常见误区

- **在 `params` 和 `param_bounds` 中同时声明一个键**——这是 `invalid_params_binding`，不是“合并”。
- **把 `param_bounds: {k: {}}` 理解为“k 不受约束”**——它确实*声明了* k（必需、键闭合并施加限制），但不约束值；这与 `params` 相反，后者中 `[]` 是最严格的限制；而且 `params:{}` ≡ 缺失 ≠ 空的 `param_bounds` Bound。

---
← [06-entailment.md](06-entailment.md) · → [08-constraints.md](08-constraints.md) · 相关：[09-intersection.md](09-intersection.md)、[11-reason-codes.md](11-reason-codes.md)
