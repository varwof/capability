# Varwof PKI Core 权限说明

> scheme_id: `varwof/core` · 版本 `1.1.0` · 厂商 `varwof` / 产品 `core`

Varwof PKI 核心引擎操作权限

完整能力标识格式：`varwof/core:capability_id`（如 `varwof/core:cert:issue`）。

## 能力目录

| 能力 | 摘要 | 相关能力 |
|------|------|----------|
| `agent:manage` | 管理 AI Agent（注册/踢线/配置） | cert:issue |
| `ca:create` | 创建新的证书颁发机构（CA） | ca:list, ca:info, ca:issue-sub |
| `ca:delete` | 删除已存在的证书颁发机构 | ca:create |
| `ca:info` | 查看单个 CA 的详细信息 | ca:list |
| `ca:issue-sub` | 签发子 CA 证书（层级扩展） | ca:create, cert:issue |
| `ca:list` | 列出所有 CA | ca:info |
| `cert:batch` | 批量签发多张证书 | cert:issue |
| `cert:export` | 导出证书（PEM/DER 格式） | cert:list |
| `cert:issue` | 签发终端实体证书 | cert:renew, cert:revoke, cert:list |
| `cert:list` | 查询证书列表（可按 CA/状态/主体筛选） | ca:list, cert:info |
| `cert:renew` | 续期已有证书 | cert:issue, cert:revoke |
| `cert:revoke` | 吊销已签发的证书 | cert:issue, cert:list |
| `config:read` | 读取系统配置 | config:write |
| `config:write` | 修改系统配置 | config:read |
| `crl:generate` | 生成证书吊销列表（CRL） | cert:revoke, crl:read |
| `crl:read` | 读取 CRL 内容 | crl:generate, cert:list |
| `cross-cert:issue` | 签发交叉证书（跨信任域桥接） | ca:issue-sub |
| `cross-cert:revoke` | 吊销交叉证书 | cross-cert:issue |
| `dns:manage` | 管理 DNS 记录（证书签发前的域名验证） | cert:issue |
| `key:recover` | 密钥恢复（私钥找回） | cert:issue |
| `log:export` | 导出审计日志 | log:read |
| `log:read` | 读取审计日志 | log:export |
| `ocsp:respond` | OCSP 在线证书状态响应 | cert:revoke, crl:read |
| `ra:approve` | RA 审批通过（注册机构审批） | ra:reject, cert:issue |
| `ra:reject` | RA 审批拒绝 | ra:approve |
| `report:export` | 导出报表数据 | report:view, report:generate |
| `report:generate` | 生成新报表 | report:view |
| `report:view` | 查看统计报表 | report:generate, report:export |
| `swagger:view` | 查看 API 文档（Swagger/OpenAPI） | web:view |
| `trust:delete` | 删除信任锚 | trust:import |
| `trust:import` | 导入信任锚/根证书 | trust:list, trust:delete |
| `trust:list` | 查询信任锚列表 | trust:import |
| `user:list` | 查询用户列表 | user:manage |
| `user:manage` | 管理用户账号（创建/删除/改角色） | user:list, user:revoke-all |
| `user:revoke-all` | 吊销某用户的全部证书 | user:manage, cert:revoke |
| `web:view` | 访问 Web 控制台 | swagger:view |
| `webhook:manage` | 管理 Webhook 通知（创建/删除/改地址） | cert:issue, cert:revoke |

## 能力详细语义

> 阅读指引：本节的 `usage`/`when_not`/`examples` 用于判断**何时需要该能力、何时不应授予**。AI 生成最小权限集合时以此为依据。

### `agent:manage`

**摘要**：管理 AI Agent（注册/踢线/配置）

**说明**：管理 AI Agent

**何时需要**：需要管理接入网关的 AI Agent 身份、会话时使用。

**何时不应授予**：Agent 自身执行任务不需要管理其他 Agent 的能力。

**示例**：

- 踢掉异常 Agent 连接

**相关能力**：`cert:issue`

---

### `ca:create`

**摘要**：创建新的证书颁发机构（CA）

**说明**：创建 CA

**何时需要**：需要初始化新的 PKI 层级、建立新的信任根或签发子 CA 时使用。属于一次性初始化操作，创建完成后通常不需要重复授权。

**何时不应授予**：常规证书签发/查询任务不需要；仅运维管理员初始化 PKI 时需要。

**示例**：

- 初始化 Root CA
- 创建新的 Sub CA

**相关能力**：`ca:list`, `ca:info`, `ca:issue-sub`

---

### `ca:delete`

**摘要**：删除已存在的证书颁发机构

