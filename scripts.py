import subprocess


def test():
    """
    Run all unittests. Equivalent to:
    `poetry run python -u -m unittest discover`
    """
    subprocess.run(["python", "-u", "-m", "unittest", "discover"])


def parse_test():
    subprocess.run(
        ["python", "-m", "unittest", "tests.test_parser.TestParser.test_create_xer"]
    )


def rem_hours_per_day_test():
    subprocess.run(
        ["python", "-m", "unittest", "tests.test_parser.TestParser.test_rem_hour_calc"]
    )
