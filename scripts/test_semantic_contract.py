import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
from lxml import etree as E
from test_structure_rules import fixture
from ooxml_model import OOXMLModel, q, ns
from apply_official_rules import main as apply
from check_official_document import main as check


class SemanticContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.src = Path(self.tmp.name)/'source.docx'
        self.out = Path(self.tmp.name)/'output.docx'
        fixture(self.src, automatic=False)

    def test_context_plan_promotes_plain_text_and_preserves_nonheading(self):
        plan = Path(self.tmp.name)/'roles.json'
        plan.write_text(json.dumps({'paragraphs': [
            {'text': '前言正文', 'role': 'heading-2'},
            {'text': '结束正文', 'role': 'body'}]}))
        apply(self.src, self.out, 24, 1.35, False, role_map=plan)
        rows = {r['text']:r for r in OOXMLModel(self.out).paragraphs()}
        self.assertEqual(rows['前言正文']['role'], 'heading-2')
        self.assertEqual(rows['结束正文']['role'], 'body')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check(self.out, role_map=plan), 0)

    def test_checker_rejects_semantic_heading_left_as_body(self):
        apply(self.src, self.out, 24, 1.35, False)
        plan = Path(self.tmp.name)/'roles.json'
        plan.write_text(json.dumps({'paragraphs': [{'text':'前言正文','role':'heading-2'}]}))
        with contextlib.redirect_stdout(io.StringIO()) as log:
            result = check(self.out, role_map=plan)
        self.assertEqual(result, 1)
        self.assertIn('semantic role', log.getvalue())

    def test_body_and_headings_get_real_two_character_indent(self):
        apply(self.src, self.out, 24, 1.35, False)
        for row in OOXMLModel(self.out).paragraphs():
            if row['text'] and (row['role']=='body' or row['role'].startswith('heading-')):
                self.assertEqual(row['pPr'].find(q('ind')).get(q('firstLineChars')), '200')

    def test_zero_heading_indent_override_passes_numeric_checker(self):
        apply(self.src, self.out, 24, 1.35, False, heading_indent_chars=0)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check(self.out, expected_heading_indent_chars=0), 0)

    def test_checker_rejects_missing_body_indent(self):
        apply(self.src, self.out, 24, 1.35, False)
        with ZipFile(self.out) as z: files={n:z.read(n) for n in z.namelist()}
        doc=E.fromstring(files['word/document.xml'])
        p=next(p for p in doc.xpath('//w:body/w:p',namespaces=ns)
               if ''.join(p.xpath('.//w:t/text()',namespaces=ns))=='结束正文')
        pp=p.find(q('pPr')); pp.find(q('ind')).set(q('firstLineChars'),'0')
        files['word/document.xml']=E.tostring(doc)
        with ZipFile(self.out,'w') as z:
            for n,b in files.items():z.writestr(n,b)
        with contextlib.redirect_stdout(io.StringIO()) as log:
            self.assertEqual(check(self.out),1)
        self.assertIn('body indent',log.getvalue())

    def test_ambiguous_plan_fails_instead_of_guessing(self):
        from semantic_contract import apply_role_map
        model=OOXMLModel(self.src)
        first=model.doc.xpath('//w:body/w:p',namespaces=ns)[2]
        from copy import deepcopy
        model.doc.find(q('body')).append(deepcopy(first))
        plan=Path(self.tmp.name)/'roles.json'
        plan.write_text(json.dumps({'paragraphs':[{'text':'前言正文','role':'heading-2'}]}))
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            apply_role_map(model,plan)

    def test_role_plan_can_demote_misleading_source_heading(self):
        plan=Path(self.tmp.name)/'roles.json'
        plan.write_text(json.dumps({'paragraphs':[{'text':'建设目标','role':'body'}]}))
        apply(self.src,self.out,24,1.35,False,role_map=plan)
        row=next(r for r in OOXMLModel(self.out).paragraphs() if r['text']=='建设目标')
        self.assertEqual(row['role'],'body')
        self.assertIsNone(row['num'])

    def test_same_semantic_plan_is_idempotent(self):
        plan=Path(self.tmp.name)/'roles.json'
        plan.write_text(json.dumps({'paragraphs':[{'text':'前言正文','role':'heading-2'}]}))
        apply(self.src,self.out,24,1.35,False,role_map=plan)
        second=Path(self.tmp.name)/'second.docx'
        apply(self.out,second,24,1.35,False,role_map=plan)
        with ZipFile(self.out) as x,ZipFile(second) as y:
            self.assertEqual({n:x.read(n) for n in x.namelist()}, {n:y.read(n) for n in y.namelist()})

    def test_heading_two_number_symbol_is_not_left_bold(self):
        fixture(self.src,automatic=True)
        with ZipFile(self.src) as z:files={n:z.read(n) for n in z.namelist()}
        num=E.fromstring(files['word/numbering.xml'])
        for lvl in num.xpath('//w:lvl[@w:ilvl="1"]',namespaces=ns):
            rp=E.SubElement(lvl,q('rPr'));E.SubElement(rp,q('b')).set(q('val'),'1')
            E.SubElement(lvl,q('pStyle')).set(q('val'),'level_custom_2')
            lvl.find(q('lvlText')).set(q('val'),'    %2、')
        files['word/numbering.xml']=E.tostring(num)
        with ZipFile(self.src,'w') as z:
            for n,b in files.items():z.writestr(n,b)
        apply(self.src,self.out,24,1.35,False)
        row=next(r for r in OOXMLModel(self.out).paragraphs() if r['text']=='项目概述')
        self.assertEqual(row['num']['level'].find(q('rPr')).find(q('b')).get(q('val')),'0')
        self.assertEqual(row['num']['level'].find(q('lvlText')).get(q('val')),'%2、')

    def test_complete_plan_rejects_omitted_paragraph(self):
        from semantic_contract import apply_role_map
        model=OOXMLModel(self.src)
        plan=Path(self.tmp.name)/'roles.json'
        plan.write_text(json.dumps({'complete':True,'paragraphs':[{'text':'前言正文','role':'body'}]}))
        with self.assertRaisesRegex(ValueError,'incomplete semantic role map'):
            apply_role_map(model,plan)

    def test_style_definition_matches_applied_indent(self):
        apply(self.src,self.out,24,1.35,False)
        model=OOXMLModel(self.out)
        for sid in model.styles:
            if model.role(sid) in {'body','heading-1','heading-2','heading-3','heading-4','heading-5'}:
                self.assertEqual(model.effective(sid,'pPr').find(q('ind')).get(q('firstLineChars')),'200')

    def test_template_numbering_plan_rejects_disabled_numbering(self):
        fixture(self.src,automatic=True)
        apply(self.src,self.out,24,1.35,False)
        plan=Path(self.tmp.name)/'roles.json'
        plan.write_text(json.dumps({'paragraphs':[{'text':'项目概述','role':'heading-2','numbering':'template'}]}))
        with ZipFile(self.out) as z:files={n:z.read(n) for n in z.namelist()}
        doc=E.fromstring(files['word/document.xml'])
        p=next(p for p in doc.xpath('//w:body/w:p',namespaces=ns) if ''.join(p.xpath('.//w:t/text()',namespaces=ns))=='项目概述')
        np=E.SubElement(p.find(q('pPr')),q('numPr'));E.SubElement(np,q('numId')).set(q('val'),'0')
        files['word/document.xml']=E.tostring(doc)
        with ZipFile(self.out,'w') as z:
            for n,b in files.items():z.writestr(n,b)
        with contextlib.redirect_stdout(io.StringIO()) as log:
            self.assertEqual(check(self.out,role_map=plan),1)
        self.assertIn('template numbering',log.getvalue())
