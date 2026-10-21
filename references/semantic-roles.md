# 语义角色与定位

清单针对工作副本中全部非空正文直接段落。表格、图注等由组件规则处理；复杂容器由入口分流。内容保持一致时可用完整文字定位，同名段落必须加一基的`occurrence`；遗漏、歧义和不存在的段落应失败。

```json
{"complete": true, "paragraphs": [
  {"text":"技术交流安排","role":"title"},
  {"text":"交流目标","role":"heading-2","numbering":"template"},
  {"text":"围绕课程应用开展交流。","role":"body"},
  {"text":"课程案例讨论","role":"heading-3","numbering":"template"}
]}
```

允许角色：title、body、heading-1至heading-5。默认顶层为heading-2。不要预设出现某个词就必须是标题，独立核对全文语义；清单和执行程序一致不代表语义正确。

准备副本时移除自动编号将要替代的文字标记，并记录允许变化；不要删除正文条款号、日期或顺序号。模板层级决定编号形式，原稿外观不是唯一依据。

WPS在macOS拒绝CLI访问普通路径时，可把QA副本放入WPS自己的Data/tmp目录后渲染，确认其哈希与成品一致。此操作只是本地验收，不上传外部服务。
