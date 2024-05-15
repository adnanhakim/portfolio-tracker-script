# Portfolio Tracker Google Sheets 

A Python script that analyzes investment portfolio data from a Google Sheet

## Setup Google Sheets API

1. Login or create an account in Google Developer Console.
2. Create a new project and enable the Google Sheets API for your project.
4. Create a service account under IAM & Admin.
5. Create a new JSON key and save the key in the project's directory.
6. Open the Google Sheet you want to shar and click on the Share button.
7. Enter the email address of the service account (found in the JSON file downloaded earlier) and set the access level to `Viewer` or `Can view` to grant read-only access.

## Setup Environment Variables for the project

Create a new `.env` file in the project's directory.
```properties
# Google Sheets Configuration
SHEET_ID=<google-sheets-id>
CREDENTIALS_FILE=<credentials-file-name>.json

# MF Transactions Sheet
TRANSACTIONS_WORKSHEET_NAME="MF Data"
TRANSACTIONS_FIRST_ROW=4
TRANSACTIONS_FUND_NAME_COL=B
TRANSACTIONS_BUY_SELL_COL=C
TRANSACTIONS_UNITS_COL=G
TRANSACTIONS_BUY_DATE_COL=I
TRANSACTIONS_BUY_PRICE_COL=J
TRANSACTIONS_SELL_DATE_COL=M
TRANSACTIONS_SELL_PRICE_COL=N

# MF Properties Sheet
PROPERTIES_WORKSHEET_NAME="MF Properties"
PROPERTIES_FIRST_ROW=4
PROPERTIES_FUND_NAME_COL=B
PROPERTIES_AMFI_CODE_COL=D
PROPERTIES_PORTFOLIO_COL=E
PROPERTIES_ASSET_COL=F
PROPERTIES_COUNTRY_COL=G

# Benchmark Configuration
BENCHMARK_FUND=UTI Nifty 50 Index Fund
BENCHMARK_FUND_AMFI_CODE=120716
```

## Setup Google Sheets

You will need 2 sheets to process the data.  Sheet 1 will contain the transactions and Sheet 2 will contain additional mutual fund properties.

### Sheet 1 (Can be named as per your choice)

The following columns are mandatory (can be in any order).

Update the sheet name and column numbers (0 indexed) in `services/mf_data_service.py`

| Fund Name               | Buy/Sell | Units | Buy Date   | Buy Price | Sell Date  | Sell Price |
|-------------------------|----------|-------|------------|-----------|------------|------------|
| UTI Nifty 50 Index Fund | SELL     | 10    | 01-01-2022 | 100.000   | 20-02-2022 | 105.000    |
| UTI Nifty 50 Index Fund | BUY      | 10    | 01-07-2022 | 100.000   |            |            |

1. Fund Name - Name of the fund (can be any name, but has to be the same name in Sheet 2).
2. Buy/Sell - Indicator to denote if the transaction has been fully sold or yet to be sold.
    Suppose you have 2 units of a fund, but only sell 1 unit, create 2 rows in transaction sheet, one with 1 unit with SELL and the other with 1 unit as BUY.
3. Buy Date / Sell Date - Dates with `dd-MM-yyyy` format.
4. Buy Price / Sell Price - Effective price (post exit load, if any).


### Sheet 2 (Can be named as per your choice)

The following columns are recommended (can be in any order).

Update the sheet name and column numbers (0 indexed) in `services/mf_properties_service.py`

| Fund Name               | AMFI Code | Asset  | Portfolio | Country |
|-------------------------|-----------|--------|-----------|---------|
| UTI Nifty 50 Index Fund | 120716    | Equity | Core      | India   |

1. Fund Name [Mandatory] - Name of the fund (can be any name, but has to be the same name in Sheet 1).
2. AMFI Code [Mandatory] - Can be found [here](https://www.mfapi.in/) 
3. Asset [Mandatory] - Types can be `Equity`, `ELSS`, `Debt` or `Arbitrage`.
4. Portfolio [Optional] - Which portfolio does the fund belong to (New features to be added soon).
5. Country [Optional] - New features to be added soon.

## Installation

Before you begin, ensure you have the following installed:

[Python3](https://www.python.org/downloads/)

Install Poetry
```bash
pip install poetry
```

Install dependencies
```bash
poetry install
```

Run the project
```bash
python3 main.py --help
```

## License

MIT License

Copyright (c) 2024 Adnan Hakim

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

