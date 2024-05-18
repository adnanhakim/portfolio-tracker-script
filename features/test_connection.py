"""
features.test_connection
~~~~~~~~~~~~~~

This module contains a method which tests connection to Google Sheets.

"""

from models.mf_property import MFProperty
from models.mf_transaction import MFTransaction
from services.mf_data_service import MFDataService
from services.mf_properties_service import MFPropertiesService
from utils import logger as log


def test_connection():
    mf_txn_list: list[MFTransaction] = MFDataService(True).mf_txn_data()

    log.info("Printing first transaction...", True)
    log.info(mf_txn_list[0])

    mf_properties: dict[str, MFProperty] = MFPropertiesService(True).mf_properties()

    log.info("Printing first property...", True)
    key: str = next(iter(mf_properties))
    log.info(key)
    log.info(mf_properties[key])

    log.warning("Check if all mappings are correctly done.", True)
    log.warning("If mapping is incorrect, correct .env file")

    log.info("Connection established successfully!", True)
