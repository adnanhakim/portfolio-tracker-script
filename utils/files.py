"""
utils.files
~~~~~~~~~~~~~~

This module contains common file methods.

"""

import json
import os
from typing import Collection, LiteralString


def get_folder_path(folder_name: str) -> LiteralString:
    """Returns folder path taking folder name as input"""
    return os.path.join(os.getcwd(), folder_name)


def get_json_file_path(folder_name: str, file_name: str) -> LiteralString:
    """Returns json file path taking folder name and file name as input"""
    return os.path.join(os.getcwd(), folder_name, file_name + ".json")


def check_or_create_folder(folder_name: str) -> None:
    """Checks if a folder exists and creates if it does not exist"""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def check_if_json_file_exists(folder_name: str, file_name: str) -> bool:
    """Checks if a file path exists and returns the result"""
    file_path: LiteralString = get_json_file_path(folder_name, file_name)

    return os.path.exists(file_path)


def save_file_as_json(folder_name: str, file_name: str, data: Collection) -> None:
    """Saves a file as UTF-8 encoded .json file"""
    check_or_create_folder(folder_name)

    file_path: LiteralString = get_json_file_path(folder_name, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def read_file_as_json(folder_name: str, file_name: str) -> Collection | None:
    """Reads a UTF-8 encoded .json file and returns the result"""
    if check_if_json_file_exists(folder_name, file_name) is False:
        return None

    file_path: LiteralString = get_json_file_path(folder_name, file_name)

    with open(file_path, "r", encoding="utf-8") as f:
        json_data: Collection = json.load(f)

    return json_data


def delete_files_in_folder(folder_name: str) -> None:
    """Deletes all files in a folder"""
    folder_path: LiteralString = get_folder_path(folder_name)

    if os.path.exists(folder_path):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            # Check if the path is a file (not a directory)
            if os.path.isfile(file_path):
                # Delete the file
                os.remove(file_path)
