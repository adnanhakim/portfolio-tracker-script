"""
models.mf_transaction
~~~~~~~~~~~~~~

This module contains a MFTransaction model class.

"""

import datetime
from decimal import Decimal
from typing import Literal, Self

from utils.dates import to_datestring, to_datetime

BuySellType = Literal["BUY", "SELL"]


class MFTransaction:
    """A class representing a mutual fund transaction model"""

    _fund: str
    _buy_sell: BuySellType
    _units: Decimal
    _buy_date: datetime
    _buy_price: Decimal
    _sell_date: datetime
    _sell_price: Decimal

    def __init__(
        self: Self,
        fund: str,
        buy_sell: str,
        units: str,
        buy_date: str,
        buy_price: str,
        sell_date: str,
        sell_price: str,
    ) -> None:
        self._fund = fund
        self._buy_sell = buy_sell
        self._units = Decimal(units)
        self._buy_date = to_datetime(buy_date)
        self._buy_price = Decimal(buy_price)
        self._sell_date = to_datetime(sell_date)
        self._sell_price = Decimal(sell_price)

    @property
    def fund(self: Self) -> str:
        return self._fund

    @fund.setter
    def fund(self, fund: str) -> None:
        self._fund = fund

    @property
    def buy_sell(self: Self) -> BuySellType:
        return self._buy_sell

    @buy_sell.setter
    def buy_sell(self, buy_sell: BuySellType) -> None:
        self._buy_sell = buy_sell

    @property
    def units(self: Self) -> Decimal:
        return self._units

    @units.setter
    def units(self, units: Decimal) -> None:
        self._units = units

    @property
    def buy_date(self: Self) -> datetime:
        return self._buy_date

    @buy_date.setter
    def buy_date(self, buy_date: datetime) -> None:
        self._buy_date = buy_date

    @property
    def buy_price(self: Self) -> Decimal:
        return self._buy_price

    @buy_price.setter
    def buy_price(self, buy_price: Decimal) -> None:
        self._buy_price = buy_price

    @property
    def sell_date(self: Self) -> datetime:
        return self._sell_date

    @sell_date.setter
    def sell_date(self, sell_date: datetime) -> None:
        self._sell_date = sell_date

    @property
    def sell_price(self: Self) -> Decimal:
        return self._sell_price

    @sell_price.setter
    def sell_price(self, sell_price: Decimal) -> None:
        self._sell_price = sell_price

    def to_dict(self: Self) -> dict[str:str]:
        """Serialize the object to dict"""
        return {
            "fund": self._fund,
            "buy_sell": self._buy_sell,
            "units": str(self._units),
            "buy_date": to_datestring(self._buy_date),
            "buy_price": str(self._buy_price),
            "sell_date": to_datestring(self._sell_date),
            "sell_price": str(self._sell_price),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MFTransaction":
        """Create a MFTransaction object from a dictionary"""
        return cls(
            fund=data["fund"],
            buy_sell=data["buy_sell"],
            units=data["units"],
            buy_date=data["buy_date"],
            buy_price=data["buy_price"],
            sell_date=data["sell_date"],
            sell_price=data["sell_price"],
        )

    def __str__(self):
        attrs: str = ", ".join([f"{key}={value}" for key, value in vars(self).items()])
        return "{" + attrs + "}"
