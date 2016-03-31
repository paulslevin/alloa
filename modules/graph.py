import networkx as nx
import sys


class AgentNode(object):
    def __init__(self, agent, polarity):
        self.agent = agent
        self.polarity = polarity

    def __repr__(self):
        return str(self.agent) + "(" + self.polarity + ")"


class AllocationGraph(nx.DiGraph):
    def __init__(self, block_list):
        super(AllocationGraph, self).__init__()
        self.blocks = block_list
        # should be enums
        self.source = "SOURCE"
        self.sink = "SINK"
        self.first_block = block_list[0]
        self.last_block = block_list[-1]
        self.hierarchies = [block.hierarchy for block in self.blocks]
        self.first_level_agents = self.hierarchies[0].agents
        self.first_level = self.hierarchies[0].level
        self.last_level = self.hierarchies[-1].level
        self.flow = None
        self.flow_cost = None
        self.max_flow = None
        self.simple_flow = None
        self.allocation = []

    def __str__(self):
        return "Graph with {} blocks".format(len(self.blocks))

    def populate_edges_from_source(self):
        for node in self.first_block.positive_agent_nodes():
            self.add_edge(self.source, node, weight=0)

    def populate_internal_edges(self):
        for block in self.blocks:
            weight = nx.get_edge_attributes(block, "weight")
            capacity = nx.get_edge_attributes(block, "capacity")
            for edge in block.edges():
                self.add_edge(edge[0], edge[1],
                              weight=weight[edge],
                              capacity=capacity[edge])

    def populate_edges_to_sink(self):
        for node in self.last_block.negative_agent_nodes():
            self.add_edge(node, self.sink, weight=0)

    def glue_blocks(self, block1, block2, cost_function):
        for agent in block1.preferred_agents:
            for preference in agent.preferences:
                out_node = block1.agent_to_negative_node(agent)
                in_node = block2.agent_to_positive_node(preference)
                self.add_edge(out_node,
                              in_node,
                              weight=cost_function(agent, preference))

    def setup_graph(self, *costs):
        self.populate_edges_from_source()
        self.populate_edges_to_sink()
        self.populate_internal_edges()
        for i, block in enumerate(self.blocks[1:]):
            cost = costs[i]
            self.glue_blocks(self.blocks[i], block, cost)

    def set_flow(self):
        try:
            self.flow = nx.max_flow_min_cost(self, self.source, self.sink)
            self.flow_cost = nx.cost_of_flow(self, self.flow)
            self.max_flow = nx.maximum_flow(self, self.source, self.sink)[0]
        except nx.NetworkXUnfeasible:
            print 'Allocation satisfying the lower bounds is not possible.'
            print 'Try reducing lower bounds.'
            sys.exit(1)
        except nx.NetworkXError:
            print "The input graph is not directed or not connected."
            print "Please check the data:"
            print "e.g. if all the choices on the level 1 list are" \
                  " included in the level 2 list and same for levels 2, 3."
            sys.exit(1)
        except nx.NetworkXUnbounded:
            print "Allocation is not possible because some upper capacity" \
                  "bounds at level 1 have not been set up. Please check " \
                  "the data."
            sys.exit(1)

    def simplify_flow(self):
        positives = {k.agent: v for k, v in self.flow.items() if
                     isinstance(k, AgentNode) and k.polarity == "-"}
        for k in positives:
            positives[k] = {k.agent: v for k, v in positives[k].items() if
                            isinstance(k, AgentNode) and v}
        self.simple_flow = {k: v for k, v in positives.items() if positives[k]}

    def get_single_agent_allocation(self, agent):
        if agent.level == self.last_level:
            return [agent]
        next_agent = next(self.simple_flow[agent].iterkeys())
        if self.simple_flow[agent][next_agent] == 1:
            del self.simple_flow[agent][next_agent]
        else:
            self.simple_flow[agent][next_agent] -= 1
        return [agent] + self.get_single_agent_allocation(next_agent)

    def allocate(self):
        matrix = [self.get_single_agent_allocation(agent) for
                  agent in self.first_level_agents]
        for row in matrix:
            row += [row[i].preference_position(agent) for i, agent in
                    enumerate(row[1:])]
        self.allocation = matrix


class Block(nx.DiGraph):
    def __init__(self, hierarchy, preferred_agents):
        super(Block, self).__init__()
        self.hierarchy = hierarchy
        self.level = hierarchy.level
        self.in_nodes = []
        self.out_nodes = []
        self.preferred_agents = preferred_agents
        self.positive_dict = {}
        self.negative_dict = {}

    def __repr__(self):
        return "BLOCK_{}".format(self.level)

    def __str__(self):
        return "BLOCK_{}".format(self.level)

    def agents_to_nodes(self):
        for agent in self.preferred_agents:
            positive_node = AgentNode(agent, "+")
            negative_node = AgentNode(agent, "-")
            self.positive_dict[agent] = positive_node
            self.negative_dict[agent] = negative_node

    def generate_agent_nodes(self):
        self.agents_to_nodes()
        for agent in self.preferred_agents:
            demand = agent.upper_capacity()
            out_node = self.agent_to_positive_node(agent)
            in_node = self.agent_to_negative_node(agent)
            capacity = agent.capacity_difference()
            self.add_node(out_node, demand=demand)
            self.add_node(in_node, demand=-demand)
            self.add_edge(out_node,
                          in_node,
                          capacity=capacity,
                          weight=0)

    def agent_to_positive_node(self, agent):
        return self.positive_dict[agent]

    def positive_agent_nodes(self):
        # Keep these in order
        return [self.positive_dict[agent] for agent in self.preferred_agents]

    def agent_to_negative_node(self, agent):
        return self.negative_dict[agent]

    def negative_agent_nodes(self):
        return [self.negative_dict[agent] for agent in self.preferred_agents]
