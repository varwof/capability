# 14 · 实战手册 — 场景驱动的配方

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) 附录 B 及锁定的向量文件所对应的一致性语料库
> 本页是便于阅读的指南。如有冲突，以规范为准。
> 状态：Preview — 不供生产环境使用。
> 每个配方都提炼自语料库场景；文中引用向量 id，便于重放。

## 速览

本篇以场景为主，概述语料库锁定的行为：构建授权、编写操作，并得到语料库断言的判定。配方的 reason code 可与 [11-reason-codes](11-reason-codes.md) 交叉查阅，具体细节则见对应页面。

## 1. 授权数据库查询

**授权：** `std/database-v1:query:SELECT`，`params: {"limit":100, "tables":["a","b"]}`。
**操作：** `std/database-v1:query:SELECT`，`params: {"limit":50, "tables":["a"]}`。
**判定：** `allow`——参数在边界内且属于子集（[`combined-001`](../../../data/_vectors/clc-v1/vectors.json)，通配符变体；正向 entailment 见 [`params-001`](../../../data/_vectors/clc-v1/vectors.json)）。将 `limit` 提到 150 → `deny("params_exceed_grant")`（[`combined-002`](../../../data/_vectors/clc-v1/vectors.json)）；请求 `tables:["a","b","c"]` → `not_in_enum`（[`params-004`](../../../data/_vectors/clc-v1/vectors.json)）。

**需要记住的快速检查：** 授权中的标量数字是**上限**；授权数组是**成员集合**（06/07）。显式请求 `tables:[]` → `deny("empty_bound_denies_class")`；这是授权侧规则，不是请求侧规则。

## 2. 合并两个来源

**来源 A：** `std/database-v1:query:SELECT`，`params: {"limit":100}`。**来源 B：** 相同 id，`params: {"limit":50}`。
**有效授权：** `{"limit":50}`——更紧的边界胜出（取最小值，不是取空；[09-intersection](09-intersection.md)）（[`intersect-004`](../../../data/_vectors/clc-v1/vectors.json)）。allowlist 取交集后只保留共同成员（[`intersect-001`](../../../data/_vectors/clc-v1/vectors.json)）；allowlist 不相交 → `deny("no_overlap")`。

**委派形式：** 三个来源中有一个未携带授权 → `deny("no_overlap")`（[`combined-008`](../../../data/_vectors/clc-v1/vectors.json)）；**零个**来源 → `deny("absent_source")`（[`intersect-007`](../../../data/_vectors/clc-v1/vectors.json)）；某一委派跳声明 `tables:[]` → 传播 `empty_bound_denies_class`（[`combined-011`](../../../data/_vectors/clc-v1/vectors.json)）。

## 3. 约束与残余通道

**授权 + 约束：** `std/database-v1:query:SELECT`，`constraints: ["varwof/constraint-v1:max_rows:100"]`；操作参数 `{"max_rows":500}` → `deny("max_rows:violated")`；`{"max_rows":100}` → `allow`（违规条件为严格 `>`；`decide-027`）。

**已识别但未求值：** 授权包含 `network:cidr:["192.0.2.0/24"]` → `allow_unresolved` + `unresolved:[<constraint>]`（[`decide-020`](../../../data/_vectors/clc-v1/vectors.json)）；跨午夜拆分的 `time:window` 同理（[`decide-024`](../../../data/_vectors/clc-v1/vectors.json)）。两个覆盖授权分别携带 `network:` 和 `time:` → 会携带二者的并集（[`decide-035`](../../../data/_vectors/clc-v1/vectors.json)）。**使用者必须求值或确认每个条目，否则必须拒绝**（[08-constraints](08-constraints.md) §3）。

**约束拒绝必须失败关闭：** 未知 `(scheme,type)` → `deny("unknown_constraint")`（[`decide-003`](../../../data/_vectors/clc-v1/vectors.json)；[`payments-002`](../../../data/_vectors/clc-v1/vectors.json)）；值不符合文法 → `deny("invalid_constraint")`（[`decide-019/-021/-022`](../../../data/_vectors/clc-v1/vectors.json)）；操作值超出定义域 → `max_rows:violated`（[`decide-031..034`](../../../data/_vectors/clc-v1/vectors.json)）。

