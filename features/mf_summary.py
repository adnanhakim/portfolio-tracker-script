"""
features.mf_summary
~~~~~~~~~~~~~~

This module contains a method which calculates mutual fund portfolio summary on a given month.

"""

from argparse import Namespace
from datetime import datetime
from decimal import Decimal

from colorama import Fore, Style
from tabulate import tabulate

from apis.mf_api_client import MFApiClient
from features.mf_asset_value import calculate_asset_value
from models.mf_property import MFProperty
from models.mf_transaction import MFTransaction
from services.mf_data_service import MFDataService
from services.mf_properties_service import MFPropertiesService
from utils.functions import format_inr


def calculate_portfolio_summary(args: Namespace) -> None:
    # Parse arguments
    date: datetime = args.date
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

    filter_map: list[tuple[str, str]] = [
        ("Portfolio", portfolio.capitalize() if portfolio is not None else "None"),
        ("Country", country.capitalize() if country is not None else "None"),
    ]

    # Calculate which type of assets to include
    assets_to_include: list[str] = ["equity", "elss", "debt", "arbitrage"]

    result: dict = calculate_asset_value(
        mf_txn_list,
        mf_properties,
        mf_api_client,
        date,
        assets_to_include,
        portfolio=portfolio,
        country=country,
    )

    meta: dict[str:dict] = result["meta"]
    data: list[list] = result["data"]

    value_map: list[tuple[str, str]] = [
        ("Invested", format_inr(data[1])),
        ("Current", format_inr(data[2])),
        ("Unrealized", (format_inr(data[2] - data[1]))),
        ("Realized", format_inr(data[5])),
    ]

    returns_map: list[tuple[str, str]] = [
        ("Absolute", data[3]),
        ("XIRR", data[4]),
    ]

    asset_split: list[tuple[str, str]] = [
        ("Equity", data[6]),
        ("Debt", data[7]),
        ("Cash", data[8]),
    ]

    portfolio_split: dict = {}
    country_split: dict = {}
    fund_split: dict = {}

    # Calculate types of splits
    for key, value in meta.items():
        current_value: Decimal = value["units"] * value["nav"]

        # Calculate portfolio split
        if value["portfolio"] not in portfolio_split:
            portfolio_split[value["portfolio"]] = current_value
        else:
            portfolio_split[value["portfolio"]] += current_value

        # Calculate country split
        if value["country"] not in country_split:
            country_split[value["country"]] = current_value
        else:
            country_split[value["country"]] += current_value

        # Calculate fund split
        fund_split[key] = current_value

    print_header("Filters Applied")
    print_list(filter_map)

    # Generate portfolio label
    label: str = country.capitalize() + " " if country is not None else ""
    label += portfolio.capitalize() + " " if portfolio is not None else ""
    label = label if label is not None else "Overall "

    print_header(f"{label}Portfolio Summary as on {data[0]}:")

    print_header("Value")
    print_list(value_map)

    print_header("Returns")
    print_list(returns_map)

    print_header(f"By Asset Type ({len(asset_split)})")
    print_list(asset_split)

    # Print portfolio split only if not filtered by portfolio
    if portfolio is None:
        print_header(f"By Portfolio ({len(portfolio_split)})")
        print_list(sort_list(portfolio_split, data[2]))

    # Print country split only if not filtered by country
    if country is None:
        print_header(f"By Country ({len(country_split)})")
        print_list(sort_list(country_split, data[2]))

    print_header(f"By Mutual Funds ({len(fund_split)})")
    print_list(sort_list(fund_split, data[2]))


def print_header(header: str) -> None:
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{header}{Style.RESET_ALL}")


def print_list(tuple_list: list[tuple]) -> None:
    print(tabulate(tuple_list, tablefmt="plain"))


def sort_list(split_map, total_value):
    sorted_split_list: list[tuple] = sorted(
        split_map.items(), key=lambda item: item[1], reverse=True
    )

    return [
        (key, str(round((value / total_value) * 100, 2)) + "%")
        for key, value in sorted_split_list
    ]
