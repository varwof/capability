# 12 · 委派包含关系（CLC-D）

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §13（13.1–13.8、13.11、13.12）
> 本页是便于阅读的指南。如有冲突，以规范为准。
> 状态：Preview — 不供生产环境使用。

## 速览

包含关系是第三种授权层关系，另外两种是 Entailment（§6.1）和 Intersection（§7）：**`Contains(parent, child)`** 回答“子项*声明的*授权是否位于父项*声明的*授权内？”这正是委派链每一跳要回答的问题。它是叠加在 CLC-A 上的**可选**一致性类别 CLC-D：只做增量的补充，不改变任何 CLC-A 判定，任何 CLC-A 实现都可以采用。

## 1. 为什么 Entailment 和 Intersection 不够（§13.1）

- **Entailment** 回答“授权是否覆盖操作？”——§6.1。
- **Intersection** 回答“多个授权的有效集合是什么？”——§7。
- 二者都不能回答委派问题：**子项声明的授权是否位于父项声明的授权内？** 适配两个授权所得的结果，无法证明一个授权是特定父授权的子集。

CLC-D 服务于 AIC 生态的两个具体边界：**委派**（子代理请求的能力必须位于主体授权的范围内）和**发布边界**（证书持有者发布的规则不得超出持有者自身的授权）。

## 2. 关系签名与失败关闭规范（§13.3）

```
Contains(GP: Grant, GC: Grant) -> ContainmentResult
ContainmentResult = { "contains": <boolean>, "reason": <string> }
```

- 只有 §13.4 的**每一层**都通过时，`contains = true`；每层都失败关闭，只要存在疑点就返回 `false`。
- 成功时 `reason` 为空；失败时携带**首个失败层**的代码（遵循 §13.4 顺序，输入顺序绝不会影响哪一层先报告）。
- 该关系在**语义等价类上反对称**，而不是在 Grant 对象上：只有当 A 和 B 表示相同的标识符覆盖、参数键集和边界时，`Contains(A,B) ∧ Contains(B,A)` 才成立（`params:{}` ≡ 未声明等表面写法被视为相同）。两个不同等价类却相互包含属于矛盾，不得报告（[`contain-040`/`contain-041`](../../../data/_vectors/clc-d/containment-vectors.json)：反对称性探针对）。

## 3. 四个层级（§13.4）

严格按顺序解析；首次失败决定原因代码。

| 层级 | 检查 | 失败原因 |
|-------|--------|-------------------|
| **1. 授权有效性**（§13.4.1） | 两侧的 §3 标识符均有效；子项 `params` 符合授权侧的 §6.2 文法。无效的*父项*也会失败——无法评估的边界不得授权子项 | 复用 CLC-A 语法代码（`invalid_capability_id`、`missing_capability_id`、`invalid_params_<n>`）——[`contain-011`](../../../data/_vectors/clc-d/containment-vectors.json)：父项 id 为空 |
| **2. 标识符覆盖**（§13.4.2） | 完全采用 CLC-v1 路径覆盖关系（Entails 的标识符规则，不含 params）：命名空间相同；随后字面深度相同，或父项末尾 `*` 覆盖子项末尾段（`*` 匹配一个或多个，绝不匹配零个）。标识符中间使用通配符仍是 `unsupported_wildcard` | `different_namespace`（命名空间不同——[`contain-004`](../../../data/_vectors/clc-d/containment-vectors.json)）；`child_exceeds_parent`（存在覆盖缺口） |
| **3. 参数收窄**（§13.4.3） | 子项声明的每个参数都位于父项声明的边界内（数字 ≤、字符串/布尔值完全相等、数组 ⊆ enum、对象递归），且键集**完全相同**（对称闭包，取 `params` + `param_bounds` 键的并集）。对于 `param_bounds` Bounds：子项 `min` 提高或相等，`max` 降低或相等，`step` 是整数倍，enum ⊆ 子集，并递归处理嵌套；父项必填键会强制子项同键必填。父项 `{}`（或未声明）不受约束，可包含任何子项；有*边界*的父项下，子项 `{}` 失败 | `params_not_narrower`（子项任一值或键集检查失败）——[`contain-041`](../../../data/_vectors/clc-d/containment-vectors.json) |
| **4. 委派模式格**（§13.4.5） | **这是绑定配置预检，不是关系层**：Grant 值不携带模式，`Contains` 也不接收模式参数。携带模式的载体必须自行执行格检查；当子项放宽父项时，由配置报告 `delegation_mode_not_narrower`（AIC-JWT 顺序：`authorized < representative`） | `delegation_mode_not_narrower`（由配置负责；`Contains` 绝不报告） |

**约束不在此关系内**（§13.4.4）：`Contains` 不读取、比较或验证 `constraints` 字段——约束差异绝不会改变判定。约束沿链通过 **union** 组合（§7，合取），所以子项无须重新声明父项约束，添加约束只会收窄。如果使用者仅以 `Contains` 作为*唯一*门禁，就必须组合链的交集，让父项约束继续生效。

