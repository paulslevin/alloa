'''Module for classes/functions related to costs.'''
from utils.enums import GraphElement

class SPACosts(object):
    '''Costs for student project allocation as described in the paper.'''

    def __init__(self, graph):
        self.graph = graph
        self.total = self.graph.number_of_hierarchies

    def exponent(self, node1, node2):
        level1, level2 = node1.level, node2.level
        agent1, agent2 = node1.agent, node2.agent

        term = agent1.preference_position(agent2)
        upper_hierarchies = self.graph.hierarchies[node2.level: self.total - 1]
        _sum = sum(
            hierarchy.max_preferences_length for hierarchy in upper_hierarchies
        )
        return term - 1 + _sum

    def cost(self, node1, node2):
        exponent = self.exponent(node1, node2)
        return (self.graph.min_upper_capacity_sum + 1) ** exponent
