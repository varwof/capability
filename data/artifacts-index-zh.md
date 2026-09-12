# capability/data 制品清单（artifacts index）

日期：2026-09-11　维护：closeout P8 审计

## 结构

```
data/
├── std/          # 标准 scheme（规范级，可被各方引用）
│   ├── database-v1/  robot-line-v1/  deploy-v1/
│   ├── mcp-v1/       wallet-v1/
├── varwof/       # varwof 自营 scheme（前缀 varwof/）
│   ├── core-v1/  gateway-v1/  llm-v1/  constraint-v1/
│   └── demo-mysql-v1/
├── x-vendor/     # 示例/演示 vendor 目录
│   └── acme-v1/
└── _vectors/clc-v1/   # CLC-v1 一致性向量 + 离线向量（见其 README）
```

## 已登记 scheme（12 份 `v1.json`）

| 目录 | scheme_id | 用途 |
|---|---|---|
| `std/database-v1` | std/database-v1 | 查询/写库授权（向量主力 scheme） |
| `std/robot-line-v1` | std/robot-line-v1 | 机器人产线（OCMP 离线场景参考，§6 工业映射） |
| `std/deploy-v1` | std/deploy-v1 | 部署动作 |
| `std/mcp-v1` | std/mcp-v1 | MCP tool 能力桥 |
| `std/wallet-v1` | std/wallet-v1 | 钱包/密钥能力 |
| `varwof/core-v1` | varwof/core-v1 | varwof 核心能力 |
| `varwof/gateway-v1` | varwof/gateway-v1 | 网关决策 |
| `varwof/llm-v1` | varwof/llm-v1 | LLM 能力 |
| `varwof/constraint-v1` | varwof/constraint-v1 | 约束命名空间 |
| `varwof/demo-mysql-v1` | varwof/demo-mysql-v1 | 演示 MySQL 场景 |
| `x-vendor/acme-v1` | x-vendor/acme-v1 | 示例 vendor |

## 审计结论（2026-09-11，P8）

问题：数值参数是**上界语义还是数组成员（enum）语义**直接决定 §6.2 的表意
——若 scheme 里声明了数字数组而文档没写清，实现会按 enum 误读。

审计范围：全部 12 份 `v1.json` 的 params 声明，扫描 `type: number` 的
数组形态参数。

**结论：仅 `std/robot-line-v1/v1.json` 声明数字数组**（参数 `station`，
[1,2,3] 形式）。这是**有意为之**，与 CLC v1.1 §6.2 enum 语义对齐：station
是分类参数（站号集合），按允许值集合处理，绝不按"上界"放大（grant
`{"station":[3]}` 不覆盖站 2）。其余 11 份 scheme 无数字数组参数，
无 enum/上界歧义。

衍生维护注意：新增 scheme 若含 `number` 数组 params，必须按 §6.2 声明为
分类/集合语义（或改挂 `enum` 词表），并在本节登记。