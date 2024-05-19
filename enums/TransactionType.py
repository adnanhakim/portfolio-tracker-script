"""
enums.transactiontype
~~~~~~~~~~~~~~

This module contains an enum class with different types of transaction types.

"""

from enum import Enum


class TransactionType(Enum):
    BUY = "BUY"
    SELL = "SELL"
