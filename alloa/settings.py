"""Import settings from configuration file"""
import configparser
import os
import time

from typing import Dict


def parse_config(filename: str) -> Dict:
    date = time.strftime('%d%m%y')
    current = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.abspath(os.path.join(current, os.pardir))

    config = configparser.RawConfigParser()
    config.read(os.path.join(config_path, filename))

    allocation_profile_filename = f'allocation_profile_{date}.txt'
    allocation_filename = f'allocation_{date}.csv'

    # Path for storing temporary files
    input_files = config.get('temporary_files', 'input_files')
    output_files = config.get('temporary_files', 'output_files')

    output_files_path = os.path.abspath(
        os.path.join(current, os.pardir, output_files)
    )
    os.makedirs(output_files_path, exist_ok=True)

    allocation_profile_path = os.path.abspath(
        os.path.join(
            current, os.pardir, output_files, allocation_profile_filename
        )
    )

    allocation_path = os.path.abspath(
        os.path.join(current, os.pardir, output_files, allocation_filename)
    )

    level_files = config.get('main_allocation_data', 'level_files').split(',')
    level_paths = [
        os.path.abspath(os.path.join(current, os.pardir, input_files, filename))
        for filename in level_files
    ]

    randomised = config.getboolean('randomisation', 'randomised')

    return {
        'allocation_path': allocation_path,
        'allocation_profile_path': allocation_profile_path,
        'level_paths': level_paths,
        'randomised': randomised,
    }
