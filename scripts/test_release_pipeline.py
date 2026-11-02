import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile
from lxml import etree as E
import apply_official_rules as rules
import check_official_document as checker
from ooxml_model import OOXMLModel

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('demo_builder',ROOT/'examples/build_demo.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class ReleasePipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name);self.src=builder.build(self.path/'input.docx');self.out=self.path/'out.docx'
        rules.main(self.src,self.out,28,1.35,False)
    def test_demo_passes_semantic_check(self):
        with contextlib.redirect_stdout(io.StringIO()):
            result=checker.main(self.out,expected_half_points=28,expected_line_multiple=1.35,require_snap_to_grid_off=True,expected_before_lines=0,expected_after_lines=25,expected_table_after_lines=50)
        self.assertEqual(result,0)
    def test_showcase_covers_five_heading_levels_figure_and_table_notes(self):
        rules.main(self.src,self.out,28,1.35,False,heading_start=1)
        model=OOXMLModel(self.out);records=list(model.paragraphs())
        roles={r['role'] for r in records}
        self.assertTrue({f'heading-{i}' for i in range(1,6)} <= roles)
        self.assertTrue(model.doc.xpath('.//*[local-name()="drawing"]'))
        texts=[r['text'] for r in records]
        self.assertTrue(any(t.startswith('图1 ') for t in texts))
        self.assertTrue(any(t.startswith('表1 ') for t in texts))
        self.assertTrue(any(t.startswith('注：') for t in texts))
    def test_wrong_requested_size_is_rejected(self):
        with contextlib.redirect_stdout(io.StringIO()):result=checker.main(self.out,expected_half_points=24)
        self.assertEqual(result,1)
    def test_second_pass_is_semantically_stable(self):
        second=self.path/'second.docx';rules.main(self.out,second,28,1.35,False)
        self.assertEqual(OOXMLModel(self.out).snapshot(),OOXMLModel(second).snapshot())
    def test_package_changes_stay_in_declared_parts(self):
        with ZipFile(self.src) as a,ZipFile(self.out) as b:
            self.assertEqual(a.namelist(),b.namelist())
            changed={n for n in a.namelist() if a.read(n)!=b.read(n)}
            self.assertTrue(changed<={'word/document.xml','word/styles.xml','word/numbering.xml'})
    def test_public_template_has_no_private_identity_or_font_binary(self):
        with ZipFile(ROOT/'assets/reference.docx') as z:
            self.assertFalse(any(n.endswith('.odttf') for n in z.namelist()))
            text='\n'.join(z.read(n).decode('utf-8',errors='ignore') for n in z.namelist() if n.endswith('.xml'))
            for term in ['/Users/apple','天津光泰','西青区','KSOTemplateDocerSaveRecord']:self.assertNotIn(term,text)

    def test_skill_entrypoint_requires_format_size_and_numbering_before_work(self):
        skill=(ROOT/'SKILL.md').read_text(encoding='utf-8')
        prompt=(ROOT/'agents/openai.yaml').read_text(encoding='utf-8')
        self.assertIn('首轮交互门禁',skill)
        self.assertIn('不能读取、检查、生成角色清单或修改DOCX',skill)
        self.assertIn('文档风格',prompt)
        self.assertIn('三项确认前不要读取或修改DOCX',prompt)
if __name__=='__main__':unittest.main()
