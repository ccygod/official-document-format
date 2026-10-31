#!/usr/bin/env python3
"""Deterministic WPS/WordprocessingML normalization for the official-document skill.

The model may decide content and structure. This script owns repeatable formatting:
styles, numbering, pagination controls, grid snapping, line spacing and tables.
It patches a copied DOCX package with lxml and preserves unlisted ZIP parts.
"""
from argparse import ArgumentParser
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from copy import deepcopy
import re

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W}; q=lambda x:'{'+W+'}'+x
from table_semantics import cell_style_id
from caption_format import normalize_captions
from ooxml_model import OOXMLModel
from structure_rules import normalize_structure
from semantic_contract import apply_role_map, materialize_indents
from policy import POLICY
from effective_format import normalize_text_format
from format_profiles import role_half_points


def ensure(parent, tag):
    node=parent.find('w:'+tag, NS)
    if node is None: node=etree.SubElement(parent,q(tag))
    return node

def set_spacing_and_grid(ppr, line, before_lines=0, after_lines=25):
    snap=ensure(ppr,'snapToGrid'); snap.set(q('val'),'0')
    sp=ensure(ppr,'spacing')
    sp.set(q('before'),'0'); sp.set(q('beforeLines'),str(before_lines))
    sp.set(q('after'),'0'); sp.set(q('afterLines'),str(after_lines))
    sp.set(q('line'),str(line)); sp.set(q('lineRule'),'auto')

def set_on(ppr, tag):
    ensure(ppr,tag).set(q('val'),'1')

def style_name(style):
    n=style.find('w:name',NS)
    return n.get(q('val')) if n is not None else ''

def style_chain(styles, sid):
    out=[]; seen=set()
    while sid and sid not in seen:
        seen.add(sid); st=styles.get(sid)
        if st is None: break
        out.append(st); b=st.find('w:basedOn',NS); sid=b.get(q('val')) if b is not None else None
    return list(reversed(out))

def effective_child(styles, sid, container, child):
    found=None
    for st in style_chain(styles,sid):
        c=st.find('w:'+container,NS)
        if c is not None:
            x=c.find('w:'+child,NS)
            if x is not None: found=x
    return deepcopy(found) if found is not None else None

def heading_role(name):
    low=(name or '').lower().replace(' ','')
    if low in ('title','标题'): return 'title'
    if low in ('normal','正文'): return 'body'
    m=re.search(r'(?:heading|标题)([1-9])',low)
    if m: return 'heading-'+m.group(1)
    if '5级标题' in name: return 'heading-5'
    return 'other'

def set_style_size_and_spacing(styles, body_half, line, before_lines=0, after_lines=25, heading_indent_chars=2, format_profile=None):
    role_to_id={}
    for sid,st in styles.items():
        if st.get(q('type'))=='paragraph':role_to_id.setdefault(heading_role(style_name(st)),sid)
    for sid,st in styles.items():
        if st.get(q('type'))!='paragraph': continue
        pp=st.find('w:pPr',NS)
        if pp is None: pp=etree.SubElement(st,q('pPr'))
        set_spacing_and_grid(pp,line,before_lines,after_lines)
        role=heading_role(style_name(st))
        if role=='body' or role.startswith('heading-'):
            chars=2 if role=='body' else heading_indent_chars
            ind=ensure(pp,'ind')
            for attr in ('hanging','hangingChars'):ind.attrib.pop(q(attr),None)
            for attr,value in [('left','0'),('leftChars','0'),('firstLine',str(round(chars*body_half*10))),('firstLineChars',str(round(chars*100)))]:
                ind.set(q(attr),value)
            rp=st.find('w:rPr',NS)
            if rp is None: rp=etree.SubElement(st,q('rPr'))
            fonts=ensure(rp,'rFonts')
            inherited=effective_child(styles,sid,'rPr','rFonts')
            if inherited is not None:
                for key,value in inherited.attrib.items():fonts.set(key,value)
            for key in list(fonts.attrib):
                if 'theme' in etree.QName(key).localname.lower():del fonts.attrib[key]
            role_size=role_half_points(format_profile,body_half,role) if format_profile else body_half
            for tag in ('sz','szCs'):
                el=ensure(rp,tag); el.set(q('val'),str(role_size))
            if format_profile:
                font=format_profile.get('fonts',{}).get(role.replace('-','_'))
                if font:
                    for attr in ('ascii','hAnsi','eastAsia','cs'):fonts.set(q(attr),'Times New Roman' if attr in ('ascii','hAnsi','cs') else font)
                if role.startswith('heading-'):
                    bold_value=bool(format_profile.get('bold',{}).get(role.replace('-','_'), role in {'heading-3'}))
                    for tag in ('b','bCs'):
                        old=rp.find(q(tag))
                        if old is None:old=etree.SubElement(rp,q(tag))
                        old.set(q('val'),'1' if bold_value else '0')
    return role_to_id

