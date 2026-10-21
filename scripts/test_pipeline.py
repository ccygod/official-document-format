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
