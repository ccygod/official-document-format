#!/usr/bin/env python3
"""Semantic regression checks for WPS official-document output."""
from zipfile import ZipFile
from lxml import etree
import argparse,re,sys
from ooxml_model import OOXMLModel, q, ns
NS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
MARKER=re.compile(r'^\s*(?:(?:\(\s*\d+\s*\)|（\s*\d+\s*）)|(?:\d+\s*[\.、）)])|(?:\(\s*[一二三四五六七八九十百千万]+\s*\)|（\s*[一二三四五六七八九十百千万]+\s*）)|(?:[一二三四五六七八九十百千万]+\s*[、\.）)]))\s*')
TABLE_TITLE=re.compile(r'^表\s*\d+\s{1,3}\S+')
ZH_EN_SPACE=re.compile(r'(?<=[\u4e00-\u9fff])\s+(?=[A-Za-z])|(?<=[A-Za-z])\s+(?=[\u4e00-\u9fff])')
from table_semantics import is_prose_cell
from caption_format import CAPTION, caption_profile, effective_run, signature
from structure_rules import structure_failures
from semantic_contract import role_map_failures, indent_failures
from policy import POLICY
from effective_format import enabled, typography_failures, paragraph_props
from format_profiles import load_profile, role_half_points
def bold(el): return el is not None and any(n is not None and n.get(q('val')) not in {'0','false','off'} for n in (el.find(q('b')), el.find(q('bCs'))))
def main(path, expected_half_points=None, require_full_pagination_controls=False, expected_line_multiple=None, require_snap_to_grid_off=False, expected_before_lines=None, expected_after_lines=None, expected_table_after_lines=None, keep_toc=False, keep_bullets=False, heading_start=2, role_map=None, expected_heading_indent_chars=2, format_profile=None):
 m=OOXMLModel(path); failures=[]; records=list(m.paragraphs())
 if role_map: failures.extend(role_map_failures(m,role_map))
 failures.extend(indent_failures(m,expected_heading_indent_chars))
 failures.extend(typography_failures(m,expected_half_points,format_profile))
 failures.extend(structure_failures(m,keep_toc=keep_toc,keep_bullets=keep_bullets,heading_start=heading_start))
 if require_full_pagination_controls:
  for i,p in enumerate(m.doc.xpath('.//w:body//w:p',namespaces=ns)):
   pp=p.find(q('pPr'))
   for tag in ('widowControl','keepNext','keepLines'):
    if pp is None or not enabled(pp.find(q(tag))):
     failures.append(f'paragraph {i} lacks required {tag} pagination control')
  for i,row in enumerate(m.doc.xpath('.//w:body//w:tbl/w:tr',namespaces=ns)):
   trpr=row.find(q('trPr'))
   if trpr is None or not enabled(trpr.find(q('cantSplit'))):
    failures.append(f'table row {i} lacks cantSplit')
 if expected_line_multiple is not None or require_snap_to_grid_off or expected_before_lines is not None or expected_after_lines is not None:
  expected_line=str(round(float(expected_line_multiple)*240)) if expected_line_multiple is not None else None
  for i,p in enumerate(m.doc.xpath('.//w:body//w:p',namespaces=ns)):
   pp=p.find(q('pPr'))
   if expected_line is not None:
    sp=pp.find(q('spacing')) if pp is not None else None
    if sp is None or sp.get(q('line')) != expected_line or sp.get(q('lineRule')) != 'auto':
     failures.append(f'paragraph {i} lacks requested line spacing {expected_line_multiple}x')
    if expected_before_lines is not None:
     expected_before = expected_table_after_lines if (p.getprevious() is not None and p.getprevious().tag == q('tbl') and expected_table_after_lines is not None) else expected_before_lines
     if sp is None or sp.get(q('beforeLines')) != str(expected_before) or sp.get(q('before')) not in {'0','0.0'}:
      failures.append(f'paragraph {i} lacks requested paragraph-before spacing {expected_before} lines')
    if expected_after_lines is not None:
     if sp is None or sp.get(q('afterLines')) != str(expected_after_lines) or sp.get(q('after')) not in {'0','0.0'}:
      failures.append(f'paragraph {i} lacks requested paragraph-after spacing {expected_after_lines} lines')
   if require_snap_to_grid_off:
    snap=pp.find(q('snapToGrid')) if pp is not None else None
    if snap is None or snap.get(q('val')) not in {'0','false','off'}:
     failures.append(f'paragraph {i} does not explicitly disable snap-to-grid')
 # Component semantics: visual formatting is insufficient if the source
 # paragraphs remain Normal. Require the named WPS styles to survive in XML.
 for ti,tbl in enumerate(m.doc.xpath('.//w:body/w:tbl',namespaces=ns)):
  rows=tbl.findall(q('tr'))
  if not rows:
   failures.append(f'table {ti} has no rows')
   continue
  first_pr=rows[0].find(q('trPr'))
  if first_pr is None or first_pr.find(q('tblHeader')) is None:
   failures.append(f'table {ti} first row is not marked as repeating header')
  if first_pr is None or first_pr.find(q('cantSplit')) is None:
   failures.append(f'table {ti} header row can split across pages')
  tpr=tbl.find(q('tblPr')); borders=tpr.find(q('tblBorders')) if tpr is not None else None
  if borders is None or any(borders.find(q(edge)) is None for edge in ('top','left','bottom','right','insideH','insideV')):
   failures.append(f'table {ti} lacks explicit complete borders')
  prev=tbl.getprevious()
  prev_text=''.join(prev.xpath('.//w:t/text()',namespaces=ns)).strip() if prev is not None and prev.tag==q('p') else ''
  if not TABLE_TITLE.match(prev_text): failures.append(f'table {ti} lacks a reference-style 表n table title immediately before it')
  elif prev.xpath('./w:pPr/w:jc/@w:val',namespaces=ns) != ['center']:
   failures.append(f'table {ti} title is not centered')
  elif m.style_name(m.p_style(prev)) != '图片':
   failures.append(f'table {ti} title does not use the 图片 style shared with figure captions')
  elif any(bold(r.find(q('rPr'))) for r in prev.findall(q('r'))):
   failures.append(f'table {ti} title remains bold instead of matching figure-caption formatting')
  if expected_table_after_lines is not None:
   nxt=tbl.getnext()
   if nxt is None or nxt.tag != q('p'):
    failures.append(f'table {ti} lacks a following paragraph for table-after spacing')
   else:
    spp=nxt.find(q('pPr')); sp=spp.find(q('spacing')) if spp is not None else None
    if sp is None or sp.get(q('beforeLines')) != str(expected_table_after_lines):
     failures.append(f'table {ti} following paragraph lacks table-after spacing {expected_table_after_lines} lines')
  for ri,row in enumerate(rows):
   for ci,cell in enumerate(row.findall(q('tc'))):
    for p in cell.findall(q('p')):
     sid=m.p_style(p)
     txt=''.join(p.xpath('.//w:t/text()',namespaces=ns)).strip()
     prose=is_prose_cell(txt)
     expected='表格正文' if prose else '表格'
     if m.style_name(sid) != expected: failures.append(f'table {ti} cell paragraph ({ri},{ci}) expected {expected} style')
     if prose and p.xpath('./w:pPr/w:jc/@w:val',namespaces=ns) not in (['both'],[]): failures.append(f'table {ti} prose cell ({ri},{ci}) is not justified')
 # Table titles and figure captions share actual effective typography, including
 # inherited formatting and direct run overrides. Font/size drift must fail.
 if any(CAPTION.match(''.join(p.xpath('.//w:t/text()',namespaces=ns)).strip()) for p in m.doc.xpath('.//w:body/w:p',namespaces=ns)):
  try:
   caption_sid, profile = caption_profile(m.doc,m.styles)
   for p in m.doc.xpath('.//w:body/w:p',namespaces=ns):
    txt=''.join(p.xpath('.//w:t/text()',namespaces=ns)).strip()
    if not CAPTION.match(txt): continue
    if m.p_style(p) != caption_sid: failures.append(f'caption {txt!r} does not use 图片 style')
    for r in p.xpath('.//w:r[w:t]',namespaces=ns):
     if signature(effective_run(m.styles,p,r)) != signature(profile):
      failures.append(f'caption {txt!r} font/size/weight differs from figure-caption profile')
  except ValueError as exc: failures.append(str(exc))
 # Inline drawing paragraphs and captions must be explicitly 图片 style.
 for i,p in enumerate(m.doc.xpath('.//w:body/w:p',namespaces=ns)):
  if p.xpath('.//w:drawing',namespaces=ns):
   if m.style_name(m.p_style(p)) != '图片': failures.append(f'image paragraph {i} is not 图片 style')
  text=''.join(p.xpath('.//w:t/text()',namespaces=ns)).strip()
  if re.match(r'^图\s*\d+', text) and m.style_name(m.p_style(p)) != '图片':
   failures.append(f'image caption paragraph {i} is not 图片 style')
  if ZH_EN_SPACE.search(''.join(p.xpath('.//w:t/text()',namespaces=ns))):
   failures.append(f'paragraph {i} contains a Chinese-English boundary space')
 for i,cell in enumerate(m.doc.xpath('.//w:body//w:tc',namespaces=ns)):
  if ZH_EN_SPACE.search(''.join(cell.xpath('.//w:t/text()',namespaces=ns))):
   failures.append(f'table cell {i} contains a Chinese-English boundary space')
 if expected_half_points is not None:
  for sid,s in m.styles.items():
   role=m.role(sid)
   allowed_roles={'body',*(f'heading-{i}' for i in range(1,6))}
   if format_profile: allowed_roles |= {'title','caption'}
   if s.get(q('type'))=='paragraph' and role in allowed_roles:
    r=m.effective(sid,'rPr'); sz=r.find(q('sz'))
    expected_size=role_half_points(format_profile,expected_half_points,role) if format_profile else expected_half_points
    if sz is None or sz.get(q('val'))!=str(expected_size): failures.append(f'style {sid} ({m.style_name(sid)}) lacks requested size {expected_half_points}')
  for p in records:
   if not p['num'] or p['num'].get('level') is None: continue
   lvl=p['num'].get('level'); ilvl=p['num'].get('ilvl')
   if ilvl not in {'1','2','3','4'}: continue
   rr=lvl.find(q('rPr')); sz=rr.find(q('sz')) if rr is not None else None
   role_for_number=p['role']
   expected_size=role_half_points(format_profile,expected_half_points,role_for_number) if format_profile else expected_half_points
   if sz is None or sz.get(q('val'))!=str(expected_size): failures.append(f'numbering level {ilvl} lacks requested size {expected_size}')
 for rec in records:
  role=rec['role']; p=rec['element']; pp=rec['pPr']; ind=pp.find(q('ind')) if pp is not None else None
  if role.startswith('heading-') and rec['num'] and rec['num'].get('level') is not None:
   marker=rec['num']['level'].find(q('lvlText'))
   if marker is not None and re.match(r'^[\s\u3000]+',marker.get(q('val')) or ''):
    failures.append(f'heading paragraph {rec["index"]} numbering embeds whitespace indentation')
  if rec['num'] and MARKER.match(rec['text']): failures.append(f'paragraph {rec["index"]} has effective numbering plus manual marker')
  if role=='heading-2':
   if bold(rec['effective_rPr']) or any(bold(r.find(q('rPr'))) for r in p.findall(q('r'))): failures.append(f'level-2 heading paragraph {rec["index"]} is bold')
   lvl=rec['num'].get('level') if rec['num'] else None
   if lvl is not None and bold(lvl.find(q('rPr'))): failures.append(f'level-2 numbering symbol paragraph {rec["index"]} is bold')
  if role=='heading-5' and (rec['text'].startswith('时间安排：') or rec['text'].startswith('阶段性成果：')):
   runs=p.findall(q('r'))
   if len(runs)<2: failures.append(f'inline level-5 label paragraph {rec["index"]} is not split at colon')
   elif bold(runs[1].find(q('rPr'))): failures.append(f'inline body paragraph {rec["index"]} remains bold')
 # Exactly one blank Normal paragraph between title block and first non-empty body.
 ti=next((i for i,r in enumerate(records) if r['role']=='title'),None)
 if ti is not None:
  blank_i=next((i for i in range(ti+1,len(records)) if records[i]['role']=='body' and not records[i]['text']),None)
  body_after=next((i for i in range(blank_i+1,len(records)) if records[i]['role']=='body' and records[i]['text']),None) if blank_i is not None else None
  if blank_i is None or body_after is None: failures.append('title block lacks a blank paragraph before body')
 if failures: print('FAIL'); print('\n'.join(failures)); return 1
 print('PASS'); return 0
if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('docx'); ap.add_argument('--expected-half-points',type=int); ap.add_argument('--format-profile'); ap.add_argument('--require-full-pagination-controls',action='store_true'); ap.add_argument('--expected-line-multiple',type=float); ap.add_argument('--require-snap-to-grid-off',action='store_true'); ap.add_argument('--expected-before-lines',type=int); ap.add_argument('--expected-after-lines',type=int); ap.add_argument('--expected-table-after-lines',type=int); ap.add_argument('--keep-toc',action='store_true'); ap.add_argument('--keep-bullets',action='store_true'); ap.add_argument('--heading-start',type=int,choices=range(1,6),default=2); ap.add_argument('--role-map'); ap.add_argument('--expected-heading-indent-chars',type=float,default=POLICY['heading_indent_chars']); a=ap.parse_args(); sys.exit(main(a.docx,a.expected_half_points,a.require_full_pagination_controls,a.expected_line_multiple,a.require_snap_to_grid_off,a.expected_before_lines,a.expected_after_lines,a.expected_table_after_lines,a.keep_toc,a.keep_bullets,a.heading_start,a.role_map,a.expected_heading_indent_chars,load_profile(a.format_profile) if a.format_profile else None))
