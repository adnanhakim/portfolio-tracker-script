"""
models.mf_price
~~~~~~~~~~~~~~

This module contains a MFPrice model class.

"""

import datetime
from typing import Self

from utils.dates import to_datestring, to_datetime


class MFPrice:
    """A class representing a mutual fund price model"""

    _date: datetime
    _nav: str

    def __init__(
        self: Self,
        date: str,
        nav: str,
    ) -> None:
        self._date = to_datetime(date)
        self._nav = nav

    @property
    def date(self: Self) -> datetime:
        return self._date

    @date.setter
    def buy_date(self, date: datetime) -> None:
        self._date = date

    @property
    def nav(self: Self) -> str:
        return self._nav

    @nav.setter
    def nav(self, nav: str) -> None:
        self._nav = nav

    def to_dict(self: Self) -> dict[str:str]:
        """Serialize the object to dict"""
        return {
            "date": to_datestring(self._date),
            "nav": self._nav,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MFPrice":
        """Create a MFPrice object from a dictionary"""
        return cls(
            date=data["date"],
            nav=data["nav"],
        )
