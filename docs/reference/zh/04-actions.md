# 04 · Actions——Operation、ObservedAction、Identity

> **规范来源：** [`capability-language-core-v1.md`](../../capability-language-core-v1.md) §4 (Action)
> 本页是一份易读指南。如有冲突，以规范原文为准。
> 状态：Preview——不得用于生产环境。

## 速览

该语言围绕 actions 展开。它定义两种具体的 Action 形式，以及两个 identity 层级：

- **Operation**（§4.1）——authorization side 请求：一个 CapabilityId 加上参数。
- **ObservedAction**（§4.2）——evidence side 制品：effect boundary 对某个 material action 的投影，并绑定到 digest。
- **Identity**（§4.3）——**Class** = CapabilityId（覆盖一类 actions）；**Instance** = ActionId（通过 digest 标识某个 action 的 material 内容）。

Authorization 看到的是*类别*，evidence 看到的是*内容实例*。两者检查不同内容，绝不能混为一谈：“Entailment 检查 class 覆盖；Match 检查内容绑定”（§4.3）。

## 4.1 Operation（authorization side）

Operation 是接受授权的对象：`id`（CapabilityId）+ 可选的 `params`。

```
{ "id": "std/database-v1:query:SELECT",
  "params": { "tables": ["customers"], "limit": { "max": 50 } } }
```

- `id` 是 CapabilityId，其 class 成员关系由 [entailment](06-entailment.md) 检查。
- `params` 是 request 的参数绑定，受 [parameters](07-parameters.md) 规则约束。
- 没有 `id` 的 Operation 会在其他任何检查之前，在 layer 1 被拒绝——`deny("missing_capability_id")`（[`decide-017`](../../../data/_vectors/clc-v1/vectors.json)，grant `std/database-v1:query:SELECT`，request `{}`）。

## 4.2 ObservedAction（evidence side）

Effect boundary 根据 **executor 控制的事实**构建 ObservedAction。未经推导或检查相应事实，它绝不能直接复制 requester 提供的 action digest。

ObservedAction 包含：

| 字段 | 含义 |
|-------|---------|
| `action_type` | relying-party 固定的 type definition 所声明的 action-type 名称，也就是该投影所属的 class |
| `material_fields` | type definition 声明为 **material** 的所有字段 |
| `digest` | 根据规范化的 **material projection** 计算所得 |

**Material projection 是确定性的，也具有规范效力：**

1. Action type 声明一个 **material field set**（必需字段，以及可选但纳入的字段）。只有该集合参与 digest 计算。
2. 规范化序列化采用 **JCS**（[RFC 8785]）；v1 定义的唯一 suite 是 `jcs-sha256`。
3. Projection identity 使用语言自身定义的格式：`clc-action:1:<type>:<suite>:<b64url>`。**CAID** [CAID] 在自己的 suite registry 中覆盖*完整* Action Object，用于标识 action object，而不是某次 occurrence。二者通过 relying-party 固定的 **Action-Mapping Profile**（§6.4）关联，绝不能把两个字符串视为可互换。
4. Type **未**声明为 material 的字段必须从 digest 中排除，且绝不能影响 **Match**。携带未声明字段的 ObservedAction **不会因此失效**，但这些字段不携带 action identity。
5. Type 声明为 material 却**缺失**的字段，会使 ObservedAction **无法匹配**。绝不能推断、默认填充或修复其覆盖情况（`UNSATISFIED`，§10）。这是 key closure（§6.2）在 evidence side 的对应规则：缺少治理字段时必须 fail-closed，绝不 fail-open。

> 示例（取自 §4.3 identity 表自身的一行，省略 digest）：以 `clc-action:1:payment.release.1:jcs-sha256:...` 作为 ActionId，绑定某个 payment-release action 的 material projection，而不是其 occurrence。

## 4.3 Identity——两个层级

| 层级 | Identity | 范围 | 示例 |
|-------|----------|-------|---------|
| **Class** | `CapabilityId` | 覆盖一类*actions* | `std/database-v1:query:*` |
| **Instance** | `ActionId`（projection digest） | 某个 action 的 material *内容*，**不是** occurrence | `clc-action:1:payment.release.1:jcs-sha256:…` |

- CapabilityId 覆盖一个 class；ActionId 标识某个 action 的 material 内容。
- ActionId **不标识某次 occurrence**。它绑定的是已声明的 material 内容。要进一步关联到特定 occurrence，消费 profile 还必须定义并检查 **occurrence discriminator**。CAID-02 Section 4.5 将其作为可选的 `occurrence_id`；如果 profile 使用该字段，它必须出现在已声明的 material fields 中，才能影响 digest。唯一 occurrence 的分配，以及一次性消费/执行证明，不属于这两份文档的范围（CAID-02 Section 7）。
- **Entailment 检查 class 覆盖；Match 检查内容绑定**。这两种机制刻意位于不同层级。

## 这些内容如何参与判定

Decision function（[10-decisions.md](10-decisions.md)）在 authorization 时消费 Operation（`allow`/`deny`/`allow_unresolved`），在 evidence side 则消费用于 Match 的 ObservedAction（§6.4）。上述 material-projection 规则让不同消费方得到确定一致的 Match：同一组事实必须产生同一 digest。

## 常见误区

- **把 CAID 当作 projection identity。** 二者是范围不同的对象，只有 Action-Mapping Profile 能关联它们。
- **假定 ActionId 标识 occurrence。** 它不能；occurrence 关联由消费 profile 负责。
- **把未声明字段传入 Match。** 未声明字段不携带任何 identity，既不会增强也不会破坏可匹配性；但*已声明却缺失*的 material 字段会使 action 无法匹配。
- **盲目信任 Digest。** Effect boundary 必须根据 executor 控制的事实构建 ObservedAction。未经检查底层事实，绝不能使用 requester 提供的 digest。

---
← [03-identifiers.md](03-identifiers.md) · → [05-grants.md](05-grants.md) · 相关：[10-decisions.md](10-decisions.md)、[12-containment.md](12-containment.md)
