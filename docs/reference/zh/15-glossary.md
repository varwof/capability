# 15 · 术语表

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §2、§13.2
> 本页是便于阅读的指南。如有冲突，以规范为准。
> 状态：Preview — 不供生产环境使用。

## A

**Action** — 被引用的对象：抽象操作类别（授权侧），或具体声明的效果（证据侧）。见 [04-actions](04-actions.md)。

**ActionId** — 证据侧标识符：ObservedAction 所声明材料投影的 JCS 摘要（§4.2/§6.4）。未声明字段不得影响它；缺少已声明的材料字段会使该操作无法匹配。

**allow** — 授权判定：操作已被完全执行，不存在残余义务。与 `allow_unresolved` 不同（§9/§11）。

**allow_unresolved** — 授权判定：授权成立，但 `unresolved` 中至少携带一个已识别但未求值的约束。它绝不等同于 `allow`；无法求值或确认约束的使用者必须拒绝（§8.4）。

**Authorize** — Decision 函数：`Authorize(grants, operation) → Decision`（§9）。

**AuthorizeWithChain** — 融合式链检查（CLC-D）：先对每一对相邻跳执行 `Contains`，再执行 `Intersect(chain...)`，最后执行 `Authorize`（§13.11）。

## B

**Binding** — 将 Identity 关联到 Action 的关系：Entailment（授权侧）或 Match（证据侧）。*不是*密钥绑定（cnf/DPoP/mTLS），后者属于原生工件的规范（§11）。

**Bound** — 按 §6.2/§8.1 值语义解释的已声明约束值（§13.2）。

**BoundMeet** — `Intersect` 用来跨来源组合 `param_bounds` 的 §6.6 meet（§6.6）。见 [07-parameters](07-parameters.md)。

## C

**CapabilityId** — 按 §3 文法标识某 scheme 内一类 Action 的结构化名称（§2/§3）。

**CLC-A / CLC-D / CLC-E** — 一致性类别：授权基线（已声明）、委派包含（已声明）、证据侧（**已实现，未声明**）（§12）。见 [13-conformance](13-conformance.md)。

**CLC-<major>.<minor>** — 实现所声明、且各输入编写时所依据的语言修订；未声明的输入视为 CLC-1.0（§12.1）。

**Constraint** — 对 Action 可如何使用（授权侧）或需要哪些证据（证据侧）的限制；其身份是 `(scheme,type)` 对（§8.1）。不属于 `Contains` 关系（§13.4.4）。

**ConstraintUnion** — 派生投影：链中约束字符串经规范化后按确定顺序排列的并集（§7.1）。见 [09-intersection](09-intersection.md)。

**Contains(parent, child)** — 包含关系（CLC-D）：子项声明的授权是否位于父项声明的授权内？（§13.4）

## D

**Decision** — 授权侧结果：`{verdict: "allow"|"deny"|"allow_unresolved", reason, unresolved}`（§9）。

**Declared set** — 授权作为操作限制而携带的参数（§6.2 值语义），以及其已声明键集（`params` 和 `param_bounds` 键的并集）（§13.2/§13.4.3）。

**delegation_mode_not_narrower** — 由**绑定配置预检**产生的 CLC-D reason code（§13.4.5），绝不由 `Contains` 产生（§13.5）。见 [12-containment](12-containment.md)。

**deny** — 授权判定：操作未获授权，并带有稳定 reason code（§9）。

## E

**Empty bound** — `[]`/`{}` **出现在值位置**——显式为空，因此拒绝该类。注意区别于 `params:{}`（不构成限制）（§7 规则 6、§13.2）。

**Entailment** — 授权侧绑定：授权覆盖操作（⊆）（§6.1）。

**Evidence side** — Match（§6.4）/ Satisfy（§10）机制及证据侧约束（§8.2）；已锁定，但**未声明为** CLC-E（§12）。

## G

**Grant** — Principal 对某个 CapabilityId 的授权，可带可选 params、`param_bounds` 和约束（§5）。

## I

**Intersection** — 将多个授权来源组合成有效集合（∩）；P_effective = P_principal ∩ C_agent ∩ P_gateway（§7）。

## M

**Match** — 证据侧绑定：证据绑定到完全相同的 Action（MATCH / NOT_EQUIVALENT / INDETERMINATE）（§6.4）。

**Mode lattice** — 载体定义的委派模式顺序，由绑定配置检验（§13.4.5）；AIC-JWT：`authorized < representative`。

## N

**Narrower** — 子项授权的每个声明值都位于父项边界内，且其键集由父项键集闭包（§13.2）。

**Native verification** — 原生工件规范所涵盖的签名、模式、时效性检查，位于 CLC 之外（§11）。

## O

**Operation** — 具体 Action 请求：一个 CapabilityId 加参数（§4.1）。

**ObservedAction** — 证据侧对已执行具体 Action 的记录（§4.2）。

## P

**params** — 授权上声明的参数限制（§6.2）。`params:{}` ≡ 未声明 = 不受约束。

**param_bounds** — 扩展参数边界字段（CLC-1.10+）（§6.5）；一个键只能位于 `params` **或** `param_bounds`，绝不能同时位于两者。

**Profile (binding)** — 载体将其原生授权结构映射到 CLC grants 的方式（§13.8.1）。

## R

**Reason code** — 稳定标识符；规范代码 = 第一个 `:` 之前的所有内容；`: <detail>` 只是诊断后缀（§9.2）。

**Resolve** — 决策后函数，消费 Decision 并履行残余义务（§8.5）。

**Residual obligation** — `unresolved` 中携带的、已识别但未求值的约束（§8.4）。

## S

**Satisfaction** — 证据侧判定：`SATISFIED` 或 `UNSATISFIED`（二值；`unknown` 只在内部使用）（§10）。

## U

**unsupported_language_revision** — 输入声明的修订不兼容时，失败关闭所用的原因（§12.1）。

**unresolved** — Decision 上已识别但未求值约束的增量列表；只有与 `allow_unresolved` 一起才表示授权，绝不会单独授权（§8.4/§11）。

## V

**Verdict** — 求值结果：`allow`/`deny`/`allow_unresolved`（授权侧，小写），或 `SATISFIED`/`UNSATISFIED`（证据侧，大写）（§2/§9/§10）。

## W

**Wildcard** — 标识符末尾的 `*` Action 段；匹配一个或多个末尾段，绝不匹配零个。v1 中，裸 `*`、部分段、`**`、`{a,b}`、`[a-z]` 均为 `unsupported_wildcard`（§3）。

---
← [14-cookbook.md](14-cookbook.md) · → [16-principles.md](16-principles.md) · 相关：[02-overview.md](02-overview.md)、[README.md](README.md)
