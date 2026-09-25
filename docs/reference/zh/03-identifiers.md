# 03 · 标识符——`capability-id` 语法

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §3 (Grammar)、§6.1 (Entailment, namespace)、§9.1 layer 3/4 (reason ordering)
> 本页是一份易读指南。如有冲突，以规范原文为准。
> 状态：Preview——不得用于生产环境。

## 速览

Capability identifier 的形式是 `scheme:action`（如 `std/database-v1:query:SELECT`），可在末尾附加一个**末尾通配符** segment `*`。v1 只定义**一种**通配符形态：完整的最后一个 segment。其他形式（`*:query...`、`re*`、`**`、`{a,b}`、`[a-z]`）保留给 v2，符合 v1 的实现必须拒绝它们。namespace 不同的标识符（scheme + action Class）绝不可能互相 entail。

## 语法（v1，封闭）

```
capability-id = scheme ":" action [ ":" wildcard ]
wildcard      = "*"
scheme        = vendor "/" product "-v" major
vendor        = 1*( ALPHA / DIGIT / "-" )
product       = 1*( ALPHA / DIGIT / "-" )
major         = 1*DIGIT
action        = segment *( ":" segment )
segment       = 1*( ALPHA / DIGIT / "-" / "_" / "." )
```

这项语法带来两个重要的结构约束：

1. **Scheme 由*最后*一个 `-v<digits>` 锚定。** `product` 自身可以包含 `-`，因此 `-v` 后缀必须是**最后**一次出现的 `-v`，且后面跟数字。若 product 内部含有双字符序列 `-v`，结果是无效（`invalid_capability_id`），而不是歧义。`a/b-v1-v2` 会被**拒绝**，绝不会解析成两种形式；product 名 `b-v1` 在 v1 中则根本无法表达。
2. **末尾通配符是语法的一部分。** `std/database-v1:query:*` 是格式正确的 capability-id，不是格式错误的 action。只有“完整末尾 segment”这一形态才是通配符。

同一字符串如果既未通过 wildcard 形态检查，也未通过通用语法检查，**wildcard 检测先执行**，并返回 `unsupported_wildcard`（§3，“before the generic `invalid_capability_id` test”）。

## 标识符的三个层级

| 层级 | 内容 | v1 规则 | 示例 |
|------|-----------|---------|---------|
| 格式正确的普通形式 | 符合完整语法，无通配符 | `valid` | `std/database-v1:query:SELECT` |
| 格式正确的通配符形式 | 只能有末尾 `*` | 对 grant/request patterns 而言为 `valid` | `std/database-v1:query:*` |
| 禁止的通配符形态 | partial / bare / nested / bracket | `unsupported_wildcard`（v2 保留） | `std/crm-v1:re*`、`*`、`**`、 `{a,b}`、`[a-z]` |
| 格式错误的 scheme/action | 缺少 scheme、major 无效、`-v` 有歧义 | `invalid_capability_id` | `database:query`、`a/b-v1-v2` |

## 字段示例（真实测试集 ids）

**有效标识符**——[`vectors.json → syntax-001`](../../../data/_vectors/clc-v1/vectors.json)

```json
request = { "id": "std/database-v1:query:SELECT" }   →  valid
```

**默认标识符可以比一个 action segment 更深**——[`vectors.json → syntax-009`](../../../data/_vectors/clc-v1/vectors.json)

```json
request = { "id": "std/data-v1:fetch:item:42" }      →  valid
```

**禁止的通配符形态**——每一种都会得到 `unsupported_wildcard`，绝不会尝试深层匹配：

[`syntax-003`](../../../data/_vectors/clc-v1/vectors.json) `*:query:SELECT`（scheme 位置使用通配符）→ `invalid` `unsupported_wildcard` · [`syntax-004`](../../../data/_vectors/clc-v1/vectors.json) `std/database-v1:query:SEL*`（部分 action）→ 相同 · [`syntax-005`](../../../data/_vectors/clc-v1/vectors.json) `std/database-v1:query:{read,write}`（展开集合）→ 相同 · [`syntax-006`](../../../data/_vectors/clc-v1/vectors.json) `std/database-v1:query:[a-z]`（字符类）→ 相同。作为 *request* 时，拒绝结果完全相同：[`decide-018`](../../../data/_vectors/clc-v1/vectors.json)。唯一允许的通配符形态作为 id 仍有效：[`syntax-002`](../../../data/_vectors/clc-v1/vectors.json) `std/database-v1:query:*` → `valid`。

