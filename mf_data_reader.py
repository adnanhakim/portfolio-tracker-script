from datetime import datetime
from decimal import Decimal

from apis.google_sheets_client import GoogleSheetsClient
from utils import files


class MutualFundDataReader:
  _WORKSHEET_NAME   = 'MF Data'
  _FUND_NAME_COL = 1
  _BUY_SELL_COL = 2
  _FOLDER_NAME = 'sheet_data'
  _FILE_NAME = 'mf_data'

  def __init__(self, override_cache = False) -> None:
    if override_cache == True or files.check_if_json_file_exists(self._FOLDER_NAME, self._FILE_NAME) == False:
       print('Fetching data from Google Sheets...')
       self._sheet = GoogleSheetsClient().get_sheet()
       self._worksheet = self._sheet.worksheet(self._WORKSHEET_NAME)
       self._mf_data = self._fetch_data_from_sheets()
    else:
       print('Fetching data from cache...')
       self._mf_data = self._fetch_data_from_cache()

  def _fetch_data_from_cache(self):
    # Read JSON data from the file
    json_data = files.read_file_as_json(self._FOLDER_NAME, self._FILE_NAME)

    # Function to convert date string to datetime object
    def format_datestring_to_date(d):
        return datetime.strptime(d, '%d-%m-%Y')

    if json_data is not None:
      # Map over the list and convert the 'date' key's value to a datetime object
      formatted_data = [{**d, 
                         'date': format_datestring_to_date(d['date']),
                         'units': Decimal(d['units']),
                         'price': Decimal(d['price'])
                         } for d in json_data]

      return formatted_data
    else: 
      return None

  def _fetch_data_from_sheets(self):
    # Get all values from the worksheet
    rows = self._worksheet.get_all_values()

    # Clean and process the data
    txn_list = []

    for row in rows[4:]:
      # Add default buy transaction
      txn_list.append({
        'fund': row[1],
        'buy_sell': 'BUY',
        'units': Decimal(row[6]),
        'date': datetime.strptime(row[8], '%d-%m-%Y'),
        'price': Decimal(row[9].replace(',',''))
      })

      # Add sell transaction if any
      if row[2] == 'SELL':
        txn_list.append({
          'fund': row[1],
          'buy_sell': row[2],
          'units': Decimal(row[6]),
          'date': datetime.strptime(row[12], '%d-%m-%Y'),
          'price': Decimal(row[13].replace(',',''))
        })
    
    # Sort transactions based on date
    sorted_txn_list = sorted(txn_list, key=lambda x: (x['date'], x['fund']))

    print(len(sorted_txn_list))

    self._clean_and_save_in_cache(sorted_txn_list)

    return sorted_txn_list

  def _clean_and_save_in_cache(self, sorted_txn_list: list):
     # Function to convert datetime object to string with format 'dd-MM-yyyy'
    def format_datetime_to_string(d):
        return d.strftime('%d-%m-%Y')

    # Map over the list and convert the 'dob' key's value to a string
    clean_txn_list = [
      {**d, 
       'date': format_datetime_to_string(d['date']),
       'units': str(d['units']),
       'price': str(d['price'])
       } for d in sorted_txn_list]

    # Save file to cache
    files.save_file_as_json(self._FOLDER_NAME, self._FILE_NAME, clean_txn_list)

  def get_mf_data(self):
    return self._mf_data
