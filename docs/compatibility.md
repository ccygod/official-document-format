# Compatibility and installation

These are Agent Skills: a `SKILL.md` entry plus references, scripts and optional assets. An agent host must discover or explicitly load the directory. The Python helper scripts can also be used directly.

## Hosts

- Codex: `python3 scripts/install_skill.py --host codex` copies to `~/.codex/skills/<repository-name>`.
- Claude Code: `python3 scripts/install_skill.py --host claude` copies to `~/.claude/skills/<repository-name>`.
- Other hosts: `python3 scripts/install_skill.py --dest /your/host/skills/<repository-name>`; follow that host’s discovery rules. Metadata under `agents/` is host-specific.

The installer refuses to overwrite an existing directory. Review updates against a backup of your own rules. No global settings are modified. To remove, delete only the directory installed by this project after preserving your changes.

## Python

Python 3.10+ is the supported baseline for this release. Install `requirements.txt` in your preferred virtual environment. The macOS release check is local evidence; GitHub Actions exercises the declared Linux Python matrix. Other native desktop combinations are not claimed as visually verified.

## Optional tools

A DOCX writer and renderer are needed for Word deliverables. In Codex, Documents can provide these; another host can use python-docx or direct OOXML plus a suitable renderer. PowerPoint construction, web research, image generation and WPS Office are separate capabilities, not bundled services. If a required capability is unavailable, report the unverified step.

For WPS-targeted output, use an authorized WPS installation to render. A LibreOffice preview is useful diagnostic evidence but does not establish WPS-specific pagination. Font names are style requests; font files must be legally installed locally.
