# v1.2.3 multi-document-format：底层OOXML与WPS回归

本版本把技能从“公文格式入口”正式改成多格式文档入口。仓库URL继续使用`official-document-format`以保持已有下载和历史引用有效；技能调用名改为`multi-document-format`，旧调用名继续作为兼容别名。

## 第三轮参考与落地

- 对照[office-docx](https://github.com/arih04x/office-skills/blob/main/office-docx/SKILL.md)，把副本、模板迁移、OpenXML检查和最终渲染拆成独立证据层。
- 对照[docx-mcp](https://github.com/SecurityRonin/docx-mcp/blob/main/docx_mcp/skill/SKILL.md)，补充`w:pPr`子元素顺序检查、修订/批注保留边界和多级编号规则。
- 对照[docx-master](https://github.com/hawa130/docx-master-src)，补充overview、阻断对象、样式定义、表格检查和validate的分层思想。
- 对照[ooxmlsdk兼容性矩阵](https://github.com/KaiserY/ooxmlsdk/blob/main/COMPATIBILITY.md)，继续将字段、节、批注、宏、keep属性、样式继承、合并单元格和编号按可回写能力分流。
- 依据[Microsoft WordprocessingML tables](https://learn.microsoft.com/en-us/office/open-xml/word/working-with-wordprocessingml-tables)和[ParagraphStyleIdInLevel](https://learn.microsoft.com/en-gb/dotnet/api/documentformat.openxml.wordprocessing.paragraphstyleidinlevel?view=openxml-2.13.1)，保留表格`tblPr`/`tblGrid`分层和样式编号定义优先级。

本仓只吸收公开流程和OOXML语义规则，没有复制外部代码、模板或受限素材。

## 本次实现

- `SKILL.md`、Codex默认提示、安装器和文档统一使用`multi-document-format`。
- 安装器默认目标改为`multi-document-format`；已有`official-document-format`目录可以继续作为兼容安装。
- 新增共享`pPr_order.py`，在写入前规范化段落属性顺序；检查器对顺序错误给出明确失败信息。
- 继续保留自动/手动编号选择、表格级居中、原文人工编号归一化和复杂对象分流。

## 验证

- Python单元测试：55项通过。
- 五种格式 × 两种编号模式 × 五类材料：50/50结构执行通过。
- 正文14磅五格式矩阵通过。
- WPS五格式批量渲染成功；自动编号、手动编号、完整公文和历史方案均有渲染证据。
- 本机安装目录同步到`/Users/apple/.codex/skills/multi-document-format`并通过本机测试；旧目录保留兼容入口。
