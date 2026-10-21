#!/usr/bin/env python3
"""Report or apply content-driven WPS/Word table widths.

The heuristic is deliberately conservative: it keeps index/status/date columns
narrow, gives flexible space to long-text columns, and refuses to rewrite
tables with complex grid spans unless --force is supplied.
"""
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from pathlib import Path
import argparse, json, math, os, re, tempfile

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
q=lambda t:'{'+W+'}'+t
ns={'w':W}
NARROW=re.compile(r'(序号|编号|序列|id|no\.?|状态|类型|等级|日期|时间|数量|单位|金额)',re.I)
LONG=re.compile(r'(说明|描述|内容|主要|范围|依据|任务|措施|备注|功能|成果|工作)',re.I)

def text_width(s):
    """Approximate intrinsic width in twips at the table's normal 10.5pt size."""
    s=re.sub(r'\s+',' ',s.strip())
    total=0
    for ch in s:
        if '\u4e00' <= ch <= '\u9fff': total += 210
        elif ch in 'W@#%&M': total += 150
        elif ch.isupper() or ch.isdigit(): total += 120
        else: total += 105
    return total

def available_width(doc):
    sec=doc.find('.//w:body/w:sectPr',namespaces=ns)
    if sec is None: return 8200
    pg=sec.find(q('pgSz')); mar=sec.find(q('pgMar'))
    if pg is None or mar is None: return 8200
    try:
        return max(1,int(pg.get(q('w')))-int(mar.get(q('left')))-int(mar.get(q('right'))))
    except (TypeError,ValueError): return 8200

def infer_widths(tbl, avail):
    rows=tbl.findall(q('tr'))
    if not rows: return [], {'reason':'empty table'}
    n=max(len(r.findall(q('tc'))) for r in rows)
    headers=[]; values=[[] for _ in range(n)]
    for ri,row in enumerate(rows):
        cells=row.findall(q('tc'))
        for ci,cell in enumerate(cells):
            if cell.find('.//w:gridSpan',namespaces=ns) is not None:
                return [], {'reason':'gridSpan/merged cells; manual review required'}
            txt=''.join(cell.xpath('.//w:t/text()',namespaces=ns)).strip()
            values[ci].append(txt)
            if ri==0: headers.append(txt)
    while len(headers)<n: headers.append('')
    mins=[]; prefs=[]; roles=[]
    for ci in range(n):
        h=headers[ci]
        allvals=values[ci]
        max_intrinsic=max([text_width(x) for x in allvals] or [420])
        # The longest value is a ceiling signal, not a demand: long prose must wrap.
        avg_chars=sum(len(x) for x in allvals)/max(1,len(allvals))
        long_values=max((len(v) for v in allvals[1:]),default=0)>=18
        if NARROW.search(h) and not long_values:
            role='narrow'; mn=min(900,max(560,text_width(h)+216)); pref=min(900,max(mn,700))
        elif LONG.search(h) or avg_chars>=18:
            role='flex'; mn=min(1700,max(1100,text_width(h)+216)); pref=max(mn,min(4200,max_intrinsic//2+216))
        else:
            role='regular'; mn=min(1500,max(800,text_width(h)+216)); pref=max(mn,min(2400,max_intrinsic//2+216))
        mins.append(mn); prefs.append(pref); roles.append(role)
    if sum(mins)>avail:
        # Keep semantic minimums but scale all columns down proportionally.
        scale=avail/sum(mins); widths=[max(500,int(x*scale)) for x in mins]
        return widths, {'headers':headers,'roles':roles,'mode':'compressed','available':avail}
    compact=not any(r=="flex" for r in roles) and all(max((len(v) for v in col),default=0)<=10 for col in values)
    widths=prefs[:]
    if sum(widths)<avail and not compact:
        extra=avail-sum(widths)
        # Narrow semantic columns keep their compact width; flexible space goes
        # to descriptive columns first instead of recreating equal-width tables.
        weights=[0.0 if r=='narrow' else 2.0 if r=='flex' else 1.0 for r in roles]
        sw=sum(weights)
        widths=[w+int(extra*wt/sw) for w,wt in zip(widths,weights)] if sw else widths
    elif sum(widths)>avail:
        need=sum(widths)-avail
        flex=[i for i,r in enumerate(roles) if r!='narrow' and widths[i]>mins[i]]
        while need>0 and flex:
            step=max(1,math.ceil(need/len(flex))); changed=False
            for i in list(flex):
                take=min(step,widths[i]-mins[i]); widths[i]-=take; need-=take; changed|=take>0
                if widths[i]<=mins[i]: flex.remove(i)
                if need<=0: break
            if not changed: break
    # Correct rounding drift on the longest-text column.
    drift=avail-sum(widths) if any(r!='narrow' for r in roles) and not compact else 0; target=max(range(n),key=lambda i: len(values[i][0]) if values[i] else 0)
    widths[target]+=drift
    return widths, {'headers':headers,'roles':roles,'mode':'balanced','available':avail,'minimums':mins}

def patch_doc(path, apply=False):
    with ZipFile(path) as zin:
        doc=etree.fromstring(zin.read('word/document.xml')); avail=available_width(doc); report=[]
        for ti,tbl in enumerate(doc.xpath('.//w:body/w:tbl',namespaces=ns)):
            widths,meta=infer_widths(tbl,avail)
            if not widths:
                report.append({'table':ti,'widths':None,**meta}); continue
            report.append({'table':ti,'widths':widths,**meta})
            if not apply: continue
            pr=tbl.find(q('tblPr'))
            if pr is None: pr=etree.Element(q('tblPr'));tbl.insert(0,pr)
            layout=pr.find(q('tblLayout'))
            if layout is None: layout=etree.SubElement(pr,q('tblLayout'))
            layout.set(q('type'),'fixed')
            tw=pr.find(q('tblW'))
            if tw is None:tw=etree.SubElement(pr,q('tblW'))
            tw.set(q('type'),'dxa');tw.set(q('w'),str(sum(widths)))
            grid=tbl.find(q('tblGrid'))
            if grid is None: grid=etree.Element(q('tblGrid')); tbl.insert(1,grid)
            for c in list(grid): grid.remove(c)
            for w in widths: etree.SubElement(grid,q('gridCol'),{q('w'):str(w)})
            for row in tbl.findall(q('tr')):
                for ci,cell in enumerate(row.findall(q('tc'))):
                    tcp=cell.find(q('tcPr'))
                    if tcp is None: tcp=etree.Element(q('tcPr')); cell.insert(0,tcp)
                    tcw=tcp.find(q('tcW'))
                    if tcw is None: tcw=etree.SubElement(tcp,q('tcW'))
                    tcw.attrib.update({q('w'):str(widths[ci]),q('type'):'dxa'})
        if apply:
            fd,tmp=tempfile.mkstemp(prefix=Path(path).name+'.',suffix='.tmp',dir=str(Path(path).parent)); os.close(fd)
            with ZipFile(tmp,'w',ZIP_DEFLATED) as zout:
                for info in zin.infolist():
                    data=etree.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/document.xml' else zin.read(info.filename)
                    zout.writestr(info,data)
            os.replace(tmp,path)
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('docx'); ap.add_argument('--apply',action='store_true'); ap.add_argument('--json',action='store_true'); a=ap.parse_args()
    out=patch_doc(a.docx,a.apply)
    print(json.dumps(out,ensure_ascii=False,indent=2))
