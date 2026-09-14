# 能力语言核心 v1（CLC-v1）

> **预览版** —— 不可用于生产环境。正式发布前 API 与功能可能变更。

**类别**：实验性 | **状态**：工作稿 | **日期**：2026-09-10 | **最后修订**：2026-09-13

> **与英文正本的关系**
>
> 本文件是英文正本 `capability-language-core-v1.md` 的**中文对照版**，供中文评审使用。
> **规范性以英文正本为准**；两版若出现歧义，以英文正本为准。
>
> 为避免两份数据漂移，本文件**不重复**附录 B 的逐条向量表与机器可读语料 —— 它们是数据，
> 权威副本在 `data/_vectors/clc-v1/`（`vectors.json` 105 条、`property-cases.json` 1184 条、
> `evidence-vectors.json` 32 条），条目说明见英文正本 Appendix B。代码块、标识符、
> 原因码与协议字段名一律保持原样不译。

## 摘要

本文件定义**能力语言核心（CLC）** —— 一门最小化、可执行的「代理被授权做什么」描述语言。
它定义：能力标识符文法、授权（grant）与操作（operation）之间的**蕴涵**关系、多来源授权的
**交集**、约束模型，以及一个**确定性裁决函数**（带稳定原因码与三值裁决
`allow` / `deny` / `allow_unresolved`）。

本语言**与承载方式无关**：它定义「评估什么」，不定义「如何承载与如何建立信任」。信任模型、
原生验证、执行生命周期、回执或令牌格式均不在范围内（见 §11）。一致性由公开语料检验：
**105 条向量 + 1184 条性质用例**，三个共享同一作者的实现（Go / Python / TypeScript）全部通过。
**实现符合性与「本文件声称某个一致性类」是两件事。** 一个实现满足 §12 为该类列出的义务，就是符合 CLC-A，
它可以自行声称这一符合，与还存在多少别的实现无关；§12 另外为**本文件**的声称设了一条成熟度门槛
—— 两个独立实现在裁决与原因码上一致 —— 这条门槛对 CLC-A 已满足。本修订声称**授权侧一致性类 CLC-A**。
证据侧一致性类 **CLC-E 不声称**：它的关系、值文法、参考实现与语料都在本修订里，但该门槛尚未达到。

### 修订历史

（语言修订规则见 §12.1 —— 本修订为增量、可兼容读取。）

| 修订 | 日期 | 影响范围 | 变更 |
|-----|------|-------|--------|
| CLC-1.1 | 2026-09-10 | — | 基线工作稿 |
| CLC-1.2 | 2026-09-12 | §7, §8.1, §8.4(新), §9, §9.2, §11, §12, 附录 B, 安全 | 残差义务通道 `unresolved`（被识别但未求值的约束显式携带，绝不静默丢弃）；`time:window` 值文法定为多段 UTC 窗口数组；识别升级为「类型名 × 值文法」双重校验并新增 `invalid_constraint` 原因码；「time → intersection」合并规则降级到 v2；约束合并归一化并确定性排序 |
| CLC-1.3 | 2026-09-12 | §1, §6.2, §8.1, §8.4, §9, §9.1, 附录 B | 授权闭环收紧 + 约束身份命名空间化：`Decision.verdict` 三值化（`allow`/`deny`/`allow_unresolved`），残差义务不再混入 `allow`（消除「消费方只判 `verdict == allow`」导致的 fail-closed 断裂，§8.4）；约束身份改为 `(scheme,type)` 二元组，core 只识别 `varwof/constraint-v1` 下的 `max_rows`/`time`/`network`，其余一律 `unknown_constraint`（消除跨 scheme 语义污染，§8.1）；`time:window` 值文法收紧：单段必须同日内（`start < end`），**禁止单段跨午夜**（跨午夜须拆成两段，`end:"00:00"` 保留表示「次日零点」），段列升序、互不重叠、≤32；`params:{}` 与缺席等价 = 无参数约束（蕴涵与交集语义一致）；多 grant 聚合规则显式化（任一覆盖即授权 + 残差义务并集 + 确定性拒绝原因，§9.1） |
| CLC-1.4 | 2026-09-13 | §6.2, §8.1, §10, §12, 附录 B | 操作侧值域收紧：`max_rows` 请求必须携带**有限非负整数**，其余（字符串、布尔、负数、分数、非有限数）一律 `max_rows:violated`，不再未经检查地放行。尺寸上限在所有路径（解码与原始）重申并按**规范化序列化的 UTF-8 八位组**实现；以码点或 UTF-16 码元计量不符合规范（非 ASCII 边界向量 `params-028`/`params-029` 固定该行为）。同一工作修订内完成证据侧范围：证据侧值文法（`varwof/evidence-v1:*`）与 `CLC-REQUIREMENT-v1` 被定义（§8.2、§10），证据侧语料随本修订发布（§12，`evidence-vectors.json`，30 条，含 ActionId/Match）—— **CLC-E 已实现并由语料钉住，但不声称**，因为声称需要两个独立实现（§12；原则文件 P12）；通用性由 `crosswalk-vectors.json`（13 条，双向）检验 |
| CLC-1.5 | 2026-09-14 | §4.2、§4.3、§6.4、§10、§11、§12、消费者表、安全考虑 | **实例身份不再自称 CAID。** 投影身份属于本语言自己（`clc-action:1:<type>:<suite>:<b64url>`），v1 的 suite 集合只保留 `jcs-sha256`（自造的 `jcs-sha384` 删除），并写明 CAID **不是**什么：它覆盖**完整** Action Object，且不标识某次「发生」；本投影只覆盖声明的实质集合，绑定「发生」要消费执行边界提供的判别符。§10 写明逐约束三值求值 → 顶层二值报告的折叠（顶层 `unknown` **必须**产出 `UNSATISFIED`）；§11 写明 `allow_unresolved` 是授权结果而非证据，并固定分层（CAID 作素材动作身份、AEC 作证据满足、AEB 作边界生命周期）；§12、消费者表与安全考虑不再把委托链读作包含关系。CLC-A 的规范算法未变，CLC-1.4 的输入仍可读。  **本修订的 2026-09-14 复核更正**（仅文本）：致谢改为如实写明重跑了哪些套件、针对哪个修订；§12.1 声明 CLC-1.5；原因顺序与原因码两节按渲染编号引用为 §9.1/§9.2；§9 写明附录 D15 已钉住的「grant 侧预检优先」；摘要把「实现符合性」与「本文件的声称」分开；occurrence 那句点明 CAID-02 §4.5/§7。 |
| CLC-1.6 | 2026-09-14 | §4.3, §6.2, §10, §12, 附录 B | **`jcs-sha256` 现在是真正的 RFC 8785 实现。** 规范化序列化不再使用 `json.Marshal` 的 HTML 转义（它把 `&`、`<`、`>` 写成 `\u0026`、`\u003c`、`\u003e`）：对象成员按 UTF-16 码元排序（§3.2.3），字符串按 §3.2.2.2 转义（只转义 `"`、`\` 与控制字符），数字按 ECMAScript `Number::toString`（§3.2.2.3），无多余空白；非法 UTF-8 或孤立代理项直接报错，不再替换成 U+FFFD。**字节因此改变：任何包含 `&`、`<`、`>` 的素材，其 `clc-action:` 标识符与 Decision Record 输入摘要都会改变 —— 旧摘要不是 JCS，不得与新摘要直接比较。** 当 UTF-16 序与 UTF-8 字节序不一致时，非 ASCII 对象键的排序也会改变。CLC-A 的判定不变，CLC-1.4/1.5 输入仍可读；证据语料增至 32 条（新增 RFC 8785 `&` action-id 向量与断言导出 §10 `Satisfaction` 报告的 requirement 向量）。 |

---

## 1. 设计原则

CLC-v1 是一门**通用的最小语言**，它可以一致地呈现为**授权侧**或**证据侧**。

两侧共享五个基础抽象：

| 基础 | 授权侧 | 证据侧 |
|------------|-------------------|---------------|
| **动作（Action）** | Operation（具体请求） | ObservedAction（被断言的效果） |
| **身份（Identity）** | CapabilityId（类级） | ActionId（实例级） |
| **绑定（Binding）** | Entailment（grant ⊆ operation） | Match（evidence ↔ action） |
| **约束（Constraint）** | Grant 参数 / 上界 | 证据要求 / 新鲜度 |
| **裁决（Verdict）** | allow / deny | SATISFIED / UNSATISFIED |

两侧的语言结构完全相同，只是方向相反：

- 授权：「我授予你做 X 的许可」
- 证据：「我有证据表明 X 已经发生」

这套核心背后的设计原则 —— 包括语言**刻意拒绝**的东西（无控制流、无可变状态、非通用策略语言）
—— 见 `capability-language-core-principles-v1.md`：

> P1 最小核心 · P2 无控制流 · P3 值不可变 · P4 用域而非类型 · P5 确定且可终止 ·
> P6 fail-closed · P7 只定义一次、处处消费 · P8 承载与语义分离 · P9 本地可判定 ·
> P10 有界工作量 · P11 组合只收窄 · P12 ≥2 个独立实现

---

## 2. 术语

| 术语 | 定义 |
|------|-----------|
| **Action（动作）** | 被引用之物 —— 授权侧是抽象的操作类，证据侧是具体的被断言效果。 |
| **CapabilityId** | 在某个 scheme 内标识**一类**动作的结构化名称。 |
| **Operation（操作）** | 具体动作请求：CapabilityId + 参数。 |
| **Grant（授权）** | 主体对某 CapabilityId 的授权，可带参数与约束。 |
| **Binding（绑定）** | 连接「身份」与「动作」的抽象概念；Entailment（授权侧）与 Match（证据侧）是它的两个具体实例。 |
| **Entailment（蕴涵）** | 授权侧绑定：「Grant G 覆盖操作 O」（⊆）。 |
| **Match（匹配）** | 证据侧绑定：「证据 E 绑定到确切动作 A」。 |
| **Constraint（约束）** | 对动作可被如何使用（授权侧）或需要什么证据（证据侧）的上界。 |
| **Intersection（交集）** | 把多个授权来源合并为一个有效集合（∩）。 |
| **Verdict（裁决）** | 评估结果：授权侧 `allow`/`deny`/`allow_unresolved`，证据侧 `SATISFIED`/`UNSATISFIED`。 |
| **Decision（决定）** | 授权侧裁决：`allow`、`allow_unresolved` 或 `deny` + 原因（外加**可叠加**的 `unresolved`）。 |
| **Satisfaction（满足）** | 证据侧裁决：`SATISFIED` 或 `UNSATISFIED`。 |

说明：CLC-v1 中的 **Binding** 指「身份 ↔ 动作」关系（授权侧为覆盖，证据侧为匹配），
**不是**密钥绑定（cnf / DPoP / mTLS 发送方约束）—— 后者属于原生工件的规范（见 §11）。

裁决在授权侧用小写（`allow`/`deny`），在证据侧用大写（`SATISFIED`/`UNSATISFIED`），
沿用 EMILIA/AEB 的惯例。

---

## 3. 文法

```
capability-id = scheme ":" action
scheme        = vendor "/" product "-v" major
vendor        = 1*( ALPHA / DIGIT / "-" )
product       = 1*( ALPHA / DIGIT / "-" )
major         = 1*DIGIT
action        = segment *( ":" segment )
segment       = 1*( ALPHA / DIGIT / "-" / "_" / "." )
wildcard      = action ":" "*"
```

v1 标识符形如 `scheme:action`（例如 `std/database-v1:query:SELECT`）。
作为**完整段**的结尾 `*` 匹配其后**一个或多个**段（它不匹配空剩余部分：
`std/database-v1:query:*` 不覆盖 `std/database-v1:query`）。

**v1 的通配范围**：CLC-v1 核心只定义**一种**通配形状 —— 结尾的完整段 `*`。
部分通配（`std/crm-v1:re*`）、裸 `*`、`**`、`{a,b}`、`[a-z]` 均**保留给 v2**；
符合 v1 的实现**必须**拒绝它们（`unsupported_wildcard`）。若某个能力 scheme 自行声明了扩展文法，
该 scheme 的符合实现可以接受它；但 CLC-v1 核心一致性既不要求也不授权这些形式（见 §12）。

**通配检测先于文法一致性**。当同一字符串既含被禁止的通配形状、又违反基础文法（§3 `segment`）时，
报告的必须是 `unsupported_wildcard`：通配形状检查先于通用的 `invalid_capability_id` 检查。

**示例**：`std/database-v1:query:SELECT` 合法 | `database:query` 非法 |
`std/database-v1:query:*` 合法 | `std/database-v1:query:SEL*` 非法

---

## 4. 动作

动作是「被引用之物」。CLC-v1 定义两种具体形式：

### 4.1 Operation（授权侧）

一个具体动作请求：CapabilityId + 参数。

```
{ "id": "std/database-v1:query:SELECT",
  "params": {"tables":["customers"], "limit":{"max":50}} }
