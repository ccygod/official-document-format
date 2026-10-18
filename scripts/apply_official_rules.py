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
    if ppr.find('w:'+tag, NS) is None: etree.SubElement(ppr,q(tag))

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

def set_style_size_and_spacing(styles, body_half, line, before_lines=0, after_lines=25):
    role_to_id={}
    for sid,st in styles.items(): role_to_id.setdefault(heading_role(style_name(st)),sid)
    for sid,st in styles.items():
        if st.get(q('type'))!='paragraph': continue
        pp=st.find('w:pPr',NS)
        if pp is None: pp=etree.SubElement(st,q('pPr'))
        set_spacing_and_grid(pp,line,before_lines,after_lines)
        role=heading_role(style_name(st))
        if role=='body' or role.startswith('heading-'):
            rp=st.find('w:rPr',NS)
            if rp is None: rp=etree.SubElement(st,q('rPr'))
            for tag in ('sz','szCs'):
                el=ensure(rp,tag); el.set(q('val'),str(body_half))
    return role_to_id

def set_numbering(num, styles, body_half, role_to_id):
    # Map numbering levels to heading roles; level 1 is heading 2 because level 0 is the chapter role.
    for abstract in num.xpath('.//w:abstractNum',namespaces=NS):
        for lvl in abstract.findall('w:lvl',NS):
            ilvl=int(lvl.get(q('ilvl')) or 0)
            rp=ensure(lvl,'rPr')
            for tag in ('sz','szCs'):
                ensure(rp,tag).set(q('val'),str(body_half))
            sid=role_to_id.get('heading-'+str(min(ilvl+1,5)))
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

def patch_tables(root, full_pagination):
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
                    ps=ensure(pp,'pStyle'); ps.set(q('val'),cell_style_id(txt,header=(row_i==0)))
                    jc=ensure(pp,'jc'); jc.set(q('val'),'both' if cell_style_id(txt,row_i==0)=='32' else 'center')
                    if full_pagination:
                        for tag in ('widowControl','keepNext','keepLines'): set_on(pp,tag)

def main(src,dst,body_half,line_multiple,full_pagination,before_lines=0,after_lines=25,table_after_lines=50):
    line=round(float(line_multiple)*240)
    with ZipFile(src,'r') as z: files={n:z.read(n) for n in z.namelist()}
    styles=etree.fromstring(files['word/styles.xml']); style_map={s.get(q('styleId')):s for s in styles.findall(q('style'))}
    role_to_id=set_style_size_and_spacing(style_map,body_half,line,before_lines,after_lines)
    files['word/styles.xml']=etree.tostring(styles,xml_declaration=True,encoding='UTF-8',standalone=True)
    if 'word/numbering.xml' in files:
        num=etree.fromstring(files['word/numbering.xml']); set_numbering(num,style_map,body_half,role_to_id)
        files['word/numbering.xml']=etree.tostring(num,xml_declaration=True,encoding='UTF-8',standalone=True)
    doc=etree.fromstring(files['word/document.xml']); patch_tables(doc,full_pagination)
    normalize_captions(doc,style_map)
    files['word/document.xml']=etree.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
    patch_paragraph_parts(files,line,full_pagination,before_lines,after_lines,table_after_lines)
    out=Path(dst); tmp=out.with_name(out.name+'.tmp')
    with ZipFile(tmp,'w',ZIP_DEFLATED) as z:
        for n,data in files.items(): z.writestr(n,data)
    tmp.replace(out)

if __name__=='__main__':
    ap=ArgumentParser(); ap.add_argument('input'); ap.add_argument('output'); ap.add_argument('--body-half-points',type=int,required=True); ap.add_argument('--line-multiple',type=float,default=1.35); ap.add_argument('--before-lines',type=int,default=0); ap.add_argument('--after-lines',type=int,default=25); ap.add_argument('--table-after-lines',type=int,default=50); ap.add_argument('--full-pagination-controls',action='store_true'); a=ap.parse_args(); main(a.input,a.output,a.body_half_points,a.line_multiple,a.full_pagination_controls,a.before_lines,a.after_lines,a.table_after_lines)
