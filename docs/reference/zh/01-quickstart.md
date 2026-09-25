# 01 · 快速入门——四步完成首次授权判定

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §5 (Grant)、§6 (Binding)、§9 (Decision Function)
> 本页是一份易读指南。如有冲突，以规范原文为准。
> 状态：Preview——不得用于生产环境。

## 速览

CLC-v1 回答一个问题：**这个请求是否属于我的授权范围？** 你编写一份 **grant**（agent 可以做什么），系统提供一个 **request**（agent 想做什么），语言则返回 `allow`、`deny` 或 `allow_unresolved`，并始终附上稳定的 reason code。以下内容仅用于讲解：无需安装，也无需运行时。示例都是真实的测试集 vectors，日后可用任意一致性运行器重新执行。

## 心智模型

`grant` 和 `request` 采用相同结构：一个 **capability identifier**（`id`），以及可选的 **params**、**param_bounds** 和 **constraints**。decision function 依次检查：标识符是否兼容？params 是否处于 grant 的边界内？grant 的 constraints 是否满足？

```
grant   { id, params?, param_bounds?, constraints? }
request { id, params? }          ← an Operation
                 ↓
        verdict + reason   (allow / deny / allow_unresolved)
```

## 第 1 步——最小闭环（完全相同的标识符）

最小案例：request 标识符与 grant 标识符**逐字相同**。

**输入**——[`vectors.json → entail-001`](../../../data/_vectors/clc-v1/vectors.json)

```json
grant   = { "id": "std/database-v1:query:SELECT" }
request = { "id": "std/database-v1:query:SELECT" }
```

**输出**：`allow`（reason：*—*）。**推导过程**：literal match（§6.1）。

标识符采用 `scheme:path:action` 形式。匹配按层级从左到右进行，因此更具体的 request 仍必须落在 grant 范围内。这就引出了通配符。

## 第 2 步——添加通配符（授权一类操作）

末尾的 `*` 可匹配**一个或多个**剩余 segment。

**输入**——[`vectors.json → entail-002`](../../../data/_vectors/clc-v1/vectors.json)

```json
grant   = { "id": "std/database-v1:query:*" }
request = { "id": "std/database-v1:query:SELECT" }
```

**输出**：`allow`。该 grant 覆盖 `std/database-v1:query:` 下的任意单个 action。

通配符容易误用，详见下方误区。路径中较靠前的 `*` 完全是另一回事：

**输入**——[`vectors.json → entail-007`](../../../data/_vectors/clc-v1/vectors.json)

```json
grant   = { "id": "std/database-v1:*" }
request = { "id": "std/database-v1:query:SELECT" }
```

**输出**：`deny` `different_namespace`。位于 *class*（product）位置的 `*`**不是**末尾 action 通配符（§6.1/§9.1 layer 3）。完整规则见 [`03-identifiers.md`](03-identifiers.md)。

## 第 3 步——添加 params 和边界（收窄 grant）

grant 可以携带 `params`，用于规定 request 必须遵守的精确值；也可以携带 `param_bounds`，表达数组形式的 `params` 无法表达的范围。

**params——数值上限**——[`vectors.json → params-001`](../../../data/_vectors/clc-v1/vectors.json)

```json
grant   = { "id": "std/database-v1:query:SELECT", "params": { "limit": 100 } }
request = { "id": "std/database-v1:query:SELECT", "params": { "limit": 50 } }
```

**输出**：`allow`（50 ≤ 100）。

**param_bounds——包含端点的范围**——[`param-bounds-vectors.json → pb-001 / pb-004`](../../../data/_vectors/clc-v1/param-bounds-vectors.json)

```json
grant   = { "id": "std/database-v1:query:SELECT",
            "param_bounds": { "limit": { "min": 10, "max": 100 } } }
request = { "id": "std/database-v1:query:SELECT", "params": { "limit": 50 } }
```

**输出**：`allow`。但若改为 `"limit": 9`（[`pb-004`](../../../data/_vectors/clc-v1/param-bounds-vectors.json)），同一 grant 会返回 **`deny` `params_out_of_range`**。

**数组参数是一个 *set*（enum）——request 只能选择集合成员。**——[`vectors.json → params-004`](../../../data/_vectors/clc-v1/vectors.json)

