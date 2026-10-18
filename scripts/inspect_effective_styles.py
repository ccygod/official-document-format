#!/usr/bin/env python3
import argparse,json
from ooxml_model import OOXMLModel
ap=argparse.ArgumentParser(); ap.add_argument('docx'); ap.add_argument('--json',dest='out'); a=ap.parse_args(); m=OOXMLModel(a.docx)
out={'path':a.docx,'styles':[],'paragraphs':[]}
for sid in sorted(m.styles):
 r=m.effective(sid,'rPr'); sz=r.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz'); out['styles'].append({'id':sid,'name':m.style_name(sid),'role':m.role(sid),'size':None if sz is None else sz.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')})
for p in m.paragraphs(): out['paragraphs'].append({'index':p['index'],'style_id':p['style_id'],'style_name':p['style_name'],'role':p['role'],'text':p['text'],'numbering':None if p['num'] is None else {k:v for k,v in p['num'].items() if k!='level'}})
print(json.dumps(out,ensure_ascii=False,indent=2))
if a.out: open(a.out,'w').write(json.dumps(out,ensure_ascii=False,indent=2))
