<!-- Published copy in varwof/capability. Working draft and rationale live in the
     design repository; treat this copy as canonical once committed. -->

# CLC-v1 设计说明

> English decision record: [design-notes.md](design-notes.md)（本文件是完整中文历史，英文版是裁决摘要）

> ⚠️ **Preview** — 仅供预览，勿用于生产。正式发布前接口与特性可能变更。

日期：2026-09-10（v2：通用授权-证据语言重构）

---

## 1. 设计目标回顾

CLC-v1 的目标是回答一个问题：**给定一组授权授予和一个操作请求，网关如何确定性地判断"允许"还是"拒绝"？**

v2 扩展目标：**这种语言能否在授权侧和证据侧一致呈现？**

核心约束：
- 最小（9 概念，含 5 共享 + 2 授权侧 + 2 证据侧）
- 可执行（决策/满意度函数确定性、fail-closed）
- 通用（不绑定 AIC 或 EMILIA，但两侧都能引用）
- 人和 AI 都能理解

---

## 2. 九概念取舍

### 2.1 共享基础（5 个）

| # | 概念 | 授权侧 | 证据侧 | 为什么是核心 |
|---|------|--------|--------|-------------|
| 1 | Action | Operation | ObservedAction | 两侧共用的"被引用之物" |
| 2 | Identity | CapabilityId | ActionId | 如何命名/引用动作 |
| 3 | Binding | Entailment | Match | 连接身份与动作 |
| 4 | Constraint | Grant params | Evidence requirements | 两侧都有"限制" |
| 5 | Verdict | allow/deny | SATISFIED/UNSATISFIED | 两侧都有"判定" |

### 2.2 授权侧专用（2 个）

| # | 概念 | 为什么需要 |
|---|------|-----------|
| 6 | Grant | 授权的载体；principal 签发的就是 Grant |
| 7 | Intersection | 多来源合成；ACA §4.2 P_effective 公式 |

### 2.3 证据侧专用（2 个）

| # | 概念 | 为什么需要 |
|---|------|-----------|
| 8 | Match | 证据绑定到精确实例；CAID 的 CLC 抽象 |
| 9 | Satisfaction | 证据满足需求的判定；AEC 的 CLC 抽象 |

**被排除的概念**：
- **Scheme 信任模型**：属于注册表层（ACA §2.2/§3.3），CLC 只引用 scheme-id
- **Delegation chain**：属于 AIC-JWT DA 层，CLC 只定义单层 Grant 的语义
- **Execution lifecycle**：属于执行层（EMILIA AEB），CLC 的 Verdict ≠ 执行证据
- **Native verification**：属于各原生规范（签名、schema、新鲜度），CLC 只定义接口

---

## 3. 通用性设计

### 3.1 为什么是"共享基础 + 两侧专用"

并集（"把所有概念混在一起"）的问题：
1. 授权侧不需要 Match/Satisfaction（它只需要 Entailment/Decision）
2. 证据侧不需要 Grant/Intersection（它只需要 Match/Satisfaction）
3. 混在一起会导致概念膨胀，违反最小性

共享基础（Action/Identity/Binding/Constraint/Verdict）是两侧都用的
**抽象词汇**；两侧专用概念是这些抽象的**具体实例**。

### 3.2 为什么 Binding 是抽象概念

Binding 覆盖两个看似不同的操作：
- 授权侧：Entailment（grant ⊆ operation）— "这个授权覆盖这个请求"
- 证据侧：Match（evidence ↔ action）— "这个证据绑定到这个动作"

但它们的**结构相同**：都是"连接一个 Identity 到一个 Action"。
抽象为 Binding 后，两侧可以引用同一个概念，不需要各自定义。

### 3.3 为什么 Constraint 是共享的

授权侧约束（max_rows, time:window）和证据侧约束（freshness,
consumption, quorum）用同一个文法：

```
constraint = scheme ":" type [ ":" params ]
```

区别只在于**谁来评估**：授权侧由 validator 评估，证据侧由 evidence
evaluator 评估。文法和合并规则完全相同。

---

## 4. 文法设计

### 4.1 为什么用 `scheme:action` 而不是纯路径

ACA 草案用 `{vendor}/{product}-v{major}` 作为 scheme identifier，
能力 ID 用 `query:SELECT`。CLC 统一为 `scheme:action` 两段式：
- scheme 引用 ACA 的 scheme identifier（不变）
- action 用冒号分隔（与现有 `query:SELECT` 格式一致）

### 4.2 为什么 v1 只允许完整末段通配

wit-wpt-interop 的 subset.go 已经实现了 `*`、`**`、`{a,b}`、`[a-z]`。
但 v1 只保留完整末段 `*`，理由：
1. **最小性**：`*` 覆盖 90% 的实际需求（"所有查询操作"、"所有管理操作"）
2. **安全性**：部分段通配（`crm.re*`）容易误配；`**` 跨段匹配语义复杂
3. **可审计**：完整末段通配的匹配结果可人工复核；`{a,b}`/`[a-z]` 需要正则专业知识