```json
grant   = { "id": "std/database-v1:query:SELECT", "params": { "tables": ["a"] } }
request = { "id": "std/database-v1:query:SELECT", "params": { "tables": ["a", "b"] } }
```

**输出**：`deny` `not_in_enum`——`"b"` 不在允许的集合中。详见 [`07-parameters.md`](07-parameters.md)。

## 第 4 步——添加 constraints（管理限制）并得到第三种 verdict

Constraints 是 grant 上的 `(scheme,type):value` 字符串。core 会直接求值 `max_rows`；它能识别 `network`/`time`，但不对它们求值，而是将其作为义务返回。

**已求值的 constraint**——[`vectors.json → decide-006`](../../../data/_vectors/clc-v1/vectors.json)

```json
grant = { "id": "std/database-v1:query:SELECT",
          "constraints": [ "varwof/constraint-v1:max_rows:10" ] }
request = { "id": "std/database-v1:query:SELECT", "params": { "max_rows": 50 } }
```

**输出**：`deny` `max_rows:violated`。

**可识别但未求值——第三种 verdict**——[`vectors.json → decide-035`](../../../data/_vectors/clc-v1/vectors.json)（两个覆盖请求的 grants，`multi`）

```json
grant-zero = { "id": "std/database-v1:query:SELECT",
               "constraints": [ "varwof/constraint-v1:network:cidr:[\"192.0.2.0/24\"]" ] }
grant-one  = { "id": "std/database-v1:query:SELECT",
               "constraints": [ "varwof/constraint-v1:time:window:[{\"start\":\"00:00\",\"end\":\"06:00\"}]" ] }
request    = { "id": "std/database-v1:query:SELECT" }
```

**输出**：`allow_unresolved`，并包含

```json
"unresolved": [ "varwof/constraint-v1:network:cidr:[\"192.0.2.0/24\"]",
                "varwof/constraint-v1:time:window:[{\"start\":\"00:00\",\"end\":\"06:00\"}]" ]
```

`allow_unresolved`**不是**`allow`：消费方必须自行履行每项义务，否则必须拒绝（§8.4）。见 [`08-constraints.md`](08-constraints.md) 和 [`10-decisions.md`](10-decisions.md)。

## 你已经构建了什么

| 步骤 | Grant 特性 | 得到的 Verdict | 真实测试集 id |
|------|---------------|--------------|----------------|
| 1 | literal identifier | allow | `entail-001` |
| 2 | 末尾 `*` 通配符 / class 位置的 `*` | allow / `different_namespace` | `entail-002` / `entail-007` |
| 3 | params 上限、`param_bounds` 范围、enum set | allow / `params_out_of_range` / `not_in_enum` | `params-001`、`pb-001`/`pb-004`、`params-004` |
| 4 | 已求值 + 剩余 constraints | `max_rows:violated` / `allow_unresolved` | `decide-006` / `decide-035` |

## 常见误区

- **末尾 `*` 匹配一个或多个 segment，而不是零个。** `std/database-v1:query:*` 这一 grant **不**覆盖裸值 `std/database-v1:query`。该 request 没有可匹配的末尾 segment，因此返回 `wildcard_requires_trailing_segment`（[`entail-005`](../../../data/_vectors/clc-v1/vectors.json)）。
- **`*` 只能作为 action 通配符。** 放在其他任何位置，都会使标识符变成另一类别，而不是通配符的超集（`different_namespace`）。
- **`params` 中的数组是枚举，不是范围。** request 只能选择集合成员。若 grant 为 `["a"]`，request 为 `["a","b"]`，结果就是 `deny`，因为整个 request 集合都必须被覆盖。
- **字面量不匹配**——grant 为 `...:SELECT`，request 为 `...:INSERT`——会返回 `literal_mismatch`，即使二者都属于“一种 query action”（[`entail-006`](../../../data/_vectors/clc-v1/vectors.json)）。
- **`allow_unresolved` 不是 `allow`。** 消费方绝不能把第三种 verdict 并入 allow 决定。

---
← [README.md](README.md) · → [`02-overview.md`](02-overview.md) · 相关：[`03-identifiers.md`](03-identifiers.md)、[`07-parameters.md`](07-parameters.md)、[`08-constraints.md`](08-constraints.md)
