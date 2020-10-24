"""Import settings from configuration file"""

import configparser
import os
import time

DATE = time.strftime('%d%m%y')
CURRENT = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(CURRENT, os.pardir))

config = configparser.RawConfigParser()
config.read(os.path.join(CONFIG_PATH, 'alloa.conf'))

ALLOCATION_PROFILE_FILENAME = f'allocation_profile_{DATE}.txt'
ALLOCATION_FILENAME = f'allocation_{DATE}.csv'

# Path for storing temporary files
INPUT_FILES = config.get('temporary_files', 'input_files').replace('\'', '')
OUTPUT_FILES = config.get('temporary_files', 'output_files').replace('\'', '')

OUTPUT_FILES_PATH = os.path.abspath(
    os.path.join(CURRENT, os.pardir, OUTPUT_FILES)
)
os.makedirs(OUTPUT_FILES_PATH, exist_ok=True)

ALLOCATION_PROFILE_PATH = os.path.abspath(
    os.path.join(CURRENT, os.pardir, OUTPUT_FILES, ALLOCATION_PROFILE_FILENAME)
)

ALLOCATION_PATH = os.path.abspath(
    os.path.join(CURRENT, os.pardir, OUTPUT_FILES, ALLOCATION_FILENAME)
)

MAIN_ALLOCATION_INFO = config.items('main_allocation_data')
NUMBER_OF_LEVELS = int(MAIN_ALLOCATION_INFO[0][1])
LEVEL_FILES = {
    int(x[0][5]): x[1].replace('\'', '') for x in MAIN_ALLOCATION_INFO
    if x[0].endswith('data')
}
LEVEL_PATHS_DICTIONARY = {
    i: os.path.abspath(os.path.join(
        CURRENT, os.pardir, INPUT_FILES, LEVEL_FILES[i])
    ) for i in LEVEL_FILES
}
LEVEL_PATHS = [
    p[1] for p in sorted(
        LEVEL_PATHS_DICTIONARY.items(), key=lambda x: x[0]
    )
]

LEVEL4_ALLOCATION = config.get(
    'second_supervisor_allocation', 'level4_allocation'
).replace('\'', '')
LEVEL4_DATA = config.get(
    'second_supervisor_allocation', 'level4_data'
).replace('\'', '')
LEVEL4_PATH = os.path.abspath(
    os.path.join(CURRENT, os.pardir, INPUT_FILES, LEVEL4_DATA)
)

WEIGHTED_HIERARCHIES = int(
    config.get('optimisation_depth', 'weighted_hierarchies')
)