`**`、`{a,b}`、`[a-z]` 记录为 scheme 扩展点（§2.2），未来可纳入。

> **事实记录（2026-09-10）**：`wit-wpt-interop/go/subset.go` 实现了
> `*`、`**`、`{a,b}`、`[a-z]` 等较丰富形式。该实现是 **v2 前身 /
> scheme 级能力**，**不构成 CLC-v1 核心一致性**——读者不应据其推断
> "规范与实现打架"。CLC-v1 核心只定义完整末段 `*`；v1 一致性实现
> MUST 拒绝其余形式（`unsupported_wildcard`）。

### 4.3 为什么禁止裸 `*`

裸 `*` 意味着"匹配一切 scheme 的一切能力"——这不是授权，是权限提升。
fail-closed：裸 `*` → deny。

---

## 5. 蕴含规则

### 5.1 为什么用"逐分量"而不是"正则匹配"

正则匹配（`std/database-v1:query:SELECT.*`）的问题：
1. 正则语义不透明（人无法一眼看出覆盖范围）
2. 正则引擎行为不一致（不同语言的正则有差异）
3. 无法做 segment-boundary 比较（`query:SELECT` 和 `query:SELECT:deep` 的关系）

逐分量匹配：先按 `:` 分段，再逐段比较（字面或通配）。语义清晰、可审计。

### 5.2 为什么 params subset 用"类型递归"而不是"JSON Schema 匹配"

JSON Schema 匹配（`validate(operation.params, grant.params_schema)`）的问题：
1. Schema 本身是外部定义（ACA §2.1 params_schema），CLC 不应依赖外部 schema
2. Schema 匹配语义复杂（`oneOf`、`additionalProperties` 等），难以做确定性子集判定
3. 无法做"grant 限制 operation"的语义（Schema 只能验证"是否合法"，不能验证"是否被覆盖"）

类型递归：number ≤、array ⊆、object 逐键递归、其余精确。简单、确定、可实现。

---

## 6. 交集与 deny-when-declared

### 6.1 为什么用交集而不是并集

并集（"任一来源允许即可"）的问题：
1. 安全性差（只要一个来源松，整体就松）
2. 与 ACA §4.2 的 P_effective 公式不一致（P_effective = P_principal AND C_agent AND P_gateway = 交集）

交集（"所有来源都必须允许"）：
- 与 ACA 的 AND 语义一致
- 更安全（取最严约束）
- 与 EMILIA 的 bounded mapping 一致（exact action ∈ authorized class，所有约束都必须满足）

### 6.2 为什么显式空 ≠ 缺省

ACA §4.2 明确：空 bound = 拒绝整类；省略 = scheme 默认。CLC 必须保持这个区分：
- `{"tables": []}` → 空列表 → deny（没有表可以查询）
- `{"tables": null}` → **v1 拒绝**（`invalid_params_null`）；省略 → scheme 默认（通常不限制）

---

## 7. 决策函数

### 7.1 为什么决策函数是"查表 + 约束校验"而不是"逻辑编程"

逻辑编程（Prolog/Datalog）的问题：
1. 执行模型不透明（回溯、cut 等语义对 gateway 不友好）
2. 难以做确定性保证（相同输入必须相同输出）
3. 依赖外部求解器

查表 + 约束校验：遍历 grant 集 → 找到匹配 → 校验约束 → 返回。简单、确定、可测试。

### 7.2 为什么 reason code 是稳定的

reason code 稳定的原因：
1. 审计需求（同类型错误必须有相同 reason，否则无法聚合分析）
2. 调试需求（开发者需要稳定的错误码来定位问题）
3. 互操作需求（Go 和 Python 实现的 reason code 必须一致）

实现自由：实现可以添加额外细节（如 `"limit:violated: max=100, requested=150"`），但
必须包含稳定前缀（如 `"limit:violated"`）。

---

## 8. 证据侧满意度函数

### 8.1 为什么需要 Satisfaction

v1 只有 Decision（授权侧判定）。v2 加入 Satisfaction（证据侧判定），
使 CLC 成为通用语言。

Satisfaction 的结构与 Decision 对称：
- Decision: `allow` / `deny` + reason
- Satisfaction: `SATISFIED` / `UNSATISFIED` + reason

### 8.2 为什么 Satisfaction 不替代 Decision

Satisfaction 回答"证据是否满足需求"；Decision 回答"是否允许执行"。
两者是不同的判定：
- Satisfaction = "我有证据证明这个动作被授权了"（事实判定）
- Decision = "我现在允许执行这个动作"（策略判定）

