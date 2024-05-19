"""
features.mf_summary
~~~~~~~~~~~~~~

This module contains a method which calculates mutual fund portfolio summary on a given month.

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
from utils.dates import to_month_year
from utils.functions import format_inr, print_header, print_table


def calculate_portfolio_summary(args: Namespace) -> None:
    # Parse arguments
    month: datetime = args.date
    portfolio: str = args.portfolio
    country: str = args.country
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

    filter_map: list[tuple[str, str]] = [
        ("Portfolio", portfolio.capitalize() if portfolio is not None else "None"),
        ("Country", country.capitalize() if country is not None else "None"),
    ]

    # Calculate which type of assets to include
    assets_to_include: list[str] = ["equity", "elss", "debt", "arbitrage"]

    asset_value: AssetValue = asset_value_service.calculate_mf_asset_value(
        txn_list=mf_txn_list,
        mf_properties=mf_properties,
        mf_api_client=mf_api_client,
        month=month,
        assets_to_include=assets_to_include,
        portfolio=portfolio,
        country=country,
    )

    meta_dict: dict[str:"AssetValue.Meta"] = asset_value.meta_dict
    data: AssetValue.Data = asset_value.data

    portfolio_split: dict = {}
    country_split: dict = {}
    fund_split: dict = {}

    # Calculate types of splits
    for fund, meta in meta_dict.items():
        current_value: Decimal = meta.qty * meta.price

        # Calculate portfolio split
        if meta.portfolio not in portfolio_split:
            portfolio_split[meta.portfolio] = current_value
        else:
            portfolio_split[meta.portfolio] += current_value

        # Calculate country split
        if meta.country not in country_split:
            country_split[meta.country] = current_value
        else:
            country_split[meta.country] += current_value

        # Calculate fund split
        fund_split[fund] = current_value

    # Print filters
    print_header("Filters Applied")
    print_table(filter_map)

    # Print header
    print_header(
        f"{generate_portfolio_label(portfolio, country)}Portfolio Summary as on {to_month_year(data.month)}:"
    )

    # Print values
    print_header("Value")
    print_table(
        [
            ("Invested", format_inr(data.invested_value)),
            ("Current", format_inr(data.current_value)),
            ("Unrealized", (format_inr(data.current_value - data.invested_value))),
            ("Realized", format_inr(data.realized)),
        ]
    )

    # Print returns
    print_header("Returns")
    print_table(
        [
            ("Absolute", str(round(data.absolute * 100, 2)) + "%"),
            ("XIRR", str(round(data.xirr * 100, 2)) + "%"),
        ]
    )

    # Print asset split
    print_header("By Asset Type")
    print_table(
        [
            ("Equity", str(round(data.equity_pct * 100, 2)) + "%"),
            ("Debt", str(round(data.debt_pct * 100, 2)) + "%"),
            ("Cash", str(round(data.cash_pct * 100, 2)) + "%"),
        ]
    )

    # Print portfolio split only if not filtered by portfolio
    if portfolio is None:
        print_header(f"By Portfolio ({len(portfolio_split)})")
        print_table(sort_list(portfolio_split, data.current_value))

    # Print country split only if not filtered by country
    if country is None:
        print_header(f"By Country ({len(country_split)})")
        print_table(sort_list(country_split, data.current_value))

    # Print mutual fund split
    print_header(f"By Mutual Funds ({len(fund_split)})")
    print_table(sort_list(fund_split, data.current_value))


def generate_portfolio_label(portfolio: str, country: str) -> str:
    label: str = country.capitalize() + " " if country is not None else ""
    label += portfolio.capitalize() + " " if portfolio is not None else ""
    label = label if label is not None else "Overall "

    return label


def sort_list(split_map, total_value):
    sorted_split_list: list[tuple] = sorted(
        split_map.items(), key=lambda item: item[1], reverse=True
    )

    return [
        (key, str(round((value / total_value) * 100, 2)) + "%")
        for key, value in sorted_split_list
    ]
