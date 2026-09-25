# 11 · 原因代码速查

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §9.2（授权）、§13.5（包含关系）、附录 C.2（载体映射）
> 本页是便于阅读的指南。如有冲突，以规范为准。
> 状态：Preview — 不供生产环境使用。

## 速览

原因代码是**稳定标识符**：`规范代码 = 第一个 ":" 之前的所有内容`。实现可以追加 `: <detail>`（如违规参数名）作为诊断后缀，规范代码保持不变。**所有工具和兼容性检查必须只比较规范前缀**（§9.2）。下文列出了封闭的 v1 代码集；其他方案可以定义附加代码，但不得重新定义这些代码。

## 1. 各层授权代码（§9.1/9.2）

原因选择遵循 §9.1 的层级顺序（*首个适用*的层胜出；见 [10-decisions](10-decisions.md) §3）。

| 代码 | 含义（§9.2） |
|------|----------------|
| **第 1 层 — CapabilityId 有效性** | |
| `unsupported_wildcard` | v1 禁止通配符形式（裸 `*`、部分段、`**`、`{a,b}`、`[a-z]`） |
| `invalid_capability_id` | CapabilityId 不符合 §3 文法 |
| `missing_capability_id` | 操作没有 `id`（第 1 层） |
| **第 2 层 — params 规范化** | |
| `invalid_params_duplicate_key` | JSON 键重复（§6.2） |
| `invalid_params_number` | 无规范形式：数字非有限、越界或精度过高（超过 17 位有效十进制数字），或文本的 Unicode 格式错误、无法解析（§6.2 第 3/7 步） |
| `invalid_params_size` | 序列化后超过 512 字节，或嵌套深于 32 层（§6.2） |
| `invalid_params_binding` | `param_bounds` 边界格式错误（未知成员、混合族、`min > max`、`step ≤ 0`、`min_items > max_items`），或同一键同时出现在 `params` 和 `param_bounds` 中（§6.5） |
| **第 3–4 层 — 覆盖** | |
| `different_namespace` | 授权和操作的命名空间不同（scheme + action Class） |
| `literal_mismatch` | 字面标识符不同 |
| `wildcard_requires_trailing_segment` | 通配符后没有剩余段（`...:*` 不覆盖 `...`） |
| **第 5 层 — 已声明空边界时拒绝** | |
| `empty_bound_denies_class` | 参数值位置显式声明空边界（`[]`/`{}`），因此拒绝该类；`params:{}` *不是*空边界（≡ 未声明） |
| **第 6 层 — Null** | |
| `invalid_params_null` | 参数值为 `null`（v1 拒绝） |
| **第 7 层 — 存在性（双向）** | |
| `params_missing` | 授权设限的参数被请求省略，或请求完全没有 `params`（失败关闭，§6.3 第 4 步） |
| `undeclared_param` | 操作参数键未由授权声明（键闭包，§6.2） |
| **第 8–9 层 — 值** | |
| `not_in_enum` | 请求值不是授权所声明数组集合的成员（§6.2） |
| `params_cardinality` | 请求基数超出 `param_bounds` 的 `min_items`/`max_items`（§6.5） |
| `params_out_of_range` | 请求值超出 `param_bounds` 的包含端点 `min`/`max`（§6.5） |
| `params_not_multiple` | 按 IEEE-754 规则，请求值不是 `step` 的整数倍（§6.5） |
| `params_exceed_grant` | 请求参数超出授权边界 |
| **第 10 层 — 覆盖为空** | |
| `capability_not_authorized` | 有效集合中没有授权覆盖该操作 |
| `no_overlap` | 多个来源的交集为空 |
| `absent_source` | 对零个来源取交集，即没有有效集合（§7 规则 5） |
| **第 11 层 — 约束** | |
| `unknown_constraint` | 未知约束类型（失败关闭） |
| `invalid_constraint` | 已知类型的值不符合 §8.1 值文法 |
| `{type}:violated` | 违反已知约束（如 `max_rows:violated`）；对于 `Resolve` 判定为已履行但违反的义务，也会报告此代码（§8.5） |
| **跨层** | |
| `unsupported_language_revision` | 声明的 CLC 修订与实现不兼容（§12.1；失败关闭，不降级） |
| `invalid_resolution` | `Resolve` 的 resolution 条目格式错误（`status` 未知，或 `constraint` 非字符串/为空）（§8.5） |
| `invalid_timestamp` | `Resolve` 的 `now` 参数不是有效的 UTC 时刻（§8.5） |