```

缺少 `id` → `deny("missing_capability_id")`。

### 4.2 ObservedAction（证据侧）

由**效果边界**依据**执行方掌控的事实**构造出的**实质动作**。CLC-v1 定义的是**接口**，
不是构造算法。

ObservedAction 携带：

- `action_type`：由依赖方钉定的类型定义所声明的动作类型名（本投影所属的类）
- `material_fields`：类型定义中声明为**实质（material）**的全部字段
- `digest`：对规范化**实质投影**（见下）计算的摘要

实质投影是确定性的，且属规范内容：

- 动作类型声明一个**实质字段集合**（必填字段与「可选但计入」的字段都列在其中）。
  **只有**该集合进入摘要。
- 规范化序列化采用 JSON 规范化方案（JCS）[RFC8785]；v1 只定义一个 suite，即 `jcs-sha256`（§4.3）。
- 投影身份属于**本语言自己**，不是 CAID：形如 `clc-action:1:<type>:<suite>:<b64url>`。
  CAID [CAID] 覆盖的是**完整** Action Object 并使用它自己的 suite 注册表，标识的是动作对象而非
  某次「发生」；本投影只覆盖声明的实质集合。二者由依赖方钉定的 Action-Mapping Profile 关联
  （§6.4），**不得**把两者的字符串当作可互换。
- 类型**未**声明为实质的字段**必须**被排除在摘要之外，且**不得**影响 Match：
  携带未声明字段的 ObservedAction 并不因此无效，但这些字段不承载任何动作身份。
- 类型声明为实质的字段**缺失**时，该 ObservedAction **不可匹配**：覆盖关系**不得**被推断、
  默认或修补（`UNSATISFIED`，§10）。这是**键闭包**（§6.2）在证据侧的镜像：
  治理字段缺失时 fail-closed，绝不 fail-open。

效果边界**必须**用自己掌控的事实构造 ObservedAction；**不得**直接照抄请求方提供的动作摘要
而不独立推导或校验对应事实。

### 4.3 身份

两个身份层级，对应两种动作形式：

| 层级 | 身份 | 范围 | 示例 |
|-------|----------|-------|---------|
| 类 | CapabilityId | 覆盖一类动作 | `std/database-v1:query:*` |
| 实例 | ActionId（投影摘要） | 标识一个动作的实质内容，**不是**某次「发生」 | `clc-action:1:payment.release.1:jcs-sha256:...` |

CapabilityId 覆盖一类；ActionId 标识一个动作的实质内容。它**不**标识某次「发生」：ActionId 绑定的是
声明的实质内容，而要与某次具体「发生」关联，还需要由消费方 profile 定义并校验的 occurrence 判别符。
CAID-02 §4.5 就把这样一个判别符作为动作对象的可选 `occurrence_id`；profile 若使用它，必须让它出现在声明的
实质字段里，才能影响摘要。分配唯一「发生」、证明一次性消费或已执行，都不在这两份文件范围内（CAID-02 §7）。
蕴涵检查**类**的覆盖，Match 检查内容的绑定。

---

## 5. Grant

一个 grant = CapabilityId + 可选参数 + 可选约束。

```
grant       = capability-id [ params ] [ constraints ]
constraint  = scheme ":" type [ ":" params ]
```

约束遵循「声明即拒绝」：显式空上界（例如零上界、空白名单）**拒绝整个类**；
省略上界则采用该 scheme 的默认值。

---

## 6. Binding

Binding 是「把身份连接到动作」的抽象概念。CLC-v1 定义两个具体实例：

### 6.1 Entailment（授权侧绑定）

当满足下列之一时，Grant G 覆盖操作 O：

1. **字面相等**：G = O（归一化后逐字节相等）。
2. **结尾通配**：G = `scheme:prefix:*`，且 O 在 `scheme:prefix:` 之后**至少有一个**段
   （按**段边界**比较，不是词法前缀）。

| Grant | Operation | 结果 |
|-------|-----------|--------|
| `std/database-v1:query:*` | `std/database-v1:query:SELECT` | 覆盖：通配匹配 |
| `std/database-v1:query:*` | `std/database-v1:query:SELECT:deep` | 覆盖：匹配多段 |
| `std/database-v1:query:*` | `std/database-v1:admin:DDL` | 不覆盖：命名空间不同 |
| `std/database-v1:query:SELECT` | `std/database-v1:query:INSERT` | 不覆盖：字面不符 |

### 6.2 参数

| 类型 | 规则 | 示例 |
|------|------|---------|
| number | op ≤ grant | 50 ≤ 100（成立） |
| string | 精确相等 | "a" = "a"（成立） |
| boolean | 精确相等 | true = true（成立） |
| array | **允许值集合（枚举）**：请求为标量时须等于某成员；请求为数组时每个元素都须等于某成员 | `{"station":[1,2,3]}` ⊇ `2`（成立）；⊇ `9`（不成立） |
| object | grant 的每个键都出现在 op 中，值递归比较 | `{"t":["id"]}` ⊆ `{"t":["id","name"]}`（成立） |
| 其他 | 精确相等 | — |

**布尔参数只有精确相等。** 布尔 grant 值只由精确相等匹配（`true` 只覆盖 `true`）。
布尔**不是**数字：实现**不得**把 `true`/`false` 解释为 `1`/`0`，**不得**让它们走数值上界规则
（op ≤ grant），它们也不参与任何数值比较或上界。（grant 侧的布尔上界在实践中罕见；
真正要紧的场景 —— 键闭包下操作侧的布尔值 —— 由 `undeclared-001` 固定。）

表中的行对应向量：number → `params-001`/`params-002`；数组成员为标量 → `params-009`（成立）/
`params-010`（不成立）；数组逐元素 → `params-011`（成立）/ `params-012`（不成立）；
对象递归允许 → `params-015`，拒绝方向 → `params-005`；分类值守卫 → `params-014`。
在旧的（v1.1 之前）「数组即上界」规则下，对象那一例读作「不成立」；按 v1.1 的枚举规则，
请求侧元素 `id` 是授权集合的成员，因此该行是「成立」（见 `clc-v1-ambiguities.md` §2）。

**数组的枚举语义（v1.1）。** 数组型 grant 参数是**允许值集合**，不是顺序。请求**可以**是
单个标量（须为集合成员），也可以是数组（每个元素都须为集合成员）。成员之间按**精确相等**比较：
授权数组中的数字表示该**确切数值**，不是上界。这正是分类标识符安全的原因 ——
`grant {"station":[3]}` **不**覆盖 `station 2`（失败 → `deny("not_in_enum")`）。
scheme 作者**应当**把分类参数（station、cell、batch、tool id）编码为数组；grant 中的标量数字
则保持「上界」语义，用于有序量（`max_rows`、`speed`、`angle`）。

显式空的 grant 数组 `[]` 拒绝整个类（`empty_bound_denies_class`）。

**无 params 的 grant**（或 **`"params":{}` 空对象**）覆盖任意操作参数（不受约束）。
`params` 缺席与 `"params":{}` **语义等价** —— 在蕴涵（§6.3）与交集（§7 规则 6、§9.1）中一致。

`null` 参数值在 v1 中非法 → 拒绝（`invalid_params_null`）。**缺席 ≠ 显式空**（见 §8）。

**键闭包（Plan A）。** 带边界的 grant 管辖它声明的键：操作携带 grant 未声明的参数键即被拒绝
→ `deny("undeclared_param")`（fail-closed，§9.1 第 7 层请求侧）。无约束 grant（无 `params`
或 `params:{}`）接受任意操作参数，因此不适用键闭包。在第 7 层内部，缺键检查
（`params_missing`）先于未声明键检查（`undeclared_param`）；两者都是键级检查，
先于枚举/上界值检查（第 8–9 层）。

**Params 表示与输入归一化（v1.1）。** 任何 §9.1 层运行之前，`params` 对象在**输入边界**归一化：

1. **规范化序列化。** params 按 JSON 规范化方案（I-JSON，RFC 8785）序列化 —— 键序、数字形式、
   空白都精确保留。评估绝不猜测；有损的重新序列化（例如会丢重复键的 map）**不**用于裁决。
2. **重复键。** params 对象含重复 JSON 键即被拒绝：`deny("invalid_params_duplicate_key")`。
3. **数字形状。** 非有限或过精度（有效十进制位 > 17，例如 `1e400`）的数值参数被拒绝：
   `deny("invalid_params_number")`。无法解析为对象的畸形 JSON 落同一原因码。位数统计作用于
   **收到的 JSON token** —— 输入边界处的原始数字字符序列，在它进入任何存储/浮点/十进制表示之前
   —— 因此 float64 与 decimal/bignum 实现**不得**出现分歧：被评判的输入始终是原始 token 文本
   （语料中的 `params-*` 数字探针；`1.0000000000000001` 这类近边界形式只是扩展探针，不改变规则）。
4. **尺寸与深度。** JCS 序列化后超过 **512 个 UTF-8 八位组**（规范化序列化以**八位组**计量
   —— 绝不用码点或 UTF-16 码元；rev CLC-1.4），或嵌套深度超过 32 的 params 被拒绝：
   `deny("invalid_params_size")`。嵌套深度**同时**计入对象与数组，最外层对象计为第 1 层
   （因此顶层对象内嵌 31 层数组 = 深度 32）。
5. **检查顺序。** 尺寸/深度（4）先于重复键（2），重复键先于数字形状（3）；第一个失败的检查胜出。
   五项全部早于 §9.1 第 1 层运行，因此各层看到的只有归一化后的 params。
6. **已解码对象路径。** 调用方若直接提供**已解码**的 params（没有 `raw_params` 文本），
   无法还原原始字节流；此时尺寸检查（4）作用于**规范化序列化**（已解码对象的 JCS 形式：
   键排序、紧凑），深度检查（4）直接作用于解码后的结构。与某份原始文本的字节级一致只对
   raw 路径有保证；但**两条入口都必须**拒绝超限 —— 超尺寸/超深度的 params 对象无论从哪条路径
   到达都要拒绝。

### 6.3 算法

```
Entails(G, O) → bool:
  1. G.namespace ≠ O.namespace → false      (namespace = scheme + action Class, §9.1 layer 3)
  2. G.id doesn't cover O.id → false        (path coverage, §9.1 layer 4)
  3. G.params absent (or `{}`) → true       (grant unconstrained — absent ≡ empty object)
  4. O.params absent → false                (bounded grant, request omits it → fail-closed)
  5. params_subset(O.params, G.params)      (both present → compare, §9.1 layers 5–9)
