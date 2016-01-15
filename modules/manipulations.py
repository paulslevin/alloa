from copy import deepcopy


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


def results_to_preferences2(results, id):
    preference_list = []
    results_copy = deepcopy(results)[1:]
    for result in results_copy:
        id_list = [id[agent] for agent in result[4:]]
        next_list = result[2:4] + id_list
        preference_list.append(next_list)
    return preference_list


def results_to_capacities(results):
    return [result[2:] for result in results[1:]]


def max_preference_length(preferences):
    return  max(len(preference[2:]) for preference in preferences)