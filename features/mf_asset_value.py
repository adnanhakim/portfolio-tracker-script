"""
features.mf_asset_value
~~~~~~~~~~~~~~

This module contains a method which calculates mutual fund performance monthly.

"""

from argparse import Namespace
from datetime import datetime
from decimal import Decimal

from tabulate import tabulate
from xirr.math import listsXirr

from apis.mf_api_client import MFApiClient
from models.mf_property import MFProperty
from models.mf_transaction import MFTransaction
from services.mf_data_service import MFDataService
from services.mf_properties_service import MFPropertiesService
from utils import dates
from utils.functions import format_inr

HEADERS: list = [
    "Month",
    "Invested",
    "Current",
    "Absolute",
    "XIRR",
    "Realized",
    "Equity%",
    "Debt%",
    "Cash%",
]


def calculate_monthly_asset_value(args: Namespace):
    # Parse arguments
    from_date: datetime = args.from_date
    to_date: datetime = args.to_date
    is_benchmark: bool = args.benchmark
    equity_benchmark: int = args.equity_benchmark
    equity_only: bool = args.equity
    override_cache: bool = args.override_cache

    # Get transactions
    mf_data_service: MFDataService = MFDataService(override_cache)
    mf_txn_list: list[MFTransaction] = mf_data_service.mf_txn_data()

    # Get properties
    mf_api_client = MFApiClient(override_cache)
    mf_properties: dict[str, MFProperty] = MFPropertiesService(
        override_cache
    ).mf_properties()

    # Calculate which type of assets to include
    assets_to_include: list[str] = ["equity", "elss"]
    if not equity_only:
        assets_to_include.append("debt")
        assets_to_include.append("arbitrage")

    print(
        f"\nCalculating asset value from {dates.to_month_year(from_date)} to {dates.to_month_year(to_date)}...\n"
    )

    mf_data: list[list] = []
    mf_data.append(HEADERS)

    temp_date = from_date
    while temp_date <= to_date:
        mf_data.append(
            calculate_asset_value(
                mf_txn_list, mf_properties, mf_api_client, temp_date, assets_to_include
            )["data"]
        )
        temp_date: datetime = dates.add_month(temp_date)

    for data in mf_data:
        print("\t".join(map(str, data)))

    last_month_data: list = mf_data[len(mf_data) - 1]

    print(f"\nPortfolio Returns (XIRR) on {last_month_data[0]} is {last_month_data[4]}")

    if is_benchmark:
        # Get benchmark transactions
        benchmark_txn_list = []
        if is_benchmark:
            benchmark_txn_list: list[MFTransaction] = mf_data_service.benchmark_txn_data(
                mf_properties, mf_api_client, equity_benchmark
            )

        mf_properties["Benchmark"] = MFProperty(equity_benchmark, "Benchmark", "Equity", "India")

        print("\n------------------------")

        print(
            f"\nCalculating benchmark value from {dates.to_month_year(from_date)} to {dates.to_month_year(to_date)}...\n"
        )

        benchmark_data: list = []
        benchmark_data.append(HEADERS)

        temp_date = from_date
        while temp_date <= to_date:
            benchmark_data.append(
                calculate_asset_value(
                    benchmark_txn_list,
                    mf_properties,
                    mf_api_client,
                    temp_date,
                    assets_to_include,
                )["data"]
            )
            temp_date: datetime = dates.add_month(temp_date)

        for data in benchmark_data:
            print("\t".join(map(str, data)))

        last_month_benchmark_data: list = benchmark_data[len(benchmark_data) - 1]

        benchmark_fund_name: str = mf_api_client.get_fund_name(equity_benchmark)

        print(
            f"\n{benchmark_fund_name} Returns (XIRR) on {last_month_benchmark_data[0]} is {last_month_benchmark_data[4]}"
        )

        print("\n------------------------")

        print_summary(last_month_data, last_month_benchmark_data)


