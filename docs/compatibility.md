# 兼容性与安装

技能目录由SKILL.md入口、参考文件、脚本及素材组成。智能体宿主需要发现或显式加载该目录，Python脚本也可以独立执行。

## 宿主与目录

- Codex：运行`python3 scripts/install_skill.py --host codex`，复制到`~/.codex/skills/仓库名`。
- Claude Code：运行`python3 scripts/install_skill.py --host claude`，复制到`~/.claude/skills/仓库名`。
- 其他宿主：通过`--dest`传入包含技能名称的目标目录，并按宿主规则加载。

安装器遇到已有目录会停止，不覆盖用户修改，也不修改全局设置。更新前请对比并备份。卸载时仅移除该项目安装的目录，保留自己的修改。

## 运行条件

本版支持Python 3.10及以上版本；在虚拟环境中安装requirements.txt即可运行相关脚本。GitHub自动测试覆盖Linux下Python 3.10和3.12；本地页面检查使用macOS WPS，不据此承诺其他平台页貌一致。

Word交付需要文档编辑与渲染工具。Codex的Documents插件是一种选择，其他宿主可使用python-docx、直接OOXML编辑及合适的渲染器。PPT制作、生图、联网和WPS软件由外部提供，不包含在本包中。缺少必要能力时，应如实说明未验项。

面向WPS的文档，应在合法安装的WPS中渲染。LibreOffice预览可作辅助诊断，不能代替WPS特有分页验收。字体名称是样式请求，不提供字体文件或相关授权。
