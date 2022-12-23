import unittest
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from xerparser import Xer

cost_values = {
    "BFBPS04": {
        "budget": 42_529_386.00,
        "actual": 0,
        "this_period": 0,
        "remaining": 0,
    },
    "BFBPS05": {
        "budget": 42_529_386.00,
        "actual": 0,
        "this_period": 0,
        "remaining": 0,
    },
    "BFBPS06": {
        "budget": 42_529_386.00,
        "actual": 0,
        "this_period": 0,
        "remaining": 0,
    },
    "BFBPS07": {
        "budget": 42_529_386.00,
        "actual": 0,
        "this_period": 0,
        "remaining": 0,
    },
    "BFBPS08": {
        "budget": 42_529_386.00,
        "actual": 0,
        "this_period": 0,
        "remaining": 0,
    },
    "BFBPS09": {
        "budget": 42_772_886.00,
        "actual": 0,
        "this_period": 0,
        "remaining": 0,
    },
    "BFBPS10": {
        "budget": 42_772_886.00,
        "actual": 0,
        "this_period": 0,
        "remaining": 0,
    },
    "BFBPS11": {
        "budget": 43_013_804.00,
        "actual": 0,
        "this_period": 0,
        "remaining": 0,
    },
    "BFBPS12": {
        "budget": 43_013_804.00,
        "actual": 0,
        "this_period": 0,
        "remaining": 0,
    },
    "BFBPS13": {
        "budget": 43_270_130.00,
        "actual": 0,
        "this_period": 0,
        "remaining": 0,
    },
    "BFBPS14": {
        "budget": 43_296_475.81,
        "actual": 0,
        "this_period": 0,
        "remaining": 0,
    },
    "BFBPS15": {
        "budget": 43_296_475.81,
        "actual": 0,
        "this_period": 0,
        "remaining": 0,
    },
}


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
