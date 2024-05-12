import pprint
from datetime import datetime, timedelta
from decimal import Decimal

from readers.mf_properties import MutualFundProperties

from apis.mf_api_client import MutualFundApiClient
from mf_data_reader import MutualFundDataReader


def get_price(json_data: list, date: datetime):
  for data in json_data:
    if data['date'] > date:
      continue
    
    return Decimal(data['nav'])

command = 'asset-value'
# date = 'apr-2023'

txn_data = MutualFundDataReader(False).get_mf_data()

apiClient = MutualFundApiClient()

mf_properties = MutualFundProperties().get_mf_properties()

def get_value(to_date: datetime):
  filtered_data = []

  # to_date = datetime.strptime(date, '%b-%Y').replace(day=1)

  price_map = {}
  unit_map = {}
  values_list = []
  dates_list = []

  for txn in txn_data:  
    if (to_date < txn['date']):
      break

    if txn['buy_sell'] == 'SELL':
      price = txn['price']
      value = txn['units'] * price
      # total_current_value -= value
      values_list.append(value)
      dates_list.append(txn['date'])
      if txn['fund'] in unit_map:
        unit_map[txn['fund']] -= txn['units']
      else:
        unit_map[txn['fund']] = txn['units']
      # print(f'Subtracting => {txn['units']}')
    else:
      if txn['fund'] in price_map:
        price = price_map[txn['fund']]
      else:
        amfi_code = mf_properties[txn['fund']]['amfi_code']
        data = apiClient.get_data(amfi_code)
        price = get_price(data, to_date)
        price_map[txn['fund']] = price
      value = txn['units'] * price
      values_list.append(value * -1)
      dates_list.append(txn['date'])
      # total_current_value += value
      if txn['fund'] in unit_map:
        unit_map[txn['fund']] += txn['units']
      else:
        unit_map[txn['fund']] = txn['units']
      # print(f'Adding => {txn['units']}')


    txn['value'] = value
    filtered_data.append(txn)

    total_current_value = Decimal(0)
    for key in unit_map.keys():
      total_current_value += unit_map[key] * price_map[key]


  # pprint.pprint(filtered_data)
  # print(len(filtered_data))
  # pprint.pprint(price_map)
  # print(unit_map)
  # print(total_value)
  print(f'{to_date.strftime('%b-%Y')}\t{round(total_current_value)}')

to_date = datetime.strptime('oct-2021', '%b-%Y').replace(day=1)

for i in range (0, 31):
  get_value(to_date)
  to_date = to_date + timedelta(days=31)
  to_date = to_date.replace(day=1)
#   print(f'Value as of {to_date.strftime('%b-%Y')} is {get_value(to_date)}')


