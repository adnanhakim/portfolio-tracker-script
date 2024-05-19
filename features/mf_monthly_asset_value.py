"""
features.mf_monthly_asset_value
~~~~~~~~~~~~~~

This module contains a method which calculates mutual fund performance monthly.

"""

from argparse import Namespace
from datetime import datetime
from decimal import Decimal

from apis.mf_api_client import MFApiClient
from models.asset_value import AssetValue
from models.mf_property import MFProperty
from models.mf_transaction import MFTransaction
from services.asset_value_service import AssetValueService
from services.mf_data_service import MFDataService
from services.mf_properties_service import MFPropertiesService
from utils import dates
from utils.functions import format_inr, print_header, print_table

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

    # Initialize asset value service
    asset_value_service = AssetValueService()

    # Calculate which type of assets to include
    assets_to_include: list[str] = ["equity", "elss"]
    if not equity_only:
        assets_to_include.append("debt")
        assets_to_include.append("arbitrage")

    print(
        f"\nCalculating asset value from {dates.to_month_year(from_date)} to {dates.to_month_year(to_date)}...\n"
    )

    mf_asset_value_data: list[AssetValue.Data] = []

    # Calculate asset value for each month
    month: datetime = from_date
    while month <= to_date:
        mf_asset_value_data.append(
            asset_value_service.calculate_mf_asset_value(
                txn_list=mf_txn_list,
                mf_properties=mf_properties,
                mf_api_client=mf_api_client,
                month=month,
                assets_to_include=assets_to_include,
            ).data
        )
        month = dates.add_month(month)

    # Print results
    print("\t".join(HEADERS))
    for data in mf_asset_value_data:
        print(data)

    # Print summary
    print_summary(mf_asset_value_data, "Overall Portfolio")

    # If benchmark flag is present, calculate benchmark returns
    if is_benchmark:
        # Get benchmark name
        benchmark_fund_name: str = mf_api_client.get_fund_name(equity_benchmark)

        print(f"\nSimulating portfolio with benchmark set to {benchmark_fund_name}...")

        # Get benchmark transactions
        benchmark_txn_list = []
        if is_benchmark:
            benchmark_txn_list: list[MFTransaction] = (
                mf_data_service.benchmark_txn_data(
                    mf_properties, mf_api_client, equity_benchmark
                )
            )

        # Creating fake entry
        mf_properties["Benchmark"] = MFProperty(
            equity_benchmark, "Benchmark", "Equity", "India"
        )

        print(
            f"\nCalculating benchmark value from {dates.to_month_year(from_date)} to {dates.to_month_year(to_date)}...\n"
        )

        benchmark_asset_value_data: list[AssetValue.Data] = []

        # Calculate benchmark value for each month
        month = from_date
        while month <= to_date:
            benchmark_asset_value_data.append(
                asset_value_service.calculate_mf_asset_value(
                    txn_list=benchmark_txn_list,
                    mf_properties=mf_properties,
                    mf_api_client=mf_api_client,
                    month=month,
                    assets_to_include=assets_to_include,
                ).data
            )
            month: datetime = dates.add_month(month)

        # Print results
        print("\t".join(HEADERS))
        for data in benchmark_asset_value_data:
            print(data)

        # Print comparison with benchmark
        print_comparison(
            mf_asset_value_data,
            "Overall Portfolio",
            benchmark_asset_value_data,
            benchmark_fund_name,
        )


