#!/usr/bin/env python3
"""Remove duplicated manual list markers when effective OOXML numbering is present."""
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from pathlib import Path
import argparse, os, re, tempfile
NS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; XML='http://www.w3.org/XML/1998/namespace'; ns={'w':NS}; q=lambda t:'{'+NS+'}'+t
MARKER=re.compile(r'^\s*(?:(?:\(\s*\d+\s*\)|（\s*\d+\s*）)|(?:\d+\s*[\.、）)])|(?:\(\s*[一二三四五六七八九十百千万]+\s*\)|（\s*[一二三四五六七八九十百千万]+\s*）)|(?:[一二三四五六七八九十百千万]+\s*[、\.）)]))\s*')
def style_num(styles,sid):
    seen=set()
    while sid and sid not in seen:
        seen.add(sid); s=styles.get(sid)
        if s is None:return False
        p=s.find(q('pPr'))
        if p is not None and p.find(q('numPr')) is not None:return True
        b=p.find(q('basedOn')) if p is not None else None; sid=b.get(q('val')) if b is not None else None
    return False
def normalize(src,dst):
    with ZipFile(src) as zin:
        doc=etree.fromstring(zin.read('word/document.xml')); st=etree.fromstring(zin.read('word/styles.xml')); styles={s.get(q('styleId')):s for s in st.findall(q('style'))}; changed=[]
        for i,p in enumerate(doc.xpath('.//w:body/w:p',namespaces=ns)):
            pp=p.find(q('pPr')); ps=pp.find(q('pStyle')) if pp is not None else None; sid=ps.get(q('val')) if ps is not None else None
            effective=(pp is not None and pp.find(q('numPr')) is not None) or style_num(styles,sid)
            if not effective: continue
            nodes=p.xpath('.//w:t',namespaces=ns); full=''.join((n.text or '') for n in nodes); m=MARKER.match(full)
            if not m: continue
            left=len(m.group(0))
            for n in nodes:
                t=n.text or ''
                if left>=len(t): n.text=''; left-=len(t)
                else: n.text=t[left:]; n.set('{%s}space'%XML,'preserve'); left=0; break
            changed.append((i,m.group(0)))
        fd,tmp=tempfile.mkstemp(prefix=Path(dst).name+'.',suffix='.tmp',dir=str(Path(dst).parent)); os.close(fd)
        with ZipFile(tmp,'w',ZIP_DEFLATED) as zout:
            for info in zin.infolist(): zout.writestr(info, etree.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/document.xml' else zin.read(info.filename))
        os.replace(tmp,dst)
    print(changed)
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('input'); ap.add_argument('output'); a=ap.parse_args(); normalize(a.input,a.output)