一个动作可能 SATISFIED 但被 deny（证据充分但策略不允许）；
也可能 UNSATISFIED 但被 allow（证据不足但策略豁免）。

---

## 9. 消费面

### 9.1 AIC-JWT DA

DA 的 `capabilities[]` 就是一组 Grant。网关拿到 DA 后：
1. 提取 Grant 集
2. 对每个操作调用 `Authorize(grants, operation)`
3. 返回 Decision

CLC 的价值：DA 只需要携带 Grant，不需要定义"什么是允许"——CLC 的 Decision 函数就是"什么是允许"。

### 9.2 EMILIA AEB

AEB 中**被 VERIFIED 的授权工件**承载 CLC 的 Grant（VERIFIED 是 AEB
对工件的**判定层级**，Grant 是**工件内容**，两者不可混同）。
AEB 的 exact-action 对应 CLC 的 ObservedAction（"观测到的动作"）。
AEB 的 bounded mapping = CLC 的 Match（"证据绑定到精确动作"）。
AEC 的 SATISFIED = CLC 的 Satisfaction（"证据满足需求"）。

CLC 的价值：AEB 不需要重新定义授权/证据语义——直接引用 CLC 的 Decision 和 Satisfaction 函数。

### 9.3 RAR authorization_details

RFC 9396 的 `authorization_details` 中 `type="capability"` 的 `capability_id`
就是 CLC 的 CapabilityId。AS 拿到后调用 `Authorize(grants, operation)` 即可。

CLC 的价值：AS 不需要自己实现授权逻辑——引用 CLC 的 Decision 函数。

---

## 10. 与 ACA 草案的关系

| ACA 章节 | CLC 对应 | 关系 |
|----------|---------|------|
| §2.1 Scheme | §3 Grammar | CLC 引用 scheme-id，不定义 scheme 信任模型 |
| §3.1 DA | §5 Grant | DA 的 capabilities[] = Grant 集 |
| §3.3 双层签名 | 不在 CLC 范围 | CLC 只关心 Grant 的语义，不关心签名 |
| §4.1 流水线 | §9 Decision | Decision 函数是流水线的"计算 P_effective"步骤 |
| §4.2 P_effective | §7 Intersection | P_effective = ∩(P_principal, C_agent, P_gateway) |

---

## 11. 遗留开放问题

1. **params_schema digest**：~~CLC v1 用 JCS (RFC 8785) 做 params canonicalization，但
   ACA 的 `params_schema_digest` 用什么 hash 算法？需要与 ACA 对齐。~~
   **裁决（2026-09-10）：定 SHA-256 over RFC 8785 (JCS) 规范化字节；以 register 仓
   现有实现为准回填 ACA，规范侧只引用。**

2. **通配与 scheme 扩展**：~~v1 只有 `*`，但 wit-wpt-interop 已实现 `**`/`{a,b}`/`[a-z]`。
   何时纳入 v2？~~
   **裁决（2026-09-10）：v1 保持只有完整末段 `*`（语义：匹配 ≥1 个剩余段）；
   `**`/`{a,b}`/`[a-z]` 记为 v2 扩展点。v2 讨论的输入为 AIC-JWT 评审结论：
   字面段比通配段更具体、`*` 比 `**` 更具体、交替与字符类是段内算子、不构成全局优先级。**

3. **Deny-when-declared 的"省略"判定**：~~JSON 中 `null` vs 缺省字段的区分取决于
   序列化实现。~~
   **裁决（2026-09-10）：v1 规定 `null` 参数值一律拒绝（`invalid_params_null`，
   fail-closed，稳定 reason code）；`params` 字段缺省 = scheme 默认；
   显式空容器（`[]`/`{}`）= deny 整类。三者语义互不相同，跨语言实现按此对齐。**

4. **操作完全无 `params` 字段的判定**：~~有界 grant 与"无 params 字段的操作"
   之间的语义未明文。~~
   **裁决（2026-09-10）：有界 grant（params 存在且非 scheme 默认）与操作
   无 `params` 字段（整个字段缺失，而非单个键缺失）→ `Entails → false` →
   `deny("params_missing")`。§6.3 已并入明文规则；`decide-009` 向量锁定该
   语义；`params_missing` 的释义涵盖"缺整个字段"与"缺单个被约束键"两种
   情形（即第 46 条向量）。**

5. **Satisfaction 与 Decision 的交叉**：v2 新增 Satisfaction 函数后，
   一个动作可能 SATISFIED 但被 deny，或 UNSATISFIED 但被 allow。
   这是设计意图还是需要强制对齐？**待决。**

---

## 12. 参考实现素材

