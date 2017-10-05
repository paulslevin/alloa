'''Module for constructing a directed graph (network) to model the allocation.
Hierarchies are converted into subgraphs (HierarchyGraph) of the main allocation
graph (AllocationGraph). Edges between the subgraphs represent the preferences 
of the agents between each hierarchy level.

Example (cont. from agents.py)
------------------------------
Paul, Michael and Patricia are level 1 agents with preferences on level 2:
Paul:     [Spheres, Circles, Lines]
Michael:  [Circles, Algebra, Cones]
Patricia: [Triangles, Mechanics, Algebra]
Then the allocation graph looks like
             _________                __________
SOURCE------|Paul     |-------\------|Spheres   |------SINK
   |        |---------|     ___\_____|----------|      /
   \--------|Michael  |----/    \----|Circles   |-----/
    \       |---------|    \     \   |----------|    /
     \------|Patricia |-\   \     \--|Lines     |---/
            |_________|  \   \_______|----------|   |
                          \---\------|Algebra   |---/
                           \   \     |----------|   |
                            \   \----|Cones     |---/
                             \       |----------|   |
                              \------|Triangles |---/
                               \     |----------|   |
                                \----|Mechanics |---/
                                     |__________|
'''
from   collections import OrderedDict
from   itertools import izip
from   agents import Agent, Hierarchy
import networkx as nx
import sys
from   utils.enums import GraphElement, Polarity
from   utils.parsers import parse_repr


POSITIVE=Polarity.POSITIVE
NEGATIVE=Polarity.NEGATIVE


class AgentNode(object):
    '''Agent nodes split into positive and negative component nodes. An edge is
    drawn between them when the graph is built.
    '''
    def __init__(self, agent, polarity):
        '''
        Parameters
        ----------
        agent: Agent
            Single Agent that this node represents (together with its opposite
            polarity pair).
        polarity: Polarity
            Either POSITIVE(+) or NEGATIVE(-).
        '''
        self.agent = agent
        self.polarity = polarity

    def __str__(self):
        return '{}({})'.format(self.agent, self.polarity)

    def __repr__(self):
        str_kwargs = ['agent={}'.format(str(self.agent)),
                      'polarity={}'.format(self.polarity) ]
        return parse_repr(self, str_kwargs)

    def __hash__(self):
        '''These objects are used as nodes in the graph, in particular they are
        used as dictionary keys. There only exists one agent with each id and
        level, so those keys plus polarity suffice as identifiers.
        '''
        return hash((self.agent.id, self.agent.level, self.polarity))

    def __eq__(self, other):
        '''These represent nodes on the allocation graph and are compared to
        other objects in the networkx module, so makes sense to define rich
        comparison operators. Also useful for testing.
        '''
        if not isinstance(other, self.__class__):
            return False
        return self.agent == other.agent and self.polarity == other.polarity

    def __neq__(self, other):
        if not isinstance(other, self.__class__):
            return True
        return not(self.agent == other.agent and self.polarity == other.polarity)
    
    @property
    def level(self):
        return self.agent.level


