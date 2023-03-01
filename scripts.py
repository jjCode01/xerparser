import subprocess


def test():
    """
    Run all unittests. Equivalent to:
    `poetry run python -u -m unittest discover`
    """
    subprocess.run(["python", "-u", "-m", "unittest", "discover"])


def parse_test():
    """
    Run xer parser unittests. Equivalent to:
    `poetry run python -u -m unittest discover`
    """
    subprocess.run(
        ["python", "-m", "unittest", "tests.test_parser.TestParser.test_create_xer"]
    )
