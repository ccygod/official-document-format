# v1.2.0 多格式文档格式Skill

本版本把`official-document-format`从单一公文路径扩展为可选择格式的文档排版入口。用户现在必须先选择格式包或提供正式模板，再确认正文字号，处理才会开始。

新增格式包：

- `official_cn` 中文公文；
- `briefing_cn` 中文汇报材料；
- `industry_report_cn` 中文行业报告；
- `academic_thesis_cn` 中文学位论文通用起点；
- `technical_manual_cn` 中文技术手册。

格式包把字体、相对字号、行距、缩进和编号行为结构化；正文字号由用户确认，标题、编号、题注按比例计算。外部借鉴包括Format Agent的FormatSpec/RoleMap和预检边界、official-document-drafting的单一主源与文种路由、Paper Format Agent的内容指纹和报告诊断、ManuWeave的路由与UNVERIFIED状态。没有复制外部代码；格式包仍以用户正式模板优先。

本版本新增/修复：

- 实际文字直接格式、主题字体冲突和分页控制关闭值的检查；
- 短字段和长时间安排的内容驱动列宽；
- 统一pipeline入口与失败不交付机制；
- 完整角色清单、复杂结构预检分流、表题显式输入和组件准备；
- 47项自动化测试、独立陌生材料、四组历史材料和WPS页面回归。

仍需注意：模型负责语义角色判断，角色清单需要独立复核；内容控件、文本框、修订、多节复杂结构和合并单元格仍然分流；结构通过不等于WPS视觉通过。
