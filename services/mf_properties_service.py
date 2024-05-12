"""
services.mf_properties_service
~~~~~~~~~~~~~~

This module contains a service class which reads and stores MF Properties sheet.

"""

from typing import Self

from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet

from apis.google_sheets_client import GoogleSheetsClient
from models.mf_property import MFProperty
from utils import files


class MFPropertiesService:
    """This service file reads and stores MF Properties sheet locally"""

    _sheet = None
    _worksheet = None
    _mf_properties: dict[str, MFProperty]

    _WORKSHEET_NAME = "MF Properties"

    _FUND_NAME_COL = 1
    _AMFI_CODE_COL = 3
    _PORTFOLIO_COL = 4
    _ASSET_COL = 5
    _COUNTRY_COL = 6

    _FOLDER_NAME = "sheet_data"
    _FILE_NAME = "mf_properties"

    def __init__(self, override_cache=False) -> None:
        if override_cache is True:
            self._mf_properties: dict[str, MFProperty] = self._fetch_data_from_sheets()
        else:
            self._mf_properties: dict[str, MFProperty] = self._fetch_data_from_cache()

    def _fetch_data_from_sheets(self: Self) -> dict[str, MFProperty]:
        print(f"Fetching {self._WORKSHEET_NAME} from Google Sheets...")

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

        serialized_dict: dict[str, str] = self._serialize(mf_properties)

        # Save file to cache
        files.save_file_as_json(self._FOLDER_NAME, self._FILE_NAME, serialized_dict)

        return mf_properties

    def _fetch_data_from_cache(self: Self) -> dict[str, MFProperty]:
        print(f"Fetching {self._WORKSHEET_NAME} from cache...")

        json_data: dict[str, str] | None = files.read_file_as_json(
            self._FOLDER_NAME, self._FILE_NAME
        )

        if json_data is None:
            print(f"Did not find {self._WORKSHEET_NAME} in cache")
            return self._fetch_data_from_sheets()

        mf_properties: dict[str, MFProperty] = {
            key: MFProperty.from_dict(value) for key, value in json_data.items()
        }

        return mf_properties

    def _serialize(self: Self, mf_properties: dict[str, MFProperty]) -> dict[str:dict]:
        return {key: value.to_dict() for key, value in mf_properties.items()}

    def get_mf_properties(self: Self) -> dict[str, MFProperty]:
        return self._mf_properties
