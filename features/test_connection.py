"""
features.test_connection
~~~~~~~~~~~~~~

This module contains a method which tests connection to Google Sheets.

"""

from models.mf_property import MFProperty
from models.mf_transaction import MFTransaction
from services.mf_data_service import MFDataService
from services.mf_properties_service import MFPropertiesService


def test_connection():
    mf_txn_list: list[MFTransaction] = MFDataService(True).mf_txn_data()

    print(f"\nFound {len(mf_txn_list)} mutual fund transactions")

    print("\nPrinting first transaction...")
    print(mf_txn_list[0])

    mf_properties: dict[str, MFProperty] = MFPropertiesService(True).mf_properties()

    print(f"\nFound {len(mf_properties)} mutual fund properties")

    print("\nPrinting first property...")
    key: str = next(iter(mf_properties))
    print(key, mf_properties[key])

    print("\nConnection established successfully!")