class HierarchyGraph(nx.DiGraph):
    '''Represent a hierarchy as a directed graph (network). The full allocation
    graph consists of these objects, glued together with edges. For each agent,
    split them into positive and negative agent nodes and draw an edge between
    these. The capacity of the edge represents the capacity of the agent. The
    rules are:

      1) edge capacity = agent upper capacity - agent lower capacity.
      2) positive node demand = agent lower capacity.
      3) negative node demand = agent lower capacity * (-1).
      
    Example
    -------
    Suppose project 'Spheres' has upper capacity 2 and lower capacity 1, meaning
    it must have either 1 or 2 students working on it. Then:
       capacity = upper_capacity - lower_capacity = 2 - 1 = 1.
       (+) demand = 1,  (-) demand = -1
            ________________________________________
           |  __________                __________  |
    ...--->| |Spheres(+)| -----------> |Spheres(-)| | --->...
           | | demand=1 |  capacity=1  | demand=-1| |
           |  ----------               -----------  |
            -----------------------------------------
    '''
    def __init__(self, hierarchy, agents):
        '''
        Parameters
        ----------
        hierarchy: Hierarchy
            The hierarchy we are modelling as a graph.
        agents: list of Agent
            Agents used to populate the graph. These don't necessarily have to
            be the same agents as those on the hierarchy -- there's no need to
            include agents that aren't preferred by anyone on the level beneath,
            for example.
        '''
        super(HierarchyGraph, self).__init__()
        self.hierarchy = hierarchy
        self.level = hierarchy.level
        self.agents = agents

        self._agent_positive_node_map = OrderedDict()
        self._agent_negative_node_map = OrderedDict()

    def __str__(self):
        return "HIERARCHY_GRAPH_{}".format(self.level)

    def __repr__(self):
        str_kwargs = ['hierarchy={}'.format(self.hierarchy)]
        if self.agents:
            agent_strs = [str(agent) for agent in self.agents]
            str_kwargs.append('agents={}'.format(agent_strs).replace("'",'') )
        return parse_repr(self, str_kwargs)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all([
            list(sorted(self.edges(data=True))) == list(sorted(other.edges(data=True))),
            self.hierarchy == other.hierarchy,
            self.agents == other.agents
        ])

    def __neq__(self, other):
        if not isinstance(other, self.__class__):
            return True
        return not all([
            list(sorted(self.edges(data=True))) == list(sorted(other.edges(data=True))),
            self.hierarchy == other.hierarchy,
            self.agents == other.agents
        ])

    def assign_agents_to_nodes(self):
        '''Construct two AgentNode objects for each agent, and update
        dictionary which keeps track of these.
        '''
        for agent in self.agents:
            positive_node = AgentNode(agent, POSITIVE)
            negative_node = AgentNode(agent, NEGATIVE)
            self._agent_positive_node_map[agent] = positive_node
            self._agent_negative_node_map[agent] = negative_node

    def generate_agent_nodes(self):
        '''Construct the AgentNodes for each edge and draw an edge between them.
        Set the capacity of the edge to be the difference between the agent's
        upper and lower capacity. Set demand to be (node polarity)*lower_capacity.
        '''
        for agent in self.agents:
            demand = agent.lower_capacity
            out_node = self.positive_node(agent)
            in_node = self.negative_node(agent)
            capacity = agent.capacity_difference
            self.add_node(out_node, demand=demand)
            self.add_node(in_node, demand=-demand)
            self.add_edge(out_node, in_node, capacity=capacity, weight=0)

    @classmethod
    def full_subgraph(cls, hierarchy, agents):
        '''Create graph with all agent nodes and edges set up.'''
        graph = cls(hierarchy, agents)
        graph.assign_agents_to_nodes()
        graph.generate_agent_nodes()
        return graph

    def positive_node(self, agent):
        '''Return positive node corresponding to the agent.'''
        return self._agent_positive_node_map[agent]

    @property
    def positive_agent_nodes(self):
        '''Return all positive agent nodes.'''
        # Keep these in order
        return [self._agent_positive_node_map[agent] for agent in self.agents]

    def negative_node(self, agent):
        '''Return negative node corresponding to the agent.'''
        return self._agent_negative_node_map[agent]

    @property
    def negative_agent_nodes(self):
        '''Return all negative agent nodes.'''
        return [self._agent_negative_node_map[agent] for agent in self.agents]