**说明**：删除 CA

**何时需要**：彻底移除不再使用的 CA 及其关联配置时使用。危险操作，通常仅限超级管理员。

**何时不应授予**：日常签发、查询任务严禁授权；删除操作影响整个信任链。

**示例**：

- 清理废弃的测试 CA

**相关能力**：`ca:create`

---

### `ca:info`

**摘要**：查看单个 CA 的详细信息

**说明**：查看 CA 详情

**何时需要**：查看 CA 的证书、有效期、状态等详情时使用。

**何时不应授予**：无特殊限制，只读能力。

**示例**：

- 检查 CA 证书有效期
- 查看 CA 基本信息

**相关能力**：`ca:list`

---

### `ca:issue-sub`

**摘要**：签发子 CA 证书（层级扩展）

**说明**：签发子 CA 证书

**何时需要**：需要扩展 PKI 层级、为独立业务域创建子 CA 时使用。

**何时不应授予**：普通证书签发（cert:issue）不需要此能力；仅在创建新 CA 层级时需要。

**示例**：

- 为部门创建独立子 CA
- 建立多级信任链

**参数**：

| 参数 | 类型 | 默认值 | 约束 | 说明 |
|------|------|--------|------|------|
| `ca_scope` | `list` |  |  | 可签发的子 CA 范围（限制 sub-CA 作用范围） |
| `max_validity_days` | `int` | 1825 | min=1, max=3650 | 最大有效期（天） |

**相关能力**：`ca:create`, `cert:issue`

---

### `ca:list`

**摘要**：列出所有 CA

**说明**：列出 CA

**何时需要**：需要查看系统中存在哪些 CA（浏览 PKI 结构、选择签发目标）时使用。

**何时不应授予**：无特殊限制，属于只读能力，可作为多数角色的基础授权。

**示例**：

- 浏览可用 CA 列表
- 确认签发目标 CA 存在

**相关能力**：`ca:info`

---

### `cert:batch`

**摘要**：批量签发多张证书

**说明**：批量签发证书

**何时需要**：一次性为大量设备/服务签发证书（批量上线、批量扩展）时使用。

**何时不应授予**：单张证书签发用 cert:issue 即可，无需批量权限。

**示例**：

- 批量签发 100 台设备证书

**相关能力**：`cert:issue`

---

### `cert:export`

**摘要**：导出证书（PEM/DER 格式）

**说明**：导出证书

**何时需要**：需要下载证书文件、交付给对端、备份时使用。只读能力。

**何时不应授予**：无特殊限制，但注意导出的是公开证书而非私钥。

**示例**：

- 导出服务证书给 Nginx 配置
- 下载证书用于客户端部署

**相关能力**：`cert:list`

---

### `cert:issue`

**摘要**：签发终端实体证书

**说明**：签发证书

**何时需要**：为服务、设备、用户或 Agent 签发新证书时使用。最常见的证书操作。

**何时不应授予**：纯查询任务（list/info）不需要；已有证书续期应使用 cert:renew 而非重新签发。

**示例**：

- 为 HTTPS 服务签发证书
- 为 AI Agent 签发 AIC 证书
- 签发客户端 mTLS 证书

**参数**：

| 参数 | 类型 | 默认值 | 约束 | 说明 |
|------|------|--------|------|------|
| `ca_scope` | `list` |  |  | 允许签发的 CA 列表（限制子 CA 发行范围） |
| `max_validity_days` | `int` | 365 | min=1, max=3650 | 最大有效期（天） |

**相关能力**：`cert:renew`, `cert:revoke`, `cert:list`

---

### `cert:list`

**摘要**：查询证书列表（可按 CA/状态/主体筛选）

**说明**：查询证书列表

**何时需要**：需要检索已签发的证书、查看证书状态（有效/吊销/过期）时使用。只读能力。

**何时不应授予**：无特殊限制，只读能力，可作为基础授权。

**示例**：

- 列出某 CA 下全部证书
- 查找某证书的吊销状态

**相关能力**：`ca:list`, `cert:info`

---

### `cert:renew`

**摘要**：续期已有证书

**说明**：续期证书

**何时需要**：证书即将到期、需要保持同一主体继续使用时使用。通常保留原公钥或重新生成。

**何时不应授予**：新主体首次接入应使用 cert:issue；到期回收应使用 cert:revoke。

**示例**：

- 自动续期服务证书
- Agent 证书到期续签

**相关能力**：`cert:issue`, `cert:revoke`

---

### `cert:revoke`

**摘要**：吊销已签发的证书

**说明**：吊销证书

