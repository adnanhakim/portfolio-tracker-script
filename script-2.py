import pprint
from datetime import datetime, timedelta
from decimal import Decimal

from xirr import math

from apis.mf_api_client import MFApiClient
from models.mf_property import MFProperty
from services.mf_data_service import MFDataService
from services.mf_properties_service import MFPropertiesService


def get_price(json_data: list, date: datetime):
  for data in json_data:
    if data['date'] > date:
      continue
    
    return Decimal(data['nav'])

command = 'asset-value'
# date = 'apr-2023'

txn_data = MFDataService(False).mf_txn_data()

apiClient = MFApiClient()

mf_properties: dict[str, MFProperty] = MFPropertiesService().get_mf_properties()

def get_value(to_date: datetime, txn_data: list):
  filtered_data = []

  # to_date = datetime.strptime(date, '%b-%Y').replace(day=1)

  price_map = {}
  unit_map = {}
  values_list = []
  dates_list = []
  realized_profits = Decimal(0)

  total_buy_value, total_current_value = Decimal(0), Decimal(0)

  for txn in txn_data:  
    # if txn['asset'] == 'Debt' or txn['asset'] == 'Arbitrage':
    #   continue

    if (txn.buy_sell == 'BUY' and to_date > txn.buy_date) or (txn.buy_sell == 'SELL' and txn.buy_date < to_date and txn.sell_date > to_date):
      if txn.fund in price_map:
        sell_price = price_map[txn.fund]
      else:
        amfi_code = mf_properties[txn.fund].amfi_code
        sell_price = apiClient.get_nav_price(amfi_code, to_date)
        # sell_price = get_price(data, to_date)
        price_map[txn.fund] = sell_price
      buy_value = txn.units * txn.buy_price
      total_buy_value += buy_value
      sell_value = txn.units * sell_price
    #   txn.buy_value = buy_value
    #   txn.sell_value = sell_value
      if txn.fund in unit_map:
          unit_map[txn.fund] += txn.units
      else:
          unit_map[txn.fund] = txn.units
    #   filtered_data.append(txn)

      values_list.append(float(buy_value) * -1)
      dates_list.append(txn.buy_date)
      values_list.append(float(sell_value))
      dates_list.append(to_date)

    if txn.buy_sell == 'SELL' and txn.buy_date < to_date and txn.sell_date < to_date:
      buy_value = txn.units * txn.buy_price
      sell_value = txn.units * txn.sell_price
      realized_profits += sell_value - buy_value
      values_list.append(float(buy_value) * -1)
      dates_list.append(txn.buy_date)
      values_list.append(float(sell_value))
      dates_list.append(txn.sell_date)
    
  for key in unit_map.keys():
    total_current_value += unit_map[key] * price_map[key]

  # pprint.pprint(filtered_data)
  # print(len(filtered_data))
  # pprint.pprint(price_map)
  # print(unit_map)
  # print(total_value)

  xirr = math.listsXirr(dates_list, values_list)
  absolute = ((total_current_value - total_buy_value) / total_buy_value)

  print(f'{to_date.strftime('%b-%Y')}\t{round(total_buy_value)}\t{round(total_current_value)}\t{round(xirr, 4)}\t{round(absolute, 4)}\t{round(realized_profits)}')

to_date = datetime.strptime('oct-2021', '%b-%Y').replace(day=1)

for i in range (0, 31):
  get_value(to_date, txn_data)
  to_date = to_date + timedelta(days=31)
  to_date = to_date.replace(day=1)

print()
print('<-- Benchmark Data -->')

benchmark_data = MFDataService(False).get_benchmark_data()
pprint.pprint(len(benchmark_data))

to_date = datetime.strptime('oct-2021', '%b-%Y').replace(day=1)
for i in range (0, 31):
  get_value(to_date, benchmark_data)
  to_date = to_date + timedelta(days=31)
  to_date = to_date.replace(day=1)
