import contextlib,io,json,tempfile,unittest
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from test_release_pipeline import builder
from pipeline import execute,inventory
from ooxml_model import OOXMLModel,q,ns
class PipelineTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.src=builder.build(self.root/'source.docx');self.out=self.root/'output.docx';self.plan=self.root/'roles.json';self.report=self.root/'report.json'
  m=OOXMLModel(self.src);plan=[]
  for row in m.paragraphs():
   if not row['text'].strip() or m.style_name(row['style_id'])=='图片':continue
   role=row['role'] if row['role'] in {'body','title',*(f'heading-{i}' for i in range(1,6))} else 'body'
   plan.append({'text':row['text'],'role':role})
  self.plan.write_text(json.dumps({'complete':True,'paragraphs':plan}))
 def test_complete_pipeline_preserves_media_and_is_idempotent(self):
  result=execute(self.src,self.out,self.plan,24,self.report,heading_start=1)
  self.assertEqual(result['status'],'structural_pass_visual_pending');self.assertTrue(result['idempotence'])
  with ZipFile(self.src) as x,ZipFile(self.out) as y:
   self.assertEqual(x.read('word/media/demo-workflow.png'),y.read('word/media/demo-workflow.png'))
 def test_failed_plan_does_not_install_output(self):
  self.plan.write_text(json.dumps({'complete':False,'paragraphs':[]}))
  with self.assertRaisesRegex(ValueError,'complete'):execute(self.src,self.out,self.plan,24,self.report)
  self.assertFalse(self.out.exists());self.assertEqual(json.loads(self.report.read_text())['status'],'failed')
 def test_complex_structure_is_reported_before_mutation(self):
  with ZipFile(self.src) as z:files={n:z.read(n) for n in z.namelist()}
  d=E.fromstring(files['word/document.xml']);E.SubElement(d.find(q('body')),q('sdt'));files['word/document.xml']=E.tostring(d)
  with ZipFile(self.src,'w',ZIP_DEFLATED) as z:
   for n,b in files.items():z.writestr(n,b)
  with self.assertRaisesRegex(ValueError,'Specialist'):execute(self.src,self.out,self.plan,24,self.report)
  self.assertFalse(self.out.exists())

 def test_preflight_scans_non_main_story_parts(self):
  with ZipFile(self.src) as z:files={n:z.read(n) for n in z.namelist()}
  files['word/header99.xml']=b'<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:sdt/></w:hdr>'
  files['word/settings.xml']=b'<w:settings'
  with ZipFile(self.src,'w',ZIP_DEFLATED) as z:
   for n,b in files.items():z.writestr(n,b)
  report=inventory(self.src)
  self.assertIn('word/header99.xml',report['story_parts'])
  self.assertGreaterEqual(report['story_counts']['content_controls'],1)
  self.assertIn('content_controls',report['requires_specialist_review'])
  self.assertIn('word/settings.xml',report['package_parse_errors'])
  self.assertIn('malformed_xml',report['requires_specialist_review'])

 def test_text_box_is_a_preserve_only_warning(self):
  with ZipFile(self.src) as z:files={n:z.read(n) for n in z.namelist()}
  d=E.fromstring(files['word/document.xml']);body=d.find(q('body'))
  textbox=E.SubElement(body,q('txbxContent'))
  p=E.SubElement(textbox,q('p'));r=E.SubElement(p,q('r'));t=E.SubElement(r,q('t'));t.text='保留文本框内容'
  E.SubElement(p,q('bookmarkStart'),{q('id'):'42',q('name'):'保留书签'})
  E.SubElement(p,q('fldSimple'),{q('instr'):'PAGE'})
  files['word/document.xml']=E.tostring(d)
  with ZipFile(self.src,'w',ZIP_DEFLATED) as z:
   for n,b in files.items():z.writestr(n,b)
  report=inventory(self.src)
  self.assertGreaterEqual(report['story_counts']['text_boxes'],1)
  self.assertIn('text_boxes',report['preserve_only_warnings'])
  self.assertIn('fields',report['preserve_only_warnings'])
  self.assertIn('bookmarks',report['preserve_only_warnings'])
  self.assertNotIn('text_boxes',report['requires_specialist_review'])
  result=execute(self.src,self.out,self.plan,24,self.report,heading_start=1)
  self.assertEqual(result['status'],'structural_pass_visual_pending')
  self.assertTrue(self.out.exists())
 def test_overwrite_original_is_rejected(self):
  with self.assertRaisesRegex(ValueError,'differ'):execute(self.src,self.src,self.plan,24,self.report)
 def test_independently_authored_forward_case_is_now_regression(self):
  root=Path(__file__).resolve().parents[1]/'examples/forward-case'
  result=execute(root/'input.docx',self.out,root/'roles.json',24,self.report)
  self.assertTrue(result['content_preserved'])
  m=OOXMLModel(self.out);rows=list(m.paragraphs())
  self.assertEqual(sum(r['role']=='heading-2' for r in rows),4)
  self.assertEqual(sum(r['role']=='heading-3' for r in rows),2)
  dates=[r for r in rows if r['text'].startswith('统计日期：')]
  self.assertEqual(len(dates),1);self.assertEqual(dates[0]['role'],'body')
 def test_default_does_not_chain_body_or_figure_captions(self):
  result=execute(self.src,self.out,self.plan,24,self.report,heading_start=1)
  m=OOXMLModel(self.out)
  for row in m.paragraphs():
   if row['role']=='body' or row['text'].startswith('图1 '):
    keep=row['element'].find('./'+q('pPr')+'/'+q('keepNext'))
    self.assertTrue(keep is None or keep.get(q('val'))=='0')