```

当多个检查同时失败时，报告的原因遵循 §9.1 固定的**已解析原因顺序**。本节其余规则不变。

**操作参数缺失的规则**：若 grant 带有参数上界（第 3 步不适用），而操作**完全没有 `params` 字段**
（不只是某个键缺失，而是整个字段不存在），则适用第 4 步：`Entails → false` →
`deny("params_missing")`。这同时覆盖「操作省略整个 params 对象」与「操作省略某个有上界的键」，
两者都 fail-closed。

若某能力 scheme 为某参数声明了默认值，实现**必须**在第 4 步之前把该 scheme 默认值应用到 O；
没有这样的声明默认值时，第 4 步拒绝。

**第 6 层（null）先于存在性判定。** 若 grant 的 params 携带 `null` 值（或操作的 params 携带），
失败原因是 `invalid_params_null`（§9.1 第 6 层），**即使**操作完全省略 `params` 字段也照此报告 ——
即第 6 层先于第 4 步的 `params_missing`。这是 §9.1 的固定顺序；它**遮盖**了上面算法中
「先列存在性、后列 null 检查」的字面步骤顺序。

### 6.4 Match（证据侧绑定）

当满足下列全部条件时，证据 E 绑定到确切动作 A：

1. E 携带合法 ActionId，形式为本语言的投影形式（`clc-action:1:…`，§4.3）。CAID 是另一个对象，
   只能通过钉定的 Action-Mapping Profile 与之关联。
2. E 的 ActionId 等于对 ObservedAction 重新计算的 ActionId。
3. 该 ActionId 是在**依赖方钉定的 suite 与定义来源**下计算的。

Match **只是内容关联**：它不校验原生工件，也不授权执行。它同样不标识某次「发生」：要与某次具体**发生**关联，
还需要由消费方 profile 定义并校验的 occurrence 判别符（CAID-02 §4.5），使用它的 profile
**必须**钉定判别符的来源，以及语言如何通过声明的实质字段看到它。

跨格式映射（E 的原生格式 ≠ A 的规范形式）使用 **Action-Mapping Profile**：由依赖方钉定、
以哈希标识的投影，结果为 `EQUIVALENT_UNDER_PROFILE`、`NOT_EQUIVALENT` 或 `INDETERMINATE`。

---

## 7. 交集（∩）

P_effective = P_principal ∩ C_agent ∩ P_gateway（ACA §4.2）。

规则：

1. 每个来源提供一个 grant 集合。
2. 有效 grant **必须**被**每一个**来源中的至少一个 grant 覆盖。
3. 同能力的约束合并：**最紧的上界胜出**。
4. 任一来源缺少该能力 → 该能力不在有效集合中。
5. **零来源或来源缺席一律 fail-closed。** 对**完全没有**来源的交集 —— 空来源列表，
   或所有来源都缺席 —— 没有有效集合：`deny("absent_source")`。（来源**存在**但没有该能力的
   grant 属于规则 4，不是规则 5。）
6. **空 params 不声明任何约束。** 某来源的 grant 带有「存在但为空」的 `params` 对象时，
   它不贡献任何限制。已累积的上界被保留：先有界后空 与 先空后有界**必须**得到相同结果 ——
   来源顺序**不得**改变结果（与直接授权侧 `params:{} ≡ 缺席` 一致，§6.3 第 3 步）。

**标识符比较与 params 无关（规则 2）。** 有效标识符是**被所有来源覆盖的最窄**那个，
仅由 §6.1 的标识符规则决定。**不得**通过带 params 的 `Entails` 来求解 —— 有界 grant 遇到
无 params 的同级来源会触发存在性处理（§6.3 第 4 步），从而错误地 fail-open；
**标识符单独比较，params 单独合并**（规则 3）。

**性质：组合只收窄。** 若 `Intersect` 成功，结果**必须**被每个来源覆盖，且**不得**依赖来源顺序；
否则**必须**以规范原因码拒绝，且**绝不**抛出异常。这条 meet 律正是 §6.2 参数子集代数在跨来源时
保持的东西；它由 `property-cases.json`（1184 条，§12）固定。

**本节记号**：params 为 JSON 对象（如 `{"tables":["a"]}`）；约束使用冒号三元组记法
（如 `varwof/constraint-v1:time:window:[{"start":"00:00","end":"01:00"}]`）。下面的示例表为
可读性使用紧凑写法；每行只展示相关的 params 或约束。

**声明即拒绝**：`{"tables":[]}`（显式为空）= 拒绝整个类。省略 = scheme 默认值。
`null` 值在 v1 中非法 → 拒绝（`invalid_params_null`）。规范化**不得**放宽
（按段边界比较，不是词法前缀）。

| 来源 A | 来源 B | 结果 |
|----------|----------|--------|
| `{"tables":["a","b"]}` | `{"tables":["a"]}` | `{"tables":["a"]}`（成立） |
| `{"tables":["a"]}` | `{"tables":[]}` | 拒绝 |
| （无约束） | （无 grant） | 拒绝 |
| `{"limit":100}` | `{"limit":50}` | `{"limit":50}`（成立） |
| （无约束） | 约束 `time:window:[{"start":"00:00","end":"01:00"}]` | 已识别但 core 不求值（→ `allow_unresolved` + `unresolved`） |
| `{"tables":["a"]}` | `{"tables":["b"]}` | 拒绝 |

**对象值求交要求键集合完全相同。** 两个对象值只有在**键集合相同**时才逐键求交；
键集合不同的对象值 → `no_overlap` 拒绝。合并「共享键」会丢掉另一来源所约束的键，
结果就不再被那个来源覆盖（P11 组合只收窄）：`{"a":1}` ∩ `{"b":1}` → 拒绝（`no_overlap`）；
`{"a":1}` ∩ `{"a":2}` → 拒绝；`{"a":1}` ∩ `{"a":1}` → `{"a":1}`。

---

## 8. 约束

约束在授权侧与证据侧共享。

### 8.1 授权侧约束

限制某能力可以怎样被使用。约束使用冒号三元组记法 `scheme:type[:params]`，
其中 **`type` 是第二个以 `:` 分隔的段**（`scheme` `:` `type` [ `:` params... ]）：

- `varwof/constraint-v1:max_rows:100` —— 类型 `max_rows`，参数 `100`
- `varwof/constraint-v1:time:window:[{"start":"00:00","end":"01:00"}]`
  —— 类型 `time`，参数 `window:` 加 UTC 窗口段数组（单个窗口 = 单元素数组）。
  标量形式（`time:window:3600`，即滑动时长/新鲜度概念）在 v1 中**不是**合法的
  `time:window` 值 → `invalid_constraint`。
- `varwof/constraint-v1:network:cidr:["10.0.0.0/8"]` —— 类型 `network`，参数
  `cidr:` 加 JSON 数组（≤ 32 个元素，每个是合法的 IPv4/IPv6 CIDR 字符串）

v1 core 按 **`(scheme, type)` 二元组**识别约束，而不是只看类型名：约束的身份是**两件事**
—— 声明的 scheme 与类型。core 恰好识别以下组合：

```
varwof/constraint-v1 : max_rows
varwof/constraint-v1 : time
varwof/constraint-v1 : network
```

其他任何 `(scheme, type)` —— 包括 `foo/database-v1:max_rows` —— 都**不**被 core 识别：
一律以 `unknown_constraint` 拒绝（fail-closed），绝不交给 core 求值器。这消灭了跨 scheme
语义污染：类型名本身永不选择求值器，因此自行定义 `max_rows` 的 scheme 不会被 Core 的
`max_rows` 求值器劫持语义（§P7 只定义一次、处处消费 —— 以声明 scheme 为界）。
scheme 自定义的约束类型属于 v2 / profile 层（由声明 scheme 求值）；core 不识别它们即
fail-closed（`unknown_constraint`）。

被识别的约束**还**必须符合该类型的**值文法**（见下表）；值不合文法的已识别类型以
`invalid_constraint` 拒绝 —— 绝不静默跳过，也绝不放行。交集本身既不求值也不校验证束值
（它只合并约束字符串；§8.1 值文法在裁决边界 §9 与下述约束合并规则中执行）。

core **只为 `max_rows` 定义求值器**；`time`/`network` 上界的求值由声明该能力的 scheme 负责
（scheme 求值，core 只拥有 §8.1 值文法「是什么」，不拥有「此刻的某时刻/某地址是否命中它」；§11）。
被识别但未被求值的约束携带在决定的**可叠加** `unresolved` 字段上 —— 绝不静默丢弃（§8.4）。
未被识别的 `(scheme,type)` → `deny("unknown_constraint")`（fail-closed）。

| 类型 | 值文法（v1） | core 行为 |
|------|--------------------|---------------|
| `max_rows` | 严格非负整数（JSON 数字文法：无前导 `+`、无 `0x`、无尾随字符） | 对操作参数求值；**操作侧值域**是有限非负整数 —— 参数缺席、字符串、布尔、负数、分数、非有限数，或超过上界的值 → `max_rows:violated`（无法证明合规即 fail-closed；rev CLC-1.4）；约束值不合文法 → `invalid_constraint` |
| `time`（`window`） | 非空 JSON 数组（≤ 32 个元素），元素为 `{"start":"HH:MM[:SS]","end":"HH:MM[:SS]"}`，UTC、每日重复，单窗口 = 单元素数组；**单段必须在同一日内 `start < end`（按时间词法序）**，单段**不得跨午夜**；跨午夜窗口必须拆成两段（`22:00→00:00` + `00:00→06:00`），其中 `end:"00:00"` 保留表示**次日零点**（即段末 24:00，且要求 `start != end`）；段列按 (start,end) 升序、**段间互不重叠** | 仅识别 → `allow_unresolved` + `unresolved`（§8.4） |
| `network`（`cidr`） | 合法的 IPv4/IPv6 CIDR 字符串（`addr/mask`），仅作语法级检查；JSON 数组 ≤ 32 个元素 | 仅识别 → `allow_unresolved` + `unresolved`（§8.4） |

可表达的窗口集合不含空窗口与全天窗口；需要这类窗口的声明 scheme 扩展文法即可（§11）。

v1 的合并规则：数值 → 取最小；白名单 → 求交；未知 → 拒绝。白名单即 §6.2 的数组枚举集合；
求交即取共享成员。v1 core **不定义任何黑名单约束** —— 合并只适用于 core 自己求值的
`varwof/constraint-v1` 类型；它不定义也不合并 scheme 自定义类型（§11）。
约束集合的合并**始终归一化且确定性排序**（重复字符串折叠、结果有序）—— 相同输入在任何实现中
得到相同的约束序列。v1 在交集处**不**收紧 `time`/`network` 上界：交集只保留它遇到的约束字符串
（不求值、不收窄，§8.4）。

### 8.2 证据侧约束

要求特定的证据属性：新鲜度、一次性消费、法定人数、发起人排除等。

它们在结构上与授权侧约束完全相同 —— 一个 `type` 加可选 `params` —— 但求值对象是**证据工件**
而不是操作参数。

### 8.3 统一的约束文法

```
constraint = scheme ":" type [ ":" params ]
```

两侧使用同一套文法。由校验器（授权侧）或证据求值器（证据侧）解释类型专属的 params。

### 8.4 已识别但未求值（残差义务通道）

对于某个**已被识别、其值符合 §8.1 值文法、但 v1 core 未定义求值器**的约束
—— v1 中是 `time` 与 `network`，其求值属于声明 scheme（§11）—— **不得**静默丢弃：
它必须出现在决定的**可叠加** `unresolved` 列表中（§9），且裁决必须是
**`allow_unresolved`**（不是 `allow`）：

```
Decision = { verdict: "allow"|"deny"|"allow_unresolved",
             reason, unresolved: string[] }