CLC v1 的语义直接来自 wit-wpt-interop 的 subset.go（§6.1-6.3
Entailment、§6.2 params subset）和 ACA §4.2（deny-when-declared、
P_effective 公式）。v2 的 Match/Satisfaction 抽象来自 EMILIA AEB-04
§5.3-5.7 和 CAID-02 §8 的 Action-Mapping Profile。
规范将这些"已实测的语义"转正为正式定义，不引入新机制。

---

## 13. 2026-09-10 修订记录（本轮）

1. **向量条款引用随章节重编号同步**：章节整体后移（§2→§3、§5→§6、§6→§7、
   §7→§8、§8→§9、§9→§12），45 条向量的 `spec_clause` 已按映射更新；重跑
   Go/Python 仍是 45/45、100% 一致。
2. **§12 一致性分两类**：`CLC-A`（授权侧，v1 基线：grammar + entailment +
   intersection + decision）与 `CLC-E`（证据侧可选：match + satisfaction）。
   理由：v1 要保持"最小"，只做授权侧的实现不应被判不合规。
3. **§9.4 错误码表转为规范性**：13 个稳定 reason code（与 parity 报告枚举一致），
   其它 scheme 可扩展但不得重定义。
4. **术语提示**：§2 明确 "Binding ≠ 密钥绑定"（后者属原生凭证规范，见 §11）；
   verdict 大小写按 EMILIA/AEB 惯例（授权侧小写 allow/deny，证据侧大写）。
5. **引用升版**：EMILIA AEB 引用从 -04 升到 **-05**，附录 A 的节号改为
   §3 / §5.1 / §7（与审查记录一致）。
6. **用词修正**：`ObservedAction (verified effect)` → `(asserted effect)`，
   避免与 §11 排除的原生验证混淆。

---

## 14. 裁决（2026-09-10）：数值参数的域语义 → 采用方案 A（v1.1）

新增工业机器人 scheme 后实测发现：`number` 参数的 `op ≤ grant` 是**上界语义**，
而工位号/区域号/工具号这类**离散标识**不能这样解释——"授权 3 号工位"会顺带
覆盖 1、2 号（Go/Python 两边一致判 allow，属规范层问题而非实现 bug）。

详情与候选修法见 `mailarchive/clc-v1-finding-param-domain-2026-09-10.md`：
- 方案 A（v1.1，已采纳）：授予侧数组表示集合，请求侧允许标量，规则改为
  "标量必须 ∈ 授予数组"，新增 reason code `not_in_enum`；
- 方案 B（v2 方向，未启动）：scheme 声明参数域（bound / enum / exact），语义按域分派。

**落地记录（2026-09-10，用户裁决方案 A）**：
- 规范：§6.2 数组 enum 语义 + §9.4 `not_in_enum`；附录 B.3 8 → 14 条，总量 46 → 52；
- 实现：Go `valueSubset` array 分支改精确成员相等（`enumEqual`），Python 同步；
  空数组 → `empty_bound_denies_class`（params-007 reason 修正）；`not_in_enum` 进入
  `Authorize` 的 params 级传播集合；
- 验证：Go/Python 52/52 全绿，两侧 reason 逐条一致；`go test ./semantics/` ok；register
  加载器装载 robot-line-v1（10 能力）通过；
- 取舍：成员比较用**精确相等**（数组内数字是精确值而非上界）；标量 number grant 保留
  上界语义——分类参数依赖 scheme 作者用数组编码（robot-line-v1 `station` 已改数组）；
- 已知遗留（v1.1 范围外，仅 reason 差异）：entail-004、intersect-002、combined-003、
  005、006、011——parity report rev 3 已记录。

**状态：已裁决 → 方案 A 已落地。** 方案 B 记为 v2 方向。

---

## 15. 裁决（2026-09-10）：Resolved Reason Ordering（v1.2）

v1.1 落地后实测发现 6 条"向量期望 vs 双实现"的 reason 差异（entail-004、
intersect-002、combined-003/005/006/011）。根因：**检查顺序未定义**——同一次
失败可能命中间隔层，实现与向量各取其一。特此引入规范性检查顺序
（规范 §9.3，正文本为英文）：

| # | 层 | 触发 | reason |
|---|-----|------|--------|
| 1 | CapabilityId 合法性 | §3 文法/通配形状 | invalid_capability_id / missing_capability_id / unsupported_wildcard |
| 2 | Params 规范化 | 重复 JSON 键；非有限/超精度数字；512B 或深 32 超限（§6.2） | invalid_params_duplicate_key / invalid_params_number / invalid_params_size |
| 3 | 命名空间 = scheme + action Class | 授权与操作的前两段不同 | different_namespace |
| 4 | 路径覆盖（同命名空间） | 字面路径、尾通配深度 | literal_mismatch / wildcard_requires_trailing_segment |
| 5 | 显式空 bound | 任一授权/交集源声明 `[]`/`{}` | empty_bound_denies_class（先于成员判定，deny-when-declared） |
| 6 | null | 任一 null 参数值 | invalid_params_null |
| 7 | 参数存在性 | 授权有界而请求缺 key / 无 params | params_missing |
| 8 | enum 成员 | 值不在授予数组集合内 | not_in_enum |
| 9 | 上界比较 | 数值超界 | params_exceed_grant |
| 10 | 覆盖空 | 交集结果空 / 无授权覆盖 | no_overlap / capability_not_authorized |
| 11 | 约束 | 未知约束类型 / 已知类别违规 | unknown_constraint / {type}:violated |

