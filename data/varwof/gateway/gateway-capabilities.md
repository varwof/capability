# Varwof Gateway 权限说明

> scheme_id: `varwof/gateway` · 版本 `1.1.0` · 厂商 `varwof` / 产品 `gateway`

Varwof 网关操作权限（管理 API + 数据面）

完整能力标识格式：`varwof/gateway:capability_id`（如 `varwof/gateway:cert:issue`）。

## 能力目录

| 能力 | 摘要 | 相关能力 |
|------|------|----------|
| `admin:agents` | Agent 目录与踢线管理 | admin:connections |
| `admin:branch` | 策略分支控制（灰度发布） | admin:policy |
| `admin:config` | 读取/修改网关配置 | admin:reload |
| `admin:connections` | 实时连接/接入点查看 | ops:metrics |
| `admin:plugins` | 管理能力插件（注册/替换/删除） | ops:plugins |
| `admin:policy` | 策略版本化与回滚 | admin:branch |
| `admin:reload` | 热重载配置 | admin:config |
| `admin:renewal` | 确认续签管理（request/confirm/reject） | admin:agents |
| `audit:chain` | 跨网关审计链 DAG 引用 | audit:read |
| `audit:read` | 读取审计日志 | audit:verify, audit:search |
| `audit:search` | 审计全文检索 | audit:read |
| `audit:verify` | 验证审计链/Merkle 完整性 | audit:read |
| `ops:health` | 健康检查 | ops:metrics |
| `ops:metrics` | 读取 Prometheus 指标 | ops:health |
| `ops:plugins` | 查看能力插件列表 | admin:plugins |
| `proxy:grpc` | gRPC 代理数据面 | proxy:http |
| `proxy:http` | HTTP/HTTPS 反向代理数据面 | proxy:websocket, proxy:grpc |
| `proxy:quic` | QUIC/HTTP3 代理数据面 | proxy:udp, proxy:http |
| `proxy:tcp` | TCP 透明代理数据面 | proxy:http |
| `proxy:udp` | UDP 转发数据面 | proxy:quic |
| `proxy:websocket` | WebSocket 代理数据面 | proxy:http |

## 能力详细语义

> 阅读指引：本节的 `usage`/`when_not`/`examples` 用于判断**何时需要该能力、何时不应授予**。AI 生成最小权限集合时以此为依据。

### `admin:agents`

**摘要**：Agent 目录与踢线管理

**说明**：Agent 目录与踢线管理

**何时需要**：需要查看在线 Agent、主动断开异常 Agent 时使用。

**何时不应授予**：Agent 自身任务不需要管理其他 Agent。

**示例**：

- 踢掉异常 Agent 连接

**相关能力**：`admin:connections`

---

### `admin:branch`

**摘要**：策略分支控制（灰度发布）

**说明**：策略分支控制（灰度发布）

**何时需要**：需要按 Agent 分组灰度下发不同策略版本时使用。

**何时不应授予**：全局统一策略不需要。

**示例**：

- 对指定 Agent 灰度新策略

**相关能力**：`admin:policy`

---

### `admin:config`

**摘要**：读取/修改网关配置

**说明**：读取/修改网关配置

**何时需要**：需要调整网关监听器、路由、上游配置时使用。

**何时不应授予**：常规数据面任务严禁授权；仅运维管理员需要。

**示例**：

- 修改路由映射

**参数**：

| 参数 | 类型 | 默认值 | 约束 | 说明 |
|------|------|--------|------|------|
| `config_key` | `string` |  |  | 允许访问的配置键（空 = 全部） |

**相关能力**：`admin:reload`

---

### `admin:connections`

**摘要**：实时连接/接入点查看

**说明**：实时连接/接入点查看

**何时需要**：需要监控当前活跃连接、查看接入点时使用。只读。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 查看当前连接数

**相关能力**：`ops:metrics`

---

### `admin:plugins`

**摘要**：管理能力插件（注册/替换/删除）

**说明**：管理能力插件（注册/替换/删除）

**何时需要**：需要动态调整能力判定插件（allowlist/denylist/rbac）时使用。

**何时不应授予**：纯数据面任务不需要。

**示例**：

