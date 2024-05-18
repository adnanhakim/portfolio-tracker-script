from datetime import datetime
from decimal import Decimal, InvalidOperation
import pprint
import sys

from pandas import read_excel, DataFrame, to_datetime


def process_transactions(args):
    file_path: str = args.filepath

    if file_path is None:
        print("File path is required")
        sys.exit(1)

    print(file_path)

    read_excel_sheet(file_path, "MF Transactions")


# Define a function to convert the column to decimal
def convert_to_decimal(value):
    try:
        return Decimal(value)
    except InvalidOperation as e:
        print(f"Error converting '{value}' to Decimal: {e}")
        return Decimal(0)  # Or handle the error in a different way


def read_excel_sheet(file_path, sheet_name):
    df: DataFrame = read_excel(
        file_path,
        sheet_name,
        # converters={"Date": to_datetime},
        # dtype={"Date": "datetime"},
        # parse_dates=["Date"],
        # converters={"Date": str},
        # date_format="%Y-%m-%d",
        # dtype={"Date": "datetime64"},
        # converters={"NAV": convert_to_decimal, "Units": convert_to_decimal},
    )

    # df["Date"] = datetime.strptime(df["Date"], "%Y-%m-%d %H:%M:%S")
    # df["Date"] = df["Date"].apply(
    #     lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
    # )

    mask = (df["Units"] != 0) & (df["Units"].notna())

    filtered_df = df[mask]
    # print(filtered_df)

    sorted_df = filtered_df.sort_values(by=["Date", "Fund Name"])
    print(sorted_df)

    # sorted_df.rename(
    #     columns={
    #         "Fund Name": "fund_name",
    #         "Date": "buy_date",
    #         "Units": "units",
    #         "NAV": "buy_price",
    #     },
    #     inplace=True,
    # )
    # sorted_df["units"] = sorted_df["units"].apply(lambda x: Decimal(x))
    # sorted_df["buy_price"] = sorted_df["buy_price"].apply(lambda x: Decimal(x))
    # sorted_df["type"] = "BUY"
    # sorted_df["sell_date"] =
    # sorted_df["sell_price"] = Decimal(0)

    # print(sorted_df)
    data = []

    sell_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for index, row in sorted_df.iterrows():
        data.append(
            {
                "fund_name": row["Fund Name"],
                "type": "BUY",
                "units": Decimal(str(row["Units"])),
                # "buy_date": datetime.strptime(row["Date"], "%Y-%m-%d %H:%M:%S"),
                "buy_date": row["Date"].to_pydatetime(),
                "buy_price": row["NAV"],
                "sell_date": sell_date,
                "sell_price": Decimal(0),
            }
        )

    process_data(data)


def process_data(data):
    pprint.pprint(data)
    # for index, row in df.iterrows():
    #     if row["units"] < 0:
    #         print(
    #             f"The first negative number is {row['units']} at index {index}. {row}"
    #         )

    #         fund_name = row["fund_name"]

    #         for index2, row2 in df.iterrows():
    #             if row2["fund_name"] == fund_name and row["units"] > 0:
    #                 print(f"Found {row}")

    #         break
