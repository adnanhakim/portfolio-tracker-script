from datetime import datetime
from decimal import Decimal
from typing import Self

from numpy import absolute

from utils.dates import to_month_year


class AssetValue:

    class Meta:
        def __init__(
            self: Self,
            price: Decimal,
            qty: Decimal,
            asset: str,
            portfolio: str,
            country: str,
        ) -> None:
            self._price: Decimal = price
            self._qty: Decimal = qty
            self._asset: str = asset
            self._portfolio: str = portfolio
            self._country: str = country

        @property
        def price(self: Self) -> Decimal:
            return self._price

        @property
        def qty(self: Self) -> Decimal:
            return self._qty

        def add_qty(self: Self, additional_qty: Decimal):
            if additional_qty < 0:
                raise ValueError("Quantity to add cannot be negative")
            self._qty += additional_qty

        @property
        def asset(self: Self) -> str:
            return self._asset

        @property
        def portfolio(self: Self) -> str:
            return self._portfolio

        @property
        def country(self: Self) -> str:
            return self._country

        def __repr__(self: Self) -> str:
            return f"Meta(price={self._price}, qty={self._qty}, asset='{self._asset}', portfolio='{self._portfolio}', country='{self._country}')"

    class Data:
        def __init__(
            self: Self,
            month: datetime,
            invested_value: Decimal,
            current_value: Decimal,
            xirr: str,
            realized: Decimal,
            equity_value: Decimal,
            debt_value: Decimal,
            cash_value: Decimal,
        ) -> None:
            self._month: datetime = month
            self._invested_value: Decimal = round(invested_value)
            self._current_value: Decimal = round(current_value)
            self._absolute: Decimal = self._calculate_absolute_returns()
            self._xirr: Decimal = round(Decimal(xirr), 4)
            self._realized: Decimal = round(realized)
            self._equity_pct: Decimal = self._calculate_pct(equity_value)
            self._debt_pct: Decimal = self._calculate_pct(debt_value)
            self._cash_pct: Decimal = self._calculate_pct(cash_value)

        @property
        def month(self: Self) -> datetime:
            return self._month

        @property
        def invested_value(self: Self) -> Decimal:
            return self._invested_value

        @property
        def current_value(self: Self) -> Decimal:
            return self._current_value

        def _calculate_absolute_returns(self: Self) -> Decimal:
            if self._invested_value == 0:
                return Decimal(0)
            else:
                return round(
                    (self._current_value - self._invested_value) / self._invested_value,
                    4,
                )

        @property
        def absolute(self: Self) -> Decimal:
            return self._absolute

        @property
        def xirr(self: Self) -> Decimal:
            return self._xirr

        @property
        def realized(self: Self) -> Decimal:
            return self._realized

        def _calculate_pct(
            self: Self,
            value: Decimal,
        ) -> Decimal:
            if self._current_value == 0:
                return 0
            else:
                return round(value / self._current_value, 4)

        @property
        def equity_pct(self: Self) -> Decimal:
            return self._equity_pct

        @property
        def debt_pct(self: Self) -> Decimal:
            return self._debt_pct

        @property
        def cash_pct(self: Self) -> Decimal:
            return self._cash_pct

        def __str__(self: Self) -> str:
            return "\t".join(
                [
                    to_month_year(self.month),
                    str(self.invested_value),
                    str(self.current_value),
                    str(self.realized),
                    str(round(self.absolute * 100, 2)) + "%",
                    str(round(self.xirr * 100, 2)) + "%",
                    str(round(self.equity_pct * 100, 2)) + "%",
                    str(round(self.debt_pct * 100, 2)) + "%",
                    str(round(self.cash_pct * 100, 2)) + "%",
                ]
            )

        def __repr__(self: Self) -> str:
            return (
                f"Data(month='{self._month}', invested_value={self._invested_value}, current_value={self._current_value}, "
                f"absolute={self._absolute}, xirr={self._xirr}, realized={self._realized}, equity_pct={self._equity_pct}, "
                f"debt_pct={self._debt_pct}, cash_pct={self._cash_pct})"
            )

    def __init__(
        self: Self, meta_dict: dict[str, "AssetValue.Meta"], data: "AssetValue.Data"
    ) -> None:
        self._meta_dict: dict[str, AssetValue.Meta] = meta_dict
        self._data: AssetValue.Data = data

    @property
    def meta_dict(self: Self) -> dict[str, "AssetValue.Meta"]:
        return self._meta_dict

    @property
    def data(self: Self) -> "AssetValue.Data":
        return self._data

    def __repr__(self: Self) -> str:
        return f"AssetValue(meta_dict={self._meta_dict}, data={self._data})"
