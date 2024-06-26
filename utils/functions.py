"""
utils.functions
~~~~~~~~~~~~~~

This module contains commonly used helper functions.

"""

from decimal import Decimal

from babel.numbers import format_currency
from colorama import Fore, Style
from tabulate import tabulate


def to_num(column_letter: str) -> int | None:
    """Converts Google Sheets Column Name (A, B, C...) to numbers"""
    if column_letter is None:
        return None

    col_num = 0
    for char in column_letter.upper():
        col_num: int = col_num * 26 + (ord(char.upper()) - ord("A"))
    return col_num


def format_inr(amount: Decimal) -> str:
    """Converts decimal number to INR notation"""
    return format_currency(amount, "INR", locale="en_IN")


def print_header(header: str) -> None:
    """Print coloured bold header"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{header}{Style.RESET_ALL}")


def print_table(tuple_list: list[tuple]) -> None:
    """Print tuple list as table"""
    print(tabulate(tuple_list, tablefmt="plain"))
