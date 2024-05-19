"""
services.asset_value_service
~~~~~~~~~~~~~~

This module contains a class which returns details of asset value in a month.

"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Self

from xirr.math import listsXirr

from apis.mf_api_client import MFApiClient
from enums.Asset import Asset
from enums.TransactionType import TransactionType
from models.asset_value import AssetValue
from models.mf_property import MFProperty
from models.mf_transaction import MFTransaction


class AssetValueService:
    """Returns details of asset value in a month"""

    def calculate_mf_asset_value(
        self: Self,
        txn_list: list[MFTransaction],
        mf_properties: dict[str:MFProperty],
        mf_api_client: MFApiClient,
        month: datetime,
        assets_to_include: list[str],
        portfolio=None,
        country=None,
    ) -> AssetValue:
        # Contains the units, nav, asset type of each fund
        fund_map: dict[str:"AssetValue.Meta"] = {}

        # Cashflow values for XIRR
        cashflow_values: list[float] = []
        cashflow_dates: list[datetime] = []

        # Contains the total buy value
        invested_value: Decimal = Decimal(0)

        # Contains the total realized profit
        realized_profit: Decimal = Decimal(0)

        logging.debug("Processing %s transactions...", len(txn_list))

        for txn in txn_list:
            mf_property: MFProperty = mf_properties[txn.fund]

            # Filter by asset type
            if mf_property.asset.lower() not in assets_to_include:
                logging.debug(
                    "Skipping %s due to asset type %s", txn.fund, mf_property.asset
                )
                continue

            # Filter by portfolio
            if (
                portfolio is not None
                and mf_property.portfolio.lower() != portfolio.lower()
            ):
                logging.debug(
                    "Skipping %s due to portfolio %s", txn.fund, mf_property.portfolio
                )
                continue

            # Filter by country
            if country is not None and mf_property.country.lower() != country.lower():
                logging.debug(
                    "Skipping %s due to country %s", txn.fund, mf_property.country
                )
                continue

            # Two types of transactions will be eligible
            # 1 -> Transaction which has not been sold at any date and has been bought after current date
            # 2 -> Transaction has been sold, but was bought before the current date and sold after the current date
            if (
                txn.buy_sell.upper() == TransactionType.BUY.value
                and txn.buy_date < month
            ) or (
                txn.buy_sell.upper() == TransactionType.SELL.value
                and txn.buy_date < month
                and txn.sell_date > month
            ):
                # Calculate nav price at date
                current_price: Decimal

                if txn.fund in fund_map:
                    current_price = fund_map[txn.fund].price
                    fund_map[txn.fund].add_qty(txn.units)
                else:
                    current_price = mf_api_client.get_nav_price(
                        mf_property.amfi_code, month
                    )
                    fund_map[txn.fund] = AssetValue.Meta(
                        price=current_price,
                        qty=txn.units,
                        asset=mf_property.asset,
                        portfolio=mf_property.portfolio,
                        country=mf_property.country,
                    )

                buy_value: Decimal = txn.units * txn.buy_price
                current_value: Decimal = txn.units * current_price

                # Add to invested value
                invested_value += buy_value

                # Add cashflow values for XIRR
                cashflow_values.append(float(buy_value) * -1)
                cashflow_dates.append(txn.buy_date)
                cashflow_values.append(float(current_value))
                cashflow_dates.append(month)

            # These transactions are NOT eligible but are added to cashflows for XIRR and realized profits
            # These transactions are those transactions that have been bought and sold before the current date
            # Hence they are not part of the asset value at the current date but will be used to calculate realized profit and XIRR
            elif (
                txn.buy_sell == TransactionType.SELL.value
                and txn.buy_date < month
                and txn.sell_date < month
            ):
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
            value: Decimal = data.qty * data.price

            # Calculate asset level split
            asset: str = data.asset.lower()
            if asset == Asset.EQUITY.value or asset == Asset.ELSS.value:
                equity_value += value
            elif asset == Asset.DEBT.value:
                debt_value += value
            elif asset == Asset.LIQUID.value or asset == Asset.ARBITRAGE.value:
                cash_value += value

            current_value += value

        # Calculate XIRR
        xirr: float | None = listsXirr(cashflow_dates, cashflow_values)
        xirr = xirr if xirr is not None else 0

        return AssetValue(
            meta_dict=fund_map,
            data=AssetValue.Data(
                month=month,
                invested_value=invested_value,
                current_value=current_value,
                xirr=str(xirr),
                realized=realized_profit,
                equity_value=equity_value,
                debt_value=debt_value,
                cash_value=cash_value,
            ),
        )
