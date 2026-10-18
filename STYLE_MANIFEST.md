# 公文模板反向工程契约

- Reference: `assets/reference.docx`
- SHA-256: `952efbaa17c2dacbf7dbc101987bd620c0b3b3da991e2951181ef60c8ce0e9f1`
- Package parts: 26
- Intended target: WPS Office on macOS/Windows, with DOCX/OOXML preservation

## Page system
- Section 1: page `{'w': '11906', 'h': '16838'}`; margins `{'top': '1440', 'right': '1800', 'bottom': '1440', 'left': '1800', 'header': '851', 'footer': '992', 'gutter': '0'}`; headers `[]`; footers `[]`
- Section 2: page `{'w': '11906', 'h': '16838'}`; margins `{'top': '1440', 'right': '1800', 'bottom': '1440', 'left': '1800', 'header': '851', 'footer': '992', 'gutter': '0'}`; headers `[]`; footers `[{'id': 'rId5', 'type': 'default'}]`

Interpretation: page size 11906×16838 twips (A4); margins top/bottom 1440 twips, left/right 1800 twips; header 851 twips; footer 992 twips. Two portrait sections, second section has its own footer reference.

## Style system

Every style is retained with its ID, name, basedOn, next, paragraph properties, and run properties. Raw OOXML values are authoritative; do not normalize or convert them unless a requested output explicitly needs conversion.