def print_summary(monthly_asset_value_data: list[AssetValue.Data], portfolio_name):
    if len(monthly_asset_value_data) == 0:
        return

    if len(monthly_asset_value_data) == 1:
        month_data: AssetValue.Data = monthly_asset_value_data[0]

        print_header(
            f"\n{portfolio_name} Summary as on {dates.to_month_year(month_data.month)}\n"
        )

        print_table(
            [
                ("Invested", format_inr(month_data.invested_value)),
                ("Current", format_inr(month_data.current_value)),
                (
                    "Unrealized",
                    (format_inr(month_data.current_value - month_data.invested_value)),
                ),
                ("Realized", format_inr(month_data.realized)),
                ("Absolute", str(round(month_data.absolute * 100, 2)) + "%"),
                ("XIRR", str(round(month_data.xirr * 100, 2)) + "%"),
            ]
        )

        return

    # 2 or more values
    first_month_data: AssetValue.Data = monthly_asset_value_data[0]
    last_month_data: AssetValue.Data = monthly_asset_value_data[
        len(monthly_asset_value_data) - 1
    ]

    print_header(
        f"\n{portfolio_name} Summary from {dates.to_month_year(first_month_data.month)} to {dates.to_month_year(last_month_data.month)}\n"
    )

    print_table(
        [
            (
                "",
                dates.to_month_year(first_month_data.month),
                dates.to_month_year(last_month_data.month),
            ),
            (
                "Invested",
                format_inr(first_month_data.invested_value),
                format_inr(last_month_data.invested_value),
            ),
            (
                "Current",
                format_inr(first_month_data.current_value),
                format_inr(last_month_data.current_value),
            ),
            (
                "Unrealized",
                (
                    format_inr(
                        first_month_data.current_value - first_month_data.invested_value
                    )
                ),
                (
                    format_inr(
                        last_month_data.current_value - last_month_data.invested_value
                    )
                ),
            ),
            (
                "Realized",
                format_inr(first_month_data.realized),
                format_inr(last_month_data.realized),
            ),
            (
                "Absolute",
                str(round(first_month_data.absolute * 100, 2)) + "%",
                str(round(last_month_data.absolute * 100, 2)) + "%",
            ),
            (
                "XIRR",
                str(round(first_month_data.xirr * 100, 2)) + "%",
                str(round(last_month_data.xirr * 100, 2)) + "%",
            ),
        ]
    )


def print_comparison(
    portfolio_asset_value_data: list[AssetValue.Data],
    portfolio_name,
    benchmark_asset_value_data: list[AssetValue.Data],
    benchmark_name,
):
    if len(portfolio_asset_value_data) == 0 or len(benchmark_asset_value_data) == 0:
        return

    portfolio: AssetValue.Data = portfolio_asset_value_data[
        len(portfolio_asset_value_data) - 1
    ]
    benchmark: AssetValue.Data = benchmark_asset_value_data[
        len(benchmark_asset_value_data) - 1
    ]

    print_header(
        f"\n{portfolio_name} vs {benchmark_name} as on {dates.to_month_year(portfolio.month)}\n"
    )

    portfolio_unrealized: Decimal = portfolio.current_value - portfolio.invested_value
    benchmark_unrealized: Decimal = benchmark.current_value - benchmark.invested_value

    print_table(
        [
            ("", portfolio_name, benchmark_name, "Difference"),
            (
                "Invested",
                format_inr(portfolio.invested_value),
                format_inr(benchmark.invested_value),
                format_inr(portfolio.invested_value - benchmark.invested_value),
            ),
            (
                "Current",
                format_inr(portfolio.current_value),
                format_inr(benchmark.current_value),
                format_inr(portfolio.current_value - benchmark.current_value),
            ),
            (
                "Unrealized",
                format_inr(portfolio_unrealized),
                format_inr(benchmark_unrealized),
                format_inr(portfolio_unrealized - benchmark_unrealized),
            ),
            (
                "Realized",
                format_inr(portfolio.realized),
                format_inr(benchmark.realized),
                format_inr(portfolio.realized - benchmark.realized),
            ),
            (
                "Absolute",
                str(round(portfolio.absolute * 100, 2)) + "%",
                str(round(benchmark.absolute * 100, 2)) + "%",
                str(round((portfolio.absolute - benchmark.absolute) * 100, 2)) + "%",
            ),
            (
                "XIRR",
                str(round(portfolio.xirr * 100, 2)) + "%",
                str(round(benchmark.xirr * 100, 2)) + "%",
                str(round((portfolio.xirr - benchmark.xirr) * 100, 2)) + "%",
            ),
        ]
    )