```

**Fail-closed 边界**：`allow_unresolved` 是一个**独立的枚举值**，永不等于 `allow`。
消费方（PEP / profile / 声明 scheme）在放行前**必须**对每一条 `unresolved` 约束求值或确认；
**无法执行或无法确认时必须拒绝**（AAC §6.6：「无法履行或无法确认时应按拒绝处理」）。
只写 `if decision.verdict == "allow"` 的消费方，在字面枚举上就不可能把一条残余义务当作
「已满足的 allow」放行 —— 任何让义务悬而未决的路径都必须显式处理 `allow_unresolved` 才能通过。
**「调用方本应检查 unresolved」不构成充分防护**：裁决本身必须拒绝二值短路。

`unresolved` 的语义与顺序：`deny` 与已完全求值的 `allow` 为 `[]`；`allow_unresolved` 为
归一化 + 排序后的约束串（重复折叠、结果有序）—— 顺序确定：相同输入在任何实现中得到相同序列。

**组合义务（消费方一侧）**：同一 `(scheme,type)` 的多条 `unresolved` 约束构成**合取（AND）**
—— 满足 A 且满足 B 才算全部满足；OR、任取一条、首条胜出、忽略部分条目，**全部禁止**。
不同 `(scheme,type)` 的约束互不干涉，各自在声明 scheme 下求值（P11 组合只收窄：合取只收窄）。

core 只拥有**值文法**（「它是什么」）；「这个窗口/CIDR 此刻是否构成边界」（「怎么求值」）
属于声明 scheme（§11）—— 但**边界时刻语义是文法的一部分**（§8.1：半开区间 `[start, end)`、
单段同日内、跨午夜拆段），scheme **不得**改变该解释，只能在其上求值。

---

## 9. 裁决函数（授权侧）

```
Authorize(grants, operation) → Decision
Decision = { verdict: "allow"|"deny"|"allow_unresolved",
             reason: string|null,
             unresolved: string[] }   // additive, §8.4
