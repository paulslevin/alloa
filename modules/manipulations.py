import settings
import codecs
import csv
import itertools
from copy import deepcopy


# helper functions
# in case the 'csv file' is really a unicode .txt file
def remove_bom(line):
    return line[3:] if line.startswith(codecs.BOM_UTF8) else line


def new_csv_to_results(csv_file, delimiter):
    opened_file = open(csv_file, "r")
    reader = csv.reader(opened_file,
                        delimiter=delimiter,
                        quoting=csv.QUOTE_NONE)
    results = [[x.strip() for x in row if x] for row in reader]
    results[0][0] = remove_bom(results[0][0])
    return results


# delete
def get_integer(choice):
    assert ":" in choice
    return int(choice[:choice.index(":")])


# delete
def csv_to_results(csv_file, delimiter):
    opened_file = open(csv_file, "r")
    results, count = [], 0
    for line in opened_file.readlines():
        stripped_line = line.strip()
        results.append([str(count)] + stripped_line.split(delimiter))
        count += 1
    opened_file.close()
    return results


def new_results_to_preferences(results, lower_id, higher_id):
    return [[lower_id[x[0]]] + [higher_id[y] for y in x[3:]] for x in
            results[1:]]


def new_results_to_capacities(results, lower_id):
    return [[lower_id[x[0]]] + [int(x[1]), int(x[2])] for x in results[1:]]


def results_to_id(results):
    return dict((result[0], index) for index, result in enumerate(results))


def results_to_preferences1(results):
    preference_list = []
    results_copy = deepcopy(results)[1:]
    for result in results_copy:
        numbers = [get_integer(choice) for choice in result[4:]]
        next_list = [int(result[0])] + result[2:4] + numbers
        preference_list.append(next_list)
    return preference_list


def results_to_preferences2(results, ids):
    preference_list = []
    results_copy = deepcopy(results)[1:]
    for result in results_copy:
        id_list = [ids[agent] for agent in result[4:]]
        next_list = result[2:4] + id_list
        preference_list.append(next_list)
    return preference_list


def results_to_capacities(results):
    return [result[2:] for result in results[1:]]


# unused
def max_preference_length(preferences):
    return max(len(preference[3:]) for preference in preferences)


def chosen(preference, level):
    idx = 3
    if level == 2:
        idx = 2
    return preference[idx:]


# memoization
def new_chosen(*args):
    if len(args) == 1:
        return set(itertools.chain.from_iterable(
                preference[1:] for preference in args[0]
        ))
    highest = args[-1]
    return set(itertools.chain.from_iterable(
            preference[1:] for preference in highest if
            preference[0] in new_chosen(*args[:1])
    ))


def preference(level, agent, higher_agent):
    i, preferences = 0, []
    if level == 1:
        preferences = level1_preferences
        i = 3
        if settings.WEIGHTED_HIERARCHIES == 0:
            return "N/A"
    elif level == 2:
        preferences = level2_preferences
        i = 2
        if settings.WEIGHTED_HIERARCHIES in {0, 1}:
            return "N/A"
    if higher_agent in preferences[agent - 1][i:]:
        return str(preferences[agent - 1][i:].index(higher_agent) + 1)
    else:
        return None


# Convert csv files to lists
results1 = new_csv_to_results(settings.LEVEL1_PATH, ",")
results2 = new_csv_to_results(settings.LEVEL2_PATH, ",")
results3 = new_csv_to_results(settings.LEVEL3_PATH, ",")
level1_number = len(results1) - 1
level2_number = len(results2) - 1
level3_number = len(results3) - 1

# Create dictionaries that assign to each agent a number
level1_id = results_to_id(results1)
level2_id = results_to_id(results2)
level3_id = results_to_id(results3)

# Inverse dictionaries
id_level1 = dict((v, k) for k, v in level1_id.items())
id_level2 = dict((v, k) for k, v in level2_id.items())
id_level3 = dict((v, k) for k, v in level3_id.items())

# Create lists that store the data in the format needed
# Final agent has no preferences as yet
level1_preferences = new_results_to_preferences(results1, level1_id, level2_id)
level2_preferences = new_results_to_preferences(results2, level2_id, level3_id)

# Get capacities for each agent
level1_capacities = new_results_to_capacities(results1, level1_id)
level2_capacities = new_results_to_capacities(results2, level2_id)
level3_capacities = new_results_to_capacities(results3, level3_id)

# Determine the maximal length of preference lists at levels 1 and 2
max1 = max_preference_length(results1)
max2 = max_preference_length(results2)

# Determine agents of hierarchy > 1 that were actually chosen
level2_chosen_all = new_chosen(level1_preferences)
level3_chosen_all = new_chosen(level1_preferences, level2_preferences)
level2_chosen_number = len(level2_chosen_all)
level3_chosen_number = len(level3_chosen_all)
