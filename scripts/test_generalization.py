"""Adversarial cases use real package mutation, not matching writer output text."""
import contextlib,io,json,tempfile,unittest
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from test_structure_rules import fixture
from apply_official_rules import main as apply
from check_official_document import main as check
from ooxml_model import OOXMLModel,q,ns
from smart_table_widths import infer_widths
from pipeline import execute,inventory

class Adversarial(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name);self.src=self.root/'in.docx';self.out=self.root/'out.docx'
  fixture(self.src);apply(self.src,self.out,24,1.35,True)
 def patch(self,fn):
  with ZipFile(self.out) as z:files={n:z.read(n) for n in z.namelist()}
  doc=E.fromstring(files['word/document.xml']);fn(doc);files['word/document.xml']=E.tostring(doc)
  with ZipFile(self.out,'w',ZIP_DEFLATED) as z:
   for n,b in files.items():z.writestr(n,b)
 def test_font_and_actual_size_override_is_rejected(self):
  def change(d):
   p=next(p for p in d.xpath('//w:body/w:p',namespaces=ns) if ''.join(p.xpath('.//w:t/text()',namespaces=ns))=='项目概述')
   r=p.find(q('r'));rp=r.find(q('rPr'));rp.find(q('rFonts')).set(q('eastAsia'),'宋体');rp.find(q('sz')).set(q('val'),'48')
  self.patch(change)
  with contextlib.redirect_stdout(io.StringIO()) as log:self.assertEqual(check(self.out,24),1)
  self.assertIn('effective run size',log.getvalue());self.assertIn('effective font',log.getvalue())
 def test_false_pagination_properties_are_rejected(self):
  def change(d):
   for p in d.xpath('//w:body/w:p',namespaces=ns):
    for x in p.find(q('pPr')):
     if x.tag in [q('keepLines'),q('keepNext'),q('widowControl')]:x.set(q('val'),'0')
  self.patch(change)
  with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(check(self.out,24,True),1)
 def test_body_emphasis_is_preserved(self):
  def change(d):
   p=next(p for p in d.xpath('//w:body/w:p',namespaces=ns) if ''.join(p.xpath('.//w:t/text()',namespaces=ns))=='结束正文')
   E.SubElement(p.find(q('r')).find(q('rPr')),q('b')).set(q('val'),'1')
  self.patch(change);second=self.root/'second.docx';apply(self.out,second,24,1.35,True)
  m=OOXMLModel(second);p=next(r for r in m.paragraphs() if r['text']=='结束正文')['element']
  self.assertEqual(p.find('./'+q('r')+'/'+q('rPr')+'/'+q('b')).get(q('val')),'1')
 def test_all_narrow_table_columns_do_not_crash_or_expand(self):
  t=E.Element(q('tbl'));r=E.SubElement(t,q('tr'))
  for text in ['序号','数量']:
   p=E.SubElement(E.SubElement(r,q('tc')),q('p'));E.SubElement(E.SubElement(p,q('r')),q('t')).text=text
  widths,meta=infer_widths(t,8306)
  self.assertTrue(all(0<w<=900 for w in widths));self.assertLessEqual(sum(widths),8306)
 def test_source_body_list_numbering_definition_is_untouched(self):
  with ZipFile(self.src) as z:before=E.fromstring(z.read('word/numbering.xml'))
  with ZipFile(self.out) as z:after=E.fromstring(z.read('word/numbering.xml'))
  for aid in ['1','2']:
   path=f'{q("abstractNum")}[@{q("abstractNumId")}="{aid}"]'
   self.assertEqual(E.tostring(before.find(path)),E.tostring(after.find(path)))
 def test_source_theme_fonts_are_removed_from_effective_format(self):
  from effective_format import run_props
  def change(d):pass
  with ZipFile(self.src) as z:files={n:z.read(n) for n in z.namelist()}
  styles=E.fromstring(files['word/styles.xml'])
  defaults=E.SubElement(styles,q('docDefaults'));rp=E.SubElement(E.SubElement(defaults,q('rPrDefault')),q('rPr'));E.SubElement(rp,q('rFonts')).set(q('eastAsiaTheme'),'minorEastAsia')
  files['word/styles.xml']=E.tostring(styles)
  with ZipFile(self.src,'w') as z:
   for n,b in files.items():z.writestr(n,b)
  apply(self.src,self.out,24,1.35,False)
  m=OOXMLModel(self.out)
  for row in m.paragraphs():
   if row['role'] not in ['body','heading-2','heading-3']:continue
   for r in row['element'].findall(q('r')):
    f=run_props(m,row['element'],r).find(q('rFonts'))
    self.assertFalse(any('theme' in E.QName(k).localname.lower() for k in f.attrib))
 def test_short_regular_column_does_not_expand_to_page_width(self):
  t=E.Element(q('tbl'))
  for vals in [['序号','类别','数量'],['1','甲类','2']]:
   r=E.SubElement(t,q('tr'))
   for text in vals:
    p=E.SubElement(E.SubElement(r,q('tc')),q('p'));E.SubElement(E.SubElement(p,q('r')),q('t')).text=text
  widths,_=infer_widths(t,8306)
  self.assertLess(sum(widths),4000)
 def test_time_column_with_long_schedule_gets_prose_width(self):
  t=E.Element(q('tbl'))
  for vals in [['事项','时间安排','成果'],['甲','2026年10月至11月：完成准备工作；2026年12月至次年1月：完成验证','阶段性验收成果说明文字比较长']]:
   r=E.SubElement(t,q('tr'))
   for text in vals:
    p=E.SubElement(E.SubElement(r,q('tc')),q('p'));E.SubElement(E.SubElement(p,q('r')),q('t')).text=text
  widths,meta=infer_widths(t,8306)
  self.assertEqual(meta['roles'][1],'flex');self.assertGreater(widths[1],1500)
