# Import settings from configuration file
# Make configuration changes in alloa.conf (for security reasons)

import ConfigParser
import os
import time

DATE = time.strftime("%d%m%y")
CURRENT = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(CURRENT,
                                           os.pardir))

config = ConfigParser.RawConfigParser()
config.read(os.path.join(CONFIG_PATH, "alloa.conf"))

ALLOCATION_PROFILE_FILENAME = "allocation_profile_" + DATE + ".csv"
ALLOCATION_FILENAME = "allocation_" + DATE + ".csv"

# would probably be better here to allow an arbitrary number of levels
# Remove the extra quotes using replace

# Path for storing temporary files

WORKING_FILES = config.get("temporary_files", "working_files").replace("'", "")
WORKING_PATH = os.path.abspath(os.path.join(CURRENT,
                                            os.pardir,
                                            os.path.normpath(WORKING_FILES)))

ALLOCATION_PROFILE_PATH = os.path.abspath(
        os.path.join(CURRENT,
                     os.pardir,
                     WORKING_FILES,
                     ALLOCATION_PROFILE_FILENAME)
)

ALLOCATION_PATH = os.path.abspath(
        os.path.join(CURRENT,
                     os.pardir,
                     WORKING_FILES,
                     ALLOCATION_FILENAME)
)

MAIN_ALLOCATION_INFO = config.items("main_allocation_data")
NUMBER_OF_LEVELS = int(MAIN_ALLOCATION_INFO[0][1])
LEVEL_FILES = {int(x[0][5]): x[1].replace("'", "") for x in MAIN_ALLOCATION_INFO
               if x[0].endswith('data')}
LEVEL_PATHS_DICTIONARY = {i: os.path.abspath(os.path.join(CURRENT,
                                                          os.pardir,
                                                          WORKING_FILES,
                                                          LEVEL_FILES[i])
                                             ) for i in LEVEL_FILES}
LEVEL_PATHS = [p[1] for p in sorted(LEVEL_PATHS_DICTIONARY.items(), key=lambda (k, v): k)]

LEVEL1_DATA = config.get("main_allocation_data", "level1_data").replace("'", "")
LEVEL1_PATH = os.path.abspath(os.path.join(CURRENT,
                                           os.pardir,
                                           WORKING_FILES,
                                           LEVEL1_DATA))

LEVEL1_DELIMITER = config.get("main_allocation_data",
                              "level1_delimiter").replace("'", "")
LEVEL1_NAME = config.get("output_files", "level1").replace("'", "")

LEVEL2_DATA = config.get("main_allocation_data", "level2_data").replace("'", "")
LEVEL2_PATH = os.path.abspath(os.path.join(CURRENT,
                                           os.pardir,
                                           WORKING_FILES,
                                           LEVEL2_DATA))
LEVEL2_DELIMITER = config.get("main_allocation_data",
                              "level2_delimiter").replace("'", "")
LEVEL2_NAME = config.get("output_files", "level2").replace("'", "")

LEVEL3_DATA = config.get("main_allocation_data", "level3_data").replace("'", "")
LEVEL3_PATH = os.path.abspath(os.path.join(CURRENT,
                                           os.pardir,
                                           WORKING_FILES,
                                           LEVEL3_DATA))
LEVEL3_DELIMITER = config.get("main_allocation_data",
                              "level3_delimiter").replace("'", "")
LEVEL3_NAME = config.get("output_files", "level3").replace("'", "")

LEVEL4_ALLOCATION = config.get("second_supervisor_allocation",
                               "level4_allocation").replace("'", "")

LEVEL4_DATA = config.get("second_supervisor_allocation",
                         "level4_data").replace("'", "")
LEVEL4_PATH = os.path.abspath(os.path.join(CURRENT,
                                           os.pardir,
                                           WORKING_FILES,
                                           LEVEL4_DATA))
LEVEL4_DELIMITER = config.get("main_allocation_data",
                              "level1_delimiter").replace("'", "")
LEVEL4_NAME = config.get("output_files", "level4").replace("'", "")

# Delete temporary files at completion (Yes/No)
delete_files = 'No'

WEIGHTED_HIERARCHIES = int(config.get("optimisation_depth",
                                      "weighted_hierarchies"))