> **2026-09-11 修订**：层 2 为新增的 **Params 规范化**（输入边界，先于一切层比较，
> 见 §17）；原层 2–10 顺延为层 3–11。表中层号已按当前状态重排。

**落地**：
- 命名空间定义 = 前两段（scheme + Class）；`matchID` 先做该检查，entail-004
  （query vs admin）→ `different_namespace`；
- `paramsSubset` 按 5→9 层内顺序扫描（空 bound → null → 存在性 → 成员/上界）；
- `Intersect` 在合并前扫所有源，任一显式空 bound → `empty_bound_denies_class`
  （收口 intersect-002 / combined-005 / 011）；
- 向量纠偏（按新顺序，非擅改实现）：combined-003 → `params_missing`（grant 无
  max_rows 约束，op 缺 limit key）；combined-006 → `capability_not_authorized`
  （unknown scheme 属命名空间差异 → 无覆盖，非约束类型错误）；
- 验证：Go/Python 52/52 全绿，**impl ≡ 向量期望 = 0 差异**，
  Go==Python 逐条一致；改 reason 码从 v1.1 的 6 条差异降为 0。

**状态：已落地（v1.2）。** 校验顺序成为 §9.4 规范性主张的机械保证。

---

## 16. 裁决（2026-09-10）：Reason 强制断言 + 空 grant fail-closed（rev 5）

独立比对在"0 差异"结论下又挖出 3 个问题（1 个为评审工具自身）：

- **F1（规范格式）**：实现返回 `invalid_params_null: limit`，而 §9.4 与
  向量期望是裸码。双侧实现彼此一致（非双实现分歧），但字符串比较恰恰是
  互操作最容易炸的点。→ **§9.4 明确：规范码 = 首个 `:` 之前的部分；
  实现 MAY 追加 `: <detail>` 作为诊断后缀；工具一律按规范码比较。**
- **F2（fail-closed）**：Python `authorize(None, op)` 抛 `TypeError`
  （Go 侧被 runner 的 nil 短路掩盖，同风险）。→ **两侧对空/缺省 grant
  一律返回 `deny("capability_not_authorized")`（§9 层 9，第一道检查）；
  操作缺省 → `missing_capability_id`（层 1）**。runner 去掉 nil 短路，
  使加固路径被每条向量强制走过。
- **F3（工具缺口，最重要）**：两个 runner 只比 verdict，"52/52 全绿"
  不证明 reason 一致。→ **两个 runner 增加 reason 断言（按规范码比较），
  verdict 与 reason 双通过才算 PASS**；负向测试（人为改坏 decide-015
  期望）两侧均 Reason-fail: 1，证明强制定位生效。

配套：新增向量 decide-015（空 grant `{}` → `capability_not_authorized`），
总量 52 → 53；附录 B.5 → 10 条，`kind=decide` → 17 条。

**验证**：Go 默认路径 + `CLC_VECTORS` 均 53/53、Python 53/53，
Reason-fail: 0（工具强制，非临时脚本）；gofmt / vet / go test 全绿。
1–3 按建议顺序完成，为可选工作（Offline Capability Manifest / 断网 demo）留出起点。

**状态：已落地（rev 5）。**

---

## 17. 裁决（2026-09-11）：Params 规范化 + 语言修订协商 + 安全补强（v1.1 → 定稿）

closeout 审查（2026-09-11）的 P2/P3/P4 合并裁决，改动如下：

1. **§9.3 新增第 2 层 Params 规范化**（原层 2–10 → 层 3–11）。三个理由码：
   - `invalid_params_duplicate_key`：JCS 序列化下重复 JSON 键。map 解码只剩
     最后一个值，必须回到**原文**判定；
   - `invalid_params_number`：非有限（如 `1e400`）或 >17 位有效数字的数值。
     JSON 明文无法携带 +Inf；
   - `invalid_params_size`：JCS 形式 >512 字节，或嵌套 >32 层。
   - 顺序固定：大小/深度 → 重复键 → 数字形状；畸形 JSON 的兜底归
     `invalid_params_number`。
   - 生效点 = 输入边界（任何层之前），并配 `raw_params` 向量字段
     （原始 JSON 文本字符串，见 `clc-v1-ambiguities.md` #5）。
