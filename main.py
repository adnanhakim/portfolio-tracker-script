"""
main
~~~~~~~~~~~~~~

This module contains the main python runner class.
Run python3 main.py --help for more information.

"""

import sys
from argparse import ArgumentParser, Namespace

from features.mf_asset_value import calculate_monthly_asset_value
from features.process_transactions import process_transactions
from features.test_connection import test_connection
from utils import dates

last_month_datestring: str = dates.get_last_month_datestring()

parser = ArgumentParser(
    description="A Python script that analyzes investment portfolio data from a Google Sheet"
)

parser.add_argument(
    "command",
    type=str,
    help="Specify the type of analysis to be performed. Currently supporting 'test' to test your connection and 'assetvalue' to calculate month-on-month asset values.",
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
parser.add_argument(
    "--filepath",
    type=str,
    help="Specify the Excel file path to be processed",
)


args: Namespace = parser.parse_args()

command = args.command

if command == "assetvalue":
    calculate_monthly_asset_value(args)
elif command == "test":
    test_connection()
elif command == "process":
    process_transactions(args)
else:
    print("Unsupported command. Run --help for more information.")
    sys.exit(1)
