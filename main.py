"""
main
~~~~~~~~~~~~~~

This module contains the main python runner class.
Run python3 main.py --help for more information.

"""

from argparse import ArgumentParser, ArgumentTypeError, Namespace, _SubParsersAction
from datetime import datetime

from colorama import init
from dotenv import load_dotenv

from features.mf_asset_value import calculate_monthly_asset_value
from features.mf_summary import calculate_portfolio_summary
from features.test_connection import test_connection
from utils import dates
from utils import logger as log

# Load environment variables
load_dotenv()

# Initialize colorama
init()


last_month_date: datetime = dates.get_last_month_date()


def parse_month_year(date_string):
    try:
        return datetime.strptime(date_string, "%b-%Y")
    except ValueError as exception:
        raise ArgumentTypeError(
            f"Not a valid date: '{date_string}'. Expected format: 'MMM-yyyy'"
        ) from exception


parser = ArgumentParser(
    description="A Python script that analyzes investment portfolio data from a Google Sheet"
)

subparsers: _SubParsersAction = parser.add_subparsers(
    dest="command",
    help="type of command to be executed",
)

parser_test: ArgumentParser = subparsers.add_parser(
    "test", help="test connection to google sheets"
)

parser_assetvalue: ArgumentParser = subparsers.add_parser(
    "assetvalue", help="generate month-on-month asset value"
)
parser_assetvalue.add_argument(
    "-f",
    "--from",
    metavar="date",
    dest="from_date",
    type=parse_month_year,
    default=last_month_date,
    help="starting date in MMM-yyyy format, defaulted to last month",
)
parser_assetvalue.add_argument(
    "-t",
    "--to",
    metavar="date",
    dest="to_date",
    type=parse_month_year,
    default=last_month_date,
    help="ending date in MMM-yyyy format, defaulted to last month",
)
parser_assetvalue.add_argument(
    "-b",
    "--benchmark",
    action="store_true",
    help="calculate benchmark data",
)
parser_assetvalue.add_argument(
    "-eb",
    "--eqbenchmark",
    metavar="amfi_code",
    dest="equity_benchmark",
    type=int,
    default=120716,
    help="amfi code of equity benchmark mutual fund",
)
parser_assetvalue.add_argument(
    "--equity",
    action="store_true",
    help="calculate data for only equity funds",
)
parser_assetvalue.add_argument(
    "--nocache",
    dest="override_cache",
    action="store_true",
    help="invalidate cache and fetch latest values",
)

parser_summary: ArgumentParser = subparsers.add_parser(
    "summary", help="generate portfolio summary"
)
parser_summary.add_argument(
    "-d",
    "--date",
    metavar="date",
    dest="date",
    type=parse_month_year,
    default=last_month_date,
    help="date in MMM-yyyy format, defaulted to last month",
)
parser_summary.add_argument(
    "-p",
    "--portfolio",
    metavar="name",
    dest="portfolio",
    type=str,
    help="filter by portfolio name",
)
parser_summary.add_argument(
    "-c",
    "--country",
    metavar="name",
    dest="country",
    type=str,
    help="filter by country name",
)
parser_summary.add_argument(
    "--nocache",
    dest="override_cache",
    action="store_true",
    help="invalidate cache and fetch latest values",
)

# Get arguments
args: Namespace = parser.parse_args()

log.debug(args)

if args.command == "assetvalue":
    calculate_monthly_asset_value(args)
elif args.command == "test":
    test_connection()
elif args.command == "summary":
    calculate_portfolio_summary(args)
else:
    raise ArgumentTypeError(
        f"Unsupported command '{args.command}'. Run --help for more information."
    )
