# Verify a formatting pass

Run from the repository root, with dependencies installed. Replace paths on Windows. The sample does not need an AI model.

```bash
python3 examples/build_demo.py /tmp/input.docx
python3 scripts/apply_official_rules.py /tmp/input.docx /tmp/once.docx --body-half-points 28
python3 scripts/check_official_document.py /tmp/once.docx --expected-half-points 28 --expected-line-multiple 1.35 --expected-before-lines 0 --expected-after-lines 25 --expected-table-after-lines 50 --require-snap-to-grid-off
python3 scripts/check_package_preservation.py /tmp/input.docx /tmp/once.docx --allow word/document.xml --allow word/styles.xml --allow word/numbering.xml
python3 scripts/apply_official_rules.py /tmp/once.docx /tmp/twice.docx --body-half-points 28
python3 scripts/check_idempotence.py /tmp/once.docx /tmp/twice.docx
```

The expected results are `PASS` from the checker, package comparison and semantic idempotence check. An existing bare reference template is a style source, not a finished document; it must contain the expected title/body/table structures before finished-document validation applies.

## Actual appearance

On a Mac with WPS installed at the usual application path:

```bash
/Applications/wpsoffice.app/Contents/MacOS/wpscli word2photo /tmp/once.docx --output /tmp/wps-pages --suffix png --dpi 150
```

Inspect every resulting page for heading/numbering size, clipping, table wrapping, captions, page breaks and footer. If WPS is unavailable, report that WPS-specific visual validation did not run. A generic renderer can provide secondary evidence.

Full-document keep-next behavior can materially change pagination. Apply `--full-pagination-controls` only when requested, pair it with `--require-full-pagination-controls` in the checker, and render again.