2. **§12.1 语言修订协商**：实现声明 `CLC-<major>.<minor>`（本文档 **CLC-1.1**）；
   兼容读法 = 同 major 且输入 minor ≤ 自己；不兼容一律
   `deny("unsupported_language_revision")`（fail-closed，禁静默降级），
   在任何 §9.3 层之前判定。向量 revision-001（1.0 → 允许）/-002（2.0 → 拒）。
3. **§6.2 输入规范化规范块**（5 语句：JCS 优先序列化 / 重复键 / 数字形状 /
   大小深度 / 检查顺序）。
4. **Security Considerations 补 4 条**：解析分歧不得改变判决；reason 冒号后缀
   仅诊断；版本不匹配 fail-closed；资源耗尽在输入边界封顶。
5. **附录 B 同步**：B.3 → 19 条（P15–P19），B.5 → 12 条（D11/D12），
   总量 53 → **60**；`kind=entail (25)`、`kind=decide` 含两条 revision 向量。
6. **scheme 数据审计（P8）**：扫描全部 12 份 `v1.json` 的 params_schema，
   仅 `std/robot-line-v1` 声明数字数组参数（`station`，start/move*/set*/maintenance/
   override 等 9 个 cap 均有）——这是**有意**与 §6.2 enum 语义对齐的分类参数；
   其余 11 份无数字数组、无 enum/上界歧义。审计结论登记在
   `capability/data/artifacts-index-zh.md`。

**验证**：Go/Python **60/60 全绿，Reason-fail: 0**，Go == Python 逐条一致；
go test / vet 全绿；schema 校验 60 条通过。

**状态：已落地（定稿 v1）。**

---

## 18. 需求证据（2026-09-11）：三个新 scheme 压测出 CLC v1 未覆盖的语义维度

新增 scheme 覆盖面广的域压测（医疗 / 金融 / 数据三个域），用于在 CLC v1
**不新增核心语义**的前提下试出 v1 表达不动的维度，作为 **CLC v2** 的需求证据。
三者都以 `std/{clinical,payments,data}-v1` 落地（`capability/data/std/`），
只有能力清单与 scheme 作用域约束类型声明；未改动任何核心语义，未改参考实现。

- **压测结论**：三个新维度（会签、累计额度、目的/区域）在 CLC v1 里
  要么只能退化为“单次判定”的参数形态，要么因约束类型未知而 fail-closed
  （`unknown_constraint`）。这正是 v2 约束词汇表的需求清单来源。

### 18.1 累计额度 / 跨请求语义（payments:quota:daily:<n>）

- **现状（v1）**：只有单次判定的上界（`amount`，每次操作独立比对）。
  “一天累计不超过 N”这类**跨请求累加**语义 v1 未定义、参考实现也不累计。
- **压测向量** `payments-002`：grant 带 `payments:quota:daily:1000000` →
  `deny("unknown_constraint")`（fail-closed），而不是悄悄放过或半完成语义。
- **v2 建议形态（仅建议，不实现）**：
  - 输入：约束沿用同一语法 `scheme:type[:params]`，如
    `payments:quota:daily:1000000`（window + quota 两个参数位）；
  - 要求：授权判定前/中引入**有界消费状态**（key = principal+scheme+capability+
    window），把当前窗口已授权/已发生额纳入比对；窗口翻转（UTC 日界）重置；
  - 要求：**判定依赖状态**必须成为决策函数的显式输入（v1 决策函数是无状态纯函数，
    这是本需求与 v1 的最大结构性差异），并配套状态的确定性/原子性语义；
  - 后续：作为 CLC v2 的 `§9` 决策函数扩展（新增有状态判定面），v1 语义不变。

### 18.2 目的 / 区域分类约束（data:purpose:<v> / data:region:<v>）

- **现状（v1）**：v1 的数值上界只能表达“量”，表达不了“用途/流向”这类
  **分类**语义；把目的/区域转成**参数集合**（`purpose`/`region` 数组）虽可判定
  （`data-001` 允许路径），但约束权限本身的形态（谁在什么用途下可用）得靠
  每次 grant 显式携带，而不是一条约束。
- **压测向量** `data-001`：目的/区域用参数集合编码、请求成员在集内 →
  `allow`，证明“分类→集合参数”这条 v1 可判路径成立；约束三元组形态
  `data:purpose:*` 同样 fail-closed（未单独建向量，规则同一）。
- **v2 建议形态（仅建议，不实现）**：
  - 输入：约束语法不变（`data:purpose:research` 等单值枚举参数位），
    与授权参数比对采用“集合成员”而非“数值上界”；
  - 要求：分类约束在合并规则里走**交集**（§7 同 capability 合并的 tightest
    语义对集合 = 集合交），并在约束类型表里新增“分类（enum）型约束”一族，
    与数值上界分开登记；
  - 后续：`data:region` 出境语义还要结合“region 覆盖关系”（如 `cn ⊆ asia`），
    v2 需定义 region 层级/映射表作为约束参数位的受控词表。

