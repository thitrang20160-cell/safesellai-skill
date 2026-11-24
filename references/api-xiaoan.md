# REST API、AI 小安和客户服务

[开发者入口](https://safesellai.com/developer) · [交互 API 文档](https://safesellai.com/api/v1/docs) · [线上 OpenAPI](https://safesellai.com/api/v1/openapi.json) · [MCP 手册](mcp.md)

## REST API 怎么接

1. 在具备企业 API 权限的正式工作台创建自己的 API Key，查当前套餐、scope、到期时间及适用限流。Key 的 REST 能力和 MCP 网页业务能力分别验证。
2. 使用 `Authorization: Bearer YOUR_API_KEY`，JSON 请求用 `Content-Type: application/json`。服务地址 `https://safesellai.com`。从公开健康检查和 OpenAPI 开始。
3. 保存 HTTP 状态、实际响应信封及 `request_id`。成功结果通常在 `data`，错误检查 `error.code` 与 `error.message`。REST 查询与网页共用的费用按当前权限、套餐和接口核对。
4. 开发先用自有试样，用真实且已授权的小批量核对结果到 SKU 的映射、权限、额度和扣费。在用户操作或生产自动化中，对已发生的外部动作先查询再补交。

```sh
curl https://safesellai.com/api/v1/health
curl -H "Authorization: Bearer YOUR_API_KEY" https://safesellai.com/api/v1/balance
```

把占位符换成从环境变量或凭证工具读取的值。Windows 可以用 `curl.exe`。健康检查不需要 Key，余额需要认证。

## REST 路径总表

当前公开规范为 v1.1.0，精确必填字段、限额、scope 和示例请在[线上 OpenAPI](https://safesellai.com/api/v1/openapi.json)读对应端点。下面列出公开规范中的操作。离线阅读也可使用[所附 OpenAPI 快照](rest-openapi.json)。

| 方法和路径 | 用途及输入要点 |
|---|---|
| GET `/api/v1/health` | 公开健康检查 |
| GET `/api/v1/balance` | 当前账号 S算力 |
| GET `/api/v1/usage` | API 用量统计 |
| POST `/api/v1/check/brand` | `brand` 与可选场景字段，例如 `category`、`position` |
| POST `/api/v1/check/batch` | `words` 或 `items`（例如 `word`、`position`），当前公开规范每次最多 100 项 |
| POST `/api/v1/check/link` | `url`，抓取商品信息并做风险初筛 |
| POST `/api/v1/check/tro` | `brand`，返回关联历史命中 |
| POST `/api/v1/check/store-audit` | `items` 结构化清单及可选 `own_brands`，按 REST 规范检查标题、五点、描述覆盖和批量上限 |
| POST `/api/v1/check/image` | `image_b64` 或符合接口要求的 `image_url`，用于图片品牌元素检测 |
| POST `/api/v1/delogo/detect` | 批量识别图片图形标，按规范提交图并核对位置与风险 |
| POST `/api/v1/delogo/apply` | 对已有授权且允许修改的图做标识处理，核对是否成功以及单张消费 |
| POST `/api/v1/optimize/ai` | AI 改写商品 Listing，核对原 SKU 与输出 |
| GET `/api/v1/f6/hits` | 已授权的 F6 命中列表 |
| POST `/api/v1/f6/blacklist` | 新增自定义地址，确认对象、地址及授权 |
| DELETE `/api/v1/f6/blacklist/{id}` | 移除本人添加的目标条目，提交后读回 |

REST 的 `write:check`、`write:audit` 等要求随操作而异，核对当前规范和 Key 实际 scope。`400` 修正输入，`401` 核对密钥，`402`/余额错误核对余额，`403` 核对 scope 和账号资格，`429` 按实际 `Retry-After` 及业务规则退避。`502`、`503` 或 `tro_data_unavailable` 需要保留失败和数据缺口。 [API 与 ERP 接入手册](https://safesellai.com/guides/api-integration)

## AI 小安

[正式版 AI 小安](https://safesellai.com/app/xiaoan.html) · [免费版 AI 小安](https://safesellai.com/freeAI/xiaoan.html)

1. 用现有 SafeSell AI 账号登录，查看小安积分余额。页面规则当前为每天可领 **100 积分**，积分可累积，成功回答通常扣 **10 积分**，失败自动退回。以当前页面和流水为准。
2. 提供商品标题、平台站点、需查维度、已有品牌、专利号或案件号。可上传商品图片或页面支持的 Excel 产品表。使用页面模板，保留表行和 SKU 对应。页面当前标注单次最多 **10 个产品**。
3. 用小安获取侵权初筛、修改方案和 Listing 优化建议。图片检索的版权、专利、文字商标分别查证，并核对返回中「已查 / 未查 / 查询失败」及实际引用。需要视觉重查时提供更完整视角。
4. 领取和提问是不同动作。失败先查会话、任务结果和积分余额，避免重复请求。小安积分和工作台 S算力是不同余额。调用小安时发起的网页付费检测仍按其规则执行。
5. MCP 客户端从 `website_tools {"feature":"xiaoan"}` 发现授权接口，例如小安状态、历史、任务、领取、提问和预览。表单字段取当前接口。给阅读任务只查状态或结果，涉及主动领取、上传、提问或收费检测按用户任务执行。

## 查询记录、账户用量与开发者设置

- **历史与导出。** 在对应模块查询商品、批次、报告和日期，下载结果后核对 SKU、文件顺序、原图、成功数、被跳过的维度与扣费。区分查询历史、异步任务状态和积分流水。
- **账户和团队。** 在账号菜单查看套餐、余额、通知、授权、子账号和开发者密钥。企业主账号查看子账号数据须有网页相应权限，子账号各自使用已授权范围。
- **订单记录与账号设置。** 在「账户设置」查看已支持的个人资料、密码设置和订单记录。核对付款状态、套餐、时间及对应账号。
- **邀请好友。** 从账号菜单或设置打开「邀请好友」，复制当前邀请链接。查看活动规则、已邀请进度及奖励到账情况，以实际页面和 S算力流水为准。
- **账务与购买。** 在账号的 S算力、套餐或订单入口核对价格和实际消费。购买、续费、发票或对外确认收款按用户授权或相应官方流程办理。席位权限、到期和 S算力余额分别看。
- **公开服务。** 在知识中心查公开案例、方法和操作指引，使用官方记录复核。检查当前条目时间和资料来源。 [公开知识中心](https://safesellai.com/guides)

## 店铺暂停申诉服务

1. 在正式工作台打开「店铺暂停申诉服务」，保存平台原通知及店铺、站点、时间、问题 SKU 和处理范围。
2. 先确认是绩效、商品侵权、平台违规、账户验证还是其他限制。按要求回读平台事件、证据、授权材料、履约或整改记录。
3. 起草 POA 时按事实写根因、已完成的整改与预防措施，关联相应证据。将未完成和待提供材料单列。平台是否接受或恢复由实际回执确认。
4. 发送申诉、外部消息或提交附件前核对用户具体授权，提交后记录案件号、时间和平台状态。对投诉和法院措施以原通知与文书复核为准。
