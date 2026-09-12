# CLC-v1 Ambiguities

Date: 2026-09-10

## 1. Identifier shorthand vs §2 grammar

**Status**: Resolved (2026-09-10)

The original spec Appendix B used `db:query:SELECT` shorthand in
Entailment tables (B.2, B.6/C7).  §2 grammar requires
`vendor/product-vN:action` format (e.g. `std/database-v1:query:SELECT`).

**Resolution**: All vectors normalized to full `std/database-v1:...`
format.  The shorthand was a convenience in the spec; the grammar
is authoritative.

## 2. §5.3 step 3: G.params absent → true (fail-open?)

**Status**: Resolved (2026-09-10)

Original §5.3 step 3 read: "G.params absent → true (operation has
fewer params)".  This creates a fail-open path: a grant with no params
covers any operation, even if the operation has unconstrained params.

**Resolution**: §5.3 step 3 now reads "G.params absent → true (grant
unconstrained)".  The intent is: if the principal did not constrain
params, the agent may request any params.  This is correct behavior
(not fail-open) — the principal explicitly chose not to constrain.

Step 4 now reads: "O.params absent → false (bounded grant, request
omits it → fail-closed)".  If the grant constrains params but the
operation omits them, this is a fail-closed deny.

**Vectors affected**: params-006 (grant unconstrained → allow),
decide-007 (bounded grant, operation omits → deny).

## 3. null parameter handling

**Status**: Resolved (2026-09-10)

The spec defines three states for params:
- **Absent**: parameter not present → scheme default applies (or
  fail-closed per §5.3 step 4)
- **Explicitly empty**: `{"tables":[]}` → deny the class
  (deny-when-declared)
- **null**: `{"limit":null}` → reject (`invalid_params_null`)

**Resolution**: null is invalid in v1.  Any null parameter value in
grant params or operation params → deny with `invalid_params_null`.

**Vectors affected**: params-008, decide-008.

## 4. 已发布 harness 的 array-as-bound → enum 语义对齐（2026-09-11）

**Status**: Resolved (2026-09-11)

`aic-jwt/wit-wpt-interop`（README + `go/subset.go`）与
`aic-jwt/wit-demo/src/lib/subset.ts` 在 CLC v1.1 之前实现了 **array-as-bound**
语义（数组内数字按"上界"递归比较，请求必须是数组）。CLC v1.1 §6.2 改为
**enum（允许值集合）** 语义后，两处行为差异：

| 输入 | harness（旧） | CLC v1.1 |
|---|---|---|
| grant `{"station":[1,2,3]}` + 请求标量 `2` | 拒（agent 非数组） | 允许（成员） |
| grant `{"station":[3]}` + 请求 `[1]` | 允许（1 ≤ 3） | 拒（`not_in_enum`） |
| grant `{"limit":[100]}` + 请求 `50` | 允许（50 ≤ 100） | 拒（数组内数字精确相等） |

**Resolution**: 三处实现（`go/subset.go`、`wit-wpt-interop/ts/src/subset.ts`、
`wit-demo/src/lib/subset.ts`）与 README 于 2026-09-11 对齐到 CLC-v1 §6.2 (v1.1)：
数组 = 允许值集合；请求可给标量（须为成员）或数组（每元素须为成员）；
数组内数字按精确相等；标量 number 的 grant 保留上界语义。
README 顶部有对齐记录与规范指针。harness 自身场景（S1..S11）只用标量 number，
期望值不变。

## 5. 规范化输入在 map 解码后失真 → `raw_params`（2026-09-11）

**Status**: Resolved (2026-09-11)

CLC v1.1 §6.2 要求对 params 在输入边界按 JCS 规范化后再判定（拒绝重复键、
非有限/超精度数字、超 512 字节、嵌套超 32 层）。但 Go/Python 的 map 解码
必然丢失信息：重复 JSON 键只剩最后一个值，JSON 明文无法携带 `1e400` 这类
非有限数字 → 解码失败的输入在文档型向量里根本无法表达。

