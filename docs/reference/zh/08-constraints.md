# 08 · 约束、遗留义务与 `Resolve`

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §8
> 本页是便于阅读的指南。若出现冲突，以规范为准。
> 状态：预览版——不用于生产环境。

## 速览

约束限制 capability 的**使用方式**。v1 core 恰好识别三对 `(scheme, type)`；只有 `max_rows` 有 core evaluator。已识别但未求值的约束必须以 `allow_unresolved` + `unresolved` 保留在 verdict 上——绝不能静默丢弃。`Resolve` 按义务闭合 consumer 的反馈回路。

## 1. 约束身份：`(scheme, type)`

约束使用冒号记法三元组 `scheme:type[:params]`；**身份是二元组** `(scheme, type)`，绝不只是 type 名称（§8.1）。

```
varwof/constraint-v1 : max_rows      (core evaluator exists)
varwof/constraint-v1 : time          (validated, not evaluated)
varwof/constraint-v1 : network       (validated, not evaluated)
```

- `std/database-v1:max_rows` **不被识别**——scheme 范围很重要（§8.1）。未识别的二元组 → `deny("unknown_constraint")`，按 fail-closed 处理（[`decide-003`](../../../data/_vectors/clc-v1/vectors.json) `unknown:constraint:type`；[`payments-002`](../../../data/_vectors/clc-v1/vectors.json) 是 scheme 范围内的 `payments:quota:daily`，不在 v1 已知集合中）。
- 已识别的二元组必须符合该类型的**值语法**；不符合 → `deny("invalid_constraint")`。

## 2. 值语法（§8.1）

| type | 合法值（v1） | core 行为 |
|------|------------------|---------------|
| `max_rows` | 严格非负整数 | 针对 op params **求值** |
| `time:window` | JSON 数组（≤ 32），每个元素为 `{"start":"HH:MM[:SS]","end":"HH:MM[:SS]"}`；UTC 区段；区段升序、**不重叠**，采用半开 `[start, end)`，单个区段不得跨越午夜 | 仅识别 |
| `network:cidr` | 合法 IPv4/IPv6 CIDR 字符串的 JSON 数组（≤ 32） | 仅识别 |

**语法陷阱**（每种情况都有 vector 固定）：
- **标量 `time:window:3600`** 不是合法的 `time:window` 值 → `invalid_constraint`（[`decide-021`](../../../data/_vectors/clc-v1/vectors.json)）。
- **没有前缀长度的 CIDR** → `invalid_constraint`（[`decide-022`](../../../data/_vectors/clc-v1/vectors.json)）。
- **跨越午夜的单个区段**（`22:00→06:00`）必须拆成 `22:00→00:00` + `00:00→06:00`（[`decide-019`](../../../data/_vectors/clc-v1/vectors.json) → `invalid_constraint`）。`end` 值 `"00:00"` 会被读作 **86400**（次日午夜）：`22:00→00:00` 合法，因为比较依据是一天中的秒数，而不是词法字符串顺序（§8.1）。

**Operation 侧的 `max_rows` 定义域**（修订 CLC-1.4）：缺失、字符串、布尔值、负数、小数或非有限值 → `max_rows:violated`（无法证明符合 = fail-closed）。以下 vector 均固定为 `max_rows:violated`：`decide-023`（缺失）、`decide-031`（`"garbage"`）、`decide-032`（`true`）、`decide-033`（`-1`）、`decide-034`（`1.5`）。

**Core 按二元组识别，但只求值 `max_rows`。** `time`/`network` 的求值由声明它们的 scheme 负责（§11）；core 对其他二元组的拒绝是 fail-closed，可防止跨 scheme 污染：某个 scheme 自己定义的 `max_rows` 不会被 Core 的求值器劫持（§8.1）。

## 3. 遗留义务通道（§8.4）

已识别且值符合 §8.1 语法、但 v1 core **没有求值器**的约束（`time`、`network`）MUST NOT 被丢弃：它会出现在决策的附加 `unresolved` 列表中，verdict 为 `allow_unresolved`——这是一个**独立的枚举值，绝不等于 `allow`**（[`decide-020`](../../../data/_vectors/clc-v1/vectors.json) `network:cidr`；[`decide-024`](../../../data/_vectors/clc-v1/vectors.json) 拆分跨午夜窗口，二者都只是被识别）。

**Fail-closed 边界：** consumer（PEP / profile / 声明 scheme）在放行前必须求值或确认每个 `unresolved` 约束；**如果无法做到，就必须 deny**。只检查 `if verdict == "allow"` 的 consumer 不能依据字面枚举值，把遗留义务当作已经满足的 allow 放行（§8.4）。

