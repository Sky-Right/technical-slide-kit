import base64
from pathlib import Path
import shutil
import tempfile
import unittest

import build


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ["theme", "assets", "content"]:
            shutil.copytree(build.ROOT / name, self.root / name)
        for name in ["NOTICE", "LICENSE"]:
            shutil.copy(build.ROOT / name, self.root / name)
        self.source = self.root / "content/slides.md"
        self.output = self.root / "elsewhere/nested/index.html"

    def render(self, markdown, **kwargs):
        self.source.write_text(markdown, encoding="utf-8")
        build.build(self.source, self.output, root=self.root, **kwargs)
        return self.output.read_text(encoding="utf-8")

    def test_portable_output_in_arbitrary_directory(self):
        rendered = self.render('# A & B\n\n![Diagram](../assets/workflow.svg)\n')
        self.assertIn('<title>A &amp; B</title>', rendered)
        self.assertNotIn('src="vendor/', rendered)
        self.assertNotIn('href="slides.css"', rendered)
        self.assertIn('data:font/ttf;base64,', rendered)
        self.assertIn('SIL OPEN FONT LICENSE', rendered)
        self.assertIn('Permission is hereby granted', rendered)
        self.assertIn(base64.b64encode((self.root / 'assets/workflow.svg').read_bytes()).decode(), rendered)

    def test_remote_and_private_paths_fail_without_creating_output(self):
        for path in ['https://example.com/private.png', '//example.com/x.png',
                     '/etc/passwd', '../../outside.png']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.render(f'![image]({path})')
            self.assertFalse(self.output.exists())

    def test_missing_asset_is_an_error(self):
        with self.assertRaises(FileNotFoundError):
            self.render('![image](missing.png)')
        self.assertFalse(self.output.exists())

    def test_literal_code_examples_are_preserved(self):
        markdown = '# Code\n```markdown\n![Example](not-an-asset.png)\n```\n\n`![Inline](also-missing.png)`\n'
        rendered = self.render(markdown)
        self.assertIn('![Example](not-an-asset.png)', rendered)
        self.assertIn('![Inline](also-missing.png)', rendered)

    def test_html_images_and_existing_data_uris(self):
        rendered = self.render('<img src="../assets/workflow.svg" alt="flow">\n![inline](data:image/png;base64,YQ==)')
        self.assertIn('&lt;img src="data:image/svg+xml;base64,', rendered)
        self.assertIn('![inline](data:image/png;base64,YQ==)', rendered)

    def test_source_cannot_close_textarea_or_replace_template_tokens(self):
        rendered = self.render('# Hi\n</textarea><script>alert(1)</script>\n@@TITLE@@\n')
        self.assertIn('&lt;/textarea&gt;&lt;script&gt;', rendered)
        self.assertIn('@@TITLE@@', rendered)
        self.assertEqual(rendered.count('</textarea>'), 1)

    def test_optional_branding_and_language(self):
        rendered = self.render('# 标题', logo=self.root / 'assets/example-logo.svg', language='zh-CN')
        self.assertIn('<html lang="zh-CN">', rendered)
        self.assertIn('--brand-logo:url("data:image/svg+xml;base64,', rendered)

    def test_does_not_overwrite_markdown(self):
        self.source.write_text('# Keep me', encoding='utf-8')
        with self.assertRaises(ValueError):
            build.build(self.source, self.source, root=self.root)
        self.assertEqual(self.source.read_text(), '# Keep me')

    def test_css_imports_are_explicit_errors(self):
        (self.root / 'theme/custom.css').write_text('@import "https://example.com/style.css";')
        with self.assertRaises(ValueError):
            self.render('# Hi')


if __name__ == '__main__':
    unittest.main()