第 3 层的深入示例：父项 `{limit:100}`、子项 `{limit:50}` → 被包含（[`contain-040`](../../../data/_vectors/clc-d/containment-vectors.json)）；反向关系（[`contain-041`](../../../data/_vectors/clc-d/containment-vectors.json)）→ `params_not_narrower`。注意声明值的含义：父项 `{limit:100}` 的上限内包含子项 `{limit:-5}`（只取子集，不使用下界语义）——[`contain-042`](../../../data/_vectors/clc-d/containment-vectors.json)。

## 4. `AuthorizeWithChain` — 融合式链检查（§13.11）

```
AuthorizeWithChain(chain, op) → Decision   // chain = ordered Grant[], root first
```

1. **空链失败关闭** → `deny("absent_source")`（§7 规则 5；[`ac-001`](../../../data/_vectors/clc-d/authorize-chain-vectors.json)）。
2. **链门禁：** 对每对相邻项执行 `Contains(chain[i], chain[i+1])`；首个断链以该跳的 §13.5 代码结束（`child_exceeds_parent` / `params_not_narrower`，绝不是 `delegation_mode_not_narrower`）。此步骤在操作验证**之前**运行：即使操作也缺失，仍报告断链（[`ac-007`](../../../data/_vectors/clc-d/authorize-chain-vectors.json)：断链 + 无 id 操作 → `child_exceeds_parent`；[`ac-006`](../../../data/_vectors/clc-d/authorize-chain-vectors.json)：子项放宽 `limit` → `params_not_narrower`）。
3. **有效链授权** `G = Intersect(chain...)`。这一步让所有祖先的参数**和约束**同时生效（[`ac-009`](../../../data/_vectors/clc-d/authorize-chain-vectors.json)：祖先 `max_rows:10`，叶项未携带，操作请求 50 → 通过 union 轴得到 `max_rows:violated`；[`ac-015`](../../../data/_vectors/clc-d/authorize-chain-vectors.json)：`param_bounds` 取 meet 后保留祖先的 `max:50`，操作为 75 → `params_out_of_range`）。
4. **原样返回 `Authorize(G, op)`。**

**调用方义务：** 调用方必须提供完整、经过认证且以根项开头的链。该函数不会获取缺失环节，不会验证签名，也不会检测截断或重排——判定针对的是*提交的序列*（认证属于载体职责，§11）。双授权形式 `AuthorizeWithChain(parent, child, op)` 是其退化情况。

## 5. CLC-D 一致性与配置契约（§13.6、§13.8.1）

CLC-D 实现必须实现：有序各层的 `Contains`、该关系的两个 §13.5 代码（`child_exceeds_parent`、`params_not_narrower`）、配置契约、`AuthorizeWithChain`（修订 CLC-1.13）及其语料库，并且必须通过 `containment-vectors.json`。它不得改变任何 CLC-A 判定或代码。仅声明 CLC-A **并不表示**声明 CLC-D；也不得用交集代替包含关系。

**绑定配置**把载体的原生结构映射为 `Contains` 所比较的授权。其义务（§13.8.1）如下：(1) 映射前先解析载体的继承和默认值；(2) 保留身份维度（ATN `schema.digest` → 末尾 id 段，使不匹配时失败关闭）；(3) 对关系不可见的维度进行残差化——绝不能把未检查的维度也说成已检查；(4) 不得臆造载体语义（裸 AEGIS domain 不是命名空间通配符）；(5) 记录非目标：权限来源的并集、链级验证、跨载体身份都不在此关系内。

## 防混用清单

- [ ] `Contains` 只比较**标识符 + 参数**；约束和模式不参与（union 轴 + 配置预检）。
- [ ] 层顺序严格；原因 = 首个失败层，绝不会是 `delegation_mode_not_narrower`。
- [ ] 键集必须**完全相同**（对称闭包），不能只是子集。
- [ ] `AuthorizeWithChain` 门禁在操作验证前运行；只有链通过后，才会出现操作自身的第 1 层错误。
- [ ] `AuthorizeWithChain` = 门禁 → `Intersect(chain...)` → `Authorize`；交集负责让祖先约束继续生效。

## 常见误区

- **用交集代替包含关系**——交集讨论组合后的集合；包含关系则是逐子项、逐父项的准入判定。
- **允许子项删除父项约束**——需要链的 `Intersect` union，绝不能只靠包含关系。
- **缓存超过 Resolve 时域的 `allow`**——见 [08-constraints](08-constraints.md) §4；包含关系与 `allow_unresolved` 相互正交，绝不能把 `allow_unresolved` 当作包含结果。
- **（排除）§13.9 Related Work / §13.10 Open Issues**——仅供说明／记录已解决问题；见 `README.md` 覆盖图。

---
← [11-reason-codes.md](11-reason-codes.md) · → [13-conformance.md](13-conformance.md) · 相关：[09-intersection.md](09-intersection.md)、[13-conformance.md](13-conformance.md)
