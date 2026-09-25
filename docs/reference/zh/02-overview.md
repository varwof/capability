# 02 · 概览——CLC-v1 是什么，以及它刻意不做什么

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) Abstract、§1 Design Principle、§11 Semantic Boundary
> 本页是一份易读指南。如有冲突，以规范原文为准。
> 状态：Preview——不得用于生产环境。

## 速览

CLC-v1 是一种**精简、可执行、与载体无关的语言**，用于说明 agent 被授权执行哪些操作。它只求值一种关系——*grant ∈ operation*——并返回三值 verdict（`allow`、`deny`、`allow_unresolved`）和稳定的 reason code。它刻意**不是**策略引擎、信任模型或线格式：它只定义*求值什么*，绝不定义*如何承载、签名或验证*。

## 五个核心模型

CLC-v1 建立在五个基础抽象之上（规范 §1）。授权侧和 evidence 侧都使用这五个模型，区别只在方向。

| # | 模型 | Authorization side | Evidence side | 参考页 |
|---|-------|--------------------|---------------|----------------|
| 1 | **Identity** | CapabilityId（授权哪一类对象） | ActionId（实际发生了哪个具体实例） | [`03-identifiers.md`](03-identifiers.md)、[`04-actions.md`](04-actions.md) |
| 2 | **Grant** | 一项声明的权限，可以收窄 | 一项被断言的事实 | [`05-grants.md`](05-grants.md) |
| 3 | **Binding** | entailment：grant ⊆ operation | match：evidence ↔ action | [`06-entailment.md`](06-entailment.md) |
| 4 | **Constraints** | params / `param_bounds` / constraints | evidence requirements / freshness | [`07-parameters.md`](07-parameters.md)、[`08-constraints.md`](08-constraints.md) |
| 5 | **Intersection** | 来自多个来源的 grants 取 ∩，然后判定 | — | [`09-intersection.md`](09-intersection.md) |

这五个模型的设计意图——以及该语言**拒绝承担**的事项——在 `capability-language-core-principles-v1.md` 的十二项原则中均有说明：

> P1 minimal core · P2 no control flow · P3 immutable values ·
> P4 domains, not types · P5 deterministic and terminating ·
> P6 fail-closed · P7 define once, consume everywhere ·
> P8 carriers separate from semantics · P9 local decidability ·
> P10 bounded work · P11 composition narrows only ·
> P12 ≥2 independent implementations

其中两项原则对理解其余内容最为关键：

- **P6 fail-closed**——任何无法识别或格式错误的输入都会得到 deny 和 reason code，绝不静默 allow，也绝不崩溃。
- **P11 composition narrows only**——多个 grants 相交，所得权限绝不会比任一来源更宽。测试集用 1184 个 property cases 固定了这一规则（§7，即 P11 的“墙”）。

## Verdict 采用三值

| Verdict | 含义 | 消费方可以做什么 |
|---------|---------|------------------------|
| `allow` | request 完全位于覆盖它的 grant 内，且每个已求值 constraint 都成立 | invoke |
| `deny` | 不属于任何 grant，或违反 constraint/param | 拒绝；reason code 会说明原因 |
| `allow_unresolved` | 位于某个 grant 内，但至少一个已识别的 constraint 未被 core **求值**（如 `network`、`time`） | 自行履行每项 `unresolved` 义务，否则拒绝。绝不能视为 `allow`（§8.4） |

第三种 verdict 既不是 evidence，也不是“附带保留意见的 allow”。§11 明确规定，`allow_unresolved` 是一种*授权*结果，不能理解为“仍需 evidence”。无法求值某项义务的消费方必须 deny。

## 与载体无关的边界

CLC-v1 准确定义*求值什么*和*输出表示什么*，然后就此停止。§11 列出了该语言**不**定义的内容：

- **Trust models**——谁签署什么、issuer trust、委派链（属于 AIC-JWT、OAuth、SPIFFE 等）。
- **Native verification**——签名检查、schema 验证、freshness 强制执行（各自原生制品的规范负责）。
- **Execution lifecycle**——消费、调用、对账、结果分类（EMILIA AEB 或同等机制）。
- **Receipt 或 token formats**——承载 grants、evidence 或 bindings 的线格式。

因此，两者之间有清晰边界：*CLC-v1 定义**什么**；消费方定义**如何处理**以及**拿到结果后做什么**。同理，§6.2 的输入边界拒绝也严格对应收到的文本。规范化后的解码值并不等同；一个流水线若能把 permit 用于从未检查过文本的 request，就已越出 CLC 边界（§11）。

## Constraints：已求值，或可识别但未求值

在 `varwof/constraint-v1` scheme 下，core 只识别 `max_rows`、`time` 和 `network`（§8.1）：

- **`max_rows`**——core 使用 request 的 `max_rows` param 对它求值（`max_rows:violated`）。
- **`network` / `time`**——可识别、进行语法检查，并放入 `unresolved`，但此处不求值（§8.4）。这是*剩余义务通道*。系统会明确返回义务，绝不静默丢弃。

其他任何 scheme 或 type 都会返回 deny `unknown_constraint`。详见 [`08-constraints.md`](08-constraints.md)。

## 当前一致性状态（真实范围）

- **CLC-A**（authorization side）是已声明的基线，公开的 `vectors.json` 和 `property-cases.json` 测试集对其进行覆盖（§12）。
- **CLC-D**（containment，§13）随本修订版提供，并配有独立测试集。见 [`12-containment.md`](12-containment.md)。
- **CLC-E**（evidence side）已有实现和测试集固定，但本修订版**未声明支持**。
- 三个实现（Go/Python/TypeScript）**由同一作者完成**。它们的一致性只是针对规范文本的回归测试，**不是独立验证**。因此，§12 要求的两个独立实现（原则 P12）明确记录为**未满足**。

完整的措辞，以及各实现声明每一类别时必须满足的条件，见 [`13-conformance.md`](13-conformance.md)。

为完整起见，规范还包含 Security、IANA、Privacy Considerations 和 References 部分（normative：BCP 14、RFC 2119/RFC 8174、RFC 3339、RFC 7493、RFC 8785）。这些页面不复现它们，但在规范中具有权威性；上线前值得阅读。

## 常见误区

- **把 `allow_unresolved` 当作 `allow`** 是最危险的误读，它会破坏 fail-closed 设计（§8.4/§11）。
- **误以为 CLC 是策略语言。** 它没有控制流、可变状态或通用逻辑（P2/P3）；判定是确定性且必然终止的（P5）。
- **把载体语义化。** grant/SIGNED 放在其他 envelope 中，并不意味着 CLC 定义了签名；那是载体的工作（P8）。
- **期望 `intersect` 扩大权限。** 由于组合只会收窄（P11），两个 grants 相交绝不会授予比任一来源更多的权限。

---
← [01-quickstart.md](01-quickstart.md) · → [`03-identifiers.md`](03-identifiers.md) · 相关：[`13-conformance.md`](13-conformance.md)、[`15-glossary.md`](15-glossary.md)