## 4. 多授权聚合

**场景：** G1 `{"limit":10}`、G2 `{"limit":100}`、op `{"limit":50}` → `allow`——任一授权覆盖即可授权（[`decide-029`](../../../data/_vectors/clc-v1/vectors.json)）。反过来：G1 `{"limit":10}`、G2 `{"limit":6}`、op `{"limit":50}` → `deny("params_exceed_grant")`，并采用**规范顺序中首个覆盖该操作的授权**（具有确定性；[`decide-030`](../../../data/_vectors/clc-v1/vectors.json)）。操作 id 模型：授权缺失或为空 + 操作缺失 → `capability_not_authorized`（[`decide-016`](../../../data/_vectors/clc-v1/vectors.json)）；有效授权 + 操作 id 缺失 → `missing_capability_id`（[`decide-017`](../../../data/_vectors/clc-v1/vectors.json)）。

## 5. 包含关系与链授权

**父项：** `query:SELECT`，`params:{"limit":100}`。**子项：** `query:SELECT`，`params:{"limit":50}` → `contains:true`（[`contain-040`](../../../data/_vectors/clc-d/containment-vectors.json)）；反向 → `params_not_narrower`（[`contain-041`](../../../data/_vectors/clc-d/containment-vectors.json)）；scheme 不同 → `different_namespace`（[`contain-004`](../../../data/_vectors/clc-d/containment-vectors.json)）。

**融合式链：** `AuthorizeWithChain`——空链 → `absent_source`（[`ac-001`](../../../data/_vectors/clc-d/authorize-chain-vectors.json)）；子项跳放宽 → `params_not_narrower`（[`ac-006`](../../../data/_vectors/clc-d/authorize-chain-vectors.json)）；断链本会掩盖无 id 操作 → `child_exceeds_parent`（[`ac-007`](../../../data/_vectors/clc-d/authorize-chain-vectors.json)）；祖先约束仅通过 `Intersect` 生效 → `max_rows:violated`（[`ac-009`](../../../data/_vectors/clc-d/authorize-chain-vectors.json)）。

## 6. 证据侧 satisfaction（暂不声明的 CLC-E 摘要）

证据关系（§6.4/§10）已实现，并由 `evidence-vectors.json`（32）锁定，但该类别**未声明**（[13-conformance](13-conformance.md)）。如果现在基于这些关系开发，请注意：`Satisfy` 报告二值 `SATISFIED`/`UNSATISFIED`；顶层内部 `unknown` 必须是 `UNSATISFIED`，绝不是 `SATISFIED`；`ActionId` 是**所声明材料投影**的 JCS 摘要——未声明字段不得影响它，缺少已声明的材料字段会使操作无法匹配。

## 7. 必须牢记的配方反模式

| 反模式 | 失败原因 | 修复方式 |
|--------------|-------------|-----|
| 把 `allow_unresolved` 当作 `allow` | 枚举值不同；残余义务是增量的 | 求值/确认，否则拒绝（08） |
| 在 enum 交集中合并字符串 `"1"` 和数字 `1` | 相等性对 JSON 类型敏感 | §6.2 规范化后再比较（intersect-011/-012） |
| 允许子项删除祖先约束 | 约束不属于 `Contains`，而是通过 union 组合 | 链式 `Intersect` 让祖先约束生效（ac-009） |
| 把标量数字向下规范化为 bool(`1`) | 布尔值要求完全相等，绝不按数值比较 | `{"flag":1}` 与授权 `{"flag":true}` → deny（params-022） |
| 预期无 id 操作会得到 `capability_not_authorized` | 第 1 层操作 id 代码会明确传播 | `missing_capability_id`（decide-017） |
| 假设各 minor 的 `param_bounds` meet 判定稳定 | 1.10→1.15 的历史在此不稳定 | 声明正确修订，使用 §12.1 门禁（13） |

---
← [13-conformance.md](13-conformance.md) · → [15-glossary.md](15-glossary.md) · 相关：[01-quickstart.md](01-quickstart.md)、[11-reason-codes.md](11-reason-codes.md)