**Resolution**: 向量新增可选 `raw_params` 字段——以**字符串**嵌入请求 params
的原始 JSON 文本。runner 在输入边界校验之，非法即短路 `deny(<code>)`
（`invalid_params_duplicate_key` / `invalid_params_number` /
`invalid_params_size`），不再进入任何 §9.3 层比较。校验顺序固定：
大小/深度 → 重复键 → 数字形状。普通可判定的向量不设此字段。

**Vectors affected**: params-016（重复键）、params-017（`1e400`）、
params-018（600 字符串超 512B）、params-019（嵌套 33 层）。

## 6. 三语言实现（Go/Python/TypeScript）跨实现分歧（2026-09-11）

**Status**: Resolved（2026-09-11，规范文本已钉死 A–D 的取舍；corpus 仍未覆盖，
三 runner 在 76 向量 + 524 property cases 上逐字一致，TS 输出与 Python 逐字节相同）。

TypeScript 独立实现（`aic-capability-demo/ts/clc_semantics.ts`）按 spec 文本
推导时，对照 Go/Python 检出 4 处**corpus 未覆盖、三实现选择不一致**的分界点。
TS 一律服从 spec；Go/Python 的偏差均不可被现有向量观测（否则 runner 早失败）：

| # | 输入形态 | Go | Python | spec / TS | 出处 |
|---|----------|----|--------|-----------|------|
| A | grant bool 参数（§6.2 boolean = exact） | `case bool` 精确相等 ✓ | `isinstance(x,(int,float))` 把 bool 当数字 0/1 参与上界比较 ✗ | boolean 精确相等 | corpus 仅有 `undeclared-001` 里 op 侧 `extra:true`，永不进入值比较 |
| B | decide 向量 op id 为通配符形态（如 `*:query:SELECT`） | `Authorize` 把一切 id 校验错误坍缩为 `invalid_capability_id` | 传播具体码（`unsupported_wildcard`） | 传播具体码（§9.3 layer 1 三个码） | corpus decide 只测 `invalid_capability_id`（decide-004/combined-010）与 `missing_capability_id`（decide-017） |
| C | 已知约束类型集 | `{max_rows, time:window, network:cidr}` 但按 `parts[1]` 查 → 实际拒绝 `time:window:3600`/`network:cidr:...` | `{max_rows, time, network}`（按 §8.3 文法 type=第二段） | 同 Python | corpus 只测 `max_rows` 与 unknown（decide-003, payments-002） |
| D | grant 含 null 参数 且 op 无 params 字段 | `Entails` 先走 step 4 → `params_missing` | §9.3 layer 6 null 先于 layer 7 presence → `invalid_params_null` | layer 6 先 → 同 Python | corpus 无此组合 |