- 替换 RBAC 插件

**相关能力**：`ops:plugins`

---

### `admin:policy`

**摘要**：策略版本化与回滚

**说明**：策略版本化与回滚

**何时需要**：需要管理授权策略版本、执行回滚时使用。

**何时不应授予**：只读策略查看用 ops:plugins 即可。

**示例**：

- 回滚到上一策略版本

**相关能力**：`admin:branch`

---

### `admin:reload`

**摘要**：热重载配置

**说明**：热重载配置

**何时需要**：配置变更后需要无中断热加载时使用。

**何时不应授予**：无配置变更任务不需要。

**示例**：

- SIGHUP 触发配置重载

**相关能力**：`admin:config`

---

### `admin:renewal`

**摘要**：确认续签管理（request/confirm/reject）

**说明**：确认续签管理（request/confirm/reject）

**何时需要**：需要管理短命证书的确认续签流程时使用。

**何时不应授予**：无短命证书场景不需要。

**示例**：

- 确认 Agent 证书续签

**相关能力**：`admin:agents`

---

### `audit:chain`

**摘要**：跨网关审计链 DAG 引用

**说明**：跨网关审计链 DAG 引用

**何时需要**：需要查看多网关审计链引用关系时使用。只读。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 查看跨网关审计链

**相关能力**：`audit:read`

---

### `audit:read`

**摘要**：读取审计日志

**说明**：读取审计日志

**何时需要**：需要查看网关访问/连接审计记录时使用。只读。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 查看连接审计

**相关能力**：`audit:verify`, `audit:search`

---

### `audit:search`

**摘要**：审计全文检索

**说明**：审计全文检索

**何时需要**：需要按关键字/时间段检索审计记录时使用。只读。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 搜索某 Agent 的审计记录

**相关能力**：`audit:read`

---

### `audit:verify`

**摘要**：验证审计链/Merkle 完整性

**说明**：验证审计链/Merkle

**何时需要**：需要验证审计日志哈希链完整性（防篡改）时使用。只读。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 校验审计链

**相关能力**：`audit:read`

---

### `ops:health`

**摘要**：健康检查

**说明**：健康检查

**何时需要**：需要探测网关存活状态时使用。公开能力。

**何时不应授予**：无限制，通常公开。

**示例**：

- 负载均衡健康检查

**相关能力**：`ops:metrics`

---

### `ops:metrics`

**摘要**：读取 Prometheus 指标

**说明**：读取 Prometheus 指标

**何时需要**：需要拉取网关监控指标（连接数/PPS/延迟）时使用。只读。

**何时不应授予**：无特殊限制，只读。

**示例**：

- Prometheus 抓取指标

**相关能力**：`ops:health`

---

### `ops:plugins`

**摘要**：查看能力插件列表

**说明**：查看能力插件列表

**何时需要**：需要查看当前加载的插件、其方案定义时使用。只读。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 查看已注册插件

**相关能力**：`admin:plugins`

---

### `proxy:grpc`

**摘要**：gRPC 代理数据面

**说明**：gRPC 代理数据面

**何时需要**：需要代理 gRPC 双向流服务时使用。

**何时不应授予**：REST/HTTP 服务不需要。

**示例**：

- 代理 gRPC 微服务

**相关能力**：`proxy:http`

---

### `proxy:http`

**摘要**：HTTP/HTTPS 反向代理数据面

**说明**：HTTP/HTTPS 反向代理数据面

**何时需要**：需要经网关访问 HTTP/HTTPS 后端服务（Web 应用、REST API）时使用。最常见的数据面能力。

**何时不应授予**：TCP/UDP 专有协议服务不需要；纯管理操作不需要。

**示例**：

- 经网关访问内网 Web 服务
- 调用后端 REST API

**相关能力**：`proxy:websocket`, `proxy:grpc`

---

### `proxy:quic`

**摘要**：QUIC/HTTP3 代理数据面

**说明**：QUIC/HTTP3 代理数据面

**何时需要**：需要支持 QUIC/HTTP3 客户端访问时使用。

**何时不应授予**：传统 TCP 客户端不需要。

**示例**：

- 支持 HTTP3 的 Web 服务

