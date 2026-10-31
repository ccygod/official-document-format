"""Resolve Word property attributes without losing inherited font/indent fields."""
from copy import deepcopy
from lxml import etree
from ooxml_model import q, ns
from format_profiles import role_half_points
FALSE={'0','false','off'}
def enabled(node):
    return node is not None and node.get(q('val'),'1').lower() not in FALSE

def merge(target,source):
    if source is None:return target
    for child in source:
        old=target.find(child.tag)
        if old is not None and child.tag in {q('rFonts'),q('ind'),q('spacing'),q('lang')}:
            old.attrib.update(child.attrib)
        else:
            if old is not None:target.remove(old)
            target.append(deepcopy(child))
    return target

def style_props(model,sid,container):
    result=etree.Element(q(container))
    defaults=model.styles_xml.find('./'+q('docDefaults')+'/'+q(container+'Default')+'/'+q(container))
    merge(result,defaults)
    for s in model.style_chain(sid):merge(result,s.find(q(container)))
    return result

def run_props(model,p,r):
    result=style_props(model,model.p_style(p),'rPr')
    sid=r.find('./'+q('rPr')+'/'+q('rStyle'))
    if sid is not None:
        for st in model.style_chain(sid.get(q('val'))):merge(result,st.find(q('rPr')))
    merge(result,r.find(q('rPr')))
    return result

def paragraph_props(model,p):
    return merge(style_props(model,model.p_style(p),'pPr'),p.find(q('pPr')))

def typography_failures(model,half_points,format_profile=None):
    failures=[]
    for row in model.paragraphs():
        role=row['role']
        allowed={'body',*(f'heading-{i}' for i in range(1,6))}
        # Figure/table captions are canonicalized by normalize_captions after
        # this pass. Rewriting their typography here would reorder bold nodes
        # on the next pass and break package-level idempotence.
        if format_profile: allowed |= {'title'}
        if role not in allowed:continue
        p=row['element'];expected=style_props(model,row['style_id'],'rPr')
        ef=expected.find(q('rFonts'));expected_font=ef.get(q('eastAsia')) if ef is not None else None
        for r in p.xpath('.//w:r[w:t]',namespaces=ns):
            actual=run_props(model,p,r);text=''.join(r.xpath('.//w:t/text()',namespaces=ns))
            size=actual.find(q('sz'))
            expected_size=role_half_points(format_profile,half_points,role) if format_profile else half_points
            if half_points is not None and (size is None or size.get(q('val'))!=str(expected_size)):
                failures.append(f'paragraph {row["index"]} effective run size differs from {half_points}')
            font=actual.find(q('rFonts'))
            if font is not None and any('theme' in etree.QName(k).localname.lower() for k in font.attrib):
                failures.append(f'paragraph {row["index"]} unresolved theme font conflicts with fixed profile')
            if expected_font and any('\u4e00'<=c<='\u9fff' for c in text) and (font is None or font.get(q('eastAsia'))!=expected_font):
                failures.append(f'paragraph {row["index"]} effective font differs from style {expected_font}')
            if role.startswith('heading-') and enabled(actual.find(q('b')))!=enabled(expected.find(q('b'))):
                failures.append(f'paragraph {row["index"]} effective heading weight differs from style')
    return failures

def normalize_text_format(model,half_points,format_profile=None):
    # Preserve body emphasis, links, breaks and runs. Typography belongs to roles.
    for row in model.paragraphs():
        role=row['role']
        allowed={'body',*(f'heading-{i}' for i in range(1,6))}
        if format_profile: allowed |= {'title','caption'}
        if role not in allowed:continue
        expected=style_props(model,row['style_id'],'rPr');fonts=expected.find(q('rFonts'))
        for r in row['element'].xpath('.//w:r[w:t]',namespaces=ns):
            rp=r.find(q('rPr'))
            if rp is None:rp=etree.Element(q('rPr'));r.insert(0,rp)
            for tag in ('rFonts','sz','szCs'):
                for x in rp.findall(q(tag)):rp.remove(x)
            if fonts is not None:
                frozen=deepcopy(fonts)
                for key in list(frozen.attrib):
                    if 'theme' in etree.QName(key).localname.lower():del frozen.attrib[key]
                rp.append(frozen)
            expected_size=role_half_points(format_profile,half_points,role) if format_profile else half_points
            for tag in ('sz','szCs'):etree.SubElement(rp,q(tag)).set(q('val'),str(expected_size))
            if role.startswith('heading-'):
                for tag in ('b','bCs'):
                    for x in rp.findall(q(tag)):rp.remove(x)
                    etree.SubElement(rp,q(tag)).set(q('val'),'1' if enabled(expected.find(q(tag))) else '0')
