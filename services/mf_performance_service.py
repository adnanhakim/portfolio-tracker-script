"""
services.mf_performance_service
~~~~~~~~~~~~~~

This module contains a service methods which performs analysis.

"""

from datetime import datetime
from decimal import Decimal

from xirr.math import listsXirr

from apis.mf_api_client import MFApiClient
from models.mf_property import MFProperty
from models.mf_transaction import MFTransaction
from utils import dates


def calculate_monthly_asset_value(
    txn_list: list[MFTransaction],
    mf_properties: dict[str:MFProperty],
    mf_api_client: MFApiClient,
    from_datestring: str,
    to_datestring: str,
    is_benchmark: bool,
    benchmark_txn_list: list[MFTransaction],
    equity_only: bool,
):
    from_date: datetime = dates.from_month_year(from_datestring)
    to_date: datetime = dates.from_month_year(to_datestring)

    print(
        f"\nExecuting from {from_datestring.capitalize()} to {to_datestring.capitalize()}"
    )

    print(
        "\n<--------------------------- Monthly Asset Value --------------------------->"
    )

    temp_date = from_date
    while temp_date <= to_date:
        calculate_asset_value(
            txn_list, mf_properties, mf_api_client, temp_date, equity_only
        )
        temp_date: datetime = dates.add_month(temp_date)

    if is_benchmark and len(benchmark_txn_list) != 0:
        print(
            "\n<------------------------- Monthly Benchmark Value ------------------------->"
        )

        temp_date = from_date
        while temp_date <= to_date:
            calculate_asset_value(
                benchmark_txn_list, mf_properties, mf_api_client, temp_date, equity_only
            )
            temp_date: datetime = dates.add_month(temp_date)


def calculate_asset_value(
    txn_list: list[MFTransaction],
    mf_properties: dict[str:MFProperty],
    mf_api_client: MFApiClient,
    date: datetime,
    equity_only: bool,
):
    # Contains the price of each fund at the current date
    fund_price_map: dict[str:Decimal] = {}

    # Contains the units of each fund at the end of the date
    fund_units_map: dict[str:Decimal] = {}

    # Cashflow values for XIRR
    cashflow_values: list[float] = []
    cashflow_dates: list[datetime] = []

    # Contains the total buy value
    invested_value: Decimal = Decimal(0)

    # Contains the total realized profit
    realized_profit: Decimal = Decimal(0)

    for txn in txn_list:
        mf_property: MFProperty = mf_properties[txn.fund]

        # Ignore non-equity if equity only flag is enabled
        if equity_only and (
            mf_property.asset == "Debt" or mf_property.asset == "Arbitrage"
        ):
            continue

        # Two types of transactions will be eligible
        # 1 -> Transaction which has not been sold at any date and has been bought after current date
        # 2 -> Transaction has been sold, but was bought before the current date and sold after the current date
        if (txn.buy_sell == "BUY" and txn.buy_date < date) or (
            txn.buy_sell == "SELL" and txn.buy_date < date and txn.sell_date > date
        ):
            # Calculate nav price at date
            current_price: Decimal
            if txn.fund in fund_price_map:
                current_price = fund_price_map[txn.fund]
            else:
                current_price = mf_api_client.get_nav_price(mf_property.amfi_code, date)
                fund_price_map[txn.fund] = current_price

            # Add units to map
            if txn.fund in fund_units_map:
                fund_units_map[txn.fund] += txn.units
            else:
                fund_units_map[txn.fund] = txn.units

            buy_value: Decimal = txn.units * txn.buy_price
            current_value: Decimal = txn.units * current_price

            # Add to invested value
            invested_value += buy_value

            # Add cashflow values for XIRR
            cashflow_values.append(float(buy_value) * -1)
            cashflow_dates.append(txn.buy_date)
            cashflow_values.append(float(current_value))
            cashflow_dates.append(date)

        # These transactions are NOT eligible but are added to cashflows for XIRR and realized profits
        # These transactions are those transactions that have been bought and sold before the current date
        # Hence they are not part of the asset value at the current date but will be used to calculate realized profit and XIRR
        elif txn.buy_sell == "SELL" and txn.buy_date < date and txn.sell_date < date:
            buy_value: Decimal = txn.units * txn.buy_price
            sell_value: Decimal = txn.units * txn.sell_price

            # Add to realized profits
            realized_profit += sell_value - buy_value

            # Add cashflow values for XIRR
            cashflow_values.append(float(buy_value) * -1)
            cashflow_dates.append(txn.buy_date)
            cashflow_values.append(float(sell_value))
            cashflow_dates.append(txn.sell_date)

    # Calculate equity/debt/cash split
    equity_value: Decimal = Decimal(0)
    debt_value: Decimal = Decimal(0)
    cash_value: Decimal = Decimal(0)

    # Calculate current value
    current_value = Decimal(0)
    for fund, units in fund_units_map.items():
        asset: str = mf_properties[fund].asset
        value: Decimal = units * fund_price_map[fund]

        if asset == "Equity" or asset == "ELSS":
            equity_value += value
        elif asset == "Debt":
            debt_value += value
        else:
            cash_value += value

        current_value += value

    # Calculate XIRR
    xirr: float | None = listsXirr(cashflow_dates, cashflow_values)

    # Calculate absolute returns
    absolute_returns: Decimal = (current_value - invested_value) / invested_value

    print(
        f"{dates.to_month_year(date)}\t{round(invested_value)}\t{round(current_value)}\t{round(xirr, 4)}\t{round(absolute_returns, 4)}\t{round(realized_profit)}\t{round(equity_value / current_value, 4)}\t{round(debt_value / current_value, 4)}\t{round(cash_value / current_value, 4)}"
    )