- `unresolved` 的顺序（§8.4，修订 CLC-1.15）：使用规范化字符串，折叠重复项，并**按 UTF-8 字节序列**排序——使用 §7.1 的 collation，*而不是* ECMAScript 默认（UTF-16 码元）顺序。输出前只连接一次，并且只排序一次。
- **组合义务**（consumer 侧）：同一 `(scheme,type)` 的多个 `unresolved` 构成**合取（AND）**——满足 A 和 B 就满足全部；禁止 OR、任选其一、首个胜出或忽略其中一部分。不同 `(scheme,type)` 之间不会相互影响（§8.4）。

## 4. `Resolve`——consumer 的反馈回路（§8.5）

```
Resolution = { constraint: string, status: "satisfied" | "violated" | "unknown" }
Resolve(decision, resolutions, now?) → Decision
```

按以下顺序处理：**(1)** 终态 verdict 固定——`deny`/`allow` 原样返回，忽略 `resolutions`；**(2)** 输入格式错误时 fail-closed——错误的 `status`/约束 → `invalid_resolution`，错误的 `now` → `invalid_timestamp`；**(3)** 履行义务——对每个义务，按 **`violated` ≻ `satisfied` ≻ `unknown`** 合并 core 时钟与 consumer resolutions；**(4)** 重复条目也按同样方式合并；**(5)** 忽略无关 resolutions（`O` 才是权威依据）；**(6)** 任一项被违反 → `deny({type}:violated)`；全部满足 → `allow`；否则为 `allow_unresolved`，并保留仍为 `unknown` 的子集。

**Core 时钟：** 如果提供了 `now`，值类型为 §8.1 窗口数组的 `varwof/constraint-v1:time` 义务由 core 求值：在区段内 → satisfied，在区段外 → `time:violated`（[`resolve-015`](../../../data/_vectors/clc-v1/resolve-vectors.json)：`now=21:00` 在 `[22:00,24:00)` 之外；格式错误的 `now` 在 [`resolve-024`](../../../data/_vectors/clc-v1/resolve-vectors.json) 中被拒绝）。其他情况：部分满足 → `allow_unresolved`，并保留剩余项（[`resolve-006`](../../../data/_vectors/clc-v1/resolve-vectors.json)）；任一项被违反 → deny，并给出相应的 `{type}:violated`（[`resolve-009`](../../../data/_vectors/clc-v1/resolve-vectors.json)）；`O` 之外的 resolution 会被忽略（[`resolve-013`](../../../data/_vectors/clc-v1/resolve-vectors.json)）；无法识别的 `status` → `invalid_resolution`（[`resolve-023`](../../../data/_vectors/clc-v1/resolve-vectors.json)）。

**不得超出时间范围缓存：** core 时钟完成的义务只在调用瞬间有效。依据 `Resolve` 结果采取行动的 consumer，必须在行动前立即用当前 `now` 重新调用，或者不得缓存到当前区段结束之后——缓存的 `allow` 不能比其窗口活得更久（§8.5）。

`Resolve` 是确定性、fail-closed、幂等（`Resolve(Resolve(d,r,now),r,now) = Resolve(d,r,now)`）且单调的。它既不会创造义务，也不会丢弃义务。

## 防混用清单

- [ ] 身份是 `(scheme,type)`：`foo/database-v1:max_rows` 是 `unknown_constraint`，绝不会被 Core 的求值器处理。
- [ ] 已识别但未求值 ⇒ `allow_unresolved` + `unresolved`——`allow_unresolved` 不是 `allow`。
- [ ] 语法拒绝是 `invalid_constraint`（值不符合语法），不同于 `unknown_constraint`（二元组未被识别）。
- [ ] 跨越午夜的 `time:window` 拆成两个同日区段；`end` 中的 `"00:00"` = 86400。
- [ ] `Resolve` 不会让 `deny` 复活，不会通过无关 resolution 扩大权限，并且会把缺少 `now` 的 `time` 义务解析为 `unknown`（没有 TTL）。

## 常见误区

- **静默跳过未求值的约束**——这是 conformance bug；遗留义务是附加的（§8.4）。
- **误以为 `time`/`network` 已经求值**——core 只识别值语法；求值属于声明它们的 scheme。
- **把 `Resolve` 的 allow 缓存到区段结束之后**——这会让缓存结果超出其履行范围（§8.5）。

---
← [07-parameters.md](07-parameters.md) · → [09-intersection.md](09-intersection.md) · 相关：[10-decisions.md](10-decisions.md)、[11-reason-codes.md](11-reason-codes.md)