**在不同函数中复用。** `Resolve`（`Decision` 的消费者，§8.5）只引入 `invalid_resolution`、`invalid_timestamp`，以及已履行的 `{type}:violated`；其余代码来自 §9.1。`no_overlap`、`absent_source`、`empty_bound_denies_class` 由 `Intersect`（§7）共用。`capability_not_authorized` 是唯一的覆盖折叠：只有覆盖失败（第 3–4、10 层）会折叠为它；操作 ID 错误会传播其对应的第 1 层代码（§9.1）。

## 2. 包含关系代码与 CLC-D（§13.5）

`Contains(parent, child)` 报告两个稳定代码；绑定配置预检还会产生第三个代码：

| 代码 | 报告方 | 含义 |
|------|-------------|---------|
| `child_exceeds_parent` | `Contains`，第 2 层（§13.4.2） | 子标识符未被父标识符覆盖 |
| `params_not_narrower` | `Contains`，第 3 层（§13.4.3） | 子参数不在父参数声明的边界或键集内 |
| `delegation_mode_not_narrower` | 绑定配置预检（§13.4.5）——`Contains` **绝不**报告 | 子委派模式（一种载体概念）比父模式更宽 |

`Contains` 在构造上就是失败关闭的：每层默认返回 `false`；任何层无法验证时都拒绝，不会先警告再放行（§13.4）。当边界不得泄露策略形状时，实现可以把 `child_exceeds_parent` 折叠为 `capability_not_authorized`，但绝不能折叠为 `params_not_narrower`（§13.5）。采用携带模式的载体时，配置也不得折叠 `delegation_mode_not_narrower`（§13.4.5）。

## 3. 载体失败代码映射（附录 C.2，说明性）

载体失败代码会折叠到 CLC-D 代码。该映射是**多对一且不可逆的**，除非载体先记录自己的代码：

| 载体失败 | CLC-D 原因 |
|-----------------|--------------|
| ATN 的 `id` 不同 · AAT 工具不在父集合内 · AAE action 子集失败 · AEGIS 缺少委派方所持 capability | `different_namespace`* |
| ATN `schema.digest` 不匹配 · AIP `aip_scope_insufficient` · AIP `aip_depth_exceeded` · AOA scope 未严格收窄 | `child_exceeds_parent` |
| ATN 提高了 `resource_bounds` · AAT 约束未被包含 · AIP `aip_budget_exceeded` · AAE 约束未更严格 · AEGIS 权限超出委派方 | `params_not_narrower` |

\* `different_namespace` 不属于 §13.5 的包含关系代码集；C.2 表是面向载体的投影，准确行见规范附录。注意表中可见的折叠：AIP scope 与 depth 失败，以及 ATN digest 不匹配，都会归为 `child_exceeds_parent`；任何载体放宽边界，都会归为 `params_not_narrower`。CLC-D 保证的是语言层面的稳定原因，而不是载体的原因。

## 原因核验清单

- [ ] 只比较第一个 `:` 之前的规范前缀；`max_rows:violated:limit` 的规范代码是 `max_rows:violated`。
- [ ] 匹配层级：操作 ID 失败有明确的第 1 层代码（`unsupported_wildcard`，绝不是 `invalid_capability_id` 或笼统代码）。
- [ ] `capability_not_authorized` 只用于覆盖失败；参数或约束拒绝保留自己的代码。
- [ ] `resolved reason` = 对授权/操作对应用 §9.1 后首个适用的层。
- [ ] 不同实现对相同输入给出相同原因，具有确定性（稳定原因代码，§9.1/§12）。

## 常见误区

- **比较包含 `: <detail>` 的完整字符串**——会破坏稳定性；细节只用于诊断。
- **把 `{type}:violated` 当成两个代码**——规范代码是第一个 `:` 之前的所有内容，`violated` *就是*被纳入规范代码的部分。
- **把操作 ID 错误折叠为 `capability_not_authorized`**——第 1 层操作代码会明确传播；只有覆盖错误会折叠。

---
← [10-decisions.md](10-decisions.md) · → [12-containment.md](12-containment.md) · 相关：[09-intersection.md](09-intersection.md)、[08-constraints.md](08-constraints.md)
