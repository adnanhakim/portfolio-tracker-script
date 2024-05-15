"""
models.mf_property
~~~~~~~~~~~~~~

This module contains a MFProperty model class.

"""

from typing import Self


class MFProperty:
    """A class representing a mutual fund property model"""

    _amfi_code: str
    _portfolio: str
    _asset: str
    _country: str

    def __init__(
        self: Self, amfi_code: str, portfolio: str, asset: str, country: str
    ) -> None:
        self._amfi_code = amfi_code
        self._portfolio = portfolio
        self._asset = asset
        self._country = country

    @property
    def amfi_code(self: Self) -> str:
        return self._amfi_code

    @amfi_code.setter
    def amfi_code(self, amfi_code: str) -> None:
        self._amfi_code = amfi_code

    @property
    def portfolio(self: Self) -> str:
        return self._portfolio

    @portfolio.setter
    def portfolio(self, portfolio: str) -> None:
        self._portfolio = portfolio

    @property
    def asset(self: Self) -> str:
        return self._asset

    @asset.setter
    def asset(self, asset: str) -> None:
        self._asset = asset

    @property
    def country(self: Self) -> str:
        return self._country

    @country.setter
    def country(self, country: str) -> None:
        self._country = country

    def to_dict(self: Self) -> dict[str:str]:
        """Serialize the object to dict"""
        return {
            "amfi_code": self._amfi_code,
            "portfolio": self._portfolio,
            "asset": self._asset,
            "country": self._country,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MFProperty":
        """Create a MFProperty object from a dictionary"""
        return cls(
            amfi_code=data["amfi_code"],
            portfolio=data["portfolio"],
            asset=data["asset"],
            country=data["country"],
        )

    def __str__(self):
        attrs: str = ", ".join([f"{key}={value}" for key, value in vars(self).items()])
        return "{" + attrs + "}"
