import tempfile
import unittest
from pathlib import Path
from install_skill import install

class InstallTests(unittest.TestCase):
    def test_install_preserves_resources_and_excludes_git(self):
        with tempfile.TemporaryDirectory() as t:
            src=Path(t)/'source';src.mkdir();(src/'SKILL.md').write_text('skill')
            (src/'references').mkdir();(src/'references'/'guide.md').write_text('guide')
            (src/'.git').mkdir();(src/'.git'/'config').write_text('local')
            dst=Path(t)/'host'/'skill';install(src,dst)
            self.assertEqual((dst/'references'/'guide.md').read_text(),'guide')
            self.assertFalse((dst/'.git').exists())
    def test_existing_install_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as t:
            src=Path(t)/'source';src.mkdir();(src/'SKILL.md').write_text('new')
            dst=Path(t)/'installed';dst.mkdir();(dst/'SKILL.md').write_text('mine')
            with self.assertRaises(FileExistsError):install(src,dst)
            self.assertEqual((dst/'SKILL.md').read_text(),'mine')
    def test_self_nested_destination_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            src=Path(t);(src/'SKILL.md').write_text('skill')
            with self.assertRaises(ValueError):install(src,src/'nested')
