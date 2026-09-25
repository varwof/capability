# 05 · Grants——授权单元

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §5 (Grant)
> 本页是一份易读指南。如有冲突，以规范原文为准。
> 状态：Preview——不得用于生产环境。

## 速览

**grant** 是最小的授权单元：`CapabilityId` + 可选的 `params` + 可选的 `constraints`。它的含义是：*持有者可以使用这一 class of action，但必须遵守这些边界和 constraints。* 所有权限证据都通过 grants 传递。一次判定针对一份或多份 grants，以及一个 operation。

## 结构

```
grant      = capability-id [ params ] [ constraints ]
constraint = scheme ":" type [ ":" params ]
```

具体来说，就是 decision edge 上看到的同一类 JSON：

```json
{
  "id": "std/database-v1:query:SELECT",
  "params": { "limit": 100, "tables": ["customers"] },
  "constraints": [ "varwof/constraint-v1:time:window:[{\"start\":\"09:00\",\"end\":\"17:00\"}]" ]
}
```

各字段的职责如下：

| 字段 | 作用 | 规范依据 |
|-------|------|-------------|
| `id` | action 的 class | §3 identifiers、§6.1 entailment |
| `params` | request 参数的值边界（数值上限、enum 数组、递归对象） | §6.2 |
| `param_bounds` | 可选的*扩展*边界：min/max/step、enum cardinality、nested、`optional`。它始终是**独立**字段，绝不混入 `params` | §6.5 |
| `constraints` | 消费方必须遵守的管理限制（time、network、`max_rows`） | §8 |

这里列出 `param_bounds`，是因为 §6.5 将它引入为 grant-level 字段。它与 `params` 共享的值代数见 [07-parameters.md](07-parameters.md)。

## 已声明即拒绝

Constraint 一旦声明，就**不是**愿望。违反它就必须拒绝；无法求值时则必须履行相应义务：

- **空边界会拒绝整个 class。** 如果 grant 的 `params` 声明空数组（`{"tables":[]}`），整个 class 都会被拒绝，持有者永远无法执行 action。这在构造上就是 fail-closed（[`params-007`](../../../data/_vectors/clc-v1/vectors.json) → `deny` `empty_bound_denies_class`）。
- **省略边界时使用 scheme 默认值。** 如果 capability scheme 为某个 constraint 声明了默认值，解析 grant 时就采用该默认值（§6.3 scheme defaults）。
- **不合规 constraints 在 layer 1 失败。** 无法识别的 scheme/type，以及违反语法的值，都会在 entailment 运行前被拒绝：`unknown_constraint`（[`decide-003`](../../../data/_vectors/clc-v1/vectors.json) `unknown:constraint:type`）和 `invalid_constraint`（[`decide-019`](../../../data/_vectors/clc-v1/vectors.json) 跨午夜单 segment window；[`decide-021`](../../../data/_vectors/clc-v1/vectors.json) v1.2 前的 scalar-second window），都不会进入 §6.1。

## 多个 Grants 的组合

Decision function *绝不*只针对一份孤立 grant：

- **在同一个 identifier 内**，多份 grants 可能覆盖同一个 request。引擎必须处理 **multi-grant** 输入（`decide-035`）。
- **在不同 identifiers 之间**，一份 grant 可与另一份 grant 上的 constraints 组合。Intersection（[09-intersection.md](09-intersection.md)）和 containment（[12-containment.md](12-containment.md)）都把 grant 视为最小的声明单元，绝不会拓宽任何来源。

P6/P11 确立的核心规则是：**只有在引擎能够证明授权时才授予权限，其他所有情况一律关门。** 空 grants、未知 constraints 和缺失字段都会导致 deny，绝不会静默扩大权限。

## 常见误区

- **把有边界的 grant 理解成“带参数 allow”。** `params` 和 `param_bounds` 会收窄 grant；它们绝不会添加 actions，也不会拓宽之前的 grant。
- **期望 CLC core 对 `constraints` 求值。** Core 会求值 `max_rows`；`time`/`network` 会作为义务返回（`allow_unresolved` + `unresolved`）。无法求值的临界值必须 deny。
- **遗漏 `id`。** 没有 identifier 的 grant 根本不是 grant，会在 layer 1 触发 `missing_capability_id`。

---
← [04-actions.md](04-actions.md) · → [06-entailment.md](06-entailment.md) · 相关：[07-parameters.md](07-parameters.md)、[08-constraints.md](08-constraints.md)
