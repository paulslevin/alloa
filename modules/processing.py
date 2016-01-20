import csv
from allocation_graph_networkx import *
from manipulations import *


# helper functions
def level1_to_level2(agent, flow):
    nodes = flow[agent + level1_number]
    return max(nodes, key=lambda m: nodes[m]) - 2 * level1_number


def level2_to_level3(agent, flow):
    nodes = flow[agent + level1_number * 2 + level2_number]
    return [node - level1_number * 2 - level2_number * 2 for node in nodes if
            nodes[node]]


def get_preferences_and_counts(agent, flow):
    name, preferences, counts1, counts2 = id_level1[agent], [], {}, {}
    higher_agent = level1_to_level2(agent, flow)
    higher_name = id_level2[higher_agent]
    line = "{},{},".format(name, higher_name)
    for even_higher_agent in level2_to_level3(higher_agent, flow):
        even_higher_name = id_level3[even_higher_agent]
        preference1 = new_preference(agent,
                                     higher_agent,
                                     level1_preferences)
        preference2 = new_preference(higher_agent,
                                     even_higher_agent,
                                     level2_preferences)
        if preference1 != "N/A":
            if preference1 in counts1:
                counts1[preference1] += 1
            else:
                counts1[preference1] = 1
        if preference2 != "N/A":
            if preference2 in counts2:
                counts2[preference2] += 1
            else:
                counts2[preference2] = 1
        new_line = line + "{},{},{}".format(even_higher_name,
                                            preference1,
                                            preference2)
        preferences.append(new_line)
    return preferences, counts1, counts2

# write allocation results
def write_and_get_counts(flow):
    end_count1, end_count2 = {}, {}
    for agent in range(1, level1_number + 1):
        preferences, count1, count2 = get_preferences_and_counts(agent, flow)
        for i in count1:
            if i in end_count1:
                end_count1[i] += count1[i]
            else:
                end_count1[i] = count1[i]
        for i in count2:
            if i in end_count2:
                end_count2[i] += count2[i]
            else:
                end_count2[i] = count2[i]
        writer.writerow(preferences)
    return end_count1, end_count2


allocation_profile = open(settings.ALLOCATION_PROFILE_PATH, "wb")
allocation = open(settings.ALLOCATION_PATH, "wb")

writer = csv.writer(allocation, delimiter="\n")


# write allocation profile
preference_count1, preference_count2 = write_and_get_counts(max_flow_min_cost)

initial_info = [
    "Total number of assigned level 1 agents is {}".format(max_flow),
    "Total cost of assignment is {}".format(flow_cost),
    "",
    "Level 1 Preference Count"
    "",
]

next_info = [
    "Number of level 2 agents that where choice #{}: {}".format(
            j, preference_count1.get(j, "N/A")
    ) for j in range(1, 8)
] + ["", "Level 2 Preference Count"]

last_info = [
    "Number of level 3 agents that where choice #{}: {}".format(
            j, preference_count2.get(j, "N/A")
    ) for j in range(1, 4)
]

profile_writer = csv.writer(allocation_profile, delimiter="\n")
profile_writer.writerow(initial_info + next_info + last_info)

allocation_profile.close()
allocation.close()
