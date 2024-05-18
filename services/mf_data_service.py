"""
services.mf_data_service
~~~~~~~~~~~~~~

This module contains a service class which reads and stores MF Data sheet.

"""

import os
import sys
from decimal import Decimal
from typing import Self

from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet

from apis.google_sheets_client import GoogleSheetsClient
from apis.mf_api_client import MFApiClient
from models.mf_property import MFProperty
from models.mf_transaction import MFTransaction
from utils import dates, files
from utils import logger as log
from utils.functions import to_num


class MFDataService:
    """This service file reads and stores MF Data sheet locally"""

    _sheet = None
    _worksheet = None
    _mf_txn_data: list[MFTransaction]

    _WORKSHEET_NAME: str | None = os.environ.get("TRANSACTIONS_WORKSHEET_NAME")

    _FIRST_ROW: int | None = int(os.environ.get("TRANSACTIONS_FIRST_ROW"))
    _FUND_NAME_COL: int | None = to_num(os.environ.get("TRANSACTIONS_FUND_NAME_COL"))
    _BUY_SELL_COL: int | None = to_num(os.environ.get("TRANSACTIONS_BUY_SELL_COL"))
    _UNITS_COL: int | None = to_num(os.environ.get("TRANSACTIONS_UNITS_COL"))
    _BUY_DATE_COL: int | None = to_num(os.environ.get("TRANSACTIONS_BUY_DATE_COL"))
    _BUY_PRICE_COL: int | None = to_num(os.environ.get("TRANSACTIONS_BUY_PRICE_COL"))
    _SELL_DATE_COL: int | None = to_num(os.environ.get("TRANSACTIONS_SELL_DATE_COL"))
    _SELL_PRICE_COL: int | None = to_num(os.environ.get("TRANSACTIONS_SELL_PRICE_COL"))

    _FOLDER_NAME = "sheet_data"
    _FILE_NAME = "mf_txn_data"
    _BENCHMARK_FILE_NAME = "benchmark_txn_data"

    _BENCHMARK_FUND: str | None = os.environ.get("BENCHMARK_FUND")
    _BENCHMARK_FUND_AMFI_CODE: str | None = os.environ.get("BENCHMARK_FUND_AMFI_CODE")

    def __init__(self, override_cache=False) -> None:
        if override_cache is True:
            self._mf_txn_data: list[MFTransaction] = self._fetch_data_from_sheets()
        else:
            self._mf_txn_data: list[MFTransaction] = self._fetch_data_from_cache()

    def _fetch_data_from_sheets(self):
        if (
            self._WORKSHEET_NAME is None
            or self._FIRST_ROW is None
            or self._FUND_NAME_COL is None
            or self._BUY_SELL_COL is None
            or self._UNITS_COL is None
            or self._BUY_DATE_COL is None
            or self._BUY_PRICE_COL is None
            or self._SELL_DATE_COL is None
            or self._SELL_PRICE_COL is None
        ):
            log.error(
                "One or more environment variables are not set for MF Transaction Sheet"
            )
            sys.exit(1)

        log.info(f"Fetching {self._WORKSHEET_NAME} from Google Sheets...", True)

        if self._sheet is None:
            self._sheet: Spreadsheet = GoogleSheetsClient().get_sheet()

        if self._worksheet is None:
            self._worksheet: Worksheet = self._sheet.worksheet(self._WORKSHEET_NAME)

        rows: list[list] = self._worksheet.get_all_values()

        txn_list: list[MFTransaction] = []

        # Data begins from the specified row
        for row in rows[self._FIRST_ROW :]:
            txn_list.append(
                MFTransaction(
                    fund=row[self._FUND_NAME_COL],
                    buy_sell=row[self._BUY_SELL_COL],
                    units=row[self._UNITS_COL],
                    buy_date=row[self._BUY_DATE_COL],
                    buy_price=row[self._BUY_PRICE_COL],
                    sell_date=row[self._SELL_DATE_COL],
                    sell_price=row[self._SELL_PRICE_COL],
                )
            )

        log.info(
            f"Fetched {len(txn_list)} transactions from sheet {self._WORKSHEET_NAME}"
        )

        # Sort transactions based on buy date
        sorted_txn_list: list[MFTransaction] = sorted(
            txn_list, key=lambda x: (x.buy_date, x.fund)
        )

        serialized_list: list[dict] = self._serialize(sorted_txn_list)

        # Save file to cache
        files.save_file_as_json(self._FOLDER_NAME, self._FILE_NAME, serialized_list)
        log.debug(f"Saved {len(serialized_list)} transactions to cache")

        return sorted_txn_list

    def _fetch_data_from_cache(self):
        log.info(f"Fetching {self._WORKSHEET_NAME} from cache...", True)

        json_data: list[dict] | None = files.read_file_as_json(
            self._FOLDER_NAME, self._FILE_NAME
        )

        if json_data is None:
            log.warning(f"Did not find {self._WORKSHEET_NAME} in cache")
            return self._fetch_data_from_sheets()

        txn_list: list[MFTransaction] = [
            MFTransaction.from_dict(value) for value in json_data
        ]

        log.info(f"Fetched {len(txn_list)} transactions from cache")

        return txn_list

    def _serialize(self: Self, txn_list: list[MFTransaction]) -> list[dict]:
        return [value.to_dict() for value in txn_list]

    def mf_txn_data(self: Self) -> list[MFTransaction]:
        return self._mf_txn_data

    def benchmark_txn_data(
        self: Self,
        mf_properties: dict[str, MFProperty],
        mf_api_client: MFApiClient,
        amfi_code: int,
    ) -> list[MFTransaction]:
        return self._create_benchmark_data(mf_properties, mf_api_client, amfi_code)

    def _create_benchmark_data(
        self: Self,
        mf_properties: dict[str, MFProperty],
        mf_api_client: MFApiClient,
        amfi_code: int,
    ) -> list[MFTransaction]:
        actual_txn_list: list[MFTransaction] = self.mf_txn_data()

        if actual_txn_list is None:
            actual_txn_list = self._fetch_data_from_cache()

        benchmark_txn_list: list[MFTransaction] = []

        for txn in actual_txn_list:
            mf_property: MFProperty = mf_properties[txn.fund]

            # Skip non-equity funds
            if mf_property.asset == "Debt" or mf_property.asset == "Arbitrage":
                benchmark_txn_list.append(
                    MFTransaction(
                        fund=txn.fund,
                        buy_sell=txn.buy_sell,
                        units=str(txn.units),
                        buy_date=dates.to_datestring(txn.buy_date),
                        buy_price=str(txn.buy_price),
                        sell_date=dates.to_datestring(txn.sell_date),
                        sell_price=str(txn.sell_price),
                    )
                )

                continue

            actual_buy_value: Decimal = txn.units * txn.buy_price

            # Get benchmark price at actual txn buy date
            benchmark_buy_price: Decimal = mf_api_client.get_nav_price(
                amfi_code, txn.buy_date
            )

            # Get estimated benchmark units up to 3 decimal places
            benchmark_units: Decimal = round(actual_buy_value / benchmark_buy_price, 3)

            benchmark_sell_price: Decimal = (
                txn.sell_price
                if txn.buy_sell == "BUY"
                else mf_api_client.get_nav_price(amfi_code, txn.sell_date)
            )

            benchmark_txn_list.append(
                MFTransaction(
                    fund="Benchmark",
                    buy_sell=txn.buy_sell,
                    units=str(benchmark_units),
                    buy_date=dates.to_datestring(txn.buy_date),
                    buy_price=str(benchmark_buy_price),
                    sell_date=dates.to_datestring(txn.sell_date),
                    sell_price=str(benchmark_sell_price),
                )
            )

        return benchmark_txn_list