### `1` Normal (paragraph)
- basedOn: `None`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLine": "480", "firstLineChars": "200", "left": "0", "leftChars": "0"}, "jc": {"val": "both"}, "spacing": {"line": "300", "lineRule": "auto"}, "widowControl": {"val": "0"}}`
- run: `{"lang": {"bidi": "ar-SA", "eastAsia": "zh-CN", "val": "en-US"}, "rFonts": {"ascii": "Times New Roman", "cs": "Times New Roman", "eastAsia": "FangSong_GB2312", "hAnsi": "Times New Roman"}, "sz": {"val": "24"}, "szCs": {"val": "24"}}`
### `2` heading 1 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLineChars": "0", "hanging": "432", "left": "432"}, "jc": {"val": "center"}, "keepLines": {}, "keepNext": {}, "numPr": [{"val": "0"}, {"val": "1"}], "outlineLvl": {"val": "0"}, "spacing": {"after": "100", "afterAutospacing": "0", "afterLines": "100", "beforeAutospacing": "0", "beforeLines": "0", "line": "240", "lineRule": "auto"}}`
- run: `{"color": {"themeColor": "text1", "val": "000000"}, "rFonts": {"eastAsia": "方正小标宋简体"}, "sz": {"val": "32"}}`
### `3` heading 2 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLine": "0", "firstLineChars": "0", "left": "0", "leftChars": "0"}, "keepLines": {}, "keepNext": {}, "numPr": [{"val": "1"}, {"val": "1"}], "outlineLvl": {"val": "1"}, "spacing": {"after": "25", "afterAutospacing": "0", "afterLines": "25", "before": "25", "beforeAutospacing": "0", "beforeLines": "25", "line": "300", "lineRule": "auto"}, "tabs": [{"pos": "0", "val": "left"}]}`
- run: `{"color": {"themeColor": "text1", "val": "000000"}, "rFonts": {"ascii": "Arial", "eastAsia": "黑体", "hAnsi": "Arial"}}`
### `4` heading 3 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLine": "0", "firstLineChars": "0", "left": "0", "leftChars": "0"}, "keepLines": {}, "keepNext": {}, "numPr": [{"val": "2"}, {"val": "1"}], "outlineLvl": {"val": "2"}, "spacing": {"after": "20", "afterAutospacing": "0", "afterLines": "20", "before": "20", "beforeAutospacing": "0", "beforeLines": "20", "line": "300", "lineRule": "auto"}}`
- run: `{"b": {}, "color": {"themeColor": "text1", "val": "000000"}, "rFonts": {"ascii": "Times New Roman Bold", "eastAsia": "楷体", "hAnsi": "Times New Roman Bold"}}`
### `5` heading 4 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLine": "0", "firstLineChars": "0", "left": "0", "leftChars": "0"}, "keepLines": {}, "keepNext": {}, "numPr": [{"val": "3"}, {"val": "1"}], "outlineLvl": {"val": "3"}, "spacing": {"after": "15", "afterAutospacing": "0", "afterLines": "15", "before": "15", "beforeAutospacing": "0", "beforeLines": "15", "line": "300", "lineRule": "auto"}}`
- run: `{"color": {"themeColor": "text1", "val": "000000"}, "rFonts": {"ascii": "Arial", "eastAsia": "宋体", "hAnsi": "Arial"}}`
### `6` heading 5 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLine": "0", "firstLineChars": "0", "left": "0"}, "keepLines": {"val": "0"}, "keepNext": {"val": "0"}, "numPr": [{"val": "4"}, {"val": "1"}], "outlineLvl": {"val": "4"}, "spacing": {"afterAutospacing": "0", "beforeAutospacing": "0", "line": "240", "lineRule": "auto"}}`
- run: `{"color": {"themeColor": "text1", "val": "000000"}}`
### `7` heading 6 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLine": "1120", "firstLineChars": "200", "left": "0"}, "keepLines": {}, "keepNext": {}, "numPr": [{"val": "5"}, {"val": "1"}], "outlineLvl": {"val": "5"}, "spacing": {"afterAutospacing": "0", "afterLines": "0", "beforeAutospacing": "0", "beforeLines": "0", "line": "240", "lineRule": "auto"}}`
- run: `{"color": {"themeColor": "text1", "val": "000000"}, "rFonts": {"ascii": "Arial", "hAnsi": "Arial"}}`
### `8` heading 7 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLineChars": "0", "hanging": "1296", "left": "1296"}, "keepLines": {}, "keepNext": {}, "numPr": [{"val": "6"}, {"val": "1"}], "outlineLvl": {"val": "6"}, "spacing": {"after": "64", "afterAutospacing": "0", "afterLines": "0", "before": "240", "beforeAutospacing": "0", "beforeLines": "0", "line": "317", "lineRule": "auto"}}`
- run: `{"b": {}, "color": {"themeColor": "text1", "val": "000000"}, "rFonts": {"eastAsia": "方正仿宋_GB2312"}}`
### `9` heading 8 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLineChars": "0", "hanging": "1440", "left": "1440"}, "keepLines": {}, "keepNext": {}, "numPr": [{"val": "7"}, {"val": "1"}], "outlineLvl": {"val": "7"}, "spacing": {"after": "64", "afterAutospacing": "0", "afterLines": "0", "before": "240", "beforeAutospacing": "0", "beforeLines": "0", "line": "317", "lineRule": "auto"}}`
- run: `{"rFonts": {"ascii": "Arial", "eastAsia": "黑体", "hAnsi": "Arial"}, "sz": {"val": "24"}}`
### `10` heading 9 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLineChars": "0", "hanging": "1583", "left": "1583"}, "keepLines": {}, "keepNext": {}, "numPr": [{"val": "8"}, {"val": "1"}], "outlineLvl": {"val": "8"}, "spacing": {"after": "64", "afterAutospacing": "0", "afterLines": "0", "before": "240", "beforeAutospacing": "0", "beforeLines": "0", "line": "317", "lineRule": "auto"}}`
- run: `{"rFonts": {"ascii": "Arial", "eastAsia": "黑体", "hAnsi": "Arial"}, "sz": {"val": "21"}}`
### `20` Default Paragraph Font (character)
- basedOn: `None`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{}`
- run: `{}`
### `19` Normal Table (table)
- basedOn: `None`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{}`
- run: `{}`
### `11` toc 3 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '39'}`
- paragraph: `{"ind": {"left": "840", "leftChars": "400"}}`
- run: `{"rFonts": {"eastAsia": "楷体"}}`
### `12` footer (paragraph)
- basedOn: `{'val': '1'}`; next: `None`; qFormat: `True`; uiPriority: `{'val': '99'}`
- paragraph: `{"jc": {"val": "left"}, "tabs": [{"pos": "4153", "val": "center"}, {"pos": "8306", "val": "right"}]}`
- run: `{"sz": {"val": "18"}, "szCs": {"val": "18"}}`
### `13` header (paragraph)
- basedOn: `{'val': '1'}`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"jc": {"val": "both"}, "outlineLvl": {"val": "9"}, "spacing": {"line": "240", "lineRule": "auto"}, "tabs": [{"pos": "4153", "val": "center"}, {"pos": "8306", "val": "right"}]}`
- run: `{"sz": {"val": "18"}}`
### `14` toc 1 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '39'}`
- paragraph: `{}`
- run: `{"rFonts": {"eastAsia": "黑体"}, "sz": {"val": "32"}}`
### `15` toc 4 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"left": "1260", "leftChars": "600"}}`
- run: `{}`
### `16` toc 2 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '39'}`
- paragraph: `{"ind": {"left": "420", "leftChars": "200"}}`
- run: `{"rFonts": {"eastAsia": "黑体"}}`
### `17` Normal (Web) (paragraph)
- basedOn: `{'val': '5'}`; next: `{'val': '5'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"left": "0", "right": "0"}, "jc": {"val": "left"}, "outlineLvl": {"val": "9"}, "spacing": {"after": "15", "afterAutospacing": "0", "before": "15", "beforeAutospacing": "0"}}`
- run: `{"lang": {"bidi": "ar"}, "rFonts": {"ascii": "Arial", "eastAsia": "宋体", "hAnsi": "Arial"}}`
### `18` Title (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLine": "0", "firstLineChars": "0"}, "jc": {"val": "center"}, "outlineLvl": {"val": "0"}, "spacing": {"line": "240", "lineRule": "auto"}}`
- run: `{"b": {}, "bCs": {}, "rFonts": {"ascii": "Cambria", "eastAsia": "宋体", "hAnsi": "Cambria"}, "sz": {"val": "36"}, "szCs": {"val": "32"}}`
### `21` Strong (character)
- basedOn: `{'val': '20'}`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{}`
- run: `{"b": {}}`
### `22` Hyperlink (character)
- basedOn: `{'val': '20'}`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{}`
- run: `{"color": {"val": "0000FF"}, "u": {"val": "single"}}`
### `23` 标题 1 Char (character)
- basedOn: `None`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{}`
- run: `{"color": {"themeColor": "text1", "val": "000000"}, "rFonts": {"eastAsia": "方正小标宋简体"}, "sz": {"val": "32"}}`
### `24` 5级标题 (paragraph)
- basedOn: `{'val': '1'}`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"spacing": {"after": "25", "afterLines": "25", "before": "25", "beforeLines": "25"}}`
- run: `{"rFonts": {"eastAsia": "宋体"}}`
### `25` _Style 17 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"jc": {"val": "center"}}`
- run: `{"rFonts": {"ascii": "Arial", "eastAsia": "宋体"}, "sz": {"val": "16"}, "vanish": {}}`
### `26` _Style 18 (paragraph)
- basedOn: `{'val': '1'}`; next: `{'val': '1'}`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"jc": {"val": "center"}}`
- run: `{"rFonts": {"ascii": "Arial", "eastAsia": "宋体"}, "sz": {"val": "16"}, "vanish": {}}`
### `27` WPSOffice手动目录 1 (paragraph)
- basedOn: `None`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"leftChars": "0"}}`
- run: `{"rFonts": {"ascii": "Times New Roman", "cs": "Times New Roman", "eastAsia": "宋体", "hAnsi": "Times New Roman"}, "sz": {"val": "20"}, "szCs": {"val": "20"}}`
### `28` WPSOffice手动目录 2 (paragraph)
- basedOn: `None`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"leftChars": "200"}}`
- run: `{"rFonts": {"ascii": "Times New Roman", "cs": "Times New Roman", "eastAsia": "宋体", "hAnsi": "Times New Roman"}, "sz": {"val": "20"}, "szCs": {"val": "20"}}`
### `29` WPSOffice手动目录 3 (paragraph)
- basedOn: `None`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"leftChars": "400"}}`
- run: `{"rFonts": {"ascii": "Times New Roman", "cs": "Times New Roman", "eastAsia": "宋体", "hAnsi": "Times New Roman"}, "sz": {"val": "20"}, "szCs": {"val": "20"}}`
### `30` 图片 (paragraph)
- basedOn: `{'val': '1'}`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLine": "0", "firstLineChars": "0"}, "jc": {"val": "center"}, "spacing": {"after": "50", "afterLines": "50", "before": "50", "beforeLines": "50", "line": "240", "lineRule": "auto"}}`
- run: `{}`
### `31` 表格 (paragraph)
- basedOn: `{'val': '1'}`; next: `None`; qFormat: `True`; uiPriority: `{'val': '0'}`
- paragraph: `{"ind": {"firstLine": "0", "firstLineChars": "0"}, "jc": {"val": "center"}, "spacing": {"line": "240", "lineRule": "auto"}, "textAlignment": {"val": "center"}, "widowControl": {}}`
- run: `{"bCs": {}, "color": {"val": "000000"}, "lang": {"bidi": "ar"}, "rFonts": {"ascii": "宋体", "cs": "宋体", "eastAsia": "宋体", "hAnsi": "宋体", "hint": "eastAsia"}, "sz": {"val": "21"}, "szCs": {"val": "22"}, "u": {"val": "none"}}`