**何时需要**：证书私钥泄露、主体不再合法、任务完成回收证书时使用。

**何时不应授予**：只读任务不需要；吊销是敏感操作，应控制到最小范围。

**示例**：

- 私钥泄露后吊销证书
- Agent 任务完成后吊销临时证书

**参数**：

| 参数 | 类型 | 默认值 | 约束 | 说明 |
|------|------|--------|------|------|
| `ca_scope` | `list` |  |  | 允许吊销的 CA 列表 |

**相关能力**：`cert:issue`, `cert:list`

---

### `config:read`

**摘要**：读取系统配置

**说明**：读取配置

**何时需要**：需要查看当前配置（监听端口、CA 路径等）时使用。只读。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 查看当前配置

**相关能力**：`config:write`

---

### `config:write`

**摘要**：修改系统配置

**说明**：修改配置

**何时需要**：需要变更配置并热重载时使用。敏感操作，修改可能影响全部服务。

**何时不应授予**：常规任务严禁授权；仅运维管理员需要。

**示例**：

- 修改证书有效期配置

**相关能力**：`config:read`

---

### `crl:generate`

**摘要**：生成证书吊销列表（CRL）

**说明**：生成 CRL

**何时需要**：吊销发生后需要生成/更新 CRL 供客户端校验时使用。

**何时不应授予**：纯查询任务不需要；通常由吊销流程自动触发。

**示例**：

- 吊销后生成最新 CRL

**相关能力**：`cert:revoke`, `crl:read`

---

### `crl:read`

**摘要**：读取 CRL 内容

**说明**：读取 CRL

**何时需要**：客户端校验证书吊销状态、审计检查时使用。只读能力。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 检查 CRL 是否包含某证书

**相关能力**：`crl:generate`, `cert:list`

---

### `cross-cert:issue`

**摘要**：签发交叉证书（跨信任域桥接）

**说明**：签发交叉证书

**何时需要**：需要建立两个 PKI 域之间的信任桥接时使用。高级 PKI 操作。

**何时不应授予**：单域内部签发不需要。

**示例**：

- 两个企业 PKI 互信

**相关能力**：`ca:issue-sub`

---

### `cross-cert:revoke`

**摘要**：吊销交叉证书

**说明**：吊销交叉证书

**何时需要**：需要撤销跨域信任桥接时使用。

**何时不应授予**：单域操作不需要。

**示例**：

- 撤销企业间信任

**相关能力**：`cross-cert:issue`

---

### `dns:manage`

**摘要**：管理 DNS 记录（证书签发前的域名验证）

**说明**：管理 DNS

**何时需要**：需要为签发证书创建 DNS 验证记录时使用（ACME 挑战等）。

**何时不应授予**：不涉及域名验证的签发任务不需要。

**示例**：

- 创建 _acme-challenge DNS 记录

**相关能力**：`cert:issue`

---

### `key:recover`

**摘要**：密钥恢复（私钥找回）

**说明**：密钥恢复

**何时需要**：需要从密钥托管中恢复私钥时使用。极高敏感度操作。

**何时不应授予**：常规任务严禁授权；仅授权密钥托管管理员。

**示例**：

- 恢复丢失的服务私钥

**相关能力**：`cert:issue`

---

### `log:export`

**摘要**：导出审计日志

**说明**：导出审计日志

**何时需要**：需要将日志交付给 SIEM、离线归档或合规审计时使用。

**何时不应授予**：仅查看用 log:read 即可。

**示例**：

- 导出近 30 天日志给审计系统

**相关能力**：`log:read`

---

### `log:read`

**摘要**：读取审计日志

**说明**：读取审计日志

**何时需要**：需要查看操作记录、排查问题时使用。只读能力。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 查看最近的证书签发记录

**相关能力**：`log:export`

---

### `ocsp:respond`

**摘要**：OCSP 在线证书状态响应

**说明**：OCSP 响应

**何时需要**：提供 OCSP 在线吊销状态查询服务时使用。通常由核心服务自身持有。

**何时不应授予**：普通 Agent/用户任务不需要此能力。

**示例**：

- OCSP 响应器服务运行

**相关能力**：`cert:revoke`, `crl:read`

---

### `ra:approve`

**摘要**：RA 审批通过（注册机构审批）

**说明**：RA 审批通过

**何时需要**：需要审批待签发的证书请求（人工复核流程）时使用。

**何时不应授予**：纯自动化签发不需要 RA 审批能力。

**示例**：

- 审批待签发的服务器证书

**相关能力**：`ra:reject`, `cert:issue`

---

### `ra:reject`

**摘要**：RA 审批拒绝

