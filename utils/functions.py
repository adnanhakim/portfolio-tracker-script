"""
utils.functions
~~~~~~~~~~~~~~

This module contains commonly used helper functions.

"""


def to_num(column_letter: str) -> int | None:
    """Converts Google Sheets Column Name (A, B, C...) to numbers"""
    if column_letter is None:
        return None

    col_num = 0
    for char in column_letter.upper():
        col_num: int = col_num * 26 + (ord(char.upper()) - ord("A"))
    return col_num
