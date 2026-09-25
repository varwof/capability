# CLC-v1 语言参考

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md)——完整的 CLC-v1 规范。
> 本参考集是一份易读指南。如有冲突，以规范原文为准。
> 状态：Preview——不得用于生产环境。

欢迎阅读 **Capability Language Core v1（CLC-v1）** 的易读语言参考。这是一种精简、确定性的语言，用于描述 agent 被授权执行的操作。

本参考的组织方式类似编程语言手册：先给出快速入门，再逐页讲解概念、字段表、来自一致性测试集的 ✅/❌ 示例，最后附上 reason code 速查表。本参考**派生自**规范：每页的论断都锚定到具体规范章节；每个 JSON 示例要么来自真实测试集 vector，要么依据明确给出的语法规则构造。

## 16 个页面一览

| # | 页面 | 内容 | 规范锚点 |
|---|------|----------------|-------------|
| — | [`README.md`](README.md) | 本索引：阅读路径、权威说明、覆盖图、规范基线 | 全文 |
| 01 | [`01-quickstart.md`](01-quickstart.md) | 无需运行时，四步构建第一个 grant → request → verdict | §5/§6/§9 |
| 02 | [`02-overview.md`](02-overview.md) | 五个核心模型、三值判定、与载体无关的边界、设计原则 | Abstract/§1/§11 |
| 03 | [`03-identifiers.md`](03-identifiers.md) | `capability-id` 语法、通配符、scheme 消歧 | §3 |
| 04 | [`04-actions.md`](04-actions.md) | Operation、ObservedAction、Identity 与 ActionId 投影 | §4 |
| 05 | [`05-grants.md`](05-grants.md) | 逐字段讲解 Grant 对象 | §5 |
| 06 | [`06-entailment.md`](06-entailment.md) | 授权绑定：entailment、§6.3 算法与 evidence Match | §6.1/6.3/6.4 |
| 07 | [`07-parameters.md`](07-parameters.md) | Params、扩展的 `param_bounds` 与 `BoundMeet` | §6.2/6.5/6.6 |
| 08 | [`08-constraints.md`](08-constraints.md) | Constraint 标识、值语法、剩余义务与 `Resolve` | §8 |
| 09 | [`09-intersection.md`](09-intersection.md) | grant 的交集 ∩ 与 `ConstraintUnion` 投影 | §7 (7.1) |
| 10 | [`10-decisions.md`](10-decisions.md) | Decision 与 satisfaction 函数、verdict、reason 排序 | §9/§10 |
| 11 | [`11-reason-codes.md`](11-reason-codes.md) | **全部** reason code 的一页速查表 | §9.1/9.2/13.5/C.2 |
| 12 | [`12-containment.md`](12-containment.md) | 委派包含、CLC-D、AIC-JWT 绑定与 `AuthorizeWithChain` | §13 |
| 13 | [`13-conformance.md`](13-conformance.md) | 一致性类别、测试集、语言修订规则 | §12/12.1/Appendix B |
| 14 | [`14-cookbook.md`](14-cookbook.md) | 从测试集提炼的场景化 ✅/❌ 配方 | 全部 vectors |
| 15 | [`15-glossary.md`](15-glossary.md) | 按字母顺序排列的术语表 | §2/§13.2 |

## 三条阅读路径

- **编写授权策略**（你负责配置 grants）：`01-quickstart` → `05-grants` → `07-parameters` → `08-constraints` → `14-cookbook`。
- **实现验证器**（你负责构建或审计求值器）：`02-overview` → `03-identifiers` → `06-entailment` → `09-intersection` → `10-decisions` → `11-reason-codes` → `13-conformance`。
- **构建委派链**（你需要 `Contains`/`AuthorizeWithChain`）：`02-overview` → `12-containment` → `13-conformance`。

## 权威说明

- **规范** [`capability-language-core-v1.md`](../../capability-language-core-v1.md)是 CLC-v1 语义、verdict、reason code 和一致性义务的*唯一*权威来源。本参考页只是编辑层面的重新呈现，不能被视为独立于规范。
- 每页都带有“规范来源”横幅，并列明它所总结的具体章节。如果本指南与规范冲突，以**规范**为准。
- 该语言的状态是 **Preview / Working Draft**。这些页面均不应作为生产决策的依据。
- JSON 示例尽可能追溯到测试集 vectors（见 id 链接），否则会标为**依据 §X grammar 构造**。不得在未给出规则的情况下随意编造。

