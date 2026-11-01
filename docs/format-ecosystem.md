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

第二轮审计又对照了几类“验证优先”的实现：

| 来源 | 审计得到的补充规则 | 本仓落地 |
|---|---|---|
| [Dmitry-Kov/ooxml-integrity](https://github.com/Dmitry-Kov/ooxml-integrity) | 只做结构一致不够，还要对比原件与成品的构造计数、关系、批注、脚注和修订；修复必须写入副本并再次检查 | 继续保留源哈希、正文内容指纹、包部件保护和二次幂等检查；复杂对象改为阻断或保留警告分流 |
| [ooxml-tools/validate](https://github.com/ooxml-tools/validate) | 可按 Office 版本做 OOXML 包级校验，验证器应与版式检查分开 | 将结构检查、WPS视觉检查和可选外部OOXML验证列为三层证据，不把其中一层冒充另外两层 |
| [AnswerDotAI/oxml](https://github.com/AnswerDotAI/oxml) | 原生对象、关系和未建模部件需要明确的保留边界；遇到修订、字段、节和依赖不能猜测修复 | 全Story inventory、`requires_specialist_review`与`preserve_only_warnings`分开；文本框/外部关系保留但必须视觉复核 |
| [Microsoft Agent Academy document skill](https://github.com/microsoft/agent-academy/blob/main/docs/operative-nextgen/06-document-skill/index.md) | 内容采集、JSON结构化、脚本生成和证据等级分层，减少模型直接改Word的自由度 | 先生成完整`roles.json`，再由确定性脚本执行；报告明确“结构通过、视觉待验收” |
| [wksudud/format-thesis-docx](https://github.com/wksudud/format-thesis-docx/blob/main/SKILL.md) / [h46373824-tech/format-thesis-docx-skill](https://github.com/h46373824-tech/format-thesis-docx-skill) | 先提取要求和审计，再在副本执行；低置信度规则暂停，保留未解决项和格式清单 | 格式包必须显式选择；不确定标题层级与复杂对象不通过“猜测”放行，报告保留可追溯字段 |

第三轮底层OOXML对照又补充了几条会影响WPS稳定性的规则：

| 来源 | 底层规则 | 本仓落地 |
|---|---|---|
| [arih04x/office-skills/office-docx](https://github.com/arih04x/office-skills/blob/main/office-docx/SKILL.md) | 源文件副本、模板样式/主题/编号迁移、OpenXML包检查和最终独立渲染要分层；样式应先定义再通过style ID使用 | 统一入口始终写副本；格式包、母版导入、结构检查、WPS渲染分成独立证据层 |
| [SecurityRonin/docx-mcp](https://github.com/SecurityRonin/docx-mcp/blob/main/docx_mcp/skill/SKILL.md) | `w:pPr`子元素有规范顺序；修订、批注和编号不能依赖高层库的隐式行为；标题编号应来自多级编号系统 | 增加`pPr`顺序规范化和顺序负例检查；自动编号使用母版编号定义，人工编号与自动编号重复时先归一化 |
| [hawa130/docx-master](https://github.com/hawa130/docx-master-src) | overview/inspect_blockers/inspect_style_def/inspect_table/validate分工具分层；样式指纹、模式规则和只读审计先于写入 | `inspect`、全Story inventory、复杂对象分流、角色清单、确定性执行和结构报告形成同一条门链 |
| [KaiserY/ooxmlsdk COMPATIBILITY](https://github.com/KaiserY/ooxmlsdk/blob/main/COMPATIBILITY.md) | 字段、节、批注、宏、keep属性、样式继承、合并单元格和编号都应按可回写能力逐项记录 | 这些对象进入保留警告或专门处理清单；不把“Word能打开”当成结构保真证明 |

这些仓库的许可证和目标范围不同，本项目只吸收公开的流程思想；没有复制代码、模板或受限素材。OOXML语义仍以[ECMA-376](https://ecma-international.org/publications-and-standards/standards/ecma-376/)和Microsoft对`keepNext`、主题字体及`rFonts`优先级的说明为准。

表格本体、表格网格和列宽的关系进一步参照了[Microsoft WordprocessingML tables](https://learn.microsoft.com/en-us/office/open-xml/word/working-with-wordprocessingml-tables)；样式编号定义的优先级参照了[ParagraphStyleIdInLevel](https://learn.microsoft.com/en-gb/dotnet/api/documentformat.openxml.wordprocessing.paragraphstyleidinlevel?view=openxml-2.13.1)。

## 当前格式包

`config/format-profiles/`目前提供：

- `official_cn`：中文公文，默认从标题2开始；
- `briefing_cn`：中文汇报材料；
- `industry_report_cn`：中文行业报告；
- `academic_thesis_cn`：中文学位论文通用起点；
- `technical_manual_cn`：中文技术手册。

格式包只定义角色、相对字号、字体和行距。**每次执行仍必须选择格式包，并明确正文字号。** 标题、题注、编号和页码按格式包比例计算，不把某一公文模板的字号硬编码成全局规则。用户给正式模板时，模板优先于通用格式包。

自动序号不再隐含在格式选择里，而是独立的强制选项：`automatic`复用母版中带编号定义的预设标题样式，`manual`移除有效自动编号并保留原文人工编号。表格本体默认使用表格级居中属性，单元格内部的居中/两端对齐仍按语义列类型处理。

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
