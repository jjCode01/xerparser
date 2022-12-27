import unittest
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from xerparser import Xer


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        directory = os.path.dirname(os.path.abspath(__file__))
        xer_directory = os.path.join(directory, "xer_files")
        self.files = Path(xer_directory).glob("*.xer")

    def test_budgeted_cost(self):
        """Tests if key is included in the xer file"""

        for file in self.files:
            with open(file, encoding=Xer.CODEC, errors="ignore") as f:
                file_contents = f.read()
            xer = Xer(file_contents)
            for project in xer.projects.values():
                with self.subTest(line=project):
                    self.assertEqual(
                        project.budgeted_cost,
                        cost_values[project.short_name]["budget"],
                        f"{project.short_name} Budgeted Cost",
                    )


if __name__ == "__main__":
    unittest.main()
