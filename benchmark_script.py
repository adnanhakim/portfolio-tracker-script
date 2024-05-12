import pprint
from datetime import datetime, timedelta
from decimal import Decimal

from readers.mf_data_reader_2 import MutualFundDataReader

from apis.mf_api_client import MutualFundApiClient
from utils import files


def get_price(json_data: list, date: datetime):
  for data in json_data:
    if data['date'] > date:
      continue
    
    return Decimal(data['nav'])

BENCHMARK_NAME = 'UTI Nifty 50 Index Fund'
BENCHMARK_AMFI_CODE = 120716
apiClient = MutualFundApiClient()

txn_data = MutualFundDataReader(False).get_mf_data()
benchmark_prices = apiClient.get_data(BENCHMARK_AMFI_CODE)

for txn in txn_data:
  if txn['asset'] == 'Debt' or txn['asset'] == 'Arbitrage':
    continue

  actual_buy_value = txn['units'] * txn['buy_price']
  benchmark_buy_price = get_price(benchmark_prices, txn['buy_date'])
  benchmark_units = round(actual_buy_value / benchmark_buy_price, 3)
  
  txn['fund'] = BENCHMARK_NAME
  txn['units'] = benchmark_units
  txn['buy_price'] = benchmark_buy_price

  if txn['buy_sell'] == 'SELL':
    benchmark_sell_price = get_price(benchmark_prices, txn['sell_date'])
    txn['sell_price'] = benchmark_sell_price

 # Function to convert datetime object to string with format 'dd-MM-yyyy'
def format_datetime_to_string(d):
    return d.strftime('%d-%m-%Y')

clean_txn_list = [
      {**d, 
       'buy_date': format_datetime_to_string(d['buy_date']),
       'sell_date': format_datetime_to_string(d['sell_date']),
       'units': str(d['units']),
       'buy_price': str(d['buy_price']),
       'sell_price': str(d['sell_price'])
       } for d in txn_data]

pprint.pprint(f'Saved {len(clean_txn_list)} transactions')

files.save_file_as_json('sheet_data', 'benchmark_data', clean_txn_list)
  
