"""
services.mf_properties_service
~~~~~~~~~~~~~~

This module contains a service class which reads and stores MF Properties sheet.

"""

import os
import sys
from typing import Self

from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet

from apis.google_sheets_client import GoogleSheetsClient
from models.mf_property import MFProperty
from utils import files
from utils import logger as log
from utils.functions import to_num


class MFPropertiesService:
    """This service file reads and stores MF Properties sheet locally"""

    _sheet = None
    _worksheet = None
    _mf_properties: dict[str, MFProperty]

    _WORKSHEET_NAME: str | None = os.environ.get("PROPERTIES_WORKSHEET_NAME")

    _FIRST_ROW: int | None = int(os.environ.get("PROPERTIES_FIRST_ROW"))
    _FUND_NAME_COL: int | None = to_num(os.environ.get("PROPERTIES_FUND_NAME_COL"))
    _AMFI_CODE_COL: int | None = to_num(os.environ.get("PROPERTIES_AMFI_CODE_COL"))
    _PORTFOLIO_COL: int | None = to_num(os.environ.get("PROPERTIES_PORTFOLIO_COL"))
    _ASSET_COL: int | None = to_num(os.environ.get("PROPERTIES_ASSET_COL"))
    _COUNTRY_COL: int | None = to_num(os.environ.get("PROPERTIES_COUNTRY_COL"))

    _FOLDER_NAME = "sheet_data"
    _FILE_NAME = "mf_properties"

    def __init__(self, override_cache=False) -> None:
        if override_cache is True:
            self._mf_properties: dict[str, MFProperty] = self._fetch_data_from_sheets()
        else:
            self._mf_properties: dict[str, MFProperty] = self._fetch_data_from_cache()

    def _fetch_data_from_sheets(self: Self) -> dict[str, MFProperty]:
        if (
            self._WORKSHEET_NAME is None
            or self._FIRST_ROW is None
            or self._FUND_NAME_COL is None
            or self._AMFI_CODE_COL is None
            or self._ASSET_COL is None
        ):
            log.error(
                "\nOne or more environment variables are not set for MF Properties Sheet"
            )
            sys.exit(1)

        log.info(f"Fetching {self._WORKSHEET_NAME} from Google Sheets...", True)

        if self._sheet is None:
            self._sheet: Spreadsheet = GoogleSheetsClient().get_sheet()

        if self._worksheet is None:
            self._worksheet: Worksheet = self._sheet.worksheet(self._WORKSHEET_NAME)

        rows: list[list] = self._worksheet.get_all_values()

        mf_properties: dict[str, MFProperty] = {}

        # Data begins from the 4th row
        for row in rows[4:]:
            if row[self._FUND_NAME_COL]:
                mf_properties[row[self._FUND_NAME_COL]] = MFProperty(
                    amfi_code=row[self._AMFI_CODE_COL],
                    portfolio=row[self._PORTFOLIO_COL],
                    asset=row[self._ASSET_COL],
                    country=row[self._COUNTRY_COL],
                )

        log.info(
            f"Fetched {len(mf_properties)} properties from sheet {self._WORKSHEET_NAME}"
        )

        serialized_dict: dict[str, str] = self._serialize(mf_properties)

        # Save file to cache
        files.save_file_as_json(self._FOLDER_NAME, self._FILE_NAME, serialized_dict)
        log.debug(f"Saved {len(serialized_dict)} properties to cache")

        return mf_properties

    def _fetch_data_from_cache(self: Self) -> dict[str, MFProperty]:
        log.info(f"Fetching {self._WORKSHEET_NAME} from cache...", True)

        json_data: dict[str, str] | None = files.read_file_as_json(
            self._FOLDER_NAME, self._FILE_NAME
        )

        if json_data is None:
            log.warning(f"Did not find {self._WORKSHEET_NAME} in cache")
            return self._fetch_data_from_sheets()

        mf_properties: dict[str, MFProperty] = {
            key: MFProperty.from_dict(value) for key, value in json_data.items()
        }

        log.info(f"Fetched {len(mf_properties)} properties from cache")

        return mf_properties

    def _serialize(self: Self, mf_properties: dict[str, MFProperty]) -> dict[str:dict]:
        return {key: value.to_dict() for key, value in mf_properties.items()}

    def mf_properties(self: Self) -> dict[str, MFProperty]:
        return self._mf_properties
