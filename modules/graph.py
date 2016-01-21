import networkx as nx


class SuperNode(object):
    def __init__(self, agent, polarity):
        self.agent = agent
        self.polarity = polarity


class AllocationGraph(nx.DiGraph):
    def __init__(self):
        super(AllocationGraph, self).__init__()


class Block(AllocationGraph):
    def __init__(self, hierarchy):
        super(Block, self).__init__()
        self.level = hierarchy.level
        self.in_nodes = []
        self.out_nodes = []

    def generate_super_nodes(self):
        pass
    #
    # def generate_in_nodes(self):
    #
    #
    #     for agent in hierarchy.agents:
    #         demand = agent.upper_capacity()
    #         self.add_node(agent, demand=demand)
    #         self.add_node(agent, demand=-demand)

from agents import Agent, Hierarchy

hierarchy = Hierarchy(1)
a = Agent(1, hierarchy)

b = Block(hierarchy)

c = a
b.add_node(a)
print b.nodes()
b.add_node(c)
print b.nodes()