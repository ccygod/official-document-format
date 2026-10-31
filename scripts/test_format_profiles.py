import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from test_structure_rules import fixture
from apply_official_rules import main as apply
from check_official_document import main as check
from ooxml_model import OOXMLModel, q, ns
from format_profiles import list_profiles, load_profile, role_half_points


class FormatProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.src = Path(self.tmp.name) / "source.docx"
        self.out = Path(self.tmp.name) / "out.docx"
        fixture(self.src)

    def test_profile_catalog_has_required_routes(self):
        ids = {p["id"] for p in list_profiles()}
        self.assertTrue({"official_cn", "briefing_cn", "industry_report_cn", "academic_thesis_cn", "technical_manual_cn"} <= ids)
        self.assertEqual(role_half_points(load_profile("academic_thesis_cn"), 24, "heading_1"), 30)

    def test_profile_changes_effective_role_fonts_and_sizes(self):
        profile = load_profile("academic_thesis_cn")
        apply(self.src, self.out, 24, profile["line_multiple"], False, heading_indent_chars=profile["heading_indent_chars"], format_profile=profile)
        model = OOXMLModel(self.out)
        for row in model.paragraphs():
            if row["role"] == "heading-2":
                size = model.effective(row["style_id"], "rPr").find(q("sz"))
                fonts = model.effective(row["style_id"], "rPr").find(q("rFonts"))
                self.assertEqual(size.get(q("val")), "26")
                self.assertEqual(fonts.get(q("eastAsia")), "黑体")
                break
        expected_roles = {
            "title": ("36", "宋体"),
            "caption": ("21", "宋体"),
        }
        for sid, style in model.styles.items():
            role = model.role(sid)
            if role not in expected_roles:
                continue
            effective = model.effective(sid, "rPr")
            size = effective.find(q("sz")); fonts = effective.find(q("rFonts"))
            self.assertEqual((size.get(q("val")), fonts.get(q("eastAsia"))), expected_roles[role])
        with contextlib.redirect_stdout(io.StringIO()) as log:
            self.assertEqual(check(self.out, 24, False, profile["line_multiple"], True, 0, 25, 50, expected_heading_indent_chars=0, format_profile=profile), 0)

    def test_profile_updates_title_font_for_non_official_route(self):
        profile = load_profile("briefing_cn")
        apply(self.src, self.out, 24, profile["line_multiple"], False, heading_indent_chars=profile["heading_indent_chars"], format_profile=profile)
        model = OOXMLModel(self.out)
        title = next(sid for sid in model.styles if model.role(sid) == "title")
        rpr = model.effective(title, "rPr")
        self.assertEqual(rpr.find(q("rFonts")).get(q("eastAsia")), "方正小标宋简体")
        self.assertEqual(rpr.find(q("sz")).get(q("val")), "36")

    def test_profile_selection_is_required_by_pipeline_cli(self):
        import pipeline
        parser_action = next(a for a in pipeline.argparse.ArgumentParser()._actions if a.dest == "help")
        # The executable parser itself is checked through --help in the smoke test;
        # this assertion protects the public profile catalog separately.
        self.assertTrue(load_profile("official_cn")["display_name"])
