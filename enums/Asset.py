"""
enums.asset
~~~~~~~~~~~~~~

This module contains an enum class with different types of asset classes.

"""

from enum import Enum


class Asset(Enum):
    EQUITY = "equity"
    ELSS = "elss"
    DEBT = "debt"
    LIQUID = "liquid"
    ARBITRAGE = "arbitrage"
