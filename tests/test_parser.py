import unittest
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from xerparser.xer_parser import xer_to_dict


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        directory = os.path.dirname(os.path.abspath(__file__))
        xer_directory = os.path.join(directory, "xer_files")
        self.files = Path(xer_directory).glob("*.xer")

    def test_has_key(self):
        """Tests if key is included in the xer file"""
        for file in self.files:
            for name in ("version", "export_date", "errors", "tables"):
                xer = xer_to_dict(file)
                with self.subTest(line=file):
                    self.assertIn(name, xer, msg=None)

    def test_export_date(self):
        """Test if export date is datetime object"""
        for file in self.files:
            xer = xer_to_dict(file)
            with self.subTest(line=file):
                self.assertIsInstance(xer["export_date"], datetime)


if __name__ == "__main__":
    unittest.main()
