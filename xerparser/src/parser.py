# xerparser
# xer.py


def xer_to_dict(xer_contents: str) -> dict[str, list]:
    """Reads contents of a P6 .xer file and converts it into a Python dictionary object.
    Args:
        file (str): .xer file contents
    Returns:
        dict: Dictionary of the xer information and data tables
    """
    if not isinstance(xer_contents, str):
        raise TypeError(
            f"TypeError: xer_contents argument must be <class 'str'>; got {type(xer_contents)}"
        )

    if not xer_contents.startswith("ERMHDR"):
        raise ValueError("ValueError: invalid XER file")

    table_delimiter = "%T\t"
    tables = xer_contents.split(table_delimiter)

    # The first row in the xer file includes file export information
    xer_data = {"ERMHDR": tables.pop(0).strip().split("\t")[1:]}
    xer_data.update(
        **{name: rows for table in tables for name, rows in _parse_table(table).items()}
    )

    return xer_data


def _parse_table(table: str) -> dict[str, list[dict]]:
    """Parse table name, columns, and rows"""

    lines: list[str] = table.split("\n")
    name = lines.pop(0).strip()  # First line is the table name
    cols = lines.pop(0).strip().split("\t")[1:]  # Second line is the column labels
    data = [dict(zip(cols, _clean_row(row))) for row in lines if row.startswith("%R")]
    return {name: data}


def _clean_row(row: str) -> list[str]:
    """Strips white space from last value in row"""
    row_values = row.split("\t")[1:]
    if row_values:
        row_values[-1] = _clean_value(row_values[-1])
    return row_values


def _clean_value(val: str) -> str:
    if val == "":
        return ""
    return val.strip()