## Named roles

- `Normal`: default body role; East Asia `FangSong_GB2312`, Latin `Times New Roman`, 24 half-points, both alignment, firstLine 480 twips / firstLineChars 200, line 300 with auto lineRule.
- `heading 1`: centered, outline level 0, 方正小标宋简体, 32 half-points, keepNext/keepLines.
- `heading 2`: outline level 1, 黑体, paragraph before/after 25 lines, line 300, keepNext/keepLines.
- `heading 3`: outline level 2, 楷体, bold, before/after 20 lines, line 300, keepNext/keepLines.
- `heading 4`: outline level 3, 宋体, before/after 15 lines, line 300, keepNext/keepLines.
- `heading 5`: outline level 4; inherits Normal, explicit keepNext/keepLines off, line 240.
- `5级标题`: custom fifth-level title style, 宋体, before/after 25 lines.
- `toc 1`–`toc 4`: TOC role styles; toc1 black体 32 half-points, toc2 black体 with 420-char indent, toc3 楷体 with 840-char indent, toc4 1260-char indent.
- `WPSOffice手动目录 1/2/3`: WPS manual TOC roles with Times New Roman + 宋体 and 0/200/400 char indents.
- `图片`: centered, before/after 50 lines, line 240.
- `表格`: centered, 宋体, 21 half-points East Asia and 22 half-points CS, line 240.
- `表格正文`: derived from `表格` for wrapped prose cells only; first-line indent 420 twips, justified alignment, same font and line spacing. Keep serial numbers, short labels, dates, and statuses on `表格` centered.
- `Title`: centered, Cambria/宋体, 36/32 half-points, outline level 0.
- Title-block rule: do not invent a subtitle or annotation. Preserve a source-marked subtitle only; when the source uses the parenthesized convention, keep it centered in parentheses.

