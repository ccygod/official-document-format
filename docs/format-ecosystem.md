# 多格式路线与外部借鉴

本文件记录了v1.2格式路由的设计依据和使用边界。外部仓库只借鉴公开的架构思想、格式分类和验证策略，没有复制受限代码或模板。

## 外部能力对照

| 来源 | 可借鉴部分 | 不能直接照搬的部分 | 我们的采用方式 |
|---|---|---|---|
| [KaguraNanaga/format-agent-skill](https://github.com/KaguraNanaga/format-agent-skill) | `FormatSpec × RoleMap`契约、真实OOXML属性解析、全Story预检、Style Pack、复杂结构阻断、内容保护、论文与APA/MLA/IEEE/Chicago/Turabian/技术手册/法律brief路由 | PolyForm Noncommercial许可；不能复制代码、文档或素材；它的通用格式不替代WPS母版 | 采用契约、预检和格式包思想，重新实现；保留母版保真和中文公文组件处理 |
| [zhaohui-yang/official-document-drafting](https://github.com/zhaohui-yang/official-document-drafting) | 单一`prompts/`主源、文种路由、事实/政策底线、在线/离线构建、文种样例与内容章节检查 | 主要解决起草和Markdown/Word导出；不能替代已有DOCX的精细OOXML母版迁移 | 采用格式路由、事实边界、主源和文种profile思想 |
| [zxyasfas/paper_format_agent](https://github.com/zxyasfas/paper_format_agent) | 正文/表格内容指纹、格式报告、可行动诊断、合成回归、批量处理、论文模板包 | 只聚焦论文，已知复杂对象仍有限；MIT许可可读，但不把其代码并入本仓 | 采用内容指纹、报告字段、合成陌生案例和失败诊断 |
| [jiassia/manuweave](https://github.com/jiassia/manuweave) | 路由式加载、公文/Word/LaTeX分片、原生对象保留、`UNVERIFIED`状态、复杂结构先阻断、模板来源和版本记录 | 仍需目标环境字体和渲染器；期刊模板不能当作通用规范 | 采用按需路由、状态不越级和结构分流 |
| [wzbwan/gongwen-format-skill](https://github.com/wzbwan/gongwen-format-skill) | 受控Markdown、编号由上游内容决定、明确字体/行距/页码基线 | 只面向公文，受控输入不适合直接处理任意已有Word；许可证未声明 | 作为公文输入协议的可选模式，不作为通用推断器 |

## 当前格式包

`config/format-profiles/`目前提供：

- `official_cn`：中文公文，默认从标题2开始；
- `briefing_cn`：中文汇报材料；
- `industry_report_cn`：中文行业报告；
- `academic_thesis_cn`：中文学位论文通用起点；
- `technical_manual_cn`：中文技术手册。

格式包只定义角色、相对字号、字体和行距。**每次执行仍必须选择格式包，并明确正文字号。** 标题、题注、编号和页码按格式包比例计算，不把某一公文模板的字号硬编码成全局规则。用户给正式模板时，模板优先于通用格式包。

后续可按同一契约增加`academic_apa7`、`academic_ieee`、`academic_mla`、`technical_report_en`和`legal_brief_en`，但每个新增包都需要独立合成样例、规则来源和视觉回归，不能只增加一个枚举值。

## 不同格式的选择顺序

1. 先判断任务类型：公文、汇报、行业报告、论文、技术手册或用户模板。
2. 若用户提供了单位/学校/期刊模板，优先选择“用户模板”。
3. 若没有模板，再选择通用格式包。
4. 用户确认正文字号后，才开始生成`roles.json`、格式处理和Word输出。
5. 对字号比例不同的格式，使用`body_half_points × role_ratio`；比例计算结果写入样式、文字直接格式和编号级别，并由检查器核对。

格式路由不能推断用户未说明的字号，也不能将论文缺少摘要、目录等结构误报成公文问题。格式包负责版式，语义角色仍需根据当前文档独立判断。

## 许可边界

本仓没有复制外部仓库代码。`format-agent-skill`明确使用PolyForm Noncommercial许可，不能把其代码包装成我们的原创或用于未经授权的商业再分发；`paper_format_agent`和`ManuWeave`声明MIT，但本仓仍只采用公开设计思路，避免把外部实现和本地母版混在一起。