def set_numbering(num, styles, body_half, role_to_id, format_profile=None):
    # Map numbering levels to heading roles; level 1 is heading 2 because level 0 is the chapter role.
    for abstract in num.xpath('.//w:abstractNum',namespaces=NS):
        for lvl in abstract.findall('w:lvl',NS):
            ilvl=int(lvl.get(q('ilvl')) or 0)
            linked_style=lvl.find(q('pStyle'))
            linked_id=linked_style.get(q('val')) if linked_style is not None else None
            # Legacy unnamed fixture lists are covered through paragraph use below.
            used_heading_levels=getattr(set_numbering,'used_heading_levels',set())
            if linked_id not in styles or not heading_role(style_name(styles[linked_id])).startswith('heading-'):
                if (abstract.get(q('abstractNumId')),str(ilvl)) not in used_heading_levels:continue
            linked=lvl.find(q('pStyle'))
            linked_sid=linked.get(q('val')) if linked is not None else None
            if linked_sid in styles and heading_role(style_name(styles[linked_sid])).startswith('heading-'):
                marker=lvl.find(q('lvlText'))
                if marker is not None:
                    # The retained template embeds four literal spaces in its
                    # heading marker. They stack with real paragraph indentation.
                    marker.set(q('val'),(marker.get(q('val')) or '').lstrip(' \t\u3000'))
            rp=ensure(lvl,'rPr')
            sid=linked_id if linked_id in styles else role_to_id.get('heading-'+str(min(ilvl+1,5)))
            role=heading_role(style_name(styles[sid])) if sid in styles else 'body'
            role_size=role_half_points(format_profile,body_half,role) if format_profile else body_half
            for tag in ('sz','szCs'):
                ensure(rp,tag).set(q('val'),str(role_size))
            if ilvl==1:
                # Heading 2 is regular Hei; a retained bold list symbol must not survive.
                for tag in ('b','bCs'): ensure(rp,tag).set(q('val'),'0')
            elif format_profile and role.startswith('heading-'):
                bold_value=bool(format_profile.get('bold',{}).get(role.replace('-','_'), role in {'heading-3'}))
                for tag in ('b','bCs'): ensure(rp,tag).set(q('val'),'1' if bold_value else '0')
            font=effective_child(styles,sid,'rPr','rFonts') if sid else None
            if font is not None:
                old=rp.find('w:rFonts',NS)
                if old is None: old=etree.SubElement(rp,q('rFonts'))
                for attr in ('ascii','hAnsi','eastAsia','cs'):
                    val=font.get(q(attr))
                    if val: old.set(q(attr),val)

def patch_paragraph_parts(files, line, full_pagination, before_lines=0, after_lines=25, table_after_lines=50):
    # The main document owns the user-visible body. Preserve headers, footers,
    # footnotes and endnotes unless a caller explicitly asks to rewrite them;
    # they often contain WPS fields and page-number drawing fallbacks.
    for name in ('word/document.xml',):
        if name not in files: continue
        try: root=etree.fromstring(files[name])
        except Exception: continue
        changed=False
        table_followers={tbl.getnext() for tbl in root.xpath('.//w:tbl',namespaces=NS) if tbl.getnext() is not None}
        for p in root.xpath('.//w:p',namespaces=NS):
            pp=p.find('w:pPr',NS)
            if pp is None: pp=etree.Element(q('pPr')); p.insert(0,pp)
            before = table_after_lines if p in table_followers else before_lines
            set_spacing_and_grid(pp,line,before,after_lines)
            if full_pagination:
                for tag in ('widowControl','keepNext','keepLines'): set_on(pp,tag)
            else:
                for tag in ('widowControl','keepLines'): set_on(pp,tag)
            changed=True
        if changed: files[name]=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)

def patch_tables(root, full_pagination, styles):
    named={style_name(st):sid for sid,st in styles.items() if st.get(q("type"))=="paragraph"}
    if root.xpath(".//w:tbl",namespaces=NS) and not {"表格","表格正文"} <= named.keys():
        raise ValueError("Missing semantic table paragraph styles")
    for tbl in root.xpath('.//w:tbl',namespaces=NS):
        for row_i,row in enumerate(tbl.findall(q('tr'))):
            trpr=row.find(q('trPr'))
            if trpr is None: trpr=etree.Element(q('trPr')); row.insert(0,trpr)
            if trpr.find(q('cantSplit')) is None: etree.SubElement(trpr,q('cantSplit'))
            if row_i==0 and trpr.find(q('tblHeader')) is None: etree.SubElement(trpr,q('tblHeader'))
            for tc in row.findall(q('tc')):
                tcp=tc.find(q('tcPr'))
                if tcp is not None:
                    for shd in tcp.findall(q('shd')): tcp.remove(shd)
                for p in tc.findall(q('p')):
                    txt=''.join(p.xpath('.//w:t/text()',namespaces=NS)).strip()
                    pp=p.find(q('pPr'))
                    if pp is None: pp=etree.Element(q('pPr')); p.insert(0,pp)
                    ps=ensure(pp,'pStyle'); ps.set(q('val'),named['表格正文' if cell_style_id(txt,header=(row_i==0))=='32' else '表格'])
                    jc=ensure(pp,'jc'); jc.set(q('val'),'both' if cell_style_id(txt,row_i==0)=='32' else 'center')
                    if full_pagination:
                        for tag in ('widowControl','keepNext','keepLines'): set_on(pp,tag)
                    else:ensure(pp,'keepNext').set(q('val'),'0')

