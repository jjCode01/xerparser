# xerparser
# parser.py

import re
from pathlib import Path
from typing import BinaryIO

CODEC = "cp1252"


def file_reader(file: str | Path | BinaryIO) -> str:
    """Reads a P6 .xer file and returns it's contents as a string.

    Args:
        file (str | Path | BinaryIO): .xer file

    Returns:
        str: Contents of .xer file
    """
    file_contents = ""

    # Path directory to file
    if isinstance(file, (str, Path)):
        with open(file, encoding=CODEC, errors="ignore") as f:
            file_contents = f.read()
        return file_contents

    # Binary file from requests, Flask, FastAPI, etc...
    file_contents = file.read().decode(CODEC, errors="ignore")

    return file_contents


def parser(xer_contents: str) -> dict[str, list]:
    """
    Parses the contents of a P6 .xer file and converts it into a
    Python dictionary object.

    Args:
        xer_contents (str): .xer file contents

    Returns:
        dict: xer information and data tables
    """
    if not isinstance(xer_contents, str):
        raise TypeError(
            f"TypeError: xer_contents must be <class 'str'>; got {type(xer_contents)}"
        )

    if not xer_contents.startswith("ERMHDR"):
        raise ValueError("ValueError: invalid XER file")

    table_delimiter = "%T\t"
    tables = xer_contents.split(table_delimiter)
    xer_data: dict[str, list] = {}

    # The first row in the xer file includes file export information
    xer_data["ERMHDR"] = tables.pop(0).strip().split("\t")[1:]
    xer_data.update(
        **{name: rows for table in tables for name, rows in _parse_table(table).items()}
    )

    return xer_data


def _parse_table(table: str) -> dict[str, list[dict]]:
    """Parse table name, columns, and rows"""

    lines: list[str] = re.split(r"\r?\n", table)

    name = lines.pop(0).strip()  # First line is the table name
    cols = lines.pop(0).strip().split("\t")[1:]  # Second line is the column labels
    data = [
        dict(zip(cols, row.split("\t")[1:])) for row in lines if row.startswith("%R")
    ]
    return {name: data}
