"""Regression tests for heading start, TOC exclusion and hidden list bullets."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
from lxml import etree as E
from apply_official_rules import main as apply
from check_official_document import main as check
from ooxml_model import OOXMLModel, q, ns


def fixture(path, automatic=True):
    styles = E.Element(q('styles'), nsmap={'w': ns['w']})
    def style(sid, name, base=None):
        s = E.SubElement(styles, q('style'), {q('type'): 'paragraph', q('styleId'): sid})
        E.SubElement(s, q('name'), {q('val'): name})
        if base: E.SubElement(s, q('basedOn'), {q('val'): base})
        return s
    default = style('base_custom', 'Normal'); default.set(q('default'), '1')
    rp = E.SubElement(default, q('rPr'))
    E.SubElement(rp, q('rFonts'), {q('eastAsia'): '仿宋', q('ascii'): 'Times New Roman'})
    E.SubElement(rp, q('sz'), {q('val'): '24'})
    for i in range(1, 6):
        s = style('level_custom_' + str(i), 'heading ' + str(i), 'base_custom')
        pp = E.SubElement(s, q('pPr'))
        E.SubElement(pp, q('outlineLvl'), {q('val'): str(i-1)})
        if automatic:
            np = E.SubElement(pp, q('numPr'))
            E.SubElement(np, q('ilvl'), {q('val'): str(i-1)})
            E.SubElement(np, q('numId'), {q('val'): '10'})
    style('caption_custom', '图片', 'base_custom')
    style('title_custom', 'Title', 'base_custom')
    style('toc_custom', 'toc 1', 'base_custom')
    bullet = style('list_base', 'List Base', 'base_custom')
    np = E.SubElement(E.SubElement(bullet, q('pPr')), q('numPr'))
    E.SubElement(np, q('numId'), {q('val'): '7'})
    style('list_child', 'List Child', 'list_base')
    num = E.Element(q('numbering'), nsmap={'w': ns['w']})
    for aid, fmt, symbol, levels in [('1', 'bullet', '•', 1), ('2', 'decimal', '%1.', 1), ('3', 'decimal', '%1.', 5)]:
        abstract = E.SubElement(num, q('abstractNum'), {q('abstractNumId'): aid})
        for level in range(levels):
            lv = E.SubElement(abstract, q('lvl'), {q('ilvl'): str(level)})
            E.SubElement(lv, q('numFmt'), {q('val'): fmt})
            E.SubElement(lv, q('lvlText'), {q('val'): symbol})
    for nid, aid in [('7', '1'), ('9', '2'), ('10', '3')]:
        E.SubElement(E.SubElement(num, q('num'), {q('numId'): nid}), q('abstractNumId'), {q('val'): aid})
    doc = E.Element(q('document'), nsmap={'w': ns['w']}); body = E.SubElement(doc, q('body'))
    def p(text, sid=None, numid=None):
        p = E.SubElement(body, q('p')); pp = E.SubElement(p, q('pPr'))
        if sid: E.SubElement(pp, q('pStyle'), {q('val'): sid})
        if numid is not None:
            np = E.SubElement(pp, q('numPr')); E.SubElement(np, q('numId'), {q('val'): str(numid)})
        E.SubElement(E.SubElement(p, q('r')), q('t')).text = text
        return p
    p('测试方案', 'title_custom'); p('', 'base_custom'); p('前言正文')
    p('目录', 'toc_custom'); p('一、项目概述……3', 'toc_custom')
    p('项目概述', 'level_custom_1'); p('建设目标', 'level_custom_2')
    p('继承项目符号', 'list_child'); p('直接项目符号', numid=7)
    literal = p('•', 'base_custom'); E.SubElement(E.SubElement(literal, q('r')), q('t')).text=' 文字项目'
    p('· 另一项目'); p('保留A·B和正文中的•符号')
    p('有序步骤', numid=9); p('显式禁用编号', 'list_child', numid=0)
    p('目录管理', 'level_custom_2'); p('结束正文')
    with ZipFile(path, 'w') as z:
        for name, root in [('word/document.xml', doc), ('word/styles.xml', styles), ('word/numbering.xml', num)]:
            z.writestr(name, E.tostring(root))
        z.writestr('word/footer1.xml', b'preserve-footer')


class StructureRules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.src = Path(self.tmp.name)/'in.docx'; self.out = Path(self.tmp.name)/'out.docx'
        fixture(self.src)

    def run_writer(self):
        apply(self.src, self.out, 24, 1.35, False)
        return OOXMLModel(self.out)

    def test_heading_roles_start_at_two_and_keep_hierarchy(self):
        model = self.run_writer(); rows = {r['text']:r for r in model.paragraphs()}
        self.assertEqual(rows['项目概述']['role'], 'heading-2')
        self.assertEqual(rows['建设目标']['role'], 'heading-3')
        self.assertEqual(rows['测试方案']['role'], 'title')
        self.assertEqual(rows['项目概述']['num']['ilvl'], '1')
        self.assertEqual(rows['建设目标']['num']['ilvl'], '2')
        self.assertEqual(rows['项目概述']['element'].xpath('./w:pPr/w:jc/@w:val',namespaces=ns),['left'])

    def test_manual_toc_removed_without_removing_content_heading(self):
        model = self.run_writer(); texts=[r['text'] for r in model.paragraphs()]
        self.assertNotIn('目录', texts); self.assertNotIn('一、项目概述……3', texts)
        self.assertIn('目录管理', texts); self.assertIn('结束正文', texts)

    def test_inherited_direct_and_literal_bullets_become_body(self):
        model=self.run_writer(); rows={r['text']:r for r in model.paragraphs()}
        for t in ['继承项目符号','直接项目符号','文字项目','另一项目']:
            self.assertIn(t, rows)
            self.assertIsNone(rows[t]['num'], t)
            self.assertEqual(rows[t]['role'], 'body')
        self.assertIn('保留A·B和正文中的•符号',rows)
        self.assertEqual(rows['有序步骤']['num']['numId'],'9')

    def test_zero_numid_is_effective_numbering_off(self):
        model=OOXMLModel(self.src)
        p=next(r for r in model.paragraphs() if r['text']=='显式禁用编号')
        self.assertIsNone(p['num'])

    def test_named_and_field_toc_blocks_removed(self):
        with ZipFile(self.src) as z: files={n:z.read(n) for n in z.namelist()}
        doc=E.fromstring(files['word/document.xml']); body=doc.find(q('body'))
        sdt=E.Element(q('sdt'));props=E.SubElement(sdt,q('sdtPr'))
        E.SubElement(E.SubElement(E.SubElement(props,q('docPartObj')),q('docPartGallery')).getparent(),q('docPartUnique'))
        props.find('.//'+q('docPartGallery')).set(q('val'),'Table of Contents')
        p=E.SubElement(E.SubElement(sdt,q('sdtContent')),q('p'))
        E.SubElement(E.SubElement(p,q('r')),q('instrText')).text=' TOC \\o "1-3" '
        E.SubElement(E.SubElement(p,q('r')),q('t')).text='缓存目录'
        body.insert(0,sdt);files['word/document.xml']=E.tostring(doc)
        with ZipFile(self.src,'w') as z:
            for n,b in files.items():z.writestr(n,b)
        model=self.run_writer()
        self.assertFalse(model.doc.xpath('//w:instrText[contains(text(),"TOC")]',namespaces=ns))
        self.assertNotIn('缓存目录',''.join(model.doc.xpath('//w:t/text()',namespaces=ns)))

    def test_second_pass_is_byte_identical_per_part(self):
        self.run_writer(); second=Path(self.tmp.name)/'second.docx'
        apply(self.out, second,24,1.35,False)
        with ZipFile(self.out) as x,ZipFile(second) as y:
            self.assertEqual(x.namelist(),y.namelist())
            self.assertEqual({n:x.read(n) for n in x.namelist()},{n:y.read(n) for n in y.namelist()})

    def test_literal_heading_numbers_remain_single_authority(self):
        with ZipFile(self.src) as z: files={n:z.read(n) for n in z.namelist()}
        doc=E.fromstring(files['word/document.xml'])
        p=next(p for p in doc.xpath('//w:body/w:p',namespaces=ns) if ''.join(p.xpath('.//w:t/text()',namespaces=ns))=='项目概述')
        p.find('.//'+q('t')).text='一、项目概述'
        files['word/document.xml']=E.tostring(doc)
        with ZipFile(self.src,'w') as z:
            for n,b in files.items():z.writestr(n,b)
        model=self.run_writer();row=next(r for r in model.paragraphs() if r['text']=='一、项目概述')
        self.assertEqual(row['role'],'heading-2');self.assertIsNone(row['num'])

    def test_explicit_overrides_preserve_requested_structure(self):
        apply(self.src,self.out,24,1.35,False,keep_toc=True,keep_bullets=True,heading_start=1)
        model=OOXMLModel(self.out);rows={r['text']:r for r in model.paragraphs()}
        self.assertIn('目录',rows);self.assertEqual(rows['项目概述']['role'],'heading-1')
        self.assertEqual(rows['继承项目符号']['num']['numId'],'7')
        from structure_rules import structure_failures
        self.assertEqual(structure_failures(model,keep_toc=True,keep_bullets=True,heading_start=1),[])

    def test_checker_rejects_legacy_structure(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            result=check(self.src)
        self.assertEqual(result,1)
        self.assertIn('heading-1',out.getvalue())
        self.assertIn('TOC',out.getvalue())
        self.assertIn('bullet',out.getvalue())


if __name__=='__main__':unittest.main()
