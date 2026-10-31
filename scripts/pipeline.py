#!/usr/bin/env python3
"""Inspect -> plan -> import -> format -> verify; never claim visual QA from XML."""
import argparse,contextlib,hashlib,io,json,tempfile
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from ooxml_model import OOXMLModel,q,ns
from policy import POLICY
from import_template import import_template, prepare_components
from apply_official_rules import main as write
from check_official_document import main as check
from smart_table_widths import patch_doc
from format_profiles import load_profile, profile_summary

ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def inventory(path):
    m=OOXMLModel(path)
    unsupported=[]
    for label,xpath in [('content_controls','.//w:sdt'),('text_boxes','.//w:txbxContent'),('tracked_changes','.//w:ins|.//w:del'),('merged_cells','.//w:gridSpan|.//w:vMerge')]:
        if m.doc.xpath(xpath,namespaces=ns):unsupported.append(label)
    if len(m.doc.xpath('.//w:sectPr',namespaces=ns))>1:unsupported.append('multiple_sections')
    return {'source_sha256':digest(path),'paragraphs':[{'index':r['index'],'text':r['text'],'source_role':r['role']} for r in m.paragraphs()], 'tables':len(m.doc.xpath('.//w:tbl',namespaces=ns)),'images':len(m.doc.xpath('.//w:drawing',namespaces=ns)),'requires_specialist_review':unsupported}
def content_signature(path):
    m=OOXMLModel(path)
    return [''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in m.doc.xpath('.//w:body//w:p',namespaces=ns)]
def execute(source,output,plan,half_points,report,full=False,heading_start=None,heading_indent=None,format_profile_id="official_cn"):
    source=Path(source);output=Path(output);report=Path(report)
    if source.resolve()==output.resolve():raise ValueError('Output must differ from original')
    data=inventory(source);result={'inventory':data,'status':'failed','visual_qa':'not_performed'}
    output.parent.mkdir(parents=True,exist_ok=True);report.parent.mkdir(parents=True,exist_ok=True)
    try:
        if data['requires_specialist_review']:raise ValueError('Specialist route required: '+', '.join(data['requires_specialist_review']))
        roles=json.loads(Path(plan).read_text())
        if roles.get('complete') is not True:raise ValueError('A complete independently reviewed role map is required')
        profile=load_profile(format_profile_id)
        start=profile.get('numbering',{}).get('heading_start',POLICY['heading_start']) if heading_start is None else heading_start
        indent=profile.get('heading_indent_chars',POLICY['heading_indent_chars']) if heading_indent is None else heading_indent
        with tempfile.TemporaryDirectory(dir=output.parent) as td:
            temp=Path(td);imported=temp/'imported.docx';first=temp/'first.docx';second=temp/'second.docx'
            import_template(source,imported,ROOT/'assets/reference.docx')
            prepare_components(imported,roles)
            args=(half_points,profile['line_multiple'],full)
            kw=dict(before_lines=POLICY['before_lines'],after_lines=POLICY['after_lines'],table_after_lines=POLICY['table_after_lines'],heading_start=start,role_map=plan,heading_indent_chars=indent)
            write(imported,first,*args,**kw,format_profile=profile)
            widths=patch_doc(first,apply=True)
            if any(r.get('widths') is None for r in widths):raise ValueError('Table width requires specialist review')
            with contextlib.redirect_stdout(io.StringIO()) as logs:
                code=check(first,half_points,full,profile['line_multiple'],True,POLICY['before_lines'],POLICY['after_lines'],POLICY['table_after_lines'],heading_start=start,role_map=plan,expected_heading_indent_chars=indent,format_profile=profile)
            result['structural_check']=logs.getvalue().strip()
            if code:raise ValueError('Structural validation failed')
            if content_signature(imported)!=content_signature(first):raise ValueError('Content changed: perform explicit marker/TOC cleanup before using this conservative pipeline')
            write(first,second,*args,**kw,format_profile=profile);patch_doc(second,apply=True)
            with ZipFile(first) as a,ZipFile(second) as b:
                if {n:a.read(n) for n in a.namelist()}!={n:b.read(n) for n in b.namelist()}:raise ValueError('Second pass changed package')
            with ZipFile(source) as a,ZipFile(first) as b:
                preserve=[n for n in a.namelist() if n not in {'word/document.xml','word/styles.xml','word/numbering.xml','[Content_Types].xml','word/_rels/document.xml.rels'}]
                if any(n not in b.namelist() or a.read(n)!=b.read(n) for n in preserve):raise ValueError('Preserve-only package part changed')
            result.update(status='structural_pass_visual_pending',format_profile=profile['id'],body_half_points=half_points,content_preserved=True,idempotence=True,source_preservation=True,widths=widths,source_sha256=digest(source),plan_sha256=digest(plan),policy_sha256=digest(ROOT/'config/official.json'),output_sha256=digest(first))
            first.replace(output)
    except Exception as exc:
        result['error']=str(exc);raise
    finally:report.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='action',required=True)
    read=sp.add_parser('inspect');read.add_argument('source');read.add_argument('--out',required=True)
    run=sp.add_parser('format');run.add_argument('source');run.add_argument('output');run.add_argument('--role-map',required=True);run.add_argument('--format-profile',required=True,choices=[p['id'] for p in __import__('format_profiles').list_profiles()]);run.add_argument('--body-half-points',required=True,type=int);run.add_argument('--report',required=True);run.add_argument('--full-pagination-controls',action='store_true');run.add_argument('--heading-start',type=int);run.add_argument('--heading-indent-chars',type=float)
    profiles=sp.add_parser('formats');profiles.set_defaults(_formats=True)
    a=ap.parse_args()
    if a.action=='inspect':Path(a.out).write_text(json.dumps(inventory(a.source),ensure_ascii=False,indent=2))
    elif a.action=='formats':print(json.dumps(profile_summary(),ensure_ascii=False,indent=2))
    else:execute(a.source,a.output,a.role_map,a.body_half_points,a.report,a.full_pagination_controls,a.heading_start,a.heading_indent_chars,a.format_profile)
