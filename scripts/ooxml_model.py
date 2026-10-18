"""Semantic OOXML model for WPS/Word documents. Resolves style inheritance and numbering."""
from copy import deepcopy
from hashlib import sha256
from zipfile import ZipFile
from lxml import etree
import re
NS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; ns={'w':NS}; q=lambda t:'{'+NS+'}'+t
class OOXMLModel:
 def __init__(self,path):
  self.path=path; self.z=ZipFile(path); self.doc=etree.fromstring(self.z.read('word/document.xml')); self.styles_xml=etree.fromstring(self.z.read('word/styles.xml')); self.num_xml=etree.fromstring(self.z.read('word/numbering.xml')) if 'word/numbering.xml' in self.z.namelist() else None
  self.styles={s.get(q('styleId')):s for s in self.styles_xml.findall(q('style'))}
  self.num_to_abs={n.get(q('numId')): (n.find(q('abstractNumId')).get(q('val')) if n.find(q('abstractNumId')) is not None else None) for n in (self.num_xml.findall(q('num')) if self.num_xml is not None else [])}
  self.abstracts={a.get(q('abstractNumId')):a for a in (self.num_xml.findall(q('abstractNum')) if self.num_xml is not None else [])}
 def style_chain(self,sid):
  out=[]; seen=set()
  while sid and sid not in seen:
   seen.add(sid); s=self.styles.get(sid)
   if s is None: break
   out.append(s); b=s.find(q('basedOn')); sid=b.get(q('val')) if b is not None else None
  return list(reversed(out))
 def style_name(self,sid):
  s=self.styles.get(sid); n=s.find(q('name')) if s is not None else None; return n.get(q('val')) if n is not None else sid
 def role(self,sid):
  st=self.styles.get(sid)
  if st is not None and st.get(q('type')) not in (None,'paragraph'):
   return 'other'
  name=(self.style_name(sid) or '').lower().replace(' ','')
  if name=='title' or name=='标题': return 'title'
  if name in ('normal','正文'): return 'body'
  m=re.search(r'(?:heading|标题)([1-9])',name)
  if m:return f'heading-{m.group(1)}'
  if '5级标题' in name:return 'heading-5'
  for s in self.style_chain(sid):
   p=s.find(q('pPr')); o=p.find(q('outlineLvl')) if p is not None else None
   if o is not None:return f'heading-{int(o.get(q("val")))+1}'
  return 'other'
 def effective(self,sid,container):
  result=etree.Element(q(container))
  for s in self.style_chain(sid):
   c=s.find(q(container))
   if c is None:continue
   for child in list(c):
    old=result.find(child.tag)
    if old is not None:result.remove(old)
    result.append(deepcopy(child))
  return result
 def p_style(self,p):
  pp=p.find(q('pPr')); s=pp.find(q('pStyle')) if pp is not None else None; return s.get(q('val')) if s is not None else '1'
 def effective_num(self,p):
  sid=self.p_style(p); pp=p.find(q('pPr')); np=pp.find(q('numPr')) if pp is not None else None
  if np is None: np=self.effective(sid,'pPr').find(q('numPr'))
  if np is None:return None
  il=np.find(q('ilvl')); ni=np.find(q('numId')); numid=ni.get(q('val')) if ni is not None else None; ilvl=il.get(q('val')) if il is not None else '0'; aid=self.num_to_abs.get(numid)
  lvl=self.abstracts.get(aid).find(f'{q("lvl")}[{q("ilvl")}="{ilvl}"]') if aid in self.abstracts else None
  return {'numId':numid,'ilvl':ilvl,'abstractNumId':aid,'level':lvl}
 def paragraphs(self):
  for i,p in enumerate(self.doc.xpath('.//w:body/w:p',namespaces=ns)):
   sid=self.p_style(p); effp=self.effective(sid,'pPr'); effr=self.effective(sid,'rPr'); yield {'index':i,'element':p,'style_id':sid,'style_name':self.style_name(sid),'role':self.role(sid),'text':''.join(p.xpath('.//w:t/text()',namespaces=ns)),'pPr':p.find(q('pPr')),'effective_pPr':effp,'effective_rPr':effr,'num':self.effective_num(p)}
 def snapshot(self):
  styles=[]
  for sid in sorted(self.styles):
   e=self.effective(sid,'rPr'); sz=e.find(q('sz')); styles.append((sid,self.style_name(sid),self.role(sid),sz.get(q('val')) if sz is not None else None,etree.tostring(self.effective(sid,'pPr'),encoding='unicode')))
  paras=[(p['style_id'],p['role'],p['text']) for p in self.paragraphs()]
  return {'styles':styles,'paragraphs':paras,'parts':sorted((n,sha256(self.z.read(n)).hexdigest()) for n in self.z.namelist())}
