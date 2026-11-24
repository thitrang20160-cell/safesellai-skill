# SafeSell AI｜跨境商品合规排查与店铺体检

准备上架一款商品，标题里的品牌词要不要改？供应商给的图片能不能用？外观相似的专利或 TRO 案件，应该先核对哪一个？

SafeSell AI 帮你从**商品链接、图片或 Excel** 开始排查。逐项查看命中词、相似图、案件线索和待复核的 SKU，再决定先改什么、查什么。适合 Walmart、Amazon 等平台的卖家、选品团队和店铺运营。

**[免费试用](https://safesellai.com/freeAI/)　·　[正式工作台](https://safesellai.com/app/)　·　[安装浏览器插件](https://safesellai.com/install)　·　[接入 AI 助手](https://safesellai.com/mcp-guide)**

## 从你手头的商品开始

| 你手里有什么 | 可以怎么查 | 查完会看到什么 |
| --- | --- | --- |
| 一个品牌词、一条标题或一批 Excel | 商标词快查、批量排查、黑白名单 | 哪个词命中、出现在什么字段、是否有关联 TRO |
| Walmart Item ID、Amazon ASIN 或商品链接 | 单品 Listing 多维评分、批量链接排查 | 对应商品、风险明细、需要修改的字段，以及本次有哪些维度已查 |
| 主图、图案或专利号 | 图片版权单张精查与批量检索、图形商标、外观专利图搜、指定专利比对 | 相似候选、参考图、权利方、专利号或相关案号 |
| 品牌、案号或下单地址线索 | TRO 案件、律所地址黑名单与 F6 命中查询 | 可复核的案件或地址条目、匹配依据和来源 |
| 一个已授权的店铺 | 全店侵权体检、绩效与店铺监控 | 问题 SKU、近期告警、历史结果和可用的报告导出 |
| 一张选品清单 | 跟卖筛查、选品库、变体和 GTIN 核对 | 选品风险与待补字段，有权限时可继续做归档恢复和上架管理 |

平台违禁品检查可以按销售平台做单品或批量排查。AI Listing 改写可以根据已核实的命中词草拟标题、五点和描述，便于修改后复查。各项费用及可用能力以当前账号和页面为准。 [查看商品排查手册](references/workbench.md) · [查看店铺和插件手册](references/store-plugin.md)

## 三种上手方式

1. **用网页查。** 打开免费版，先用一个准备上架的品牌词试查，再用 Excel 批量核对。免费版还提供 TRO 律所地址查询和白名单设置。 [打开免费版](https://safesellai.com/freeAI/)
2. **在商品页直接查。** 用电脑安装 Chrome 或 Edge 插件，打开受支持的商品页，查看页面风险标注或发起单品排查。授权账号可在支持的 Walmart 列表页做跟卖筛查。 [商店与官网下载指引](https://safesellai.com/install)
3. **交给 AI 助手。** 在 SafeSell AI 里用「AI 小安」提交问题、图片或 Excel，获取排查与 Listing 修改建议。也可让 Codex、Claude Code 或 Cursor 通过 MCP 调用你账号有权使用的功能。匿名 MCP 可免 Key 试用文字排查。 [打开 AI 小安](https://safesellai.com/app/xiaoan.html) · [MCP 接入指南](https://safesellai.com/mcp-guide)

## 把工作交给 Codex

将整个 `safesellai` 文件夹放进项目的 `.agents/skills/`，或放进用户级 `~/.agents/skills/`。Windows 的 `~` 指当前用户目录。开启新会话后输入 `$safesellai`。 [Codex 技能目录说明](https://developers.openai.com/api/reference/cli)

想先体验匿名 MCP，可运行：

```sh
codex mcp add safesellai --url https://safesellai.com/mcp
```

可以直接发这样的任务：

> $safesellai 我准备上架这批 Walmart 商品。先按 SKU 核对标题商标词和 TRO，再告诉我哪些主图还要查版权或外观专利。请在结果中标出命中、未命中和未执行的维度。

> $safesellai 帮我查看已绑定的店铺。把影响上架的商品风险和近期绩效告警分别列出来，并附上需要复核的 SKU。

## 手册与开发者资料

| 手册 | 内容 |
| --- | --- |
| [网页商品排查](references/workbench.md) | 商标、Listing、批量链接、专利、版权、TRO、图形标和平台合规 |
| [店铺体检与插件](references/store-plugin.md) | 绑定授权、报告与导出、店铺告警、选品归档、批量改价改库存及插件排错 |
| [MCP 接入](references/mcp.md) | 匿名与带 Key 配置、工具发现、任务与文件调用、只读连通检查 |
| [REST 与 AI 小安](references/api-xiaoan.md) | 公开 API、AI 小安、账号用量、店铺暂停申诉 |
| 开发者附件 | [MCP 工具参数](references/mcp-tools.json) · [REST OpenAPI](references/rest-openapi.json) · [MCP 连通脚本](scripts/mcp-smoke.py) |

排查结果用于提供线索。对命中项、未查维度和资料缺口，结合原始权利记录、授权文件及目标平台规则复核。 [SafeSell AI 知识中心](https://safesellai.com/guides)

由**泽远跨境AI团队**维护。文档与示例使用 [MIT 许可](LICENSE)。SafeSell AI 在线服务、插件和数据库按各自条款使用。
