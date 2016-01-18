import settings

from copy import deepcopy


# helper functions
def get_integer(choice):
    assert ":" in choice
    return int(choice[:choice.index(":")])


def csv_to_results(csv_file, delimiter):
    opened_file = open(csv_file, "r")
    results, count = [], 0
    for line in opened_file.readlines():
        stripped_line = line.strip()
        results.append([str(count)] + stripped_line.split(delimiter))
        count += 1
    opened_file.close()
    return results


def results_to_id(results):
    return dict(
            (result[1], index + 1) for index, result in enumerate(results[1:]))


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


def max_preference_length(preferences):
    return max(len(preference[2:]) for preference in preferences)


def chosen(preference, level):
    idx = 3
    if level == 2:
        idx = 2
    return preference[idx:]


# Convert csv files to lists
results1 = csv_to_results(settings.LEVEL1_PATH, settings.LEVEL1_DELIMITER)
results2 = csv_to_results(settings.LEVEL2_PATH, settings.LEVEL2_DELIMITER)
results3 = csv_to_results(settings.LEVEL3_PATH, settings.LEVEL3_DELIMITER)

# Create dictionaries that assign to each agent a number
level1_id = results_to_id(results1)
level2_id = results_to_id(results2)
level3_id = results_to_id(results3)

# Create lists that store the data in the format needed
level1_preferences = results_to_preferences1(results1)
level2_preferences = results_to_preferences2(results2, level3_id)

level3_capacities = results_to_capacities(results3)

# Count the number of agents in each hierarchy and print them out
level1_number = len(level1_id)
level2_number = len(level2_id)
level3_number = len(level3_id)

# Determine the maximal length of preference lists at levels 1 and 2

max1 = max_preference_length(level1_preferences)
max2 = max_preference_length(level2_preferences)

# Determine the level 2 agents that were chosen by level 1 agents
# so that we avoid unnecessary analysis

level2_all_occurrences = sum(
        (chosen(preference, 1) for preference in level1_preferences), [])

level2_chosen_all = set(level2_all_occurrences)
level1_preference_count = sorted(level2_chosen_all,
                                 key=lambda n: level2_all_occurrences.count(n))


# Determine the level 3 agents that were chosen by level 2 agents that
# were chosen by level 1 agents.

level3_chosen_all = set().union(
        *(chosen(level2_preferences[choice - 1], 2) for choice in
          level2_chosen_all))

level2_chosen_number = len(level2_chosen_all)
level3_chosen_number = len(level3_chosen_all)
