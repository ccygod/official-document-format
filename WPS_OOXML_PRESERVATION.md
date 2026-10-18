# WPS OOXML preservation rules

This template targets WPS Office on macOS and Windows. The retained `assets/reference.docx` is authoritative.

## Authoring stack

- Read and inventory with `python-docx` and `zipfile`/`lxml`.
- Author by copying the reference and patching only intended XML nodes with `zipfile`/`lxml`.
- Do not save the retained or working source through `python-docx`, LibreOffice, Pandoc, HTML-to-DOCX, or a blank-document rebuild.
- Use LibreOffice rendering only as a secondary diagnostic. Final acceptance requires opening the result in WPS.

## Preserve these package features

Keep all untouched package parts and relationships, especially `word/styles.xml`, `word/numbering.xml`, `word/settings.xml`, `word/fontTable.xml`, `word/fonts/font1.odttf`, `word/footer1.xml`, `word/customizations.xml`, `customXml/*`, theme parts, fields, and `mc:AlternateContent` WPS/VML branches.

## Slot rules

- Body paragraphs use the retained `Normal` role unless the source pattern explicitly calls for direct formatting.
- Use the retained heading ladder and preserve each style ID, outline level, numbering, keep behavior, spacing, indentation, tab stops, and font mapping.
- Keep `TOC`, `HYPERLINK`, `PAGEREF`, and page fields as fields; do not replace them with plain text unless the user explicitly requests a static copy.
- Insert pictures through the retained `图片` paragraph role and tables through the retained `表格` role, preserving surrounding paragraph properties.
- Distinguish style defaults from direct run/paragraph formatting. Direct formatting in sample paragraphs is not a new global style.

## Shortcut boundary

`word/customizations.xml` contains raw `wne:keymap` and `wne:acd` records. The DOCX stores opaque command codes (`kcmPrimary`, `argValue`, `fciIndexBasedOn`) but no human-readable WPS command registry. Preserve these records exactly; do not invent a shortcut mapping. WPS application-level shortcut settings must be audited in the WPS profile separately.

## Acceptance checks

After generating a document, verify in WPS:

1. A4 geometry, margins, header/footer distances, and section breaks.
2. Font names and fallback behavior for 黑体、楷体、仿宋_GB2312、宋体 and Times New Roman.
3. Body line spacing, first-line indentation, heading spacing, numbering and keep behavior.
4. TOC links/page references and footer page number rendering.
5. Picture and table placement, wrapping, pagination and style inheritance.
6. No unexplained package-part or relationship loss compared with the reference.

## Heading regression rules

- A heading paragraph (`heading 1` through `heading 5`) must not carry the body paragraph's direct `firstLine=480` or `firstLineChars=200`. Two-character first-line indentation belongs to body paragraphs only. Numbered heading indentation comes from the heading's numbering definition and its intended hanging/left settings.
- For an inline level-5 label such as `时间安排：正文` or `阶段性成果：正文`, keep the paragraph in the level-5 structural role, split at the first full-width colon, apply the level-5 label emphasis to the first run, and apply the Normal/body run properties to the suffix. The suffix must not inherit heading emphasis.
- If the level-5 label is followed by a separate paragraph, keep the label paragraph and body paragraph separate; do not merge them.
- Run `scripts/check_official_document.py <docx>` before delivery. It must pass alongside the normal package and visual checks.

## Numbering de-duplication gate

A paragraph may have exactly one numbering authority:

- **OOXML numbering authority:** if `w:numPr` is present, it supplies the marker. Remove a matching literal marker at the beginning of the text before applying or preserving `w:numPr`.
- **Source-text authority:** if the source already contains a leading marker and no `w:numPr`, preserve the literal marker and do not add automatic numbering.

Recognized leading markers include Arabic forms such as `（1）`, `(1)`, `1.` and `1、`, and Chinese forms such as `（一）` and `一、`. Only a marker at the beginning of a paragraph is eligible; dates, prose parentheses, and markers in the middle of text are untouched.

Run `scripts/normalize_heading_markers.py input.docx output.docx` when converting a source-text list to OOXML numbering, then run `scripts/check_official_document.py`. The checker must fail if a paragraph contains both `w:numPr` and a recognized manual marker.

## Body-size and visual-scale gate

Before changing a document, resolve the requested body size from the user's instruction. If no body size is stated, ask before changing typography. Once the size is known, apply the same size to `Normal`, heading 1–5, and the custom fifth-level heading role; preserve the main `Title` size unless the user explicitly changes it.

When the size changes from the source baseline, compute a scale ratio from the old body size to the new body size. Scale real image/figure extents by that ratio when present. Do not scale page-number text boxes or other document furniture as if they were images. If the package has no real image/figure relationships, record that no graphic scaling was needed.

For a 14-point body, the OOXML size value is 28 half-points. Run `scripts/check_official_document.py <docx> --expected-half-points 28` for this contract.

## WPS visual verification

For WPS-targeted documents, supplement the generic renderer with the installed WPS CLI:

```bash
/Applications/wpsoffice.app/Contents/MacOS/wpscli word2photo input.docx --output wps-render --suffix png --dpi 150
```

Inspect every WPS-rendered page for duplicate markers, clipped text, unexpected page breaks, heading/body size consistency, footer/page numbers, and image scaling. The WPS-rendered page count is the primary pagination signal; LibreOffice output is secondary diagnostics only.

## Heading numbering font and title line-break rules

- Numbering symbols are rendered from `word/numbering.xml`, not only from paragraph or heading style runs. When the body/heading size changes, update the `w:lvl/w:rPr/w:sz` and `w:szCs` values for the heading numbering levels used by the document; otherwise `一、`, `（一）`, and `1.` can remain smaller than the heading text.
- Do not insert a page break between the title block and the opening body paragraph unless the user explicitly requests a cover page. Remove title-block-only `w:br w:type="page"` paragraphs before WPS pagination QA.
- For multi-line official-document titles, preserve complete semantic units and proper nouns. Prefer three-line or two-line trapezoid/diamond-like balance over mechanical equal-width wrapping. For a generic example, group `示例机构` / `项目建设方案` by meaning; plan the actual title from the current request.
- Title line breaks should be explicit only after semantic planning; do not allow an automatic wrap to split an institution name, unit name, or compound term.

## Heading weight and spacing

- Level-2 headings use regular 黑体, not bold; the level-2 numbering symbol must use the same regular weight.
- Keep exactly one empty Normal-style paragraph between the top title block (main title and subtitle) and the opening body paragraph. Do not add blank paragraphs after level-1 through level-5 hierarchy headings, and do not add one when a level-5 label and its body share the same paragraph.

## v2 semantic pipeline

Use this order for every new template application:

1. **Fingerprint** the package parts, relationships, styles, numbering, sections, embedded fonts, WPS extensions and media.
2. **Resolve effective properties** by following `basedOn`, style aliases, paragraph direct formatting, run direct formatting, and numbering-level run properties.
3. **Classify roles** from style type/name, outline level, numbering level, content shape and neighboring paragraphs. Do not rely on fixed Style IDs or one `abstractNumId`.
4. **Write a change plan** containing requested overrides, affected parts, unresolved ambiguities and expected visual effects.
5. **Patch atomically** on a copy; preserve all unlisted parts and relationships.
6. **Run semantic checks**, package preservation checks, and the idempotence check.
7. **Render with WPS** and inspect every page. A successful XML check cannot replace WPS visual QA.

Reusable tools:

- `scripts/apply_official_rules.py` — deterministic postprocessor for body size, numbering parity, line spacing, snap-to-grid, pagination controls, white table cells and `表格`/`表格正文` classification. Use it after content placement and before semantic checks; do not ask the model to reproduce these XML mutations from prose.
- `scripts/table_semantics.py` — shared table-cell predicate used by the writer and checker, so style assignment and acceptance criteria cannot drift apart.
- `scripts/inspect_effective_styles.py` — inspect effective roles, inherited styles, sizes and numbering mappings.
- `scripts/check_official_document.py` — semantic regression checks.
- `scripts/normalize_heading_markers.py` — remove manual markers only when effective OOXML numbering exists.
- `scripts/check_package_preservation.py` — enforce an explicit changed-part allowlist.
- `scripts/check_idempotence.py` — verify that a second run has the same semantic snapshot.

## Table and image component rules

- Do not rely on an external table style name such as `Table Grid` being present in the retained template. Emit explicit table borders, cell margins, vertical alignment, header shading, and wrapping properties when inserting a table.
- Verify real table geometry and image relationships in WPS, not only in XML. A table with text but no visible borders is a compatibility failure.
- For images, preserve the image relationship and drawing anchor/inline extent. Scale only the image extent when a body-size override requires proportional scaling; keep page-number text boxes and other document furniture unchanged.

## Normal table and caption policy

For the current WPS公文格式 variant:

- Table-cell paragraphs use `表格` for short values and `表格正文` for narrative prose, following the shared predicate in `scripts/table_semantics.py`.
- Use white cells, black text, light-gray borders, and a bold black header row without colored fills.
- Place a figure caption in a separate centered paragraph using the retained `图片` style role, normally below the image as `图 N 说明`.
- Compute column widths from content length with minimum widths for short fields, extra width for narrative fields, and a page-width cap. Recalculate after wrapping and verify in WPS; do not use equal-width columns by default.

## Shared table-title and figure-caption typography

Table titles outside tables use the same named `图片` paragraph style and regular run typography as figure captions. Resolve existing figure-caption formatting, including direct overrides, through `scripts/caption_format.py`; when no figure caption exists, resolve the `图片` style. The deterministic normalizer applies this rule and the checker verifies font, size, weight and color parity. Cell styles `表格` and `表格正文` apply only to paragraphs inside cells.

After each table, apply a small `w:beforeLines` gap to the first following paragraph (the current official-document baseline is 50 hundredths of a line (0.5 line)) so the paragraph does not visually touch the table border. Do this on the following paragraph itself; do not insert blank paragraphs that disturb pagination.