**说明**：RA 审批拒绝

**何时需要**：需要拒绝不合规的证书请求时使用。

**何时不应授予**：同 ra:approve，仅审批人员需要。

**示例**：

- 拒绝伪造的证书请求

**相关能力**：`ra:approve`

---

### `report:export`

**摘要**：导出报表数据

**说明**：导出报表

**何时需要**：需要下载报表数据（CSV/JSON）时使用。

**何时不应授予**：仅页面查看用 report:view。

**示例**：

- 导出报表给财务系统

**相关能力**：`report:view`, `report:generate`

---

### `report:generate`

**摘要**：生成新报表

**说明**：生成报表

**何时需要**：需要按自定义条件生成统计报表时使用。

**何时不应授予**：仅查看预置报表用 report:view。

**示例**：

- 生成自定义时间段签发报表

**相关能力**：`report:view`

---

### `report:view`

**摘要**：查看统计报表

**说明**：查看报表

**何时需要**：需要查看证书签发量、吊销量等统计报表时使用。只读。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 查看月度签发报表

**相关能力**：`report:generate`, `report:export`

---

### `swagger:view`

**摘要**：查看 API 文档（Swagger/OpenAPI）

**说明**：查看 API 文档

**何时需要**：需要浏览 API 接口文档时使用。只读。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 查看 API 接口说明

**相关能力**：`web:view`

---

### `trust:delete`

**摘要**：删除信任锚

**说明**：删除信任锚

**何时需要**：需要撤销对某外部 CA 的信任时使用。

**何时不应授予**：不涉及外部信任管理不需要。

**示例**：

- 移除不再信任的 CA

**相关能力**：`trust:import`

---

### `trust:import`

**摘要**：导入信任锚/根证书

**说明**：导入信任锚

**何时需要**：需要信任新的外部 CA 时使用。

**何时不应授予**：不涉及外部信任的任务不需要。

**示例**：

- 导入客户 CA 证书

**相关能力**：`trust:list`, `trust:delete`

---

### `trust:list`

**摘要**：查询信任锚列表

**说明**：查询信任锚

**何时需要**：需要查看当前信任哪些外部 CA 时使用。只读。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 查看已信任的 CA

**相关能力**：`trust:import`

---

### `user:list`

**摘要**：查询用户列表

**说明**：查询用户列表

**何时需要**：需要查看系统用户、确认身份时使用。只读能力。

**何时不应授予**：无特殊限制，只读。

**示例**：

- 列出所有用户

**相关能力**：`user:manage`

---

### `user:manage`

**摘要**：管理用户账号（创建/删除/改角色）

**说明**：管理用户

**何时需要**：需要管理 PKI 用户身份、分配角色权限时使用。敏感管理操作。

**何时不应授予**：普通证书操作任务不需要用户管理权限。

**示例**：

- 创建新用户
- 为用户分配角色

**相关能力**：`user:list`, `user:revoke-all`

---

### `user:revoke-all`

**摘要**：吊销某用户的全部证书

**说明**：吊销用户全部证书

**何时需要**：用户离职、账号泄露时需要吊销其名下所有证书时使用。

**何时不应授予**：单张证书吊销用 cert:revoke 即可。

**示例**：

- 用户离职后吊销其全部证书

**相关能力**：`user:manage`, `cert:revoke`

---

### `web:view`

**摘要**：访问 Web 控制台

**说明**：访问 Web 控制台

**何时需要**：需要登录 Web 管理界面时使用。

**何时不应授予**：纯 API 调用任务不需要。

**示例**：

- 登录管理控制台

**相关能力**：`swagger:view`

---

### `webhook:manage`

**摘要**：管理 Webhook 通知（创建/删除/改地址）

**说明**：管理 webhook

**何时需要**：需要配置证书事件通知（签发/吊销/到期）到外部系统时使用。

**何时不应授予**：不订阅通知的任务不需要。

**示例**：

- 配置证书到期提醒 Webhook

**相关能力**：`cert:issue`, `cert:revoke`

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

### 角色 `admin`

**名称**：管理员

**Profiles**：`m-admin`

**可绑定 OU**：`admin`, `Admin`

**授权能力（grants）**：

- `ca:list`
- `ca:info`
- `cert:issue`
- `cert:revoke`
- `cert:renew`
- `cert:list`
- `cert:export`
- `cert:batch`
- `crl:generate`
- `log:read`
- `log:export`
- `report:view`
- `report:export`
- `report:generate`
- `ra:approve`
- `ra:reject`
- `cross-cert:issue`
- `cross-cert:revoke`
- `webhook:manage`
- `key:recover`
- `dns:manage`
- `trust:import`
- `trust:list`
- `trust:delete`
- `agent:manage`
- `swagger:view`
- `web:view`