```

算法。有一条优先级贯穿整个函数：**grant 侧预检先于操作校验。** grant 集缺失或为空时，
即使操作也缺失，也以 `capability_not_authorized` 拒绝（§9.1 第 10 层；附录 D15 钉住这一点），
因此两个输入都缺席的调用方拿到的是该原因码，而不是 `missing_capability_id`。

1. 校验操作：`id` 缺失/非法 → 以稳定原因码拒绝。报告操作**第 1 层的具体原因码** ——
   `missing_capability_id`（无 id）、`unsupported_wildcard`（v1 禁止的通配形状）或
   `invalid_capability_id`（其他文法违规）—— **不**折叠为通用码。
2. 通过蕴涵（§6.1）寻找覆盖型 grant。`grants` 为空/零值 → 直接
   `deny("capability_not_authorized")`（§9.1 第 10 层）。
3. 对每个覆盖型 grant：求值约束（§8.1）：未被识别的 `(scheme,type)` → `unknown_constraint`；
   已识别但值不合文法 → `invalid_constraint`；已识别且有 core 求值器
   （`varwof/constraint-v1:max_rows`）且被违反 → `{type}:violated`；已识别但无 core 求值器
   （`time`、`network`）→ 残差义务（§8.4）。
4. **聚合**（多 grant 集合，§9.1）：
   - 任一覆盖型 grant「放行」（参数层与约束层都无拒绝）→ 整体放行；
   - 残差义务 = **所有覆盖且放行的 grant** 的 `unresolved` **并集**（归一化 + 排序；
     任何覆盖型 grant 的义务都不得丢弃）；
   - 当没有任何覆盖型 grant 放行时：若至少一个覆盖型 grant 在参数/约束层拒绝 → 采用
     **规范化顺序下首个覆盖型 grant** 的拒绝原因（确定性，§9.1）；若完全没有 grant 覆盖 →
     `capability_not_authorized`。
5. 放行且残差义务非空 → `verdict = allow_unresolved`；放行且义务为空 → `verdict = allow`。

grant 集合**可以缺席或为空** —— 例如集成方用空能力记录调用 `Authorize`。
安全的求值器**不得**抛出异常；它**必须**把这类输入解析为 `deny("capability_not_authorized")`
（由第 10 层/第 2 步自然得出）。操作缺席解析为 `deny("missing_capability_id")`（第 1 层）；
求值器在那里同样**不得**抛出。

性质：确定性（相同输入 → 相同输出）、fail-closed、原因码稳定。

### 9.1 已解析原因顺序（规范性）

当一个 grant/操作组合有多个条件失败时，**已解析原因**（被报告的那一个码）是下表中
**第一个适用层**的码。它适用于 `Entails`（§6.3）、`Intersect`（§7）与 `Authorize`（本节）。

| # | 层 | 检查 | 原因码 |
|---|-------|--------|----------------|
| 1 | CapabilityId 合法性 | §3 文法、通配形状 | `invalid_capability_id`、`missing_capability_id`、`unsupported_wildcard` |
| 2 | params 归一化 | 重复 JSON 键；非有限/过精度数字；尺寸/深度上限（§6.2） | `invalid_params_duplicate_key`、`invalid_params_number`、`invalid_params_size` |
| 3 | 命名空间 = scheme + 动作 Class | grant 与操作的 scheme 与 Class | `different_namespace` |
| 4 | 路径覆盖（同命名空间内） | 字面路径段、结尾通配的深度 | `literal_mismatch`、`wildcard_requires_trailing_segment` |
| 5 | 显式空上界 | 任一 grant/交集来源声明了值为 `[]`/`{}` 的**参数值**（「存在但为空的 `params` 对象」**不是**约束，§7 规则 6） | `empty_bound_denies_class` |

| 6 | null 值 | 任何 `null` 参数值 | `invalid_params_null` |
| 7 | 参数存在性 | grant 约束了操作省略的参数（或操作没有 `params`）；操作携带 grant 未声明的键 | `params_missing`、`undeclared_param` |
| 8 | 枚举成员 | 请求值不是已授权数组集合的成员（§6.2） | `not_in_enum` |
| 9 | 上界比较 | 数值/上界被超出 | `params_exceed_grant` |
| 10 | 覆盖为空 | 交集结果为空；零来源；没有 grant 覆盖该操作 | `no_overlap`、`absent_source`、`capability_not_authorized` |
| 11 | 约束求值 | 未识别的 `(scheme,type)`；已识别类型值不合 §8.1 文法；已识别类型被违反 | `unknown_constraint`、`invalid_constraint`、`{type}:violated` |

说明：

- **命名空间**是 `scheme:action_class`（前两个以 `:` 分隔的段）。同一命名空间内的标识符只在
  Class 之下有差异；这类不匹配属于路径级（`literal_mismatch` /
  `wildcard_requires_trailing_segment`），不是 `different_namespace`。
- **params 归一化在输入边界触发**：重复键、过精度/非有限数字、尺寸/深度越界（§6.2）
  在任何 grant 与操作的比较之前检出，因此先于本表其他所有层。
- **声明即拒绝**：第 5 层在 grant/交集一侧求值 —— 值为显式空的 `[]` 或 `{}` 直接拒绝整个类，
  与请求无关，且先于任何成员或上界检查。
- **`params:{}` ≡ 缺席**：参数约束只看**声明的参数名集合**，与承载形式无关 ——
  `params` 缺席与 `"params":{}` 都表示「未声明任何参数名」= **无参数约束**
  （蕴涵与交集语义一致；同一表示不得在不同函数中语义不同）。因此：
  - 直接授权：`params:{}` 的 grant **放行**携带任意 params 的操作
    （`{x:1}` 不触发 `undeclared_param`）；
  - 交集：`params:{}` 来源**不贡献任何参数约束**（`{limit:50}` ∩ `{}` = `{limit:50}`）；
  - 键闭包（下一条）仅当 grant 声明了**非空**参数名集合时成立。
- **第 7 层键闭包双向运行**：被授权的键必须在操作中出现（`params_missing`），
  操作的键必须被 grant 声明（`undeclared_param`）；缺键检查先解析，且两者都先于第 8–9 层的值检查。
  （仅适用于非空声明名集，见上一条。）
- **第 11 层按构造最后运行**：只有在覆盖与参数都通过之后才求值约束。
- **多 grant 聚合（规范性）**：`Authorize` 作用于**有序的 grant 列表**，不是单条 grant。
  授权语义与顺序无关；只有原因选择（规则 4）使用输入顺序。规则：
  1. **任一「覆盖且放行」的 grant 即放行**（∃ `g`：Entails(g,op) ∧ 参数层无拒绝 ∧ 约束层无拒绝）；
  2. 残差义务 = **所有覆盖且放行的 grant** 的 `unresolved` **并集**（归一化 + 排序）；
     任何覆盖型 grant 的义务都不得丢弃；
  3. 没有 grant 覆盖 → `capability_not_authorized`；操作第 1 层错误始终先于任何覆盖/聚合判定；
  4. 有 grant 覆盖但全部覆盖型 grant 都在参数/约束层拒绝 → 拒绝，
     reason = **规范化顺序下首个覆盖型 grant** 的第 5–11 层拒绝原因（确定性）。
  **规范化顺序** = 输入 grant 列表中的出现顺序（能力记录体顺序）；实现**不得**按内部哈希/迭代顺序
  选择原因。被固定的反例（禁止）：不得「任一放行即放行」以外的别的规则 —— 否则持有多条 grant 时，
  窄 grant 会错误地否决宽 grant 的合法操作；不得「首个匹配胜出」—— 否则 grant 顺序会改变授权结果；
  不得「全部必须通过」—— 那与「任一覆盖即授权」同义，会让窄 grant 的存在使宽 grant 失效。
- **操作 id 校验错误传播其具体的第 1 层原因码**（`missing_capability_id` /
  `unsupported_wildcard` / `invalid_capability_id`），**绝不**变成 `capability_not_authorized`，
  也绝不编造笼统码：第 1 步报告的正是描述该操作 id 的那个码。只有**覆盖**失败
  （第 3–4 层与第 10 层）才折叠为 `capability_not_authorized`。
- **第 1 层只校验操作 id。** **grant** 中畸形的 id 会使该 grant 对任何操作都不匹配：
  `Entails` 把具体第 1 层原因码作为其 false 的原因，`Authorize` 把该不匹配折叠进覆盖
  （`capability_not_authorized`）—— grant 自身的原因码不会由决定暴露出来。
- **有效 grant 缺席/为空**直接落到第 10 层（`capability_not_authorized`）；求值器**必须**返回该决定
  而不是抛出。操作缺席落到第 1 层（`missing_capability_id`）。
- **语言修订不匹配**（§12.1）在任何层之前解析，并报告 `unsupported_language_revision`
  （fail-closed，不降级）。

---

### 9.2 原因码（规范性）

原因码是稳定标识符。v1 定义如下：

**规范码 = 第一个 `:` 之前的全部内容**。实现**可以**追加 `: <detail>`（例如违规参数名）
作为诊断后缀；规范码不变。所有工具与兼容性检查**必须**只比较规范前缀。

| 原因码 | 含义 |
|-------------|---------|
| `unsupported_wildcard` | v1 禁止的通配形状（裸 `*`、部分段、`**`、`{a,b}`、`[a-z]`） |
| `invalid_capability_id` | CapabilityId 不符合 §3 文法 |
| `missing_capability_id` | 操作没有 `id`（第 1 层） |
| `invalid_params_duplicate_key` | params 含重复 JSON 键（§6.2 表示、§9.1 第 2 层） |
| `invalid_params_number` | 数值参数非有限或过精度（> 17 位有效十进制数字）（§6.2 表示、§9.1 第 2 层） |
| `invalid_params_size` | params 超过 512 字节序列化尺寸或深度 32 的嵌套上限（§6.2 表示、§9.1 第 2 层） |
| `different_namespace` | grant 与操作的命名空间不同（scheme + 动作 Class，§9.1 第 3 层） |
| `literal_mismatch` | 字面标识符不同 |
| `wildcard_requires_trailing_segment` | 通配没有剩余段（`...:*` 不覆盖 `...`） |
| `capability_not_authorized` | 有效集合中没有任何 grant 覆盖该操作 |
| `no_overlap` | 多来源交集为空 |
| `absent_source` | 对零来源求交 —— 没有有效集合（§7 规则 5） |
| `params_exceed_grant` | 请求参数超出已授权上界 |
| `params_missing` | grant 约束了某参数但请求省略它，或请求完全没有 `params` 字段（fail-closed，§6.3 第 4 步） |
| `undeclared_param` | 操作参数键未被 grant 的 params 声明（键闭包，§6.2；§9.1 第 7 层请求侧） |
| `empty_bound_denies_class` | 参数值处显式空上界（`[]`/`{}`）拒绝整个类。`params:{}` 不是空上界：它等价于 `params` 缺席（§7 规则 6） |
| `not_in_enum` | 请求值不是以数组形式授权的允许集合的成员（§6.2 枚举规则） |
| `invalid_params_null` | `null` 参数值（v1 拒绝） |
| `unsupported_language_revision` | 声明的 CLC 修订与实现不兼容（§12.1；fail-closed，不静默降级） |
| `unknown_constraint` | 未知约束类型（fail-closed） |
| `invalid_constraint` | 已识别类型的值不符合其 §8.1 值文法 |
| `{type}:violated` | 已知约束被违反（例如 `max_rows:violated`） |

其他 scheme **可以**定义附加原因码，但**不得**重定义上述码。

---

## 10. 满足函数（证据侧）

```
Satisfy(evidence_set, requirement) → Satisfaction
Satisfaction = { verdict: "SATISFIED"|"UNSATISFIED", reason: string|null }
```

算法：

1. 按各自的**原生规则**校验每个证据工件。
2. 对每个必需的证据**角色**，检查是否有工件填入该角色。
3. 检查每个工件是否通过 Match（§6.4）绑定到确切动作。
4. 求值新鲜度、一次性消费与角色约束。证据侧值文法由本修订定义：
   `varwof/evidence-v1:freshness:sec:<n>`、`:consumption:once`、`:quorum:distinct:<n>`、
   `:exclusion:initiator|executor`（§8.2）。**其求值属于执行点**的已识别约束（consumption）
   产出**未决义务**，绝不产出 `SATISFIED`。
5. 所有必需角色都已填入并绑定 → `SATISFIED`。
6. 任一角色未填入、未绑定或被违反 → `UNSATISFIED`。

**逐约束三值、顶层报告二值。** 已识别的证据侧约束按三值求值（`satisfied` / `violated` /
`unknown`），而 `Satisfaction` 本身是二值的：顶层为 `unknown` 的约束 —— 包括其求值属于执行点
（`consumption`）的那类 —— **必须**产出 `UNSATISFIED` 并带稳定原因，绝不出 `SATISFIED`。
`unknown` 是内部求值结果，不是第三种顶层裁决。

性质：确定性、fail-closed、原因码稳定。

---

## 11. 语义边界

CLC-v1 为授权侧与证据侧定义**共享的最小词汇表**与**求值算法**。

CLC-v1 **不**定义：

- **信任模型**：谁签什么、签发者信任、委托链（属于 AIC-JWT [AIC-JWT]、OAuth、SPIFFE 等）
- **原生验证**：签名校验、schema 校验、新鲜度执行（属于各原生工件的规范）
- **执行生命周期**：消费、调用、对账、结果分类（属于 EMILIA AEB [EMILIA-AEB] 或等价物）
- **回执或令牌格式**：承载 grant、证据或绑定的线上格式（属于各协议专属规范）

边界是：

- CLC-v1 定义**评估什么**（grant ⊆ operation、evidence ↔ action）
- 消费方定义**如何评估**（原生验证、信任锚）
- CLC-v1 定义**输出的含义**（allow/deny/allow_unresolved、SATISFIED/UNSATISFIED）——
  **`allow` 与 `allow_unresolved` 是不同的枚举值**；消费方**不得**把 `allow_unresolved`
  当作 `allow`（§8.4）
- 消费方定义**拿输出做什么**（调用、记录、对账）
- CLC-v1 定义每个已知类型的**值文法**（什么算合法的约束值）；声明 scheme 定义该值**如何**被求值
  （这个窗口/CIDR 此刻是否构成边界）
- **`allow_unresolved` 是授权结果，不是证据。** 它标记的是一个**未决的授权（或策略）条件**：
  消费方若能在钉定规则下求值该义务，可以释放；不能则**必须**拒绝。只有当依赖方另行定义了证据
  角色与对应的原生验证方（AEB）时，它才取得证据角色；语言本身不作此主张，`unresolved` **不得**
  读作"证据仍不足"
- CLC-A 保持**范围语言**的位置：素材动作身份引用 CAID、证据满足引用 AEC、边界生命周期引用 AEB；
  它们之间的**窄 crosswalk** 即组合点

---

## 12. 一致性

CLC-v1 定义**两个一致性类**：

**CLC-A（授权侧）** —— v1 基线。符合实现**必须**实现：文法（§3）、蕴涵（§6.1）、交集（§7）、
裁决函数（§9）、对未被识别 `(scheme,type)` 约束的拒绝（`unknown_constraint`，§8.1）、
对已识别类型值不合文法的拒绝（`invalid_constraint`，§8.1）、把已识别但未求值的约束通过决定的
`unresolved` 字段以**独立的 `allow_unresolved` 裁决**暴露（绝不静默丢弃，§8.4）、
多 grant 聚合（§9.1）以及稳定原因码（§9.2）。

**委托收窄不属于本修订。** 委托策略可能要求「agent 请求的约束集合落在主体边界之内」，并要求
委托记录携带有效子集。该义务属于委托/授权绑定 profile，而不属于语言本身：本修订既不为它定义
一致性类，也不为它定义原因码，实现**不得**自行推断一个。未来的修订可以在所需 profile 确定之后，
把它作为**一条可复用的包含关系 + 共享语料**加入 —— 与蕴涵、交集并列。在该关系存在之前，委托
不进 CLC-A：本文档与 crosswalk 语料里的委托示例只证明**声明授权集合的交集**，并不证明子授权
留在父授权的边界之内。某个操作落在 grant 之内，不足以证明子授权不越出父授权；无法确立包含
关系时，绑定 profile **不得**授权该委托。

**CLC-E（证据侧）** —— 可选的一致性 profile，本修订**已实现并由语料钉住，但不声称**。§6.4（Match）与
§10（满足）定义证据侧关系；本修订还定义了证据侧约束值文法（`varwof/evidence-v1:freshness:sec:<n>`、
`:consumption:once`、`:quorum:distinct:<n>`、`:exclusion:initiator|executor`），并随修订提供参考实现与语料。

**不声称是原则要求，不是材料不足**：一致即门槛，而门槛是**两个独立实现**（原则文件 §12 的 P12；
本文件 §12「实现的独立性」）—— 同一作者的多实现之间的一致**不算**。第二个前提是归属：证据侧语义
正与 EMILIA 联合评审，评审之前不作声称。

将来声称 CLC-E 的修订会承担下列义务；今天若声称，实现**必须**：

只实现 CLC-A 的实现**不得**声称 CLC-E。CLC-E **不**新增线上格式：需要格式的承载方
（例如 Action Evidence Envelope）自行基于 §6.4/§10 做 profile。

**一致性语料。** CLC-A 一致性由随仓发布在 `capability/data/_vectors/clc-v1/` 的两套机器可读
参考套件检验：`vectors.json` —— **105 条**向量，映射见附录 B —— 与 `property-cases.json`
—— **1184 条**用例，固定 §7 的 meet 律、标识符收窄与来源顺序无关性。其语法由
`vectors.schema.json` 定义；`offline-vectors.json` 是带时间戳的快照镜像。符合实现**必须**通过
两套套件。

CLC-E 一致性由同目录下的 `evidence-vectors.json` 检验 —— **32 条**向量，覆盖四种证据侧约束类型、
其值文法拒绝、需求表达式绑定、闭需求对象、ActionId 计算（§4.2：声明的实质投影、未声明字段被排除、
实质字段缺失即不可匹配、带 suite 标签的标识符）以及 Match 判决（§6.4：
`MATCH` / `NOT_EQUIVALENT` / `INDETERMINATE`）。其运行器随参考实现（`register`）发布，
语法与 `vectors.json` 保持一致。

实现**不得**：重定义语义、接受 v1 禁止的通配、或在规范化期间放宽上界。

**实现的独立性（诚实的范围）。** 本仓 README 所列的三个实现（Go、Python、TypeScript）
**不构成独立证据**：它们同出一位作者，其一致性是对规范的回归测试，而非第三方验证。
我们欢迎独立实现；在其出现之前，本文档中的一致性主张限于「同一作者、三种语言、一份语料」。
评审者**应当**把单一作者的一致性主张视为「文本**可实现**」的证据，而不是「已被独立**解释**」的证据。

**实验性邻居不是 CLC。** `varwof/aic-jwt` 中的 WIT/WPT 互操作研究（`wit-wpt-interop/`）
是一个**实验性**研究产物，它实现了一套**不同且更宽**的通配面（`**`、`{a,b}`、`[a-z]`），
而本修订将其作为 `unsupported_wildcard` 拒绝（§9.2）。它不是 CLC-A 实现，
**不得**被引用为 CLC-A 实现；它的存在是为了研究 WIT/WPT 供给，自带 EXPERIMENTAL 标识。

### 12.1 语言修订

每个实现声明一个语言修订 `CLC-<major>.<minor>` —— 本文档声明 **`CLC-1.6`**。
能力输入（grant、操作或 OCM）**应当**携带其撰写时所依据的修订；未声明修订的输入按 `CLC-1.0` 处理。

- **兼容读取**：实现**可以**求值「声明主版本等于自身 且 声明次版本 ≤ 自身」的输入
  （因此 CLC-1.3 的实现读取 CLC-1.0/1.1/1.2/1.3 输入可以，但不读 CLC-1.4 或 CLC-2.0）。
- **CLC-1.2 是增量的**：它给 Decision 形状增加 `unresolved` 字段、增加 `invalid_constraint`
  原因码，且不改变既有输入上的 v1 裁决；CLC-1.1 实现**可以**对本文档声称 CLC-1.1，
  但在它暴露 `unresolved` 并拒绝已识别类型的不合规值之前，不是 CLC-A 符合
  （§12）。
- **CLC-1.3 是增量的，并重设了一个裁决值的范围**：它增加 `allow_unresolved` 裁决值，
  闭合残差义务的裁决回路，并把 `allow` 重新限定为仅表示「完全执行」；
  **没有**残差义务的输入上，`allow`/`deny` 输出不变。CLC-1.2 实现**可以**对本文档声称
  CLC-1.2，但在它产出 `allow_unresolved` 值、并应用 §8.1 的 `(scheme,type)` 身份与
  跨午夜窗口文法之前，不是 CLC-A 符合（§12）。
- **不兼容读取必须 fail closed**，以 `deny("unsupported_language_revision")` 拒绝。
  实现**不得**在不同修订下静默求值 —— 不降级、不「先告警后放行」。
- 修订检查在**任何 §9.1 层之前**解析，并产出单一已解析原因码 `unsupported_language_revision`。

向量：`revision-001`（输入 CLC-1.0，对声明 CLC-1.3 的实现 → 正常求值，allow）；
`revision-002`（输入 CLC-2.0 → 拒绝 `unsupported_language_revision`）。

---

## 附录 A：消费映射

下表是这套共享词汇表的**消费方示例**，不是必需的 profile：CLC-A 一致性不依赖其中任何一项。

| 消费方 | 文法 | 绑定 | 裁决 | 说明 |
|----------|---------|---------|---------|-------|
| AIC-JWT DA | capability[].id | Entailment（§6.1） | Decision（§9） | AIC-JWT §5 绑定 |
| EMILIA AEB | AEG capability_class | Match（§6.4）+ Entailment（§6.1） | SATISFIED（§10）+ Decision（§9） | AEB §3 判定层级（VERIFIED/MATCH/SATISFIED）+ §5.1 ObservedAction + §7 AEC 槽位；一个已 VERIFIED 的授权工件承载 Grant |
| RAR authorization_details | type="capability" | Entailment（§6.1） | Decision（§9） | RFC 9396 格式 |
| 委托链 | 每一跳声明的集合 | Intersection（§7） | Decision（§9） | 只做声明集合的交集；包含关系不在本修订范围（§12） |

---

## 附录 B：参考向量

> **本附录只给分组与说明；逐条向量表见英文正本 Appendix B 与机器可读的
> `data/_vectors/clc-v1/vectors.json`。** 为避免两份数据漂移，中文版不重复这些表。

**分组与 `kind` 的映射**：本附录按语义类别分组（B.1–B.6）。机器可读的 `vectors.json`
用 `kind` 字段把这些组**重新归并**：
`kind=entail (37)` 覆盖 B.2（6）+ B.3（27）再加 4 条 scheme 压力测试向量
（`clinical-001/-002`、`payments-001`、`data-002`）；`kind=decide (38)` 覆盖 B.5
（29：25 条 `decide-*`、2 条 `revision-*`、2 条 `undeclared-*` 第 7 层向量，包含 9 条
残差/值文法裁决向量、重新固定的 `decide-019/-020/-024` 以及新增的 `decide-028/-029/-030`）
再加 7 条组合裁决向量、`payments-002` 与 `data-001`；
`kind=intersect (14)` 覆盖 B.4（10）再加 4 条调用交集函数的组合向量
（`combined-004/-005/-008/-011`）。

| 分组 | 内容 | 条数 |
|---|---|---|
| B.1 语法 | 标识符合法性（字面、结尾通配、被禁止的通配形状、scheme 文法反例） | 9 |
| B.2 蕴涵 | 字面匹配、结尾通配、跨命名空间、缺段、字面不符 | 6 |
| B.3 参数 | 数值上界、枚举成员、数组逐元素、对象递归、键闭包、表示与归一化 | 27 |
| B.4 交集 | 多来源收窄、空上界、来源顺序无关、参数无关的标识符比较 | 10 |
| B.5 裁决 | 完整裁决路径、原因顺序、残差义务、修订兼容 | 29 |
| B.6 组合 | 交集 + 裁决的组合场景 | 11 |

---

## 安全考量

- **Fail-closed**：未定义/畸形/未知 → 拒绝。
- **声明即拒绝**：空上界拒绝整个类。
- **规范化不得放宽**：按段边界比较，不是词法前缀。
- **组合只做收窄**：交集只会移除权限。而**被委托的** grant 是否留在父授权边界内，是一个
  本修订未在任何地方回答的包含性问题（§12）。
- **原因码稳定**：相同输入在任何实现中得到相同原因。
- **证据绑定与原生验证分离**：Match 检查内容关联；原生验证是消费方的责任。
- **解析分歧不得改变裁决**：params 在输入边界按 §6.2 归一化（JCS 序列化、重复键、
  非有限/过精度数字、尺寸/深度上限）。把输入解码成可重排的 map 再重新编码的消费方会丢掉重复键、
  也无法表示非有限数；两个这样的消费方会在同一份原始输入上得出不同裁决。裁决基于**边界校验后的形式**，
  而不是有损的重新序列化。
- **「已识别但未求值」不是静默接受**：core 识别但无法求值的约束**必须**出现在决定的 `unresolved`
  字段中 —— 绝不丢弃（§8.4）。消费方在行动前必须对每条此类约束求值或确认，否则**必须**拒绝（AAC §6.6）。
- **原因码的细节后缀仅供诊断**：第一个 `:` 之后的内容（例如违规参数名）**不得**改变裁决，
  **不得**被作为裁决依据。消费方按 `:` 之前的码前缀匹配（§9.2）。
- **修订不匹配 fail-closed**：不兼容的语言修订（§12.1）产出
  `deny("unsupported_language_revision")`，在任何层之前解析 —— 绝不静默降级或尽力重解释。
- **资源耗竭在输入边界被限定**：512 字节序列化尺寸上限与深度 32 嵌套上限（§6.2 第 4 步）
  同样适用于 `raw_params` 及其他一切输入，使递归求值器不会因深嵌套与超大 params 而爆掉。

---

## IANA 考量

本文档不请求任何 IANA 动作。

约束类型（`max_rows`、`time`、`network`）与原因码由本文档定义为**固定集合**。若本工作被某工作组采纳，
该组可考虑是否为其中之一建立注册表；本修订不提议注册表。

## 隐私考量

语言本身不承载也不存储任何东西。隐私暴露来自承载方放进去的内容与求值方报告出来的内容：

- 能力标识符与参数值描述策略。它们可能泄露组织结构、服务拓扑、网段（`network` 约束）、
  工作时段（`time` 窗口）、租户名或用途。部署方应把 grant 视为策略机密材料。
- 不同的原因码会泄露 grant 的形状：`params_missing`、`undeclared_param` 与 `not_in_enum`
  之间的差别会告诉观察者该 grant 约束了什么。在请求方不可信的地方，消费方应考虑在边界处折叠原因码 ——
  正如本规范已对标识符级失败所做的那样（§9.1）。
- 若某 scheme 如此定义，参数值可能携带个人数据。scheme 作者应避免把个人标识符用作参数名或参数值。
- 残差义务（`unresolved`，§8.4）以及任何基于决定构建的审计记录会持久化策略与使用信息；
  留存是承载方的责任（§11）。
- 随本文档发布的参考语料是合成的，不含个人数据。

## 致谢

Iman Schrock（EMILIA Protocol）对照 1.1 版语料审阅了交集与约束语义，并提供了
1.2 与 1.3 修订所修复的对抗性用例：交集里的嵌套部分重叠、`max_rows` 的约束值处理，
以及公开入口点的契约。1.4 修订时他重跑了 Go、Python、TypeScript 三个实现与 1184 条性质用例，
闭环了就 `max_rows` 值域与 UTF-8 尺寸上界提出的两个反对意见；1.5 修订时他重跑的是**三套 Go 套件**
—— 105 条授权、30 条证据、13 条 crosswalk —— 并给出该修订承载的四处更正：三值求值到二值报告的
折叠（§10）、`allow_unresolved` 与证据的分离（§11）、委托的范围（§12），以及本投影身份与 CAID
的边界（§4.2、§4.3、§6.4）。

## 参考文献

### 规范性引用

- [RFC8785] "JSON Canonicalization Scheme (JCS)", RFC 8785,
  DOI 10.17487/RFC8785, June 2020,
  <https://www.rfc-editor.org/info/rfc8785>.

### 参考性引用

- [ACA] Agent Capability Authorization and Delegation Binding,
  draft-wei-agent-capability-authorization-00, Work in Progress.
- [AIC-JWT] J. Wei, "AI Agent Identity Certificate (AIC) JSON Web Token
  Profile", draft-wei-aic-jwt-01, Work in Progress, September 2026.
- [CAID] "Canonical Action Identifier",
  draft-schrock-canonical-action-identifier-02, Work in Progress.  §4.5 定义可选的
  `occurrence_id`；§7 把「发生的分配」与「一次性消费」留在标识符之外。
- [EMILIA-AEB] "Action Evidence Boundary",
  draft-schrock-action-evidence-boundary-05, Work in Progress.