## 一致性状态（简版）

完整且措辞严谨的说明见 `13-conformance` 和 `Spec` §12。简而言之：测试集和三个同一作者的实现（Go/Python/TypeScript）都覆盖 **CLC-A**（声明的基线授权类别），并提供 **CLC-D**（containment）。**CLC-E**（evidence side）已有实现和测试集固定，但**未声明支持**。它未达到 §12 要求的两个*独立*实现；由同一作者完成的多个实现彼此一致，只能算回归测试，不能算独立验证。

## 覆盖图（规范章节 → 参考页）

| 规范部分 | 参考页 | 说明 |
|-----------|----------------|-------|
| Abstract | `02-overview`, `13-conformance` | 两处均如实重复一致性的适用边界 |
| Revision History | `13-conformance`（§12.1 规则） | 逐版本表格只保留在规范中 |
| §1 Design Principle | `02-overview` | 核心存在的原因；P1–P12 |
| §2 Terminology | `15-glossary` | 全部已定义术语，按字母排序 |
| §3 Grammar | `03-identifiers` | capability-id、wildcard、scheme 消歧 |
| §4 Action | `04-actions` | 4.1 Operation / 4.2 ObservedAction / 4.3 Identity |
| §5 Grant | `05-grants` | 逐字段拆解 |
| §6 Binding | `06-entailment`, `07-parameters` | 6.1 entailment → 06；6.2 parameters → 07；6.3 algorithm → 06；6.4 match → 06；6.5 `param_bounds` → 07；6.6 `BoundMeet` → 07 |
| §7 Intersection | `09-intersection` | 7.1 `ConstraintUnion` → 09 |
| §8 Constraint | `08-constraints` | 8.1 auth-side / 8.2 evidence-side / 8.3 unified grammar / 8.4 residual channel / 8.5 `Resolve` |
| §9 Decision Function | `10-decisions`, `11-reason-codes` | 9.1 ordering → 10；9.2 reason codes → 11 |
| §10 Satisfaction Function | `10-decisions` | evidence-side 三值报告 |
| §11 Semantic Boundary | `02-overview` | CLC 刻意**不**定义的内容 |
| §12 Conformance | `13-conformance` | 12.1 Language Revision → 13 |
| §13 Delegation Containment | `12-containment` | 13.1–13.8、13.11、13.12 → 12；**不包含** §13.9 Related Work 和 §13.10 Open Issues（作为延伸阅读链接列在 12-containment 末尾） |
| Appendix A Consumption Mapping | `10-decisions` | 消费方如何映射 verdicts |
| Appendix B Reference Vectors | `13-conformance`, `14-cookbook` | 测试集布局，以及 cookbook 如何从测试集提炼内容 |
| Appendix C Carrier Vocabulary & Reason-Code Mapping | `12-containment`, `11-reason-codes` | C.1 vocabulary → 12；C.2 failure-code mapping → 11 |
| Security / IANA / Privacy Considerations | **不包含** | `02-overview` 中用一段文字指向规范对应章节 |
| Acknowledgements / References | **不包含** | 各页只在需要时列出 normative references |

**刻意排除的内容**（按任务红线固定）：Acknowledgements、References、Security/IANA/Privacy Considerations 全文，以及 §13.9 Related Work / §13.10 Open Issues。`02-overview` 和 `12-containment` 会指出这些内容的存在。

## 规范基线

`Spec baseline: 46b10d1c64433ec74592dff44cdb4c68ae91073f`（编写本参考时 capability 仓库的 `git rev-parse HEAD`；本参考集所依据的规范文本，是日期为 2026-09-25 的工作树修订版）。

---
← *本文件是索引。* · → 继续阅读 [`01-quickstart.md`](01-quickstart.md) · 相关：[`02-overview.md`](02-overview.md)、[`13-conformance.md`](13-conformance.md)
