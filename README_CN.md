# varwof-capability

> JSON 能力声明数据集 —— varwof 零信任网关的能力定义标准

[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

> ⚠️ **预览版** — 不可用于生产环境。API 和功能可能在正式发布前发生变更。

[English](README.md)

## 什么是 varwof-capability？

为 varwof 零信任网关提供 JSON 格式的能力定义数据：`std`、`varwof`、`oracle` 和 `x-vendor` 命名空间。被 `register` 模块加载用于 PKCS#7 签名验证和权限校验。

## 快速开始

```bash
export CAPABILITY_DIR=/path/to/capability/data
ls data/
# std/database-v1/v1.json
# varwof/core/v1.json
# varwof/gateway/v1.json
# varwof/constraint/v1.json
# oracle/mysql/v1.json
# x-vendor/acme/v1.json
```

## 数据结构

```
data/
├── std/database-v1/v1.json         — 标准数据库能力 schema
├── varwof/core/v1.json             — 核心权限（37 能力 + 10 角色）
├── varwof/gateway/v1.json          — 网关权限（21 能力 + 5 角色）
├── varwof/constraint/v1.json       — 执行约束能力
├── oracle/mysql/v1.json            — MySQL 操作权限
└── x-vendor/acme/v1.json           — 私有扩展示例
```

capability 是 varwof 生态的**能力数据层**。本项目是 [Open Invention Network](https://openinventionnetwork.com/) 成员。

## 链接

| | |
|---|---|
| 主页 | https://varwof.com |
| 社区 | https://varwof.org |
| IETF 草案 | [draft-wei-aic-identity-cert](https://datatracker.ietf.org/doc/draft-wei-aic-identity-cert/) |
| 许可证 | Apache-2.0 |
| 成员 | [Open Invention Network](https://openinventionnetwork.com/) |
