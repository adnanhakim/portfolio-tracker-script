"""
utils.dates
~~~~~~~~~~~~~~

This module contains common date methods.

"""

from datetime import datetime, timedelta


def to_datetime(datestring: str) -> datetime:
    """Converts a date string with format dd-MM-yyyy to a datetime object"""
    return datetime.strptime(datestring, "%d-%m-%Y")


def to_datestring(date: datetime) -> str:
    """Converts a datetime object to a date string with format dd-MM-yyyy"""
    return date.strftime("%d-%m-%Y")


def from_month_year(datestring: str) -> datetime:
    """Converts a date string with format MMM-yyyy to a datetime object with 1st day of the month"""
    return datetime.strptime(datestring, "%b-%Y").replace(day=1)


def to_month_year(date: datetime) -> str:
    """Converts a datetime object to a date string with format MMM-yyyy"""
    return date.strftime("%b-%Y")


def add_month(date: datetime) -> datetime:
    """Adds a month to the datetime object"""
    date = date + timedelta(days=31)
    return date.replace(day=1)


def get_last_month_date() -> datetime:
    """Gets last month's date as string with format MMM-yyyy"""
    current_date: datetime = datetime.now()
    last_month: datetime = current_date - timedelta(days=current_date.day)
    return last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
