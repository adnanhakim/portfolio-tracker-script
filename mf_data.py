import json
import os
from datetime import datetime

from apis.google_sheets_client import GoogleSheetsClient


class MutualFundData:
    _instance = None
    _WORKSHEET_NAME = "MF Data"
    _FUND_NAME_COL = 1
    _BUY_SELL_COL = 2
    _FOLDER_NAME = "sheet_data"
    _FILE_NAME = "mf_data.json"

    def __new__(cls, override_cache, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            if override_cache or cls._file_exists() == False:
                cls._instance._sheet = GoogleSheetsClient().get_sheet()
                cls._instance._worksheet = cls._instance._sheet.worksheet(
                    cls._WORKSHEET_NAME
                )
                cls._instance._mf_data = cls._instance._process_data()
            else:
                cls._instance._mf_data = cls._fetch_data()

        return cls._instance

    @classmethod
    def _file_exists(cls):
        file_path = os.path.join(cls._FOLDER_NAME, cls._FILE_NAME)
        return os.path.exists(file_path)

    @classmethod
    def _fetch_data(cls):
        # Read JSON data from the file
        file_path = os.path.join(cls._FOLDER_NAME, cls._FILE_NAME)
        with open(file_path, "r") as f:
            json_data = json.load(f)

        # Function to convert datetime object to string with format 'dd-MM-yyyy'
        def format_date(d):
            return datetime.strptime(d, "%d-%m-%Y")

        # Map over the list and convert the 'dob' key's value to a string
        formatted_data = [{**d, "date": format_date(d["date"])} for d in json_data]

        # print(formatted_data)

        return formatted_data

    def _process_data(self):
        # Get all values from the worksheet
        rows = self._worksheet.get_all_values()

        # Clean and process the data (example: remove empty rows/columns, convert to map)
        mf_data = []  # Placeholder for cleaned map

        for row in rows[4:]:

            mf_data.append(
                {
                    "fund": row[1],
                    "buy_sell": "BUY",
                    "date": datetime.strptime(row[8], "%d-%m-%Y"),
                    "price": float(row[9].replace(",", "")),
                }
            )

            if row[2] == "SELL":
                mf_data.append(
                    {
                        "fund": row[1],
                        "buy_sell": row[2],
                        "date": datetime.strptime(row[12], "%d-%m-%Y"),
                        "price": float(row[13].replace(",", "")),
                    }
                )

            # mf_data.append({
            #   'fund': row[1],
            #   'buy_sell': row[2],
            #   'units': float(row[6]),
            #   'buy_date': datetime.strptime(row[8], '%d-%m-%Y'),
            #   'buy_price': float(row[9].replace(',','')),
            #   # 'buy_value': row[10],
            #   'sell_date': datetime.strptime(row[12], '%d-%m-%Y'),
            #   'sell_price': float(row[13].replace(',','')),
            #   # 'sell_value': float(row[14].replace(',','')),
            # })

        # Your data processing logic here

        sorted_list = sorted(mf_data, key=lambda x: (x["date"], x["fund"]))

        print(len(sorted_list))

        # Function to convert datetime object to string with format 'dd-MM-yyyy'
        def format_date(d):
            return d.strftime("%d-%m-%Y")

        # Map over the list and convert the 'dob' key's value to a string
        formatted_data = [{**d, "date": format_date(d["date"])} for d in sorted_list]

        folder_path = "sheet_data"
        file_name = "mf_data.json"

        file_path = os.path.join(folder_path, file_name)

        # Write the data to the file
        with open(file_path, "w") as f:
            json.dump(
                formatted_data, f, indent=4
            )  # 'indent' parameter for pretty formatting (optional)

        print(f"Data saved to {file_path}")

        return sorted_list

    def get_mf_data(self):
        return self._mf_data
