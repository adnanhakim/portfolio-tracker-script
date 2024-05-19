"""
api.mf_api_client
~~~~~~~~~~~~~~

This module contains MFApiClient class.

"""

import datetime
from decimal import Decimal
from typing import Self

from requests import HTTPError, Response, get

from models.mf_price import MFPrice
from utils import files


class MFApiClient:
    """This Api Client class is used to fetch historical pricing data for a Mutual Fund"""

    _BASE_URL = "https://api.mfapi.in/mf/"

    _FOLDER_NAME = "mf_api_response"

    def __init__(self: Self, override_cache=False) -> None:
        if override_cache:
            files.delete_files_in_folder(self._FOLDER_NAME)

    def fetch_nav_prices(self: Self, amfi_code: int):
        return self._fetch_nav_prices_from_cache(amfi_code)

    def _fetch_nav_prices_from_api(self: Self, amfi_code: int) -> list[MFPrice] | None:
        url: str = self._BASE_URL + str(amfi_code)

        response: Response = get(url, timeout=10)

        # Check if the request was successful
        if response.status_code == 200:
            pricing_data_json = response.json()["data"]

            files.save_file_as_json(
                self._FOLDER_NAME, str(amfi_code), pricing_data_json
            )

            pricing_data: list[MFPrice] = [
                MFPrice.from_dict(d) for d in pricing_data_json
            ]

            return pricing_data
        else:
            return None

    def _fetch_nav_prices_from_cache(
        self: Self, amfi_code: int
    ) -> list[MFPrice] | None:
        json_data: list[dict] | None = files.read_file_as_json(
            self._FOLDER_NAME, str(amfi_code)
        )

        if json_data is None:
            return self._fetch_nav_prices_from_api(amfi_code)

        pricing_data: list[MFPrice] = [MFPrice.from_dict(d) for d in json_data]

        return pricing_data

    def get_nav_price(self: Self, amfi_code: int, date: datetime) -> Decimal:
        pricing_data: list[MFPrice] = self.fetch_nav_prices(amfi_code)

        for data in pricing_data:
            if data.date > date:
                continue

            return Decimal(data.nav)

    def get_fund_name(self: Self, amfi_code: int) -> str:
        url: str = self._BASE_URL + str(amfi_code)

        response: Response = get(url, timeout=10)

        # Check if the request was successful
        if response.status_code == 200:
            scheme_name: str = response.json()["meta"]["scheme_name"]
            return scheme_name.split("-")[0].strip()
        else:
            raise HTTPError(f"No mutual fund exists with AMFI code: {amfi_code}")