**完全不是 v1 identifier**——[`syntax-007`](../../../data/_vectors/clc-v1/vectors.json) `database:query`（没有 scheme）→ `invalid` `invalid_capability_id`。grant 格式正确但 request 格式错误时，也会使用同一 code（[`decide-004`](../../../data/_vectors/clc-v1/vectors.json)、[`decide-025`](../../../data/_vectors/clc-v1/vectors.json)）。

## Namespace：硬边界

Entailment 只能发生在**同一个 namespace** 内，其中 namespace = scheme + action Class（`std/database-v1`）（§9.1 layer 3）。如果 grant 和 operation 的 namespace 不同，引擎会在查看 path 之前就返回 `different_namespace`（§6.3 step 1）：

[`entail-004`](../../../data/_vectors/clc-v1/vectors.json)

```json
grant   = { "id": "std/database-v1:query:*" }
request = { "id": "std/database-v1:admin:DDL" }   →  deny  different_namespace
```

## Class 位置通配符陷阱

距离末尾**一个 segment**的 `*` 并非“开头就匹配全部内容”的通配符。class 位置通配符属于 v1 禁止形态，其 request 会在语法阶段被拒绝（§9.1 layer 3，`unsupported_wildcard`），不会在 entailment 阶段被静默拓宽。测试集同时固定了“窄化后 deny（相同 action）”和“无论 action 是否相同都 deny”两种读法：

[`entail-007`](../../../data/_vectors/clc-v1/vectors.json) `grant std/database-v1:*` 对 `request std/database-v1:query:SELECT` → `deny` `different_namespace`。class 位置的 `*` 不是末尾 action 通配符，namespace 不匹配。class 位置通配符为 v1 所禁止（§3；request operation 自身的 id 会因 scheme 位置存在 `*` 而被拒绝），entailment 根本不会执行到 path 覆盖判断。
[`entail-008`](../../../data/_vectors/clc-v1/vectors.json) 相同 grant 对 `request std/database-v1:SELECT` → `deny` `different_namespace`，class 不匹配。

与**唯一**合法的完整通配符比较：[`entail-002`](../../../data/_vectors/clc-v1/vectors.json) 中，`grant …query:*` 覆盖 `request …query:SELECT`（`allow`），因为 `*` 占据完整的末尾 segment，而且末尾**至少有一个** segment。末尾通配符绝不会匹配空余部分（[`entail-005`](../../../data/_vectors/clc-v1/vectors.json)、`wildcard_requires_trailing_segment`）。

## 经验法则

- 每个 vendor/product/`-v` major 对应一个 scheme；major 只能是数字。
- Grant `params` 与标识符检测都在 **segment 边界**上进行，而不是按词汇前缀判断。因此，`std/database-v1:query:` + `SEL` 不是 `SELECT`。
- 如果同一输入既是错误通配符，也不符合语法，**wildcard error 优先**，返回 `unsupported_wildcard`，而不是 `invalid_capability_id`。

## 常见误区

- **`scheme:action` 是必需项。** 没有 scheme 的 id 会得到 `invalid_capability_id`，绝不能“默认认为是 `std/…`”。
- **`-v`（后跟数字）必须是最后一次这样的连续出现。** product 内嵌 `-v1` 会导致失败；`a/b-v1-v2` 不符合语法。
- **末尾通配符要求存在余下内容。** `query:*` ≠ `query`；空余部分不受覆盖。
- **在 σ-position 上，`*` 是缺陷，不是捷径。** Path 覆盖严格按 segment 进行；未知 request segment 属于 `undeclared` 类问题，不能理解成“位于某个通配符之下”。

---
← [02-overview.md](02-overview.md) · → [04-actions.md](04-actions.md) · 相关：[06-entailment.md](06-entailment.md)、[09-intersection.md](09-intersection.md)
