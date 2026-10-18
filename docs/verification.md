# 格式处理与验收

在仓库根目录运行。先安装依赖，Windows请把示例中的/tmp路径替换成可写本地路径。

```bash
python3 examples/build_demo.py /tmp/input.docx
python3 scripts/apply_official_rules.py /tmp/input.docx /tmp/once.docx --body-half-points 28
python3 scripts/check_official_document.py /tmp/once.docx --expected-half-points 28 --expected-line-multiple 1.35 --expected-before-lines 0 --expected-after-lines 25 --expected-table-after-lines 50 --require-snap-to-grid-off
python3 scripts/check_package_preservation.py /tmp/input.docx /tmp/once.docx --allow word/document.xml --allow word/styles.xml --allow word/numbering.xml
python3 scripts/apply_official_rules.py /tmp/once.docx /tmp/twice.docx --body-half-points 28
python3 scripts/check_idempotence.py /tmp/once.docx /tmp/twice.docx
```

检查器、部件比较和幂等检查预期输出PASS。裸母版是样式来源，不是完整成品；完成内容与结构编排后才适用成品检查。

## 实际页面

已安装macOS WPS时可运行：

```bash
/Applications/wpsoffice.app/Contents/MacOS/wpscli word2photo /tmp/once.docx --output /tmp/wps-pages --suffix png --dpi 150
```

逐页核查标题、编号大小、文字裁切、表格换行、图注、分页和页脚。WPS不可用时如实说明，其他渲染器可补充证据，不能代替WPS特有验收。

全文与下段同页可能显著改变分页，仅在用户要求时用--full-pagination-controls，并搭配检查器的--require-full-pagination-controls，之后重渲染。