### 角色 `agent`

**名称**：AI Agent

**Profiles**：`agent-proxy`

**授权能力（grants）**：

- `gateway:*`

### 角色 `auditor`

**名称**：审计员

**Profiles**：`m-auditor`

**可绑定 OU**：`auditor`, `Auditor`

**授权能力（grants）**：

- `ca:list`
- `ca:info`
- `cert:list`
- `log:read`
- `log:export`
- `report:view`
- `report:export`
- `swagger:view`
- `web:view`

### 角色 `auto-renew`

**名称**：自动续期服务

**Profiles**：`m-auto-renew`

**可绑定 OU**：`auto-renew`, `AutoRenew`

**授权能力（grants）**：

- `ca:list`
- `ca:info`
- `cert:list`
- `cert:renew`
- `cert:export`
- `log:read`
- `web:view`

### 角色 `console`

**名称**：控制台用户

**Profiles**：`m-console`

**可绑定 OU**：`console`, `Console`

**授权能力（grants）**：

- `ca:list`
- `ca:info`
- `cert:issue`
- `cert:revoke`
- `cert:renew`
- `cert:list`
- `cert:export`
- `crl:generate`
- `log:read`
- `report:view`
- `report:generate`
- `ra:approve`
- `ra:reject`
- `trust:list`
- `swagger:view`
- `web:view`

### 角色 `operator`

**名称**：运营操作员

**Profiles**：`m-operator`

**可绑定 OU**：`operator`, `Operator`

**授权能力（grants）**：

- `ca:list`
- `ca:info`
- `cert:issue`
- `cert:revoke`
- `cert:renew`
- `cert:list`
- `cert:export`
- `cert:batch`
- `crl:generate`
- `log:read`
- `report:view`
- `web:view`

### 角色 `readonly`

**名称**：只读用户

**Profiles**：`m-readonly`

**可绑定 OU**：`readonly`, `ReadOnly`

**授权能力（grants）**：

- `ca:list`
- `ca:info`
- `cert:list`
- `swagger:view`
- `web:view`

### 角色 `reporter`

**名称**：报表用户

**Profiles**：`m-reporter`

**可绑定 OU**：`reporter`, `Reporter`

**授权能力（grants）**：

- `ca:list`
- `ca:info`
- `cert:list`
- `log:read`
- `report:view`
- `report:export`
- `report:generate`
- `web:view`

### 角色 `revoker`

**名称**：自动吊销器

**Profiles**：`m-revoker`

**可绑定 OU**：`revoker`, `Revoker`

**授权能力（grants）**：

- `ca:list`
- `ca:info`
- `cert:list`
- `cert:revoke`
- `log:read`
- `report:view`
- `web:view`

### 角色 `superadmin`

**名称**：超级管理员

**Profiles**：`m-superadmin`

**可绑定 OU**：`SuperAdmin`

**授权能力（grants）**：

- `ca:create`
- `ca:delete`
- `ca:list`
- `ca:info`
- `cert:issue`
- `cert:revoke`
- `cert:renew`
- `cert:batch`
- `cert:list`
- `cert:export`
- `crl:generate`
- `user:manage`
- `user:list`
- `user:revoke-all`
- `log:read`
- `log:export`
- `config:read`
- `config:write`
- `report:view`
- `report:export`
- `report:generate`
- `ra:approve`
- `ra:reject`
- `cross-cert:issue`
- `cross-cert:revoke`
- `webhook:manage`
- `key:recover`
- `dns:manage`
- `trust:import`
- `trust:list`
- `trust:delete`
- `agent:manage`
- `swagger:view`
- `web:view`

## 最小权限生成指南（AI/开发者）

为任务生成能力集合时遵循：

1. **只授予任务必需能力**：对照各能力 `usage`（何时需要）判断，`when_not` 明确说明的不授予。
2. **精确优先**：能精确到 `capability_id` 就不用通配；能用单个能力就不用域通配 `domain:*`。
3. **参数收窄**：有 `parameters` 的能力，按任务实际需要设置默认值/范围，宁可窄勿宽。
4. **只读优先**：只读能力（`*:list`、`*:read`、`*:view`）优先于写能力。
5. **禁用危险能力**：`key:recover`、`ca:delete`、`config:write` 等敏感能力默认不授予，除非任务明确需要。
6. **去除冗余**：已由通配覆盖的精确能力可省略；与任务无关的能力全部删除。

