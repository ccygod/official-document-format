#!/usr/bin/env python3
"""在公开母版上构建原创虚构示例，展示五级标题、正文、图片及图表说明。"""
import argparse
from copy import deepcopy
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
 def centered(p):E.SubElement(p.find(q('pPr')),q('jc')).set(q('val'),'center');return p
 paragraph('公文格式完整示例','Title');paragraph('','Normal')
 paragraph('本示例以虚构项目展示主标题、一至五级标题、正文及图表样式。内容用于排版演示，不涉及真实客户或采购承诺。','Normal')
 paragraph('建设目标','heading 1')
 paragraph('围绕底稿核对、格式处理与页面验收建立文档交付流程，使内容层次、编号关系和图表说明清楚可读。','Normal')
 paragraph('实施安排','heading 2')
 paragraph('先明确任务范围与交付要求，再依据母版完成内容编排和格式处理。','Normal')
 paragraph('阶段任务','heading 3')
 paragraph('各阶段明确输入材料、责任分工与完成依据，避免只罗列抽象原则。','Normal')
 paragraph('资料核对','heading 4')
 paragraph('核实材料名称、版本和适用范围，发现缺口时记录待确认事项。','Normal')
 inline=paragraph('','5级标题');pp=inline.find(q('pPr'));E.SubElement(pp,q('outlineLvl')).set(q('val'),'4')
 run=E.SubElement(inline,q('r'));rp=E.SubElement(run,q('rPr'));E.SubElement(rp,q('b'));E.SubElement(run,q('t')).text='时间安排：'
 run=E.SubElement(inline,q('r'));rp=E.SubElement(run,q('rPr'))
 normal=next(s for s in styles if s.get(q('styleId'))==names['Normal']);nr=normal.find(q('rPr'))
 if nr is not None:
  for c in nr:rp.append(deepcopy(c))
 for tag in ['b','bCs']:
  for e in list(rp.findall(q(tag))):rp.remove(e)
  E.SubElement(rp,q(tag)).set(q('val'),'0')
 E.SubElement(run,q('t')).text='在进入格式处理前完成资料核对，具体周期依据当前任务确认。'
 p=paragraph('图表与说明','heading 1');E.SubElement(p.find(q('pPr')),q('pageBreakBefore'))
 paragraph('图示用于解释工作关系，表格用于集中列示项目。图题置于图下，表题置于表上，表下注释补充统计口径或适用范围。','Normal')
 p=centered(paragraph('','图片'));E.SubElement(p.find(q('pPr')),q('keepNext'))
 # 直接写入图片关系与绘图结构，保留母版其他包部件。
 drawing=E.fromstring('''<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="5181600" cy="1312672"/><wp:docPr id="41" name="文档格式处理流程" descr="底稿核对、格式处理和页面验收的顺序关系"/><wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="41" name="demo-workflow.png"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="rIdDemoWorkflow"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="5181600" cy="1312672"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>''')
 p.append(drawing)
 centered(paragraph('图1  文档格式处理流程示意','图片'))
 centered(paragraph('表1  示例交付清单','图片'))
 table=E.SubElement(body,q('tbl'));pr=E.SubElement(table,q('tblPr'));borders=E.SubElement(pr,q('tblBorders'))
 for side in ['top','left','bottom','right','insideH','insideV']:
  el=E.SubElement(borders,q(side));el.set(q('val'),'single');el.set(q('sz'),'4');el.set(q('color'),'B8B8B8')
 grid=E.SubElement(table,q('tblGrid'))
 for width in [750,2200,5300]:E.SubElement(grid,q('gridCol')).set(q('w'),str(width))
 for row in [['序号','交付项','主要内容'],['1','正文与标题','按层级组织内容，保持字号、编号和缩进一致。'],['2','图片与图注','保留真实插图，并在图下说明其表达内容。'],['3','表格与表注','在表上放表题，在表下交代范围或口径。']]:
  tr=E.SubElement(table,q('tr'))
  for text,width in zip(row,[750,2200,5300]):
   tc=E.SubElement(tr,q('tc'));tcp=E.SubElement(tc,q('tcPr'));cw=E.SubElement(tcp,q('tcW'));cw.set(q('w'),str(width));cw.set(q('type'),'dxa')
   p=E.SubElement(tc,q('p'));pp=E.SubElement(p,q('pPr'));E.SubElement(pp,q('pStyle')).set(q('val'),names['表格'])
   E.SubElement(E.SubElement(p,q('r')),q('t')).text=text
 paragraph('注：本表仅用于展示排版。交付项为虚构示例，不构成真实项目的范围或验收承诺。','Normal')
 if section is not None:body.append(section)
 files['word/document.xml']=E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
 rel=E.fromstring(files['word/_rels/document.xml.rels']);rn='{http://schemas.openxmlformats.org/package/2006/relationships}'
 E.SubElement(rel,rn+'Relationship',Id='rIdDemoWorkflow',Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/image',Target='media/demo-workflow.png')
 files['word/_rels/document.xml.rels']=E.tostring(rel,xml_declaration=True,encoding='UTF-8',standalone=True)
 files['word/media/demo-workflow.png']=(root/'assets/demo-workflow.png').read_bytes()
 ct=E.fromstring(files['[Content_Types].xml'])
 if not any(c.get('Extension')=='png' for c in ct):E.SubElement(ct,'{http://schemas.openxmlformats.org/package/2006/content-types}Default',Extension='png',ContentType='image/png')
 files['[Content_Types].xml']=E.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True)
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 with ZipFile(output,'w',ZIP_DEFLATED) as z:
  for n,data in files.items():z.writestr(n,data)
 return output
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('output');print(build(p.parse_args().output))
