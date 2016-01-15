# Import settings from configuration file
# Make configuration changes in alloa.conf (for security reasons)

import ConfigParser
import os

config = ConfigParser.RawConfigParser()
config.read("alloa.conf")

# would probably be better here to allow an arbitrary number of levels
# Remove the extra quotes using replace

# Path for storing temporary files

WORKING_FILES = config.get("temporary_files", "working_files").replace("'","")


LEVEL1_DATA = config.get("main_allocation_data", "level1_data").replace("'","")
LEVEL1_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ),
                                           os.pardir,
                                           WORKING_FILES,
                                           LEVEL1_DATA))
LEVEL1_DELIMITER = config.get("main_allocation_data",
                              "level1_delimiter").replace("'","")
LEVEL1_NAME = config.get("output_files", "level1").replace("'", "")

LEVEL2_DATA = config.get("main_allocation_data", "level2_data").replace("'","")
LEVEL2_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ),
                                           os.pardir,
                                           WORKING_FILES,
                                           LEVEL2_DATA))
LEVEL2_DELIMITER = config.get("main_allocation_data",
                              "level2_delimiter").replace("'","")
LEVEL2_NAME = config.get("output_files", "level2").replace("'","")

LEVEL3_DATA = config.get("main_allocation_data", "level3_data").replace("'","")
LEVEL3_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ),
                                           os.pardir,
                                           WORKING_FILES,
                                           LEVEL3_DATA))
LEVEL3_DELIMITER = config.get("main_allocation_data",
                              "level3_delimiter").replace("'","")
LEVEL3_NAME = config.get("output_files", "level3").replace("'","")

LEVEL4_ALLOCATION = config.get("second_supervisor_allocation",
                               "level4_allocation").replace("'","")

LEVEL4_DATA = config.get("second_supervisor_allocation",
                         "level4_data").replace("'","")
LEVEL4_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ),
                                           os.pardir,
                                           WORKING_FILES,
                                           LEVEL4_DATA))
LEVEL4_DELIMITER = config.get("main_allocation_data",
                              "level1_delimiter").replace("'","")
LEVEL4_NAME = config.get("output_files", "level4").replace("'","")


# Delete temporary files at completion (Yes/No)
delete_files='No'


WEIGHTED_HIERARCHIES = int(config.get("optimisation_depth",
                                      "weighted_hierarchies"))