### 18.3 义务 / 会签（clinical:quorum:2）

- **现状（v1）**：证据侧（§8.2）已为 evidence-side constraints 预留位置，
  但 v1 授权侧**没有多主体确认**机制；高危操作双人核对只能写在文档里当约定
  （scheme 作用域类型 `clinical:quorum:2` 声明在 `std/clinical-v1`），
  参考实现认不出来 → fail-closed。
- **压测向量**：未为 quorum 单独建“允许”向量（v1 无法判定），规则陈述在
  `clinical-v1-capabilities.md` 与表（Constraint Types）里；如需可判演示，
  请走 `varwof/constraint-v1:time:window` 等已知类型。
- **v2 建议形态（仅建议，不实现）**：
  - 输入：证据侧约束，如
    `clinical:quorum:2:roles=clinical-physician,pharmacy`（人数 + 允许角色），
    归属 §8.2 证据侧而非授权侧；
  - 要求：新增“证据满意集合”评估——quorum=2 要求至少两个**互不相同主体**的
    证据同时在场且各角色在允许集内，重复同一主体不算数；
  - 要求：与现 §11 遗留开放问题（证据新鲜度/消费/角色约束）统一进 v2 的证据侧
    词汇表。

### 18.4 落地清单（本批）

- scheme：`std/clinical-v1`（7 cap，含 2 个 high-risk）、`std/payments-v1`
  （6 cap）、`std/data-v1`（5 cap）。分类参数一律数组、有序量一律标量上界；
  每份都含免责 note（授权边界 ≠ 临床决策 / 反欺诈风控 / 隐私合规认证）。
- 向量：追加 **clinical-001/-002、payments-001/-002、data-001/-002**，
  总量 60 → **66**，Go/Python **66/66 全绿、Reason-fail: 0**；schema 校验通过。
- 三份 capabilities.md 都含“Constraint Types”表，明示 scoped 类型在 CLC v1 中
  一律 `unknown_constraint` fail-closed。

**状态：scheme 与向量已落地；v2 词汇表仅记录需求形态，未实现。**
（2026-09-11 补录：该批 66 条之后又经 §19 P2'（→68）与 §20 补录批
（→76）两步扩充，最终状态见 §20。）

---

## 19. 裁决（2026-09-11）：P2' 参数键闭合（undeclared_param，发布前审计）

**发现（发布前复核）**：P2' 未落地——有界 grant 对操作参数中的**未声明键**
没有明确处置规则（两套实现此前都只校验“grant 键必须在 op 中出现”，
“op 键必须在 grant 中声明”从未实现，也没有任何断言存在）。

**裁决（用户选定方案 A，不回归 fail-open）**：**键闭合（Key closure）**——
有界 grant 只管辖其声明的键：

- 操作携带 grant 未声明的参数键 → `deny("undeclared_param")`（负向闸门，
  fail-closed）；
- 无参数 grant（unconstrained）接受任意操作参数，键闭合不适用；
- §9.3 层 7 内次序：**缺失键（`params_missing`）先于未声明键
  （`undeclared_param`）**，两者都先于层 8–9 的值检查；
- 只检查**顶层键**：键存在时值的嵌套对象类型递归（enum/上界）照旧。

**落地**：

- §6.2 新增规范段「Key closure (Plan A)」；§9.3 层 7 行更新为双向；
  §9.4 新增 `undeclared_param` 行。
- Go（`register/semantics`）：`ErrParamsUndeclared`；`paramsSubset` 在
  缺失键循环之后新增未声明键循环；`isParamsLevelReason` 加前缀。
- Python（`aic-capability-demo`）：`ParamsUndeclared`；`params_subset`
  同步循环；`_is_params_level_reason` 同时匹配裸码与 `: <key>` 后缀。
- 新向量 **undeclared-001**（多余请求键 → `undeclared_param`）、
  **undeclared-002**（缺失 + 未声明并存 → `params_missing` 胜出）：
  总量 66 → **68**，Go/Python **68/68 全绿、Reason-fail: 0**，与向量期望逐条
  逐码一致；既有 66 条无一改变结果。
- 修订：附录 B.5 → 14 条（D13/D14）、Total 68；parity report rev 8；
  README / 向量 README 计数同步。

**影响面**：v1 本就无 fail-open 空子，本裁决把“未声明请求键”从隐式接受
变为显式拒绝并纳入两套实现的一致性向量。

---

## 20. 落库补录（2026-09-11）：Codex 批 —— 补齐空行向量 + 参考实现未覆盖路径

