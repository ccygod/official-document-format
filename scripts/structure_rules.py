"""Default content structure for this template; shared writer/checker predicates."""
from copy import deepcopy
import re
from lxml import etree
from ooxml_model import OOXMLModel, q, ns

LITERAL_BULLET = re.compile(r'^\s*[•·●○▪▫◦‣⁃\uf0b7]\s*')
TOC_TITLE = re.compile(r'^(?:目\s*录|contents|table\s+of\s+contents)$', re.I)
TOC_STYLE = re.compile(r'^(?:toc\s*\d+|目录\s*\d+|WPSOffice手动目录\s*\d+)$', re.I)
TOC_ENTRY = re.compile(r'.+(?:[.．…·]{2,}|\t)\s*\d+\s*$')

def text(p): return ''.join(p.xpath('.//w:t/text()',namespaces=ns)).strip()

def ppr(p):
    pp=p.find(q('pPr'))
    if pp is None:pp=etree.Element(q('pPr'));p.insert(0,pp)
    return pp

def put(pp, tag, value):
    x=pp.find(q(tag))
    if x is None:x=etree.SubElement(pp,q(tag))
    x.set(q('val'),str(value));return x

def bullet_numbering(model, p):
    num=model.effective_num(p)
    if not num or num['level'] is None:return False
    fmt=num['level'].find(q('numFmt'))
    return fmt is not None and fmt.get(q('val'))=='bullet'

def toc_nodes(model):
    """Find manual, styled, SDT and field TOCs without matching prose about TOCs."""
    doc=model.doc; nodes=set(); body=doc.find(q('body'))
    # Word and WPS TOC content controls, including cached paragraphs.
    for sdt in doc.xpath('.//w:sdt',namespaces=ns):
        galleries=sdt.xpath('./w:sdtPr//w:docPartGallery/@w:val',namespaces=ns)
        instr=''.join(sdt.xpath('.//w:instrText/text()',namespaces=ns))
        if any(TOC_TITLE.match(v) for v in galleries) or re.search(r'\bTOC\b',instr):nodes.add(sdt)
    # Complex TOC fields can span several sibling paragraphs.
    for container in [body]+doc.xpath('.//w:sdtContent',namespaces=ns):
        children=list(container)
        for i,p in enumerate(children):
            instr=''.join(p.xpath('.//w:instrText/text()|.//w:fldSimple/@w:instr',namespaces=ns))
            if not re.search(r'\bTOC\b',instr):continue
            nodes.add(p)
            if p.xpath('.//w:fldSimple',namespaces=ns):continue
            depth=0; started=False
            for prior in children[max(0,i-1):i]:
                # A field begin may live in a preceding otherwise empty paragraph.
                if not text(prior) and prior.xpath('.//w:fldChar[@w:fldCharType="begin"]',namespaces=ns):
                    nodes.add(prior);depth=1;started=True
            for candidate in children[i:]:
                if candidate is not p and model.role(model.p_style(candidate)).startswith('heading-') and not TOC_STYLE.match(model.style_name(model.p_style(candidate)) or ''):break
                nodes.add(candidate)
                for fc in candidate.xpath('.//w:fldChar/@w:fldCharType',namespaces=ns):
                    if fc=='begin':depth+=1;started=True
                    elif fc=='end':depth-=1
                if (started and depth<=0) or not started:break
    # Manual TOCs: exact title through entries/reading notes, stopping at real content.
    for i,p in enumerate(list(body)):
        sid=model.p_style(p); name=model.style_name(sid) or ''
        if TOC_STYLE.match(name):nodes.add(p)
        if p.tag!=q('p') or not TOC_TITLE.match(text(p)):continue
        nodes.add(p)
        for following in list(body)[i+1:]:
            if following.tag!=q('p'):break
            ft=text(following);fn=model.style_name(model.p_style(following)) or ''
            if model.role(model.p_style(following)).startswith('heading-') and not TOC_STYLE.match(fn):break
            # Also accept source manual entries with plain spacing before page digits.
            entry=TOC_ENTRY.match(ft) or re.match(r'^[一二三四五六七八九十百\d]+[ 、.．].*\d+$',ft)
            if not ft or TOC_STYLE.match(fn) or entry or ft.startswith('阅读提示'):
                nodes.add(following)
            else:break
    return nodes