另有一处 spec 自身歧义（非实现分歧）：
- **§8.3 约束文法 `scheme:type[:params]` 与 §8.1 示例的 type 分段**：对
  `varwof/constraint-v1:time:window:3600`，按文法 type 是第二段 `time`，
  params 是 `window:3600`；但 §8.1 把 `time:window`、`network:cidr` 写成已知
  能力名。已知类型集应按单段 type 定义（TS/Python 现读法），spec 措辞宜改为
  “type` 为第二段 `time`（参数形式 `time:window:3600`）”并给出 auth 侧
  time/network 的求值定义（现仅 `max_rows` 有求值器，三实现一致）。

**Vectors affected**: 无（全部未覆盖）。建议日后补：bool-grant bound 向量、
decide 通配符 op id 向量、`time:window`/`network:cidr` 各一条、同时含
grant-null+op-无params 的决定性行。

**2026-09-11 规范文本钉死（draft §6.2 / §6.3 / §8.1 / §9 / §9.3，已同步
published copy，drift 0）**：

- §6.2 新增 **boolean = exact only** 段落：bool 不是数字，禁止当 1/0 参与
  op ≤ grant 上界比较（对应上表 A；Python 侧需随后来对齐）。
- §9 算法 step 1 + §9.3 notes 新增：op id 校验错误传播**具体 layer-1 码**
  （`missing_capability_id` / `unsupported_wildcard` /
  `invalid_capability_id`），不坍缩（对应上表 B；Go `Authorize` 的 collapsed
  行为需随后来对齐）。
- §8.1 重写示例为三段形式并明示 **type = 第二段**，v1 识别集 =
  `{max_rows, time, network}`，core 仅对 `max_rows` 定义求值器，
  `time`/`network` 求值属声明方 scheme（§11）（对应上表 C + 上述 §8.3 歧义；
  Go 的 `{time:window, network:cidr}` 查询与 `parts[1]` 不符，需随后来对齐）。
- §6.3 新增 **layer 6 (null) 先于 presence**：grant 含 null 参数即使 op 无
  `params` 字段也报 `invalid_params_null`（对应上表 D；Go `Entails` 的
  step-4-first 行为需随后来对齐）。
- §6.2 step 4 点明 512 字节 = 规范 UTF-8 形式的 octets（对应 TS/Python 的
  字符串计数口径）。

**第二批（2026-09-11 继续补，body 引用缺口，非实现分歧；行为本就三实现一致
并被 corpus 钉死）**：

- **§9.4 缺两条 reason code**：`missing_capability_id`（layer 1，D16/decide-017）
  和 `absent_source`（intersect 零 source，intersect-007）之前只出现在正文
  引用与 vectors 里、不在规范 reason 表 → 已补两行；§9.3 layer 10 的 codes
  单元格加入 `absent_source`。
- **§7 只有 rules 1–4，但正文/附录引用 rule 5–6**（B.4 I7/I8/I9、corpus
  脚注 intersect-007..010）→ 已补 rule 5（零/缺席 source → fail-closed
  `absent_source`；存在但无 grant 属 rule 4）、rule 6（空 `params` 不声明
  约束、保留下界、source 顺序无关）；并新增 rule 2 注解：**标识符比较 params-free**
  —— 取最窄 id，不得经 `Entails`（会让 bounded grant 对 params-less 兄弟
  误入 presence 判 /**§6.3 step 4**，即 intersect-010 修复点）。
- **§6.2 step 4 深度口径未写**：corpus params-021 钉死“外对象为 level 1、
  对象与数组都计数、31 层嵌套数组 = depth 32”→ 已写入规范正文。
- **§8.1 merge 规则里的 denylist 无定义**：v1 core 无比对物 → 补一句“v1 core
  无 denylist 约束，`denylist → union` 仅限 scheme 自定义类型（§11）”。

**第三批（2026-09-11 继续补，spec 自身缺口/未钉行为，行为三实现一致）**：

- **§7 缺少 P11 meet 律**：property-cases.json `_meta`（524 cases）钉的
  “result ⊆ 每个 source、source 顺序无关、失败给规范性 reason code 且不
  raise”此前只在 corpus 里、§7 无文 → 新增 “Property: composition narrows
  only” 段落并指向 property-cases.json。
- **§12 Conformance 未提机器可读 corpus**：vectors.json(76)/property-cases.json(524)
  /vectors.schema.json / offline-vectors.json 都没在规范里出现 → 补
  “Conformance corpora” 段，明确二者对 CLC-A 为规范测试集。
- **§3 通配符 vs 文法优先级未写**：S3–S6 只钉“禁形→unsupported_wildcard”，
  未钉“同串既违禁用通配符又违基础文法时先报 unsupported_wildcard”
  （三实现 validateCapabilityId 均先查 wildcard shape 再查 grammar）→ 补
  “Wildcard detection precedes grammar conformance” 段。
- **§9.3 未钉 layer 1 只验 operation id**：grant 侧 malformed id 的路径
  （Entails 报该具体码、Authorize 折叠为 capability_not_authorized，三实现一致、
  corpus 未覆盖）→ 补 “Layer 1 validates the operation id only” note。

**第四批（2026-09-11，新检出“仅记录、不改规范文本”的未覆盖分歧）**：

- **multi-fault 输入下 §6.2 规范化检查顺序**。§6.2 item 5 定序
  size/depth → duplicate keys → number shape。核对实现：
  - Go `ValidateRawParams`：walk 中 depth 越界即返 `invalid_params_size`；
    size（重序列化 buf 长）在 walk 结束后、dup/number 之前判 → 顺序 ✓。
  - Python `validate_raw_params`：预扫描 size+depth → 先判；再 parse 收集
    dup/number → dup 先于 number ✓。
  - TS `validateRawParams`：单趟扫描，dup key（`invalid_params_duplicate_key`）
    与 number shape（`checkParamsNumber`）在 parse 过程中即时抛，size 在
    parse 结束后（`compact > MAX` 在 line 362）才判 → 对“既超限又含 dup /
    既超限又含 bad number”的输入，dup/number 先于 size，与 §6.2 item 5 相反
    （TS 自身 docstring 声称遵循 §6.2 order，实为对多故障输入不符）。
- corpus 的 params-016..021 全部为单故障，不覆盖此组合 → 三 runner 仍绿，
     非一致性缺口。
  - **已解决（同日）**：补 `params-025`（超限+dup → `invalid_params_size`）、
     `params-026`（超限+bad-number → `invalid_params_size`）、`params-027`
     （dup+bad-number、未超限 → `invalid_params_duplicate_key`）；TS
     `validateRawParams` 改为两趟（先 size/depth，再 dup/number）。§6.2
     item 5 顺序与实现和向量一致。
  - 建议后续：补 combined-fault 向量（超限+dup、超限+bad-number）并把 TS
     改为先判 size（预扫描或延迟 dup/number raise）。规范 item 5 保持为目标。

## 7. CLC-1.2 落地清扫收口（2026-09-12）

**Status**: Resolved（2026-09-12；上表 A–D 全部由新增 spec 文本 + corpus
95 向量 + 1184 property cases 钉死，三实现 95/95、1184/1184）。

- **A（bool-grant bound）**：`params-022/023` + property 墙新增
  `flags: admin true vs 1` 形态 → Python 布尔分支前置已修，三实现一致；§6.2
  boolean-exact 段有向量背书。
- **B（op id 具体 layer-1 码）**：`decide-018`（通配符形状 op id →
  `unsupported_wildcard`）已入语料；corpus 现覆盖具体码传播。另钉两条新侧面：
  `decide-025`（op scheme `bad` → `invalid_capability_id`）与 `decide-026`
  （**grant 侧** malformed id → Entails 报具体码、Authorize 折叠为
  `capability_not_authorized`——grant 侧折叠是规范行为，不加向量则无歧义）。
- **C（已知约束集 + §8.1/§8.3 分段歧义）**：Go `knownConstraintTypes` 收紧为
  `{max_rows, time, network}`（按 `parts[1]`），与 Python/TS 同一集合（TS 那条
  指 Go 分歧的 NOTE 已删）；spec rev CLC-1.2 明示 type = 第二段、值 = `parts[2:]`
  join 还原；`intersect-005` 修正为数组形态。`decide-021`（标量 3600 →
  `invalid_constraint`）、`decide-022`（无掩码 CIDR → `invalid_constraint`）、
  `decide-023`（max_rows op 缺席 → `max_rows:violated`）、`decide-027`（at-bound
  allow）把值文法与 op 缺席路径逐条钉死。
- **D（null 先于 presence）**：`params-024` 入语料（layer 6 先 → 
  `invalid_params_null`）；Go `Authorize` 已传播具体码。
- **新增通道 §8.4 `unresolved`**：认识但 core 不判的约束（time/network）→
  `allow` + `unresolved:[...]`。`decide-019/020/024`（单窗口、cidr 数组、
  双窗口含跨午夜）钉死；消费方须自行求值否则 deny。
- **§3 scheme 文法**：`syntax-007/008`（`database:query`、`bad:op` →
  `invalid_capability_id`）、`syntax-009`（`std/data-v1:fetch:item:42` 正例）注入。
- **P11 dict 键集规则**：property 墙 prop-0956 抓出对象值交集**加了宽**（键集
  差异下共享键结果既不 ⊆ A 也不 ⊆ B）→ §7 补“dict 交集要求两源键集完全一致，
  否则 `no_overlap`”；三实现同日修（Go property_test 白名单羁押的
  `invalid_constraint` 后同步加入）。property 墙 524 → **1184** 例（PARAMS 扩至
  14 形状含嵌套 profile/filters/flags）。
- **计数收口**：语料 83 → **95**（syntax 9 / entail 37 / intersect 14 /
  decide 35）；附录 B、design-notes、principles 全部对齐；py/ts runner 输出
  逐字节一致。

## 8. CLC-1.3 落地收口：verdict 独立通道 / 约束身份 / §9.3 多 grant（2026-09-12）

**Status**: Resolved（2026-09-12；spec rev CLC-1.3 + corpus 98 向量 + 1184
property cases，三实现 98/98、1184/1184、py/ts runner 逐字节一致）。

- **A（`verbatim` 废弃）**：早先保留在结果的 `verbatim` 字段从三实现移除；
  §8.4 唯一残差通道是 `verdict=allow_unresolved` + `unresolved:[约束]`，
  不再有“伪 allow”叙事。spec rev CLC-1.3 新增独立 verdict 值。
- **B（约束身份按 (scheme,type) 识别）**：core 认识集从“type 名”收紧为
  全量 `scheme:type` 对，仅 `varwof/constraint-v1` 声明 core 认识类型；
  `foo/db-v1:max_rows` 这类异 scheme 同名约束 → `unknown_constraint` 而非
  按 type 放行。三实现同步收紧；`decide-017`（异 scheme）不变，
  go/py/ts 各加防御性身份门并共享「unrecognized identity first」顺序。
- **C（时间窗口值文法）**：单段不得跨午夜（`22:00→06:00` 单个 window 段 →
  `invalid_constraint`，必须拆段）；保留 end `"00:00"` = 次日零点（`22:00→00:00`
  视作同日 `[22:00,24:00)`），全长段 `00:00→00:00` 非法；段列按 (start,end)
  升序且两两不重叠（相接允许）。`decide-019` 改为非法段，`decide-024` 改为
  split-form 双段（`00:00→06:00` + `22:00→00:00`）。
- **D（grant params `{}` ≡ absent ≡ 无约束）**：空 params 对象不再触发 key
  closure，op 可带任意 params → allow；附独立向量 `decide-028`。property
  墙 closure 探针在空 params 合并结果上跳过（841 探针，此前 860）。
- **E（§9.3 多 grant 聚合）**：新增 `AuthorizeSet(grants, op)`——任一
  覆盖且放行的 grant 即放行（并集）；`unresolved` 跨全部覆盖且放行的
  grant 取并集；全部拒绝时取**首个覆盖 grant**（参数/约束层）的 reason 于
  规范（输入）序。corpus 增 `decide-029`（G1:10/G2:100, op:50 → allow）与
  `decide-030`（G1:10/G2:6, op:50 → `params_exceed_grant`）；schema 增
  `"multi": true` 开关。
- **计数收口**：decide 35 → **38**、语料 95 → **98**；schema verdict enum
  增 `allow_unresolved`，附 `multi` 布尔位；附录 D/D17/D22、parity report
  同步 CLC-1.3。
