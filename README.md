# 公文格式skill · Official Document Skill

<div align="center">

**Carry a carefully designed Word/WPS template into every document you deliver.**

![公文格式skill · Official Document Skill release artwork](assets/cover.png)

[![Tests](https://github.com/ccygod/artifact-template-wps/actions/workflows/tests.yml/badge.svg)](https://github.com/ccygod/artifact-template-wps/actions/workflows/tests.yml)
![License](https://img.shields.io/badge/license-MIT-16796f)
![Python](https://img.shields.io/badge/python-3.10%2B-3776ab)
![Release](https://img.shields.io/github/v/release/ccygod/artifact-template-wps)

[Quick start](#quick-start) · [Examples](#see-the-difference) · [中文说明](README.zh-CN.md) · [Releases](https://github.com/ccygod/artifact-template-wps/releases)

</div>

## Make the formatting part repeatable

A document can look almost right and still carry the wrong heading role, a smaller numbering symbol, a split table row or a damaged footer. This skill combines a retained template with deterministic OOXML checks, so those details can be reviewed before delivery.

Designed for Chinese project proposals, institutional briefings and formal documents in Word/WPS workflows. The profile captures a maintainer-designed style system; it is not a certification against every official-document standard.

## See the difference

![Actual fictional demo rendered in WPS](assets/demo-preview.png)

*An original fictional demo, rendered with WPS on macOS. Font availability and renderer versions can change page appearance.*

| Detail that drifts | What the workflow checks |
| --- | --- |
| Heading text and numbering use different sizes | Numbering-level typography follows the requested heading/body size |
| Body indentation leaks into headings | Body and heading roles remain distinct |
| Tables lose meaning or pagination | Caption, cell roles, geometry and row controls are reviewed |
| DOCX looks fine but loses package parts | Changes are compared against an explicit allowlist |
| Repeated processing keeps changing the file | A second pass is checked for semantic idempotence |

## Quick start

```bash
git clone https://github.com/ccygod/artifact-template-wps.git
cd artifact-template-wps
python3 -m pip install -r requirements.txt
python3 scripts/install_skill.py --host codex
```

For Claude Code use `--host claude`. For another host, specify `--dest /your/skills/artifact-template-wps`. Existing installations are not overwritten. [Compatibility →](docs/compatibility.md)

Ask your agent:

```text
Use $artifact-template-wps to format this final proposal.
Body size: 14 pt (四号). Preserve the title size.
Use the bundled public template and retain its style hierarchy.
Run the format checks and render the result in WPS.
Report any verification step that could not run.
```

**A concrete body size is required before typography changes.** The template’s original size is not an implicit user decision. Contents and requested deviations come from your current materials.

## Try it in 3 minutes

The demo uses fictional text and the bundled style system. It does not call a model or paid API.

```bash
python3 examples/build_demo.py /tmp/official-demo-input.docx
python3 scripts/apply_official_rules.py \
  /tmp/official-demo-input.docx /tmp/official-demo.docx \
  --body-half-points 28
python3 scripts/check_official_document.py /tmp/official-demo.docx \
  --expected-half-points 28 --expected-line-multiple 1.35 \
  --expected-before-lines 0 --expected-after-lines 25 \
  --expected-table-after-lines 50 --require-snap-to-grid-off
```

Expected checker output: `PASS`. Open the file in Word or WPS and inspect the pages. On Windows, replace `/tmp/...` with a writable local path. [Full validation workflow →](docs/verification.md)

## How it works

`Inspect template → resolve roles → edit a copy → normalize → check → render`

The retained DOCX keeps styles, numbering, sections, fields, footers and WPS extensions. A format pass updates declared properties; package checks expose unexpected changes. The agent still has to place content, plan title breaks, insert appropriate figures and tables, and inspect actual pagination.

**The normalizer is a postprocessor, not a one-command document writer.** It does not infer missing headings, author content or rebuild a damaged table of contents. Use the demo builder only for its fictional example.

## Included checks

- Body/heading size, numbering parity, line and paragraph spacing.
- Grid snapping and requested pagination controls.
- Manual/automatic numbering collisions.
- Caption and table paragraph semantics.
- Unchanged package parts and repeated-pass semantic stability.

```bash
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

## Public template and fonts

The release template uses generic institutions and project text. Private identity metadata and the embedded font binary were removed. Font family names remain in the style system; install legally available fonts or explicitly choose a suitable local substitute, then render again.

The main proposal title has its own size. Body and heading 1–5 follow the explicit body-size contract. The profile uses 1.35-line spacing unless the current task overrides it. These are this profile’s choices, not universal legal requirements.

[Template anatomy](STYLE_MANIFEST.md) · [WPS preservation](WPS_OOXML_PRESERVATION.md) · [Attribution](NOTICE.md)

## Compatibility and evidence

Local scripts need Python 3.10+ and `lxml`. A DOCX editing tool and renderer are external. Word and WPS can differ in fonts and pagination; the release’s visual evidence comes from WPS on macOS. Structural tests cannot establish the same appearance in another environment.

[Validation record](docs/validation.md) · [Compatibility](docs/compatibility.md) · [Contribute](CONTRIBUTING.md) · [Get help](SUPPORT.md)

Built and maintained by [ccygod](https://github.com/ccygod). Pair it with [Lecture](https://github.com/ccygod/lecture) for spoken material and page briefs. [Launch kit](docs/launch-kit.md) · [MIT license](LICENSE)
