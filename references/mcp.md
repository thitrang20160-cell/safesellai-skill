# SafeSell AI MCP 接入与调用

远程地址为 `https://safesellai.com/mcp`，传输使用 **Streamable HTTP**。先读取当前账号的 `tools/list`。带 Key 时使用 `Authorization: Bearer YOUR_API_KEY`。 [SafeSell AI MCP 官方说明](https://safesellai.com/mcp-guide) · [工具参数快照](mcp-tools.json)

## 匿名、免费账号和带权限的账号

| 模式 | 认证 | 能力与边界 |
|---|---|---|
| 匿名试用 | 不填 Authorization | `start_here`、`guest_info`、`check_brand`、`check_batch`、`check_tro` 摘要，以及 `store_audit` 的商品清单文字模式。部分其他工具虽在列表里，调用会提示需要 Key。 |
| 持 Key 的免费、试用或已到期账号 | 相应账号自己的 Key | 已注册的文字品牌排查、余额和用量、TRO 律所地址查、白名单维护和受限的网页接口。根据权限发现 AI 小安等可用接口。带 Key 不会自动解锁付费维度。 |
| 付费账号与授权的企业主账号 | 相应账号自己的 Key | 工具与实际可操作的接口由网页业务权限、套餐、店铺范围、配额及余额决定。企业主账号权限沿用网页，子账号之间按网页隔离。 |

- 匿名推广期默认文字 **100 词/天/IP**，其中 `check_batch` 单次最多 **20 词**。`check_tro` 摘要和文字排查使用同一额度。推广状态、实时余量以 `guest_info` 为准。
- 匿名商品清单体检默认单次最多 **100 SKU**，仅查商标词和 TRO 文字。基础可用一次，首次完成批量排查可能再解锁一次，以实时任务和额度为准。绑定自有店铺的 `storeId` 模式需要带 Key 与网页授权。
- 需要 Key 时登录工作台，在账号设置或企业 API 的密钥入口核对是否能创建。企业 API 密钥管理通常由具备 API 权限的主账号操作。注册免费账号后能否创建 Key 以当前入口为准。完整 Key 通常仅创建时显示，保护好它。到期、撤销、停用及账号限制仍生效。
- REST 的 scope 和 REST 速率限制按 REST 接口执行。MCP 依网站业务权限与计费校验，不套用 REST 接入的 scope 或速率额度。切换身份或密钥后重新初始化会话。

## 客户端怎么配

### Codex

匿名连接命令。

```sh
codex mcp add safesellai --url https://safesellai.com/mcp
```

认证连接之前，把 API Key 安全设置为 Codex 进程可读的环境变量 `SAFESELLAI_API_KEY`，再运行以下命令。二选一。

```sh
codex mcp add safesellai --url https://safesellai.com/mcp --bearer-token-env-var SAFESELLAI_API_KEY
```

```toml
[mcp_servers.safesellai]
url = "https://safesellai.com/mcp"
bearer_token_env_var = "SAFESELLAI_API_KEY"
```

TOML 放在 Codex 的 MCP 配置中，通常是 `~/.codex/config.toml`。匿名配置省略 `bearer_token_env_var`。客户端已经打开时重新加载连接或启动新会话，检查 `codex mcp list`。可让 Codex 显式调用 `start_here`，使纯文字客户端同样获得流程。 [SafeSell AI 的 Codex 配置](https://safesellai.com/mcp-guide)

### Claude Code、Cursor 与通用客户端

- Claude Code 匿名连接使用 `claude mcp add --transport http safesellai https://safesellai.com/mcp`。带 Key 时使用 `--header "Authorization: Bearer <你的Key>"` 或按客户端官方指引配置头。使用本机密钥管理，避免把真实密钥写进示例、共享脚本或命令记录。
- Cursor 用 `~/.cursor/mcp.json` 或项目 MCP 配置。WorkBuddy 桌面使用「连接器 → 自定义连接器 → 添加 MCP」，按客户端要求选择 HTTP 并启用。WorkBuddy 配置可在服务项中加 `"type": "http"`。同一地址与认证用于其它兼容客户端。
- 以下 JSON 使用认证占位符。匿名时删除 `headers`。真实配置优先使用客户端提供的密钥引用。 [当前客户端配置样例](https://safesellai.com/mcp-guide)

```json
{
  "mcpServers": {
    "safesellai": {
      "url": "https://safesellai.com/mcp",
      "headers": { "Authorization": "Bearer YOUR_API_KEY" }
    }
  }
}
```

## 用脚本验连接

从 Skill 根目录运行 `python scripts/mcp-smoke.py` 走匿名接入。认证时先配置环境变量，再运行 `python scripts/mcp-smoke.py --account`。需要查看专利或其他已授权网页目录时加 `--feature patents`。脚本只读工具清单、匿名额度或账号余额，指定功能时读取对应目录。

## 连接和协议验证

1. 连接后读 `tools/list`；支持的客户端也可读 `prompts/list` 和 `resources/list`。
2. 匿名先调 `guest_info {}`，带 Key 先调 `get_balance {}`。返回错误时保留错误详情。连接成功只说明协议通了。
3. 自行实现客户端时，向 `/mcp` POST `initialize`，声明 `Accept: application/json, text/event-stream` 和 `Content-Type: application/json`。后续使用服务器协商的 `MCP-Protocol-Version`，带回响应中的 `Mcp-Session-Id`（若有），再发 `notifications/initialized`。
4. 发 `tools/list` 后根据实际名称和 `inputSchema` 调 `tools/call`。解析 JSON 或 SSE。SSE 中的多个 `data:` 行需组装为一个事件，按 JSON-RPC `id` 关联响应。工具级 `isError` 与 HTTP 状态分别检查。
5. 兼容 MCP Apps 的客户端可显示欢迎面板 `ui://safesellai/welcome.html`。文字客户端读 `start_here` 即可。服务器还提供 `start_first_check`（可选 `brand`）与 `store_audit_guide` 提示词。用实时目录确认它们是否公开。

如下为一条 JSON-RPC 消息示例。初始化步骤和会话头仍应按上面设置。

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"guest_info","arguments":{}}}
```

[官方 MCP 接入与验证说明](https://safesellai.com/mcp-guide) · [MCP 协议规范](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)

## 工具速查

下表覆盖当前远程接口注册的快捷工具。工具能否执行还取决于实时账号和功能授权。参数细节、必填值和类型见 [mcp-tools.json](mcp-tools.json)。

| 工具 | 入口参数 | 操作及结果解读 |
|---|---|---|
| `start_here` | `{}` | 查看接入引导和可渲染欢迎面板 |
| `guest_info` | `{}` | 匿名额度、免费体检次数和任务进度，只读 |
| `get_balance` | `{}` | 当前账号的网页版 S算力余额与套餐，带 Key，只读 |
| `get_usage` | 可选 `days`，缺省 30 | API/MCP 用量统计。完整网页 S算力流水用网页入口查询 |
| `check_brand` | `brand`，带 Key 版可接收 `category`、`position` | 查品牌词或关键词。带 Key 的兼容字段不改变网页版词库口径 |
| `check_batch` | `words` 字符串数组，带 Key 可传 `category` | 每条保留原始词及位置。带 Key 的网页批量上限按当前业务校验 |
| `check_link` | `url`，认证时可选 `imageDepth`、`dims` | 商品链接、ASIN 或 Walmart Item ID 的 Listing 评分。匿名同名入口提示需要 Key |
| `check_tro` | `brand` | 匿名为命中摘要；有权限的认证模式走案件查询 |
| `tro_lawfirms` | 可选 `keyword` | 查询可见的 TRO 律所下单地址黑名单，区分系统及账号自定义记录 |
| `check_image` | `image_b64` 或 `image_url`，可选 `own_brands` | 单图的文字、图形标和 TRO。自有品牌以账号设置为准；使用专用功能查版权与外观专利 |
| `optimize_ai` | `items` 数组，每项可有 `title`、`brand`、`features`、`description`、`riskHits` | AI 改写草稿，按网页上限和费用。最终复查后才保存或发布 |
| `f6_hits` | 可选 `limit` 与 `offset` | 已授权的 F6 命中列表，分页核对店铺和事件 |
| `store_audit` | 在 `storeId` 与 `items` 中选一种 | 绑定店铺或提交结构化商品清单。匿名限文字清单 |
| `whitelist_list` | `{}` | 当前账号白名单 |
| `whitelist_add` / `whitelist_remove` | `brand` | 真实增删账号词库。获得相应授权后再执行并读回 |
| `website_tools` | 可选 `feature` | 读取支持的客户网页业务目录。`feature` 匹配路径片段，返回方法、路径和字段提示 |
| `website_request` | `method` 与 `path`，可选 `query`、`body`、`stream`、`files` | 调用注册的原网页业务。可能计费、修改、导出、上传或启动任务 |

### 快捷调用例子

以下为参数样例。通过客户端选择对应工具，`arguments` 只填该行 JSON。

| 调用 | arguments |
|---|---|
| 接入引导 `start_here` | `{}` |
| 匿名查额度 `guest_info` | `{}` |
| 认证余额 `get_balance` | `{}` |
| 认证用量 `get_usage` | `{"days":7}` |
| 查 TRO `check_tro` | `{"brand":"Example Garden"}` |
| 单图 `check_image` | `{"image_b64":"替换为真实图片Base64"}` |
| F6 分页 `f6_hits` | `{"limit":10,"offset":0}` |
| 读白名单 `whitelist_list` | `{}` |
| 增删白名单 `whitelist_add` / `whitelist_remove` | `{"brand":"Example Garden"}` |
| 目录 `website_tools` | `{"feature":"patents"}` |
| 匿名或认证查词 `check_brand` | `{"brand":"Example Garden"}` |
| 批量 `check_batch` | `{"words":["Example Garden","32 oz steel bottle"]}` |
| 律所地址 `tro_lawfirms` | `{"keyword":"示例街道"}` |
| 认证 Listing `check_link` | `{"url":"19904652537","dims":{"compliance":true,"compliancePlatform":"walmart"}}` |
| 文字清单体检 `store_audit` | `{"items":[{"sku":"DEMO-001","title":"32 oz steel bottle","brand":"Example Garden","features":["Leak-resistant lid"],"description":"Stainless steel bottle"}]}` |
| 绑定店铺体检 `store_audit` | `{"storeId":123,"maxItems":5,"compliance":true,"compliance_platform":"walmart"}` |
| 改写 `optimize_ai` | `{"items":[{"title":"示例原标题","features":["实际产品特点"],"riskHits":["已核实的命中词"]}]}` |

`storeId: 123` 是占位示例。先在工作台核对当前账号下的实际绑定 ID。店铺体检的认证版可按所选维度使用 `compliance`、`compliance_platform`、`patent`、`design_patent`、`copyright` 与 `trademark_vision`。清单项可提供 `images` URL 数组。具体哪些维度实际执行，以返回内容为准。`scanned:false`、缺图、失败项和部分完成分别汇报。

`check_link` 的额外 `dims` 可含 `imageCopyright`、`designPatent`、`utilityPatent`、`compliance`、`compliancePlatform`。MCP 服务端抓取与浏览器插件读取经过不同链路。抓取受限时，优先换到已验证的浏览器页面或使用结构化数据处理流程。

## 网页接口发现、上传、下载与任务

1. 调 `website_tools {"feature":"patents"}` 查看专利业务的实际路径、方法与输入提示。其他可搜索片段包括 `match`、`stores`、`guardian`、`f6`、`tro`、`platform-rules`、`check-image-copyright`、`scoin`、`subaccounts` 和 `xiaoan`。目录出现的操作仍需业务权限。
2. 先读操作说明。`website_request` 的 `path` 用实际的站内业务路径，例如 `/api/scoin/transactions`，不要填完整 URL。把实际参数分别放入 `query` 和 `body`。动态路径用已取得的实际 ID。调用接口时不用另外内嵌鉴权头。
3. 文件上传使用 `files`。每项有 `field`、`name`、`mimeType`、`base64`。字段名和限制取原网页表单或目录，原文 Base64 放在 `base64`。图片 URL 与文件字段不是同一概念。
4. 下载可能返回 MCP 内嵌 resource，按 MIME 类型和 Base64 内容保存，核对文件名、真实类型、行数及账号范围。异步任务使用已返回的任务 ID 查询当前状态。SSE 请求按路由返回多个事件，最终报告与错误信息不同。
5. `GET` 与 `POST` 都看业务语义。查询端点也可能计费。改库存、上架、写白名单、导出敏感数据和启用计划任务，只在对应授权范围内执行。

```json
{"method":"GET","path":"/api/scoin/transactions"}
```

```json
{
  "method":"POST",
  "path":"/api/check-image",
  "files":[{
    "field":"image",
    "name":"sample.png",
    "mimeType":"image/png",
    "base64":"替换为本地样本图片真实Base64"
  }]
}
```

## 出错时核对

- `401` 或会话无效时，核对用的是匿名还是带 Key 连接、密钥及会话头是否从同一次初始化取得。
- `403` 时核对当前身份、套餐和网页业务权限，包括店铺访问和子账号限制。先用该身份读目录和余额。
- `429`、余额不足、资源缺失、抓取失败、验证码和子维度失败按实际回执处理。可能已扣费或写入的超时先查记录、流水或任务，避免盲重试。
- 保存时间、商品或店铺、工具名称、参数摘要、已完成维度及请求或任务 ID。日志中只保留脱敏数据。
