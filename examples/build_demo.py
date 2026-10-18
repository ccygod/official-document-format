#!/usr/bin/env python3
"""Build an original, fictional demo on the bundled style system; no customer data."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';q=lambda n:'{'+W+'}'+n

def build(output):
 root=Path(__file__).resolve().parents[1]
 with ZipFile(root/'assets/reference.docx') as z:files={n:z.read(n) for n in z.namelist()}
 styles=E.fromstring(files['word/styles.xml'])
 names={s.find(q('name')).get(q('val')):s.get(q('styleId')) for s in styles if s.find(q('name')) is not None}
 doc=E.fromstring(files['word/document.xml']);body=doc.find(q('body'));section=body.find(q('sectPr'))
 for c in list(body):body.remove(c)
 def paragraph(text,style):
  p=E.SubElement(body,q('p'));pp=E.SubElement(p,q('pPr'));E.SubElement(pp,q('pStyle')).set(q('val'),names[style])
  if text:E.SubElement(E.SubElement(p,q('r')),q('t')).text=text
  return p
 paragraph('项目建设方案示例','Title');paragraph('','Normal')
 paragraph('本示例展示标题、正文、编号和表格的统一排版。项目与内容均为虚构，用于验证公开模板，不涉及真实客户。','Normal')
 paragraph('建设目标','heading 1')
 paragraph('围绕资料整理、协作审阅与交付复核三个环节，形成可追溯的文档工作流程。具体数量、预算和建设状态应以实际材料为准。','Normal')
 paragraph('实施安排','heading 2')
 paragraph('先核对底稿与读者需求，再完成内容编排，最后检查格式、编号、分页及表格呈现。','Normal')
 caption=paragraph('表1  示例交付清单','图片');pp=caption.find(q('pPr'));E.SubElement(pp,q('jc')).set(q('val'),'center')
 table=E.SubElement(body,q('tbl'));pr=E.SubElement(table,q('tblPr'));borders=E.SubElement(pr,q('tblBorders'))
 for side in ['top','left','bottom','right','insideH','insideV']:
  el=E.SubElement(borders,q(side));el.set(q('val'),'single');el.set(q('sz'),'4');el.set(q('color'),'B8B8B8')
 grid=E.SubElement(table,q('tblGrid'))
 for width in [750,2200,5300]:E.SubElement(grid,q('gridCol')).set(q('w'),str(width))
 for row in [['序号','交付项','主要内容'],['1','说明材料','明确目标、范围、实施安排与验收依据。'],['2','检查记录','保留格式检查结果、渲染记录与未解决问题。']]:
  tr=E.SubElement(table,q('tr'))
  for text,width in zip(row,[750,2200,5300]):
   tc=E.SubElement(tr,q('tc'));tcp=E.SubElement(tc,q('tcPr'));cw=E.SubElement(tcp,q('tcW'));cw.set(q('w'),str(width));cw.set(q('type'),'dxa')
   p=E.SubElement(tc,q('p'));pp=E.SubElement(p,q('pPr'));E.SubElement(pp,q('pStyle')).set(q('val'),names['表格'])
   E.SubElement(E.SubElement(p,q('r')),q('t')).text=text
 paragraph('说明：检查脚本验证结构与格式属性，实际页貌仍需在目标软件中渲染确认。','Normal')
 if section is not None:body.append(section)
 files['word/document.xml']=E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 with ZipFile(output,'w',ZIP_DEFLATED) as z:
  for n,data in files.items():z.writestr(n,data)
 return output
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('output');print(build(p.parse_args().output))