评审后由 Codex 补录的 10 个向量，总量 **68 → 76**。不改核心语义：
两份参考实现每次都如实允许/拒绝并产出同一规范码，向量只是把已实现但
此前未被语料覆盖的行为显式固化（并顺带补上附录 B 中一直缺向量、但行
一直存在的 P6/P13）。

- **补齐空行（2）**：`params-006`（无参数 grant 接受任意 op 参数，
  §6.2 unconstrained，→ B.3 P6）、`params-013`（数组成员 + 标量上界并存
  的允许方向，v1.1 enum 语义，→ B.3 P13）。
- **输入规范化边界（2, 正侧）**：`params-020`（序列化恰 512 B → allow，
  P18 的反侧）、`params-021`（嵌套恰深 32 → allow，P19 的反侧）；
  原始载荷走 `raw_params`，两侧实现一致通过。
- **决策层 `Authorize` 路径（2）**：`decide-016`（空 grant 且空 op →
  `capability_not_authorized`，§9.3 预检查先于一切层）、`decide-017`
  （grant 有效但 op 无 `id` → `missing_capability_id`，层 1）。
- **交集 §7 规则 5–6（4）**：`intersect-007`（零源 → fail-closed
  `absent_source`）、`intersect-008/-009`（空 params 源不得挤掉已有上界，
  且与顺序无关）、`intersect-010`（标识符比较与 params 无关——空 params
  且不同标识符时窄标识符胜出；此前两实现曾误报 `no_overlap`，已按 §7
  规则 2 校正为规范行为，未改动条文只对齐实现）。

**附录同步**：B.3 → 21（+P20/P21）、B.4 → 10（+I7..I10）、B.5 → 16
（+D15/D16）、Total **76**；向量 README、capability README 同步。
parity report rev 9 记录本批。

**当前总量 76 向量**：syntax 6 / entail 31 / intersect 14 / decide 25
（含附录 B 与 6 个 scheme 压测向量及 §19 两个键闭合向量）。

---

## 19. 探针复核（2026-09-11 晚）：第三批文本钉死的三条，各与一个实现矛盾

第三批规范文本（§6.2 boolean、§6.3 layer-6 先于 presence、§3 通配符先于文法、§7 P11 律、§12 corpora）
落定后，用 6 条探针向量对**三个**实现各跑了一遍（此前只对 Go/Python 跑过，TS 实现补跑）：

| 探针 | 规范要求 | Go（修前） | Python（修前） | TS |
|---|---|---|---|---|
| 布尔精确（grant `true` vs op `1`） | deny `params_exceed_grant` | ✅ | ❌ **allow（fail-open）** | ✅ |
| layer 6 先于 presence（grant `null` + op 无 params） | `invalid_params_null` | ❌ `params_missing` | ✅ | ✅ |
| 通配符形状 op id | `unsupported_wildcard` | ❌ `invalid_capability_id` | ✅ | ✅ |

**根因**：
1. Python `value_subset` 把布尔分支排在数值分支之后，而 `True == 1` → 布尔 grant 落进数值比较 → **放行**（fail-open）。
   修法：布尔分支前置并显式排除 `bool` 参与数值比较。
2. Go `Entails` 在 `paramsSubset` 之前先判 `op.Params == nil`（presence），且 `Authorize` 把 layer-1 具体码塌成 `invalid_capability_id`。
   修法：`ValidateGrantParams`（layer 6）提到 presence 之前；`Authorize` 传播校验器返回的具体码。
   （`paramsSubset` 内部也已按 5→6→7 重排。）

**结论：规范这批文本是照 TS 写的**——TS 三条全对，Go 违背两条、Python 违背一条。**语料当时覆盖不到任何一条**
（没有布尔-vs-数字、null+缺 params、通配符形状 op id 三类输入），所以 76/76 与 524 条属性测试全绿也看不出来。

**已补**：向量 76 → **80**（`params-022` 布尔负例、`params-023` 布尔正例、`params-024` null 先于 presence、
`decide-018` 通配符 op id）。三个实现 80/80；属性测试三方各 524 例 / 299 顺序检查 / 290 闭包探针 / 0 失败（三方一致；Go 侧必须用 -count=1，否则会回放缓存的旧计数）。
两份规范副本 drift 0。

**已修（同日）**：TS 的 `validateRawParams` 改为**两趟**——第一趟只算 size/depth 并在越界时抛 `invalid_params_size`，
第二趟才执行 dup/number 检查，与 §6.2 item 5（size/depth → dup → number）一致；depth 仍在解析中判（属检查 4）。
新增三条组合向量把这个顺序钉死：`params-025`（超限+重复键 → size）、`params-026`（超限+坏数字 → size）、
`params-027`（重复键+坏数字、未超限 → dup）。语料 80 → **83**，三方 83/83。
