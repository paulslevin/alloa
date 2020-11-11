"""Import settings from configuration file"""
import configparser
from pathlib import Path
import time

from typing import Dict


def parse_config(filename: str) -> Dict:
    date = time.strftime('%d%m%y')
    current = Path(__file__).parent
    config_path = current.parent

    config = configparser.RawConfigParser()
    config.read(Path(config_path, filename))

    allocation_profile_filename = f'allocation_profile_{date}.txt'
    allocation_filename = f'allocation_{date}.csv'

    # Path for storing temporary files
    input_files = config.get('temporary_files', 'input_files')
    output_files = config.get('temporary_files', 'output_files')

    output_files_path = Path(current.parent, output_files)
    output_files_path.mkdir(exist_ok=True)

    allocation_profile_path = Path(
        output_files_path, allocation_profile_filename
    )
    allocation_path = Path(output_files_path, allocation_filename)

    level_files = config.get('main_allocation_data', 'level_files').split(',')
    level_paths = [
        Path(current.parent, input_files, filename) for filename in level_files
    ]

    randomised = config.getboolean('randomisation', 'randomised')

    return {
        'allocation_path': allocation_path,
        'allocation_profile_path': allocation_profile_path,
        'level_paths': level_paths,
        'randomised': randomised,
    }
