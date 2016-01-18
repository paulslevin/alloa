import sys
import networkx as nx
from manipulations import *
from settings import WEIGHTED_HIERARCHIES

SOURCE = 0
SINK = 2 * (level1_number + level2_number + level3_number) + 1


# this is inefficient because we keep generating these iterators over and
# over

# level 1 node demands + AND -
def add_nodes1(graph):
    for i, preference in enumerate(level1_preferences):
        demand = int(preference[1])
        graph.add_node(i + 1, demand=demand)
        graph.add_node(i + 1 + level1_number, demand=-demand)


# level 2 node demands + AND -
def add_nodes2(graph):
    for choice in level2_chosen_all:
        # to make sure we don't overwrite an existing node
        node_value = int(choice) + level1_number * 2
        demand = int(level2_preferences[choice - 1][0])
        graph.add_node(node_value, demand=demand)
        graph.add_node(node_value + level2_number, demand=-demand)


# level 3 node demands + AND -
def add_nodes3(graph):
    for choice in level3_chosen_all:
        node_value = int(choice) + level1_number * 2 + level2_number * 2
        demand = int(level3_capacities[choice - 1][0])
        # print "+ node is", node_value,
        # print "- node is", node_value + level3_number
        graph.add_node(node_value, demand=demand)
        graph.add_node(node_value + level3_number, demand=-demand)


# Add edges from source to each level 1 agent
# No need for randomisation!
def add_edges_from_source(graph):
    for i in range(level1_number):
        graph.add_edge(0, i + 1, weight=0)


def add_level1_duplicate_edges(graph):
    for i, choice in enumerate(level1_preferences):
        graph.add_edge(i + 1,
                       i + 1 + level1_number,
                       capacity=int(choice[2]) - int(choice[1]),
                       weight=0)


def add_level1_to_level2_edges(graph):
    for i, preference in enumerate(level1_preferences):
        for j, choice in enumerate(chosen(preference, 1)):
            weight = min(WEIGHTED_HIERARCHIES, 1) * (
                level1_number ** (j + (WEIGHTED_HIERARCHIES - 1) * (max2 - 1)))
            graph.add_edge(i + 1 + level1_number,
                           int(choice) + level1_number * 2,
                           weight=weight)


def add_level2_duplicate_edges(graph):
    for choice in level2_chosen_all:
        out_node = int(choice) + level1_number * 2
        in_node = out_node + level2_number
        level2_agent = level2_preferences[choice - 1]
        capacity = int(level2_agent[1]) - int(level2_agent[0])
        graph.add_edge(out_node,
                       in_node,
                       capacity=capacity,
                       weight=0)


def add_level2_to_level3_edges(graph):
    cost_factor = {0: 0, 1: 0, 2: level1_number}[WEIGHTED_HIERARCHIES]
    for choice2 in level2_chosen_all:
        out_node = int(choice2) + level1_number * 2 + level2_number
        for j, choice3 in enumerate(chosen(level2_preferences[choice2 - 1], 2)):
            in_node = int(choice3) + level1_number * 2 + level2_number * 2
            graph.add_edge(out_node,
                           in_node,
                           weight=cost_factor ** j)


def add_level3_duplicate_edges(graph):
    # This is near identical to level2
    for choice in level3_chosen_all:
        out_node = int(choice) + level1_number * 2 + level2_number * 2
        in_node = out_node + level3_number
        level3_agent = level3_capacities[choice - 1]
        capacity = int(level3_agent[1]) - int(level3_agent[0])
        graph.add_edge(out_node,
                       in_node,
                       capacity=capacity,
                       weight=0)


def add_level3_to_sink_edges(graph):
    for choice in level3_chosen_all:
        node_value = int(choice) + 2 * (
            level1_number + level2_number) + level3_number
        graph.add_edge(node_value, SINK, weight=0)


H = nx.DiGraph()

add_nodes1(H)
add_nodes2(H)
add_nodes3(H)
add_edges_from_source(H)
add_level1_duplicate_edges(H)
add_level1_to_level2_edges(H)
add_level2_duplicate_edges(H)
add_level2_to_level3_edges(H)
add_level3_duplicate_edges(H)
add_level3_to_sink_edges(H)


# For some reason this extra edge was added in the original code!
# H.add_edge(435, 469, weight=0)

try:
    max_flow_min_cost = nx.max_flow_min_cost(H, 0, SINK)
    flow_cost = nx.cost_of_flow(H, max_flow_min_cost)
    max_flow = nx.maximum_flow(H, 0, SINK)[0]

    for d in max_flow_min_cost.items():
        print d

    print max({193: 0, 232: 0, 243: 1, 252: 0, 189: 0, 190: 0, 191: 0}, key=lambda x: {193: 0, 232: 0, 243: 1, 252: 0, 189: 0, 190: 0, 191: 0}[x] )
except nx.NetworkXUnfeasible:
    print 'Allocation satisfying the lower bounds is not possible.'
    print 'Try reducing lower bounds.'
    sys.exit(1)
except nx.NetworkXError:
    print "The input graph is not directed or not connected."
    print "Please check the data:"
    print "e.g. if all the choices on the level 1 list are included in the"
    print "level 2 list and same for levels 2, 3."
    sys.exit(1)
except nx.NetworkXUnbounded:
    print "Allocation is not possible because some upper capacity bounds at"
    print "level 1 have not been set up. Please check the data."
    sys.exit(1)
