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
    for i, capacity in enumerate(level1_capacities):
        demand = capacity[1]
        graph.add_node(i + 1, demand=demand)
        graph.add_node(i + 1 + level1_number, demand=-demand)


# level 2 node demands + AND -
def add_nodes2(graph):
    for choice in level2_chosen_all:
        # to make sure we don't overwrite an existing node
        node_value = choice + level1_number * 2
        demand = level2_capacities[choice - 1][1]

        graph.add_node(node_value, demand=demand)
        graph.add_node(node_value + level2_number, demand=-demand)


# level 3 node demands + AND -
def add_nodes3(graph):
    for choice in level3_chosen_all:
        node_value = choice + level1_number * 2 + level2_number * 2
        demand = level3_capacities[choice - 1][1]
        graph.add_node(node_value, demand=demand)
        graph.add_node(node_value + level3_number, demand=-demand)


# Add edges from source to each level 1 agent
# No need for randomisation!
def add_edges_from_source(graph):
    for i in range(level1_number):
        graph.add_edge(SOURCE, i + 1, weight=0)


def add_level1_duplicate_edges(graph):
    for i, choice in enumerate(level1_capacities):
        graph.add_edge(i + 1,
                       i + 1 + level1_number,
                       capacity=choice[2] - choice[1],
                       weight=0)


def add_level1_to_level2_edges(graph):
    for i in range(level1_number):
        for j, choice in enumerate(chosen(i + 1, level1_preferences)):
            weight = min(WEIGHTED_HIERARCHIES, 1) * (
                level1_number ** (j + (WEIGHTED_HIERARCHIES - 1) * (max2 - 1)))
            graph.add_edge(i + 1 + level1_number,
                           choice + level1_number * 2,
                           weight=weight)


def add_level2_duplicate_edges(graph):
    for choice in level2_chosen_all:
        out_node = choice + level1_number * 2
        in_node = out_node + level2_number
        level2_agent = level2_capacities[choice - 1]
        capacity = level2_agent[2] - level2_agent[1]
        graph.add_edge(out_node,
                       in_node,
                       capacity=capacity,
                       weight=0)


def add_level2_to_level3_edges(graph):
    cost_factor = {0: 0, 1: 0, 2: level1_number}[WEIGHTED_HIERARCHIES]
    for choice2 in level2_chosen_all:
        out_node = choice2 + level1_number * 2 + level2_number
        for j, choice3 in enumerate(chosen(choice2, level2_preferences)):
            in_node = choice3 + level1_number * 2 + level2_number * 2
            graph.add_edge(out_node,
                           in_node,
                           weight=cost_factor ** j)


def add_level3_duplicate_edges(graph):
    # This is near identical to level2
    for choice in level3_chosen_all:
        out_node = choice + level1_number * 2 + level2_number * 2
        in_node = out_node + level3_number
        level3_agent = level3_capacities[choice - 1]
        capacity = level3_agent[2] - level3_agent[1]
        graph.add_edge(out_node,
                       in_node,
                       capacity=capacity,
                       weight=0)


def add_level3_to_sink_edges(graph):
    for choice in level3_chosen_all:
        node_value = choice + 2 * (
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


try:
    max_flow_min_cost = nx.max_flow_min_cost(H, 0, SINK)
    flow_cost = nx.cost_of_flow(H, max_flow_min_cost)
    max_flow = nx.maximum_flow(H, 0, SINK)[0]
    for e in max_flow_min_cost:
        print e, max_flow_min_cost[e]

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