class AllocationGraph(nx.DiGraph):
    def __init__(self, subgraphs):
        '''
        Parameters
        ----------
        subgraphs: list HierarchyGraphs
            The hierarchy graphs are glued together by edges representing the
            preferences of each of their agents.
        '''
        super(AllocationGraph, self).__init__()
        self.subgraphs = subgraphs
        self.flow_cost = None
        self.max_flow = None
        self.simple_flow = None
        self.allocation = []

        self._source = None
        self._sink = None
        self.flow = None

    def __str__(self):
        return 'ALLOCATION_GRAPH({})'.format(len(self.subgraphs))
   
    def __repr__(self):
        str_kwargs = []
        if self.subgraphs:
            subgraph_strs = [str(subgraph) for subgraph in self.subgraphs]
            str_kwargs.append('subgraphs={}'.format(subgraph_strs).replace("'",'') )
        return parse_repr(self, str_kwargs)

    @property
    def level_nodes_map(self):
        sink_source_map = {0: [self.source],
                           self.number_of_hierarchies + 1: [self.sink]}
        map = {subgraph.level: list(subgraph.nodes) 
               for subgraph in self.subgraphs}
        return dict(map, **sink_source_map)

    @property
    def source(self):
        '''Cached property to generate source to avoid recreating objects.'''
        if not self._source:
            zero_hierarchy = Hierarchy(level=0)
            # Create source agent which equally prefers all level 1 agents.
            source_agent = Agent(id=1, hierarchy=zero_hierarchy,
                                 preferences=[self.first_level_agents],
                                 name=GraphElement.SOURCE)
            self._source = AgentNode(source_agent, POSITIVE)
        return self._source

    @property
    def sink(self):
        '''Cached property to generate sink to avoid recreating objects.'''
        if not self._sink:
            final_hierarchy = Hierarchy(level=self.number_of_hierarchies + 1)
            sink_agent = Agent(id=1, hierarchy=final_hierarchy,
                          name=GraphElement.SINK)
            # Each agent in the last hierarchy prefers the sink agent.
            for agent in self.last_level_agents:
                agent.preferences = [sink_agent]
            self._sink = AgentNode(sink_agent, NEGATIVE)
        return self._sink

    @property
    def first_subgraph(self):
        if self.subgraphs:
            return self.subgraphs[0]
        
    @property
    def last_subgraph(self):
        if self.subgraphs:
            return self.subgraphs[-1]

    @property
    def hierarchies(self):
        return [subgraph.hierarchy for subgraph in self.subgraphs]

    @property
    def number_of_hierarchies(self):
        return len(self.hierarchies)

    @property
    def first_level_agents(self):
        return self.hierarchies[0].agents

    @property
    def first_level(self):
        return self.hierarchies[0].level

    @property
    def last_level_agents(self):
        return self.hierarchies[-1].agents

    @property
    def last_level(self):
        return self.hierarchies[-1].level

    @property
    def min_upper_capacity_sum(self):
        capacity_sums = []
        for hierarchy in self.hierarchies:
            _sum = sum(agent.upper_capacity for agent in hierarchy)
            capacity_sums.append(_sum)
        return min(capacity_sums)

    def intermediate_hierarchies(self, node):
        '''Return all hierarchies strictly between the given node and the last
        hierarchy (non-inclusive).
        '''
        return self.hierarchies[node.level: -1]

    def add_edge_with_cost(self, out_node, in_node, cost):
        weight = cost(out_node, in_node)
        self.add_edge(out_node, in_node, weight=weight)

    def populate_edges_from_source(self, cost):
        for node in self.first_subgraph.positive_agent_nodes:
            self.add_edge_with_cost(self.source, node, cost)

    def populate_edges_to_sink(self, cost):
        for node in self.last_subgraph.negative_agent_nodes:
            self.add_edge_with_cost(node, self.sink, cost)

    def populate_internal_edges(self):
        for subgraph in self.subgraphs:
            self.add_edges_from(subgraph.edges(data=True))
        
    def glue(self, subgraph1, subgraph2, cost):
        for agent in subgraph1.agents:
            for preference in agent.preferences:

                # Handle preference ties.
                if isinstance(preference, Agent):
                    preference_list = [preference]
                elif isinstance(preference, list):
                    preference_list = preference

                for other_agent in preference_list:
                    out_node = subgraph1.negative_node(agent)
                    in_node  = subgraph2.positive_node(other_agent)
                    self.add_edge_with_cost(out_node, in_node, cost)
               
    def setup_graph(self, cost):
        self.populate_edges_from_source(cost)
        self.populate_edges_to_sink(cost)
        self.populate_internal_edges()
        for subgraph1, subgraph2 in izip(self.subgraphs, self.subgraphs[1:]):
            self.glue(subgraph1, subgraph2, cost)

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
                     isinstance(k, AgentNode) and k.polarity == NEGATIVE}
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
