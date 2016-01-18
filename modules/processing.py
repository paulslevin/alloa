from allocation_graph_networkx import *
import networkx as nx
import time
import csv
import settings
import os
from manipulations import *



def level1_to_level2(agent, flow):
    nodes = flow[agent + level1_number]
    return max(nodes, key=lambda m: nodes[m]) - 2 * level1_number



def level2_to_level3(agent, flow):
    nodes = flow[agent + level1_number * 2 + level2_number]
    return [node for node in nodes if nodes[node]]

for i in range(1, 67):
    print i, level1_to_level2(i, max_flow_min_cost)

for i in level2_chosen_all:
    print i, level2_to_level3(i, max_flow_min_cost)

allocation_profile = open(settings.ALLOCATION_PROFILE_PATH, "wb")
info = [
    "Total number of assigned level 1 agents is {}".format(max_flow),
    "Total cost of assignment is {}".format(flow_cost),
    "",
    "Level 1 Preference Count"
    "",
]



writer = csv.writer(allocation_profile, delimiter="\n")
writer.writerow(info)




allocation_profile.close()