"""Shared figure/table caption typography, resolved from actual styles and runs."""
from copy import deepcopy
import re
from lxml import etree
from ooxml_model import q, ns

CAPTION = re.compile(r'^(?:图|表)\s*\d+(?:\s|[.、：:]|$)')
FIGURE = re.compile(r'^图\s*\d+(?:\s|[.、：:]|$)')
FALSE = {'0', 'false', 'off'}
RPR_ORDER = {
    'rStyle': 10, 'rFonts': 20, 'kern': 30, 'lang': 40,
    'sz': 50, 'szCs': 60, 'b': 70, 'bCs': 80,
    'i': 90, 'iCs': 100, 'color': 110, 'u': 120,
}

def text(p):
    return ''.join(p.xpath('.//w:t/text()', namespaces=ns)).strip()

def merge_props(result, source):
    if source is None:
        return
    for child in source:
        old = result.find(child.tag)
        if old is not None and child.tag == q('rFonts'):
            old.attrib.update(child.attrib)
        else:
            if old is not None:
                result.remove(old)
            result.append(deepcopy(child))

def effective_run(styles, p, run):
    default = next((sid for sid, s in styles.items() if s.get(q('type')) == 'paragraph' and s.get(q('default')) == '1'), None)
    sid = p.xpath('./w:pPr/w:pStyle/@w:val', namespaces=ns)
    result = etree.Element(q('rPr'))
    def apply(sid):
        chain = []; seen = set()
        while sid and sid not in seen:
            seen.add(sid); st = styles.get(sid)
            if st is None: break
            chain.append(st)
            base = st.find(q('basedOn')); sid = base.get(q('val')) if base is not None else None
        for st in reversed(chain): merge_props(result, st.find(q('rPr')))
    apply(sid[0] if sid else default)
    merge_props(result, p.find('./' + q('pPr') + '/' + q('rPr')))
    if run is not None:
        rstyle = run.xpath('./w:rPr/w:rStyle/@w:val', namespaces=ns)
        if rstyle: apply(rstyle[0])
        merge_props(result, run.find(q('rPr')))
    return result

def signature(rpr):
    fonts = rpr.find(q('rFonts'))
    def val(name, default=None):
        n = rpr.find(q(name)); return n.get(q('val'), default) if n is not None else default
    def on(name):
        n = rpr.find(q(name)); return n is not None and n.get(q('val')) not in FALSE
    return (tuple(fonts.get(q(k)) for k in ('ascii', 'hAnsi', 'eastAsia', 'cs')) if fonts is not None else (),
            val('sz'), val('szCs', val('sz')), on('b'), on('bCs'), on('i'), on('iCs'), val('color', '000000'))

def canonicalize_rpr(rpr):
    """Make caption run-property child order deterministic for idempotence."""
    children=list(rpr)
    for child in children:
        rpr.remove(child)
    for child in sorted(enumerate(children), key=lambda item: (RPR_ORDER.get(etree.QName(item[1]).localname, 1000), item[0])):
        rpr.append(child[1])
    return rpr

def caption_profile(root, styles):
    image_sid = next((sid for sid, s in styles.items() if s.xpath('./w:name/@w:val', namespaces=ns) == ['图片']), None)
    if image_sid is None:
        raise ValueError('Missing required paragraph style 图片')
    captions = [p for p in root.xpath('.//w:body/w:p', namespaces=ns) if FIGURE.match(text(p))]
    if captions:
        p = captions[0]
        run = next((r for r in p.findall(q('r')) if r.xpath('.//w:t/text()', namespaces=ns)), None)
    else:
        p = etree.Element(q('p')); pp = etree.SubElement(p, q('pPr')); etree.SubElement(pp, q('pStyle')).set(q('val'), image_sid)
        run = None
    rpr = effective_run(styles, p, run)
    # Captions are regular weight; explicitly disable bold inherited from any role.
    for name in ('b', 'bCs'):
        n = rpr.find(q(name))
        if n is None: n = etree.SubElement(rpr, q(name))
        n.set(q('val'), '0')
    rstyle = rpr.find(q('rStyle'))
    if rstyle is not None: rpr.remove(rstyle)
    return image_sid, canonicalize_rpr(rpr)

def normalize_captions(root, styles):
    sid, profile = caption_profile(root, styles)
    for p in root.xpath('.//w:body/w:p', namespaces=ns):
        if not CAPTION.match(text(p)): continue
        pp = p.find(q('pPr'))
        if pp is None: pp = etree.Element(q('pPr')); p.insert(0, pp)
        for name, value in (('pStyle', sid), ('jc', 'center')):
            n = pp.find(q(name))
            if n is None: n = etree.SubElement(pp, q(name))
            n.set(q('val'), value)
        keep = pp.find(q('keepNext'))
        if keep is None: keep = etree.SubElement(pp, q('keepNext'))
        keep.set(q('val'), '0' if FIGURE.match(text(p)) else '1')
        for old in pp.findall(q('rPr')): pp.remove(old)
        for r in p.xpath('.//w:r', namespaces=ns):
            for old in r.findall(q('rPr')): r.remove(old)
            r.insert(0, deepcopy(profile))