def main(src,dst,body_half,line_multiple,full_pagination,before_lines=0,after_lines=25,table_after_lines=50,keep_toc=False,keep_bullets=False,heading_start=2,role_map=None,heading_indent_chars=2,format_profile=None):
    line=round(float(line_multiple)*240)
    with ZipFile(src,'r') as z: files={n:z.read(n) for n in z.namelist()}
    model=OOXMLModel(src)
    normalize_structure(model,keep_toc=keep_toc,keep_bullets=keep_bullets,heading_start=heading_start)
    if role_map:
        apply_role_map(model,role_map)
        normalize_structure(model,keep_toc=keep_toc,keep_bullets=keep_bullets,heading_start=heading_start)
    styles=model.styles_xml; style_map=model.styles
    # Fixed-font template import must not inherit source docDefaults theme fonts.
    for fonts in styles.xpath("./w:docDefaults/w:rPrDefault/w:rPr/w:rFonts",namespaces=NS):
        for attr in list(fonts.attrib):
            if "theme" in etree.QName(attr).localname.lower():del fonts.attrib[attr]
    role_to_id=set_style_size_and_spacing(style_map,body_half,line,before_lines,after_lines,heading_indent_chars,format_profile)
    files['word/styles.xml']=etree.tostring(styles,xml_declaration=True,encoding='UTF-8',standalone=True)
    if 'word/numbering.xml' in files:
        num=etree.fromstring(files['word/numbering.xml'])
        set_numbering.used_heading_levels={(r['num']['abstractNumId'],r['num']['ilvl']) for r in model.paragraphs() if r['role'].startswith('heading-') and r['num']}
        set_numbering(num,style_map,body_half,role_to_id,format_profile)
        files['word/numbering.xml']=etree.tostring(num,xml_declaration=True,encoding='UTF-8',standalone=True)
    materialize_indents(model,body_half,heading_indent_chars)
    normalize_text_format(model,body_half,format_profile)
    doc=model.doc
    if not full_pagination:
        # Old documents may have linked every body paragraph into one chain.
        # Default mode explicitly restores semantic keepNext instead of preserving it.
        for row in model.paragraphs():
            if row['role']=='body' and not row['element'].xpath('.//w:drawing',namespaces=NS):
                ensure(row['element'].find(q('pPr')),'keepNext').set(q('val'),'0')
    patch_tables(doc,full_pagination,style_map)
    normalize_captions(doc,style_map)
    files['word/document.xml']=etree.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
    patch_paragraph_parts(files,line,full_pagination,before_lines,after_lines,table_after_lines)
    out=Path(dst); tmp=out.with_name(out.name+'.tmp')
    with ZipFile(tmp,'w',ZIP_DEFLATED) as z:
        for n,data in files.items(): z.writestr(n,data)
    tmp.replace(out)

if __name__=='__main__':
    ap=ArgumentParser(); ap.add_argument('input'); ap.add_argument('output'); ap.add_argument('--body-half-points',type=int,required=True); ap.add_argument('--format-profile'); ap.add_argument('--line-multiple',type=float,default=POLICY['line_multiple']); ap.add_argument('--before-lines',type=int,default=POLICY['before_lines']); ap.add_argument('--after-lines',type=int,default=POLICY['after_lines']); ap.add_argument('--table-after-lines',type=int,default=POLICY['table_after_lines']); ap.add_argument('--full-pagination-controls',action='store_true'); ap.add_argument('--keep-toc',action='store_true'); ap.add_argument('--keep-bullets',action='store_true'); ap.add_argument('--heading-start',type=int,choices=range(1,6),default=POLICY['heading_start']); ap.add_argument('--role-map'); ap.add_argument('--heading-indent-chars',type=float,default=POLICY['heading_indent_chars']); a=ap.parse_args(); from format_profiles import load_profile; main(a.input,a.output,a.body_half_points,a.line_multiple,a.full_pagination_controls,a.before_lines,a.after_lines,a.table_after_lines,a.keep_toc,a.keep_bullets,a.heading_start,a.role_map,a.heading_indent_chars,load_profile(a.format_profile) if a.format_profile else None)
