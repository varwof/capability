# varwof-capability

> JSON 能力声明数据集 —— varwof 零信任网关的能力定义标准

[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

> ⚠️ **预览版** — 不可用于生产环境。API 和功能可能在正式发布前发生变更。

[English](README.md)

## 什么是 varwof-capability？

为 varwof 零信任网关提供 JSON 格式的能力定义数据：`std` 与 `varwof` 命名空间，以及 `x-vendor`（私有扩展）。第三方厂商命名空间由各所有者自行贡献，本仓不代为发布。被 `register` 模块加载用于 PKCS#7 签名验证和权限校验。

## 快速开始

```bash
export CAPABILITY_DIR=/path/to/capability/data
ls data/
# std/database-v1/v1.json
# varwof/core/v1.json
# varwof/gateway/v1.json
# varwof/constraint/v1.json
# std/database-v1/v1.json
# x-vendor/acme-v1/v1.json
```

## 数据结构

```
data/
├── std/database-v1/v1.json         — 标准数据库能力 schema
├── varwof/core/v1.json             — 核心权限（37 能力 + 10 角色）
├── varwof/gateway/v1.json          — 网关权限（21 能力 + 5 角色）
├── varwof/constraint/v1.json       — 执行约束能力
├── std/database-v1/v1.json         — 数据库操作权限（含 params_schema）
└── x-vendor/acme-v1/v1.json           — 私有扩展示例
```

capability 是 varwof 生态的**能力数据层**。本项目是 [Open Invention Network](https://openinventionnetwork.com/) 成员。

## CLC-v1 一致性向量与 scheme

本仓同时承载 **CLC-v1**（极小能力判定语言）的机器可读部分：

- `data/_vectors/clc-v1/` —— **105 条一致性向量**（syntax 9 / entail 37 / intersect 14 / decide 38）、
  `vectors.schema.json`、`clc-v1-ambiguities.md`（裁决记录）、**1184 条 P11 属性用例**
  （`property-cases.json`，由 `scripts/gen-property-cases.py` 确定性生成）与
  **12 条 OCMP 离线用例**（`offline-vectors.json`）。消费方实现：
  `varwof/register`（Go）、`varwof/aic-capability-demo`（Python）与其 `ts/`（TypeScript，仅 Node、零依赖），
  三方断言 **verdict、规范码 reason 与交集结果（`result_params` / `result_constraints`）**，
  并覆盖 CLC-1.3 的 `allow_unresolved` 独立 verdict 与 §9.3 多 grant 聚合；
  属性测试（收窄性 + 顺序无关）与 offline 用例的覆盖/词表门禁均由 `scripts/` 校验并进 CI。
- `data/std/robot-line-v1/v1.json` —— 工业机器人产线能力（10 项）；工位等分类值按
  CLC-v1 的枚举规则用数组表示（`"station": [1,2,3]`）。
- 本仓内的规范文档：`docs/capability-language-core-v1.md`（规范正文）、
  `docs/capability-language-core-principles-v1.md`（设计原则声明）、
  `docs/offline-capability-manifest-profile-v0.md`（离线 profile）、
  `docs/design-notes.md`（英文裁决记录）、`docs/capability-language-core-design-notes-zh.md`（完整中文设计说明）。

一句话设计原则：**极小的判定语言**——有限的值、三条关系（蕴含/匹配/交集）、两个判定函数、
**没有控制流**、缺省即拒绝（fail-closed）、**未声明的参数不构成授予**。

原则声明（rev 2）共 P1–P12，另有四条"可被跑"的性质：**本地可判**（核心规则不得联网）、
**有界工作量**（参数 ≤512 字节、嵌套 ≤32 层，超限即拒）、**组合只收窄**（交集必须被每个源覆盖且与顺序无关）、
**一致即门槛**（≥2 个独立实现 verdict 与规范码一致才算完成）。每条原则绑定规范条文 + 向量/测试，
台账与已记录的缺口见 `docs/capability-language-core-principles-v1.md` §7–§9。

## 链接

| | |
|---|---|
| 主页 | https://varwof.com |
| 社区 | https://varwof.org |
| IETF 草案 | [draft-wei-aic-identity-cert](https://datatracker.ietf.org/doc/draft-wei-aic-identity-cert/) |
| 许可证 | Apache-2.0 |
| 成员 | [Open Invention Network](https://openinventionnetwork.com/) |