**相关能力**：`proxy:udp`, `proxy:http`

---

### `proxy:tcp`

**摘要**：TCP 透明代理数据面

**说明**：TCP 透明代理数据面

**何时需要**：需要转发任意 TCP 协议（SSH、数据库、自定义协议）时使用。

**何时不应授予**：HTTP 服务用 proxy:http 即可。

**示例**：

- 经网关访问 SSH 服务
- 转发 MySQL 连接

**相关能力**：`proxy:http`

---

### `proxy:udp`

**摘要**：UDP 转发数据面

**说明**：UDP 转发数据面

**何时需要**：需要转发 UDP 流量（DNS、音视频、游戏）时使用。

**何时不应授予**：TCP/HTTP 服务不需要。

**示例**：

- 经网关转发 DNS 查询

**相关能力**：`proxy:quic`

---

### `proxy:websocket`

**摘要**：WebSocket 代理数据面

**说明**：WebSocket 代理数据面

**何时需要**：需要代理 WebSocket 长连接（实时推送、聊天）时使用。

**何时不应授予**：普通 HTTP 请求不需要。

**示例**：

- 代理实时消息推送服务

**相关能力**：`proxy:http`

---

## 通配符与匹配规则

grant/能力匹配支持 glob 通配，用于角色授权与最小权限校验：

| 模式 | 含义 | 示例 |
|------|------|------|
| `capability_id` | 精确匹配 | `cert:issue` |
| `domain:*` | 前缀通配（该域下全部动作） | `ca:*` 匹配 `ca:list`、`ca:create` |
| `*` / `**` | 全量通配（所有能力） | 危险，尽量避免 |
| `?` | 单字符通配 | 少用 |

**最小权限原则**：角色 grants 与 AI 生成的能力集应尽量使用**精确能力**，仅在确实需要整个域时使用 `domain:*`。

## 角色与授权映射

### 角色 `agent`

**名称**：AI Agent（数据面）

**Profiles**：`agent-proxy`

**授权能力（grants）**：

- `proxy:*`

### 角色 `gateway:admin`

**名称**：网关管理员

**Profiles**：`m-admin`

**可绑定 OU**：`gateway:admin`

**授权能力（grants）**：

- `proxy:*`
- `admin:config`
- `admin:reload`
- `admin:plugins`
- `admin:policy`
- `admin:branch`
- `admin:renewal`
- `admin:agents`
- `admin:connections`
- `ops:metrics`
- `ops:plugins`
- `ops:health`
- `audit:read`
- `audit:verify`
- `audit:search`
- `audit:chain`

### 角色 `gateway:audit`

**名称**：网关审计

**Profiles**：`m-auditor`

**可绑定 OU**：`gateway:audit`

**授权能力（grants）**：

- `audit:read`
- `audit:verify`
- `audit:search`
- `audit:chain`
- `ops:health`

### 角色 `gateway:ops`

**名称**：网关运维

**Profiles**：`m-operator`

**可绑定 OU**：`gateway:ops`

**授权能力（grants）**：

- `proxy:*`
- `admin:reload`
- `admin:renewal`
- `admin:connections`
- `ops:metrics`
- `ops:plugins`
- `ops:health`

### 角色 `gateway:read`

**名称**：网关只读

**Profiles**：`m-readonly`

**可绑定 OU**：`gateway:read`

**授权能力（grants）**：

- `ops:metrics`
- `ops:health`

## 最小权限生成指南（AI/开发者）

为任务生成能力集合时遵循：

1. **只授予任务必需能力**：对照各能力 `usage`（何时需要）判断，`when_not` 明确说明的不授予。
2. **精确优先**：能精确到 `capability_id` 就不用通配；能用单个能力就不用域通配 `domain:*`。
3. **参数收窄**：有 `parameters` 的能力，按任务实际需要设置默认值/范围，宁可窄勿宽。
4. **只读优先**：只读能力（`*:list`、`*:read`、`*:view`）优先于写能力。
5. **禁用危险能力**：`key:recover`、`ca:delete`、`config:write` 等敏感能力默认不授予，除非任务明确需要。
6. **去除冗余**：已由通配覆盖的精确能力可省略；与任务无关的能力全部删除。

