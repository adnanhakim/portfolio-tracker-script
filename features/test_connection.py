"""
features.test_connection
~~~~~~~~~~~~~~

This module contains a method which tests connection to Google Sheets.

"""

import logging

from models.mf_property import MFProperty
from models.mf_transaction import MFTransaction
from services.mf_data_service import MFDataService
from services.mf_properties_service import MFPropertiesService


def test_connection():
    mf_txn_list: list[MFTransaction] = MFDataService(True).mf_txn_data()

    logging.info("Printing first transaction...")
    logging.info(mf_txn_list[0])

    mf_properties: dict[str, MFProperty] = MFPropertiesService(True).mf_properties()

    logging.info("Printing first property...")
    key: str = next(iter(mf_properties))
    logging.info("%s: %s", key, mf_properties[key])

    logging.warning("Check if all mappings are correctly done.")
    logging.warning("If mapping is incorrect, correct .env file")

    logging.info("Connection established successfully!")
