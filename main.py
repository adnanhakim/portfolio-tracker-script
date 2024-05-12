"""
main
~~~~~~~~~~~~~~

This module contains the main python runner class.
Run python3 main.py --help for more information.

"""

import sys
from argparse import ArgumentParser, Namespace

from apis.mf_api_client import MFApiClient
from models.mf_property import MFProperty
from models.mf_transaction import MFTransaction
from services.mf_data_service import MFDataService
from services.mf_performance_service import calculate_monthly_asset_value
from services.mf_properties_service import MFPropertiesService
from utils import dates

last_month_datestring: str = dates.get_last_month_datestring()

parser = ArgumentParser(
    description="A Python script that analyzes investment portfolio data from a Google Sheet"
)

parser.add_argument(
    "command",
    type=str,
    help="Specify the type of analysis to be performed. Currently supporting 'assetvalue'.",
)
parser.add_argument(
    "--fromdate",
    type=str,
    default=last_month_datestring,
    help="Specify the starting date of the analysis period (inclusive) in MMM-yyyy format, defaulted to last month. Example Jan-2021",
)
parser.add_argument(
    "--todate",
    type=str,
    default=last_month_datestring,
    help="Specify the ending date of the analysis period (inclusive) in MMM-yyyy format, defaulted to last month. Example Jan-2021",
)
parser.add_argument(
    "--benchmark",
    action="store_true",
    help="Specify this flag to compare results with benchmark values",
)
parser.add_argument(
    "--equity",
    action="store_true",
    help="Specify this flag to calculate for only equity funds",
)
parser.add_argument(
    "--nocache",
    action="store_true",
    help="Specify this flag to invalidate cache and fetch latest values",
)


args: Namespace = parser.parse_args()

command = args.command

if command == "assetvalue":
    from_date: str = args.fromdate
    to_date: str = args.todate
    is_benchmark: bool = args.benchmark
    equity_only: bool = args.equity
    override_cache: bool = args.nocache
    benchmark_txn_list = []

    mf_data_service = MFDataService(override_cache)
    mf_txn_list: list[MFTransaction] = mf_data_service.mf_txn_data()

    mf_api_client = MFApiClient(override_cache)
    mf_properties: dict[str, MFProperty] = MFPropertiesService(
        override_cache
    ).get_mf_properties()

    if is_benchmark:
        benchmark_txn_list: list[MFTransaction] = mf_data_service.benchmark_txn_data(
            mf_properties, mf_api_client
        )

    calculate_monthly_asset_value(
        txn_list=mf_txn_list,
        mf_properties=mf_properties,
        mf_api_client=mf_api_client,
        from_datestring=from_date,
        to_datestring=to_date,
        is_benchmark=is_benchmark,
        benchmark_txn_list=benchmark_txn_list,
        equity_only=equity_only,
    )
else:
    print("Unsupported command. Run --help for more information.")
    sys.exit(1)
