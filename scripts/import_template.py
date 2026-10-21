"""Import template styles into the source package, preserving its relationships/media."""
from copy import deepcopy
from zipfile import ZipFile,ZIP_DEFLATED
from pathlib import Path
from lxml import etree
from ooxml_model import OOXMLModel,q,ns

def import_template(source,destination,reference):
    with ZipFile(source) as z:files={n:z.read(n) for n in z.namelist()}
    model=OOXMLModel(source);ref=OOXMLModel(reference)
    # Canonical roles reuse source IDs; every other template style gets a
    # collision-free ID. Source-only styles and all source relationships stay.
    canonical={'Normal','Title','heading 1','heading 2','heading 3','heading 4','heading 5','图片','表格','表格正文','5级标题'}
    names={model.style_name(sid).lower():sid for sid in model.styles if model.styles[sid].get(q('type'))=='paragraph'}
    mapping={}
    occupied=set(model.styles)
    for sid,st in ref.styles.items():
        name=ref.style_name(sid)
        if name in canonical and name.lower() in names:mapping[sid]=names[name.lower()]
        else:
            candidate='official_'+sid
            while candidate in occupied:candidate+='x'
            mapping[sid]=candidate;occupied.add(candidate)
    num_offset=max([int(x) for x in model.num_to_abs]+[0])+1
    abs_offset=max([int(x) for x in model.abstracts]+[0])+1
    if ref.num_xml is not None:
        target=model.num_xml if model.num_xml is not None else etree.Element(q('numbering'),nsmap={'w':ns['w']})
        for original in ref.num_xml:
            node=deepcopy(original)
            if node.tag==q('abstractNum'):
                node.set(q('abstractNumId'),str(int(node.get(q('abstractNumId')))+abs_offset))
                for st in node.findall('.//'+q('pStyle')):
                    if st.get(q('val')) in mapping:st.set(q('val'),mapping[st.get(q('val'))])
            elif node.tag==q('num'):
                node.set(q('numId'),str(int(node.get(q('numId')))+num_offset))
                aid=node.find(q('abstractNumId'));aid.set(q('val'),str(int(aid.get(q('val')))+abs_offset))
            else:continue
            target.append(node)
        files['word/numbering.xml']=etree.tostring(target,xml_declaration=True,encoding='UTF-8',standalone=True)
        if model.num_xml is None:
            rels=etree.fromstring(files['word/_rels/document.xml.rels']);rn='http://schemas.openxmlformats.org/package/2006/relationships'
            ids={r.get('Id') for r in rels};rid='rIdOfficialNumbering'
            while rid in ids:rid+='x'
            etree.SubElement(rels,'{'+rn+'}Relationship',Id=rid,Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering',Target='numbering.xml')
            files['word/_rels/document.xml.rels']=etree.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
            ct=etree.fromstring(files['[Content_Types].xml']);cn='http://schemas.openxmlformats.org/package/2006/content-types'
            etree.SubElement(ct,'{'+cn+'}Override',PartName='/word/numbering.xml',ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml')
            files['[Content_Types].xml']=etree.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True)
    for sid,st in ref.styles.items():
        name=ref.style_name(sid)
        # Import canonical paragraph roles and any dependencies needed by them.
        node=deepcopy(st);node.set(q('styleId'),mapping[sid])
        for default in [q('default')]:node.attrib.pop(default,None)
        if sid==ref.default_style:
            node.set(q('default'),'1')
            for old in model.styles_xml:old.attrib.pop(q('default'),None) if old.get(q('type'))=='paragraph' else None
        for tag in ('basedOn','next','link'):
            for x in node.findall(q(tag)):
                if x.get(q('val')) in mapping:x.set(q('val'),mapping[x.get(q('val'))])
        for x in node.findall('.//'+q('numId')):
            if x.get(q('val'))!='0':x.set(q('val'),str(int(x.get(q('val')))+num_offset))
        old=model.styles_xml.find(f'{q("style")}[@{q("styleId")}="{mapping[sid]}"]')
        if old is not None:model.styles_xml.remove(old)
        elif name not in canonical:
            nm=node.find(q('name'))
            if nm is not None:nm.set(q('val'),'Official '+name)
        model.styles_xml.append(node)
    files['word/styles.xml']=etree.tostring(model.styles_xml,xml_declaration=True,encoding='UTF-8',standalone=True)
    with ZipFile(destination,'w',ZIP_DEFLATED) as z:
        for n,b in files.items():z.writestr(n,b)

def prepare_components(path,plan):
    """Only deterministic layout plus table titles explicitly supplied in plan."""
    from caption_format import CAPTION
    with ZipFile(path) as z:files={n:z.read(n) for n in z.namelist()}
    m=OOXMLModel(path);body=m.doc.find(q('body'))
    named={m.style_name(sid):sid for sid,st in m.styles.items() if st.get(q('type'))=='paragraph'}
    rows=list(m.paragraphs());title_texts={p['text'] for p in plan['paragraphs'] if p['role']=='title'}
    title_nodes=[r['element'] for r in rows if r['text'] in title_texts]
    title=title_nodes[-1] if title_nodes else None
    if title is not None and title.getnext() is not None and ''.join(title.getnext().xpath('.//w:t/text()',namespaces=ns)).strip():
        blank=etree.Element(q('p'));pp=etree.SubElement(blank,q('pPr'));etree.SubElement(pp,q('pStyle')).set(q('val'),named['Normal']);title.addnext(blank)
    requested={t['index']:t['title'] for t in plan.get('tables',[])}
    for i,tbl in enumerate(body.findall(q('tbl'))):
        previous=tbl.getprevious();text=''.join(previous.xpath('.//w:t/text()',namespaces=ns)).strip() if previous is not None else ''
        if not CAPTION.match(text):
            if i not in requested:raise ValueError(f'table {i}: supply tables[index,title] in role map; no caption invented')
            cap=etree.Element(q('p'));pp=etree.SubElement(cap,q('pPr'));etree.SubElement(pp,q('pStyle')).set(q('val'),named['图片']);etree.SubElement(etree.SubElement(cap,q('r')),q('t')).text=f'表{i+1}  {requested[i]}';tbl.addprevious(cap)
        pr=tbl.find(q('tblPr'))
        if pr is None:pr=etree.Element(q('tblPr'));tbl.insert(0,pr)
        borders=pr.find(q('tblBorders'))
        if borders is None:borders=etree.SubElement(pr,q('tblBorders'))
        for edge in ('top','left','bottom','right','insideH','insideV'):
            el=borders.find(q(edge))
            if el is None:el=etree.SubElement(borders,q(edge))
            for key,value in [('val','single'),('sz','4'),('color','000000')]:el.set(q(key),value)
        for tc in tbl.findall('.//'+q('tc')):
            tcp=tc.find(q('tcPr'))
            if tcp is None:tcp=etree.Element(q('tcPr'));tc.insert(0,tcp)
            for sh in tcp.findall(q('shd')):tcp.remove(sh)
            etree.SubElement(tcp,q('shd')).set(q('fill'),'FFFFFF')
        if tbl.getnext() is None or tbl.getnext().tag!=q('p'):
            after=etree.Element(q('p'));tbl.addnext(after)
    files['word/document.xml']=etree.tostring(m.doc,xml_declaration=True,encoding='UTF-8',standalone=True)
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        for n,b in files.items():z.writestr(n,b)
