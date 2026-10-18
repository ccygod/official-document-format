# Release validation — v1.0.0

Checked locally on 2026-10-18, macOS, against the public package.

| Check | Observed result |
| --- | --- |
| Python regression suite | 8 tests passed |
| Fresh installation and existing-directory protection | Covered by three installation tests |
| Skill frontmatter | Checked with the local skill validator |
| Relative Markdown file links | Checked against repository files |
| Public package text and DOCX XML | Scanned for local paths, client names and credential-like content |
| GitHub Actions | Linux / Python 3.10 and 3.12 workflow provided; inspect the actual run on the repository |

## Document-specific evidence

The fictional demo passes the declared body-size, spacing, grid and table/heading checks. Package changes are confined to document.xml, styles.xml and numbering.xml. A second normalization pass has an identical semantic snapshot. A deliberately wrong body size is rejected.

The sanitized style template rendered to three pages, and the completed fictional demo rendered to one page in WPS on macOS. Every resulting page was inspected. The README preview is derived from that actual fictional demo. This does not establish identical layout on Windows, Microsoft Word or another font installation.

Public distribution intentionally differs from the private reference: generic text and cleaned identity metadata, no embedded font binary. The original installed reference remains unchanged.
