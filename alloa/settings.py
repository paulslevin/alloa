# Import settings from configuration file
# Make configuration changes in alloa.conf (for security reasons)

import ConfigParser

config = ConfigParser.ConfigParser()
config.read("alloa.conf")

# would probably be better here to allow an arbitrary number of levels

LEVEL1_DATA = config.get("main_allocation_data", "level1_data")
USER_DELIMITER1 = config.get("main_allocation_data", "user_delimiter1")
LEVEL1 = config.get("output_files", "level1")

LEVEL2_DATA = config.get("main_allocation_data", "level2_data")
USER_DELIMITER2 = config.get("main_allocation_data", "user_delimiter2")
LEVEL2 = config.get("output_files", "level2")

LEVEL3_DATA = config.get("main_allocation_data", "level3_data")
USER_DELIMITER3 = config.get("main_allocation_data", "user_delimiter3")
LEVEL3 = config.get("output_files", "level3")

LEVEL4_ALLOCATION = config.get("second_supervisor_allocation",
                               "level4_allocation")
LEVEL4_DATA = config.get("second_supervisor_allocation", "level4_data")
USER_DELIMITER4 = config.get("second_supervisor_allocation", "user_delimiter4")
LEVEL4 = config.get("output_files", "level4")


# Path for storing temporary files
WORKING_FILES=config.get("temporary_files", "working_files")

# Delete temporary files at completion (Yes/No)
delete_files='No'


WEIGHTED_HIERARCHIES = config.get("optimisation_depth", "weighted_hierarchies")