def structure_failures(model, keep_toc=False, keep_bullets=False, heading_start=2):
    failures=[]
    if not keep_toc and toc_nodes(model):failures.append('TOC content remains; default output must have no TOC')
    for i,p in enumerate(model.doc.xpath('.//w:body//w:p',namespaces=ns)):
        role=model.role(model.p_style(p))
        if role.startswith('heading-') and int(role.split('-')[1])<heading_start:
            failures.append(f'paragraph {i} uses forbidden {role}; begin at heading-{heading_start}')
        if not keep_bullets and (bullet_numbering(model,p) or LITERAL_BULLET.match(text(p))):
            failures.append(f'paragraph {i} retains a visible or inherited bullet')
    return failures

def normalize_structure(model, keep_toc=False, keep_bullets=False, heading_start=2):
    if not keep_toc:
        # Deepest first, so enclosing SDTs can be removed safely afterward.
        for node in sorted(toc_nodes(model),key=lambda x:len(list(x.iterancestors())),reverse=True):
            if node.getparent() is not None:node.getparent().remove(node)
    roles={}
    for sid in model.styles:
        role=model.role(sid)
        if role.startswith('heading-'):roles.setdefault(int(role.split('-')[1]),sid)
    paras=model.doc.xpath('.//w:body//w:p',namespaces=ns)
    used=[int(model.role(model.p_style(p)).split('-')[1]) for p in paras if model.role(model.p_style(p)).startswith('heading-')]
    shift=max(0,heading_start-min(used)) if used else 0
    # Resolve every source role first; simultaneous mapping makes this idempotent.
    changes=[(p,int(model.role(model.p_style(p)).split('-')[1])) for p in paras if model.role(model.p_style(p)).startswith('heading-')]
    for p,level in changes:
        target=min(9,level+shift)
        if target not in roles:raise ValueError(f'Missing heading {target} style; import reference styles before applying rules')
        pp=ppr(p);put(pp,'pStyle',roles[target]);put(pp,'outlineLvl',target-1)
        if shift:
            # Direct source typography/indent must not override the target template role.
            for tag in ('rPr','ind','jc','numPr'):
                for x in pp.findall(q(tag)):pp.remove(x)
            for rp in p.xpath('.//w:rPr',namespaces=ns):rp.getparent().remove(rp)
            # Source literal numbering remains the single numbering authority.
            manual=bool(re.match(r'^(?:[一二三四五六七八九十百]+[ 、]|[（(][一二三四五六七八九十百\d]+[）)])',text(p)))
            if manual:
                np=etree.SubElement(pp,q('numPr'));put(np,'numId',0)
            else:
                effective=model.effective_num(p)
                if effective:
                    np=pp.find(q('numPr'))
                    if np is None:np=etree.SubElement(pp,q('numPr'))
                    put(np,'numId',effective['numId']);put(np,'ilvl',target-1)
        if target==2:put(pp,'jc','left')
        put(pp,'keepNext',1);put(pp,'keepLines',1);put(pp,'widowControl',1)
    if keep_bullets:return
    for p in paras:
        literal=LITERAL_BULLET.match(text(p))
        if not bullet_numbering(model,p) and not literal:continue
        pp=ppr(p);put(pp,'pStyle',model.default_style)
        for tag in ('numPr','ind','tabs','rPr'):
            for x in pp.findall(q(tag)):pp.remove(x)
        # numId=0 explicitly overrides docDefaults and any inherited numbering.
        np=etree.SubElement(pp,q('numPr'));put(np,'numId',0)
        # WPS may retain a list's hanging layout when numId=0 is written alone.
        # Materialize the body's own indentation instead of inheriting a list indent.
        body_ind=model.effective(model.default_style,'pPr').find(q('ind'))
        if body_ind is not None:pp.append(deepcopy(body_ind))
        else:
            ind=etree.SubElement(pp,q('ind'));ind.set(q('left'),'0');ind.set(q('firstLineChars'),'200')
        for rp in p.xpath('.//w:rPr',namespaces=ns):rp.getparent().remove(rp)
        if literal:
            # Remove only the leading marker across runs; preserve internal dots and runs.
            nodes=p.xpath('.//w:t',namespaces=ns);full=''.join(x.text or '' for x in nodes)
            match=LITERAL_BULLET.match(full);left=match.end() if match else 0
            for node in nodes:
                t=node.text or '';take=min(left,len(t));node.text=t[take:];left-=take
                if not left:break