def calculate_asset_value(
    txn_list: list[MFTransaction],
    mf_properties: dict[str:MFProperty],
    mf_api_client: MFApiClient,
    date: datetime,
    assets_to_include: list[str],
    portfolio=None,
    country=None
) -> dict:
    # Contains the units, nav, asset type of each fund
    fund_map: dict[str] = {}

    # Cashflow values for XIRR
    cashflow_values: list[float] = []
    cashflow_dates: list[datetime] = []

    # Contains the total buy value
    invested_value: Decimal = Decimal(0)

    # Contains the total realized profit
    realized_profit: Decimal = Decimal(0)

    for txn in txn_list:
        mf_property: MFProperty = mf_properties[txn.fund]

        # Filter by asset type
        if mf_property.asset.lower() not in assets_to_include:
            continue

        # Filter by portfolio
        if portfolio is not None and mf_property.portfolio.lower() != portfolio.lower():
            continue

        # Filter by country
        if country is not None and mf_property.country.lower() != country.lower():
            continue

        # Two types of transactions will be eligible
        # 1 -> Transaction which has not been sold at any date and has been bought after current date
        # 2 -> Transaction has been sold, but was bought before the current date and sold after the current date
        if (txn.buy_sell == "BUY" and txn.buy_date < date) or (
            txn.buy_sell == "SELL" and txn.buy_date < date and txn.sell_date > date
        ):
            # Calculate nav price at date
            current_price: Decimal

            if txn.fund in fund_map:
                current_price = fund_map[txn.fund]["nav"]
                fund_map[txn.fund]["units"] += txn.units
            else:
                current_price = mf_api_client.get_nav_price(mf_property.amfi_code, date)
                fund_map[txn.fund] = {
                    "nav": current_price,
                    "units": txn.units,
                    "asset": mf_property.asset,
                    "portfolio": mf_property.portfolio,
                    "country": mf_property.country
                }

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
    for data in fund_map.values():
        # asset: str = mf_properties[fund].asset
        asset: str = data["asset"]
        value: Decimal = data["units"] * data["nav"]

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

    return {
        "meta": fund_map,
        "data": [
            dates.to_month_year(date),
            round(invested_value),
            round(current_value),
            str(round(absolute_returns * 100, 2)) + "%",
            str(round(xirr * 100, 2)) + "%",
            round(realized_profit),
            str(round((equity_value / current_value) * 100, 2)) + "%",
            str(round((debt_value / current_value) * 100, 2)) + "%",
            str(round((cash_value / current_value) * 100, 2)) + "%",
        ]
    }

def print_summary(last_month_data, last_month_benchmark_data):
    xirr_diff: Decimal = Decimal(last_month_data[4].rstrip("%")) - Decimal(
        last_month_benchmark_data[4].rstrip("%")
    )

    tuple_list = [
        (
            "Unrealized",
            format_inr(last_month_data[2]),
            format_inr(last_month_benchmark_data[2]),
            format_inr(last_month_data[2] - last_month_benchmark_data[2]),
        ),
        (
            "Realized",
            format_inr(last_month_data[5]),
            format_inr(last_month_benchmark_data[5]),
            format_inr(last_month_data[5] - last_month_benchmark_data[5]),
        ),
        # (
        #     "Absolute",
        #     format_inr(last_month_data[2]),
        #     format_inr(last_month_benchmark_data[2]),
        #     format_inr(last_month_data[2] - last_month_benchmark_data[2]),
        # ),
        # (
        #     "XIRR",
        #     format_inr(last_month_data[2]),
        #     format_inr(last_month_benchmark_data[2]),
        #     format_inr(last_month_data[2] - last_month_benchmark_data[2]),
        # ),
    ]

    print(tabulate(tuple_list, headers=['','Your Portfolio', 'Benchmark', 'Difference'], tablefmt="plain"))

    if xirr_diff > 0:
        print(f"\nPortfolio is outperforming benchmark as of {last_month_data[0]}")
        print(f"XIRR Gain: {str(xirr_diff) + "%"}")
        print(
            f"Additional Unrealized Gains: {format_inr(last_month_data[2] - last_month_benchmark_data[2])}"
        )
        print(
            f"Additional Realized Gains: {format_inr(last_month_data[5] - last_month_benchmark_data[5])}"
        )
    else:
        print(f"Portfolio is lagging behind benchmark as of {last_month_data[0]}")
        print(f"XIRR Loss: {str(abs(xirr_diff)) + "%"}")
        print(
            f"Additional Unrealized Losses: {format_inr(abs(last_month_data[2] - last_month_benchmark_data[2]))}"
        )
        print(
            f"Additional Realized Losses: {format_inr(abs(last_month_data[5] - last_month_benchmark_data[5]))}"
        )
