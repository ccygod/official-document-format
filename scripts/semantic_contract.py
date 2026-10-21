"""Apply agent-reviewed paragraph roles, then materialize verifiable indentation.

The agent reads context and decides roles; this module does not guess semantic
roles from a keyword list, font size, or a short-paragraph regular expression.
"""
import json
import re
from pathlib import Path
from lxml import etree
from ooxml_model import q, ns


def resolve_plan(model, path):
    plan=json.loads(Path(path).read_text())
    entries=plan['paragraphs']
    if not isinstance(entries,list) or not entries:
        raise ValueError('role map paragraphs must be a nonempty list')
    rows=list(model.paragraphs()); resolved=[]; used=set()
    for entry in entries:
        role=entry['role']
        if role not in {'body','title',*(f'heading-{i}' for i in range(1,6))}:
            raise ValueError(f'unsupported semantic role: {role}')
        matches=[r for r in rows if r['text'].strip()==entry['text'].strip()]
        if 'occurrence' in entry:
            occurrence=entry['occurrence']
            if not isinstance(occurrence,int) or occurrence<1:
                raise ValueError('occurrence must be a positive integer')
            matches=matches[occurrence-1:occurrence]
        if len(matches)!=1:
            raise ValueError(f'missing or ambiguous paragraph: {entry["text"]!r}; specify occurrence for duplicates')
        row=matches[0]
        row['planned_numbering']=entry.get('numbering')
        if row['index'] in used:raise ValueError('duplicate paragraph in role map')
        used.add(row['index']);resolved.append((row,role))
    if plan.get('complete'):
        missing=[r['text'] for r in rows if r['text'].strip() and r['index'] not in used and model.style_name(r['style_id'])!='图片']
        if missing:raise ValueError(f'incomplete semantic role map: {missing!r}')
    return resolved


def apply_role_map(model,path):
    resolved=resolve_plan(model,path)  # validate entire plan before mutation
    styles={model.role(sid):sid for sid in model.styles
            if model.styles[sid].get(q('type'))=='paragraph'}
    for row,role in resolved:
        if role not in styles:raise ValueError(f'reference lacks semantic role {role}')
        if row['role']==role:
            if row.get('planned_numbering')=='template':
                pp=row['element'].find(q('pPr'))
                if pp is not None:
                    for np in pp.findall(q('numPr')):pp.remove(np)
            continue
        p=row['element'];pp=p.find(q('pPr'))
        if pp is None:pp=etree.Element(q('pPr'));p.insert(0,pp)
        for tag in ('pStyle','outlineLvl','numPr','ind','jc','rPr'):
            for x in pp.findall(q(tag)):pp.remove(x)
        ps=etree.Element(q('pStyle'));ps.set(q('val'),styles[role]);pp.insert(0,ps)
        # Typography must come from the resolved role, not source decoration.
        for rp in p.xpath('.//w:rPr',namespaces=ns):rp.getparent().remove(rp)
        if role=='body' or (row.get('planned_numbering')!='template' and re.match(r'^(?:[一二三四五六七八九十百]+[、.]|[（(][一二三四五六七八九十百\d]+[）)]|\d+[.、])',row['text'].strip())):
            np=etree.SubElement(pp,q('numPr'));etree.SubElement(np,q('numId')).set(q('val'),'0')


def role_map_failures(model,path):
    try:
        failures=[]
        for row,role in resolve_plan(model,path):
            if row['role']!=role:
                failures.append(f'semantic role {row["text"]!r}: expected {role}, found {row["role"]}')
            elif role.startswith('heading-'):
                if row.get('planned_numbering')=='template':
                    num=row['num']
                    if not num or num.get('ilvl')!=str(int(role.split('-')[1])-1):
                        failures.append(f'semantic role {row["text"]!r}: template numbering is disabled or uses wrong level')
                pp=row['pPr']; outline=pp.find(q('outlineLvl')) if pp is not None else None
                if outline is None or outline.get(q('val'))!=str(int(role.split('-')[1])-1):
                    failures.append(f'semantic role {row["text"]!r}: wrong or missing explicit outline level')
        return failures
    except (ValueError,KeyError,TypeError) as exc:
        return [f'invalid semantic role map: {exc}']


def materialize_indents(model,body_half,heading_chars=2):
    for row in model.paragraphs():
        role=row['role']
        if role!='body' and role not in {f'heading-{i}' for i in range(1,6)}:continue
        p=row['element'];pp=p.find(q('pPr'))
        if pp is None:pp=etree.Element(q('pPr'));p.insert(0,pp)
        ind=pp.find(q('ind'))
        if ind is None:ind=etree.SubElement(pp,q('ind'))
        for attr in ('hanging','hangingChars'):ind.attrib.pop(q(attr),None)
        chars=2 if role=='body' else heading_chars
        # Paragraph indents override numbering-level left/hanging geometry;
        # otherwise template list indent + firstLine silently doubles the inset.
        ind.set(q('left'),'0')
        ind.set(q('leftChars'),'0')
        ind.set(q('firstLineChars'),str(round(chars*100)))
        ind.set(q('firstLine'),str(round(chars*body_half*10)))


def indent_failures(model,heading_chars=2):
    failures=[]
    for sid in model.styles:
        role=model.role(sid)
        if role not in {'body',*(f'heading-{i}' for i in range(1,6))}:continue
        name=(model.style_name(sid) or '').lower().replace(' ','')
        if name not in {'normal','正文','5级标题',*(f'heading{i}' for i in range(1,6)),*(f'标题{i}' for i in range(1,6))}:continue
        expected=200 if role=='body' else round(heading_chars*100)
        ind=model.effective(sid,'pPr').find(q('ind'))
        if ind is None or ind.get(q('firstLineChars'))!=str(expected):
            failures.append(f'style definition {model.style_name(sid)} indent differs from requested {expected/100:g} characters')
    for row in model.paragraphs():
        role=row['role']
        if not row['text'].strip() or (role!='body' and role not in {f'heading-{i}' for i in range(1,6)}):continue
        pp=row['pPr'];ind=pp.find(q('ind')) if pp is not None else None
        expected=200 if role=='body' else round(heading_chars*100)
        try:actual=float(ind.get(q('firstLineChars'))) if ind is not None else None
        except (ValueError,TypeError):actual=None
        if actual!=expected or (ind is not None and any(float(ind.get(q(k),'0'))!=0 for k in ('hanging','hangingChars','left','leftChars'))):
            failures.append(f'{role} indent paragraph {row["index"]}: expected {expected/100:g} characters')
    return failures
