"""
utils.logger
~~~~~~~~~~~~~~

This module contains commonly used logging functions.

"""

from colorama import Fore, Style


def debug(message: str, new_line=False) -> None:
    if new_line:
        print()
    print(f"{Style.DIM}{Fore.CYAN}[DEBUG] {message}{Style.RESET_ALL}")


def info(message: str, new_line=False) -> None:
    if new_line:
        print()
    print(f"{Fore.GREEN}[INFO] {message}{Style.RESET_ALL}")


def warning(message: str, new_line=False) -> None:
    if new_line:
        print()
    print(f"{Fore.YELLOW}[WARN] {message}{Style.RESET_ALL}")


def error(message: str, new_line=False) -> None:
    if new_line:
        print()
    print(f"{Fore.RED}[ERROR] {message}{Style.RESET_ALL}")