## Components and fields

- TOC field: `TOC \o "1-4" \h \u`.
- Sample hyperlink field: `HYPERLINK \l _Toc25206`.
- Sample page reference: `PAGEREF _Toc25206 \h`.
- Footer page number is inside a WPS drawing text box with a VML fallback; preserve `AlternateContent` and both branches.
- Inserted-table contract: add a separate centered table-title paragraph immediately before the table (`表1  ……`, `表2  ……`, sequentially numbered, same font/size/color and regular weight as figure captions, using the named 图片 style); every `w:tc/w:p` must carry the effective `表格` or `表格正文` style; the first `w:tr` must contain `w:tblHeader` and `w:cantSplit`; use explicit black borders, black text, and white cells with no blue, gray, or theme-color shading. Use `表格` for short values, names, dates, statuses, and compact enumerations; use `表格正文` for wrapped prose with sentence punctuation or long enumerations of at least 20 Chinese characters containing `、`, with first-line indent and justified alignment. The writer and checker must share this predicate. Use content-driven `tblGrid`/`tcW` widths: compute each minimum from the longest unbreakable cell plus margins, keep index/序号 columns narrow, and allocate remaining width to long description columns; never split width evenly by default. A table that only looks right in WPS while its cell paragraphs are still `Normal`/`正文` fails semantic QA.
- Inserted-image contract: the paragraph containing `w:drawing` and the separate `图1  ……` caption paragraph must both carry the effective `图片` style. Keep the image relationship and rendered extent verifiable in WPS.
- Chinese–English boundary contract: remove spaces at the boundary (`WPS中`, `Word表格`, `公文格式Skill`), while preserving spaces internal to an English phrase.

## Font and package preservation

The source has 30 font-table entries, including 黑体, 楷体, 仿宋_GB2312, 方正仿宋_GB2312, 方正小标宋简体, 汉仪楷体KW, 汉仪书宋二KW, 苹方-简, PingFang SC, Times New Roman and fallbacks. It contains `word/fonts/font1.odttf`, `word/fontTable.xml`, `word/customizations.xml`, `customXml/*`, WPS namespace data, and theme/settings parts. Preserve all untouched parts and relationships byte-for-byte where possible.

## Shortcut/customization evidence

- `word/customizations.xml` contains 10 `wne:keymap` entries and 20 `wne:acd` entries.
- The package stores `kcmPrimary`, `acdName`, `argValue`, and `fciIndexBasedOn` values, but does not contain human-readable shortcut names or a WPS command registry. Record these raw values; do not invent a shortcut mapping. WPS application-level shortcuts are outside this DOCX and must be audited separately in the WPS installation/profile.

## Content inventory

- Body paragraphs: 24; tables: 0; inline images: 0; sections: 2.
- Several sample paragraphs use direct run formatting that overrides style defaults. The skill must distinguish style defaults from direct formatting and apply direct formatting only when the source pattern calls for it.

## Fidelity gates

1. Do not save the retained source through python-docx or LibreOffice.
2. Build from a copy and patch only intended XML nodes.
3. Preserve WPS extensions, embedded fonts, fields, relationships, numbering, theme, custom XML, headers/footers, and AlternateContent.
4. Validate in WPS, then compare package inventory and targeted XML against the source.
5. Check title/body/headings 1–5, TOC, page number, images, tables, line spacing, paragraph spacing, indentation, tabs, pagination, and font fallback on both macOS and Windows WPS.

## Public distribution variant

Sample identities and document properties are sanitized. Embedded font binaries are omitted. Use legally available local fonts and verify fallback in the target renderer. The retained style definitions, numbering, sections and WPS extensions remain the formatting reference.
