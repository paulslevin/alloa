'''Module for classes/functions related to costs.'''
from utils.enums import GraphElement

class SPACosts(object):
    '''Costs for student project allocation as described in the paper.'''

    def __init__(self, graph):
        self.graph = graph

    def exponent(self, node1, node2):
        agent1, agent2 = node1.agent, node2.agent

        # Get rank of agent2 in agent1's preferences.
        term = agent1.preference_position(agent2)

        # Get all hierarchies above agent1's level, excluding the final level.
        intermediate_hierarchies = self.graph.intermediate_hierarchies(node1)

        # Sum the maximal rank at each of the intermediate hierarchies.
        _sum = sum(
            hierarchy.max_preferences_length for hierarchy in intermediate_hierarchies
        )
        return term - 1 + _sum

    def cost(self, node1, node2):
        exponent = self.exponent(node1, node2)
        return (self.graph.min_upper_capacity_sum + 1) ** exponent
