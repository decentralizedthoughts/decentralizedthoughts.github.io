"""Regression checks for broken-link patterns observed in GA's 404 report."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_site


class SiteLinksTest(unittest.TestCase):
    def test_unfinished_links_are_errors(self):
        for value in ("TBD", "...", "post on security definitions"):
            with self.subTest(value=value), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(check_site.check_target("article/index.html", value), 1)

    def test_real_paths_are_not_mistaken_for_placeholders(self):
        self.assertEqual(check_site.resolve_internal_target("index.html", "postscript.js"), "postscript.js")
        self.assertEqual(check_site.resolve_internal_target("index.html", "/img/a diagram.png"), "img/a diagram.png")

    def test_self_redirect_is_an_error(self):
        previous_root = check_site.ROOT
        try:
            with tempfile.TemporaryDirectory() as directory:
                check_site.ROOT = directory
                Path(directory, "redirects.json").write_text(json.dumps({
                    "/article/": "https://decentralizedthoughts.github.io/article/"
                }))
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(check_site.check_redirects(), 1)
        finally:
            check_site.ROOT = previous_root


if __name__ == "__main__":
    unittest.main()
