# contrib/ — 贡献的实验与证据（**非规范**）

本目录放**对本仓 CLC 语料/语义有直接关系的、由外部讨论或第三方问题触发的
可运行探针**。它们**不是** `data/` 的一部分，**不改变任何规范结论**，
也不参与 `data/` 的 schema 校验；它们的门是
`.github/workflows/clc-vectors.yml` 末尾的"两实现一致性"一步。

## In English

Everything in `contrib/` is informational or experimental. Nothing here is
normative, nothing here is cited as conformance evidence, and a passing probe is
not a claim: claims are made against `data/_vectors/` and recorded in
`conformance/registry.md`. A change confined to `contrib/` merges on CI alone
(`GOVERNANCE.md`, "Non-normative work in `contrib/`"). Promotion out of `contrib/`
into a vector, a registered binding (`BINDINGS.md`) or normative text is a normal
or core change, reviewed as one.

## 状态（audit C-6）

本目录内的一切均为 **informative / experimental**：可运行、可复核，但不构成
规范性要求。规范文本只在 `docs/capability-language-core-v1.md`；语料与
声明 schema 在 `data/_vectors/clc-v1/`。下表只说明各探针的性质，避免把实验
结论误读为强制语义。

| 目录 | 性质 | 说明 |
|---|---|---|
| `clc-unit-encoding/` | experimental | 单位编码的两种写法对比 |
| `iicp-touchpoint/` | experimental | 固定 grant/operation 对与 12 条不利用例 |
| `iicp-evaluator-binding-v0/` | experimental | 外部授权求值器绑定草案：result schema + 11 cases |
| `emilia-projection/` | informative | AEC requirement → CLC 的投影探针 |
| `gilda-projection/` | informative | 审计记录 → CLC 结果的投影探针 |
| `oasnt-projection/` | informative | 批准令牌 → Fact + 身份的投影探针 |
| `asor-authorization-projection/` | informative | ASOR 链 → Grants 的投影探针 |
| `rar-authorization-projection/` | informative | RAR details → Grants 的投影探针 |
| `quantity-domain/` | informative | CLC-1.19 `quantity` 的三语言试点输出 |

## 内容

### `clc-unit-encoding/`

CLC 里如何表达**带单位的量**。结论：语言层不需要新类型——

- 方案一（本仓已发布 scheme 的做法，见 `data/std/payments-v1/v1.json`）：
  `currency` 作为独立枚举参数（大写 ISO 码）与裸数值 `amount` 并列；
- 方案二（本探针演示）：把量建模成对象 `{"value": 50, "unit": "CNY"}`，
  由 §6.2 的 object 递归逐键比较（值走 number 上界、单位走 string 精确）。

两者都**不换算**：跨单位即不成立（fail-closed）。相关缺口与对照见
`README.md` 的 changelog 与 `docs/`。

### `iicp-touchpoint/`

把 CLC 用在**外部架构**的"选择→准入"边界上：一个固定的
`grant`/`operation` 对（取自本仓 `std/payments-v1` 的 `transfer`），
四个 adverse case（widened destination / unit ambiguity / unknown required
constraint / retry to another provider），以及"containment 之后仍未决"
（`allow_unresolved`）。它是对 IICP 架构文档 v0.3.1 §12.3 所留
review touchpoint 的可运行回答；**不代表对任何外部规范的采纳或互操作声明**。

### `iicp-evaluator-binding-v0/`

IICP 管理控制器的**外部授权求值器绑定**草案：一个可选、非激活的 result
schema，加上 11 条 positive/negative cases 和一个本地校验器。它不改
`management-profile-v1`，也不动 IICP 的 qualification baseline；讨论入口是
[`RobLe3/iicp-management#168`](https://github.com/RobLe3/iicp-management/issues/168)。

运行：

```bash
cd contrib/iicp-evaluator-binding-v0
python3 validate.py     # 11/11 cases pass
```

这是对本仓之外的 contract 的提案，**不是** CLC 规范的一部分，也不构成对
IICP 的采纳或互操作声明。

## 复现

探针的实现路径可用环境变量指到任一符合本规范的实现：

```bash
# 指向 varwof/aic-capability-demo 的 Python 与 TypeScript 端口
export CLC_PY_DIR=/path/to/aic-capability-demo
export CLC_TS_FILE=file:///path/to/aic-capability-demo/ts/clc_semantics.ts

for d in contrib/clc-unit-encoding contrib/iicp-touchpoint; do
  python3 "$d/probe.py"            > /tmp/py.txt
  node --disable-warning=ExperimentalWarning --experimental-strip-types \
       "$d/probe.mjs"              > /tmp/ts.txt
  cmp /tmp/py.txt /tmp/ts.txt      # 两实现必须逐字节一致
done
```

`out-python.txt` / `out-typescript.txt` 是**提交时的记录**（同一 sha256），
由当时的实现产生；CI 的门是**两实现一致**，不是与这两个文件逐字节比
（实现升版时打印的 `CLC_REVISION` 行会变）。

## 版本说明（重要）

- 本仓规范正文 `docs/capability-language-core-v1.md` 当前声明 **CLC-1.19**；
  语料与三个实现（`register` 的 Go、`aic-capability-demo` 的 Python/TypeScript）
  在同一版本上。
- **已发布 Internet-Draft `draft-wei-capability-language-core-00` 为 CLC-1.15**——
  落后四版（1.16–1.19），其中 **CLC-1.16 起含裁决变更**（I-JSON 整数上界、前导 BOM 拒绝、
  宿主数值载体归一化、§13.4.3 params 收窄决策表）。差异逐条列在规范正文的
  changelog 表里。**引用本仓行为时请以仓库版本为准并注明。**

## 不在本目录的内容（有意的）

ASOR 的向量与交付物**不在此处**，因为它们是 **ASOR 的**向量，不是 CLC 的：

- 正式向量集在 ASOR 上游仓库 `attenu-io/attenu-guard`：
  `src/attenu_guard/vectors/draft02/reject_reissued_parent.json` 与 `tests/vectors-02/`；
- 我方 2026-10-07 的交付留档在站点 `https://www.varwof.com/downloads/asor/2026-10-07/`；
- 对应致谢见 `draft-asor-wimse-agent-delegation-chain-02` Appendix A（"Jijie Wei"）。

在本仓放副本会造成**两处 source of truth**，故只留指针。
