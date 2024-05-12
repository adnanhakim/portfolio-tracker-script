"""
api.google_sheets_client
~~~~~~~~~~~~~~

This module contains GoogleSheetsClient class.

"""

import os
import sys
from typing import Self

from dotenv import load_dotenv
from gspread import authorize
from gspread.client import Client
from gspread.spreadsheet import Spreadsheet
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()


class GoogleSheetsClient:
    """Singleton class that returns an instance of the Google Sheet"""

    _instance = None
    _SHEET_ID: str | None = os.environ.get("SHEET_ID")
    _CREDENTIALS_FILE: str | None = os.environ.get("CREDENTIALS_FILE")

    def __new__(cls):
        if cls._SHEET_ID is None or cls._CREDENTIALS_FILE is None:
            print("One or more environment variables are not set.")
            sys.exit(1)

        if cls._instance is None:
            cls._instance: Self = super().__new__(cls)
            cls._instance._client = cls._instance._create_client()
        return cls._instance

    @classmethod
    def _create_client(cls: Self) -> Client:
        """Creates and returns a Client object"""

        scope: list[str] = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        creds: ServiceAccountCredentials = (
            ServiceAccountCredentials.from_json_keyfile_name(
                cls._CREDENTIALS_FILE, scope
            )
        )

        return authorize(creds)

    def get_sheet(self: Self) -> Spreadsheet:
        """Returns the Spreadsheet object from Google Sheets"""
        return self._client.open_by_key(self._SHEET_ID)
