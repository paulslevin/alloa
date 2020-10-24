"""Module for constructing a directed graph (network) to model the allocation.
Hierarchies are converted into subgraphs (HierarchyGraph) of the main allocation
graph (AllocationGraph). Edges between the subgraphs represent the preferences 
of the agents between each hierarchy level.
"""
from __future__ import annotations

from collections import namedtuple, OrderedDict
from functools import total_ordering
from typing import Dict, Generator

import networkx as nx

from alloa.agents import Agent, Hierarchy, List, Optional
from alloa.costs import CostFunc
from alloa.utils.enums import GraphElement, Polarity
from alloa.utils.parsers import parse_repr

AllocationDatum = namedtuple('AllocationDatum', ['agent', 'rank'])


@total_ordering
class AgentNode:
    """Agent nodes split into positive and negative component nodes. An edge is
    drawn between them when the graph is built.
    """
    def __init__(self, agent: Agent, polarity: Polarity) -> None:
        """
        Parameters
        ----------
        agent:
            Single Agent that this node represents (together with its opposite
            polarity pair).
        polarity:
            Either POSITIVE(+) or NEGATIVE(-).
        """
        self.agent = agent
        self.polarity = polarity

    def __str__(self) -> str:
        return f'{self.agent}({self.polarity.value})'

    def __repr__(self) -> str:
        str_kwargs = [
            f'agent={self.agent}, polarity={self.polarity.value}'
        ]
        return parse_repr(self, str_kwargs)

    def __hash__(self) -> int:
        """These objects are used as nodes in the graph, in particular they are
        used as dictionary keys. There only exists one agent with each id and
        level, so those keys plus polarity suffice as identifiers.
        """
        return hash((self.agent.level, self.agent.agent_id, self.polarity))

    def __eq__(self, other: AgentNode) -> bool:
        """These represent nodes on the allocation graph and are compared to
        other objects in the networkx module, so makes sense to define rich
        comparison operators. Also useful for testing.
        """
        return all(self._agent_node_eq_comparison(other))

    def _agent_node_eq_comparison(
        self, other: AgentNode
    ) -> Generator[bool, None, None]:
        """Generator of all attributes which define agent node equality."""
        yield isinstance(other, self.__class__)
        yield self.agent == other.agent
        yield self.polarity == other.polarity

    def __lt__(self, other: AgentNode) -> bool:
        """Lexicographic ordering by agent and polarity. We treat positive as
        less than negative since the graph flows from positive to negative
        between two agent nodes at the same level."""
        if self.agent == other.agent:
            return (
                self.polarity == Polarity.POSITIVE
            ) and (
                other.polarity == Polarity.NEGATIVE
            )
        return self.agent < other.agent

    @property
    def level(self) -> int:
        return self.agent.level


class HierarchyGraph(nx.OrderedDiGraph):
    """Represent a hierarchy as a directed graph (network). The full allocation
    graph consists of these objects, glued together with edges. For each agent,
    split them into positive and negative agent nodes and draw an edge between
    these. The capacity of the edge represents the capacity of the agent. The
    rules are:

      1) edge capacity = agent upper capacity - agent lower capacity.
      2) positive node demand = agent lower capacity.
      3) negative node demand = agent lower capacity * (-1).
    """

    edge_attr_dict_factory = dict

    def __init__(self, hierarchy: Hierarchy, agents: List[Agent]) -> None:
        """
        Parameters
        ----------
        hierarchy:
            The hierarchy we are modelling as a graph.
        agents:
            Agents used to populate the graph. These don't necessarily have to
            be the same agents as those on the hierarchy -- there's no need to
            include agents that aren't preferred by anyone on the level beneath,
            for example.
        """
        super().__init__()
        self.hierarchy = hierarchy
        self.level = hierarchy.level
        self.agents = agents

        self._agent_positive_node_map = None
        self._agent_negative_node_map = None

    def __str__(self) -> str:
        return f'HIERARCHY_GRAPH_{self.level}'

    def __repr__(self) -> str:
        str_kwargs = [f'hierarchy={self.hierarchy}']
        if self.agents:
            agent_strs = [str(agent) for agent in self.agents]
            str_kwargs.append(f'agents={agent_strs}'.replace('\'', ''))
        return parse_repr(self, str_kwargs)

    def __eq__(self, other: HierarchyGraph) -> bool:
        return all(self._graph_eq_comparison(other))

    def _graph_eq_comparison(
            self, other: HierarchyGraph
    ) -> Generator[bool, None, None]:
        """Generator of all attributes which define graph equality."""
        yield isinstance(other, self.__class__)
        yield self.nodes == other.nodes
        yield sorted(self.edges(data=True)) == sorted(other.edges(data=True))
        yield self.hierarchy == other.hierarchy
        yield self.agents == other.agents

    def generate_agent_nodes(self) -> None:
        """Construct the AgentNodes for each agent and draw an edge between
        them. Set the capacity of the edge to be the difference between the
        agent's upper and lower capacity. Set demand to be
        (node polarity)*lower_capacity. Update internal dictionary keeping track
        of which nodes have been assigned to agents.
        """
        for agent in self.agents:
            out_node = AgentNode(agent, Polarity.POSITIVE)
            in_node = AgentNode(agent, Polarity.NEGATIVE)
            demand = agent.lower_capacity
            capacity = agent.capacity_difference
            self.add_node(out_node, demand=demand)
            self.add_node(in_node, demand=-demand)
            self.add_edge(out_node, in_node, capacity=capacity, weight=0)
        self.generate_agent_node_maps()

    @property
    def positive_agent_nodes(self) -> List[AgentNode]:
        """Return generator of all positive agent nodes, in order."""
        return [node for node in self if node.polarity == Polarity.POSITIVE]

    @property
    def negative_agent_nodes(self) -> List[AgentNode]:
        """Return generator of all negative agent nodes, in order."""
        return [node for node in self if node.polarity == Polarity.NEGATIVE]

    def generate_agent_node_maps(self) -> None:
        self._agent_positive_node_map = OrderedDict(
            zip(self.agents, self.positive_agent_nodes)
        )
        self._agent_negative_node_map = OrderedDict(
            zip(self.agents, self.negative_agent_nodes)
        )

    @classmethod
    def full_subgraph(
        cls, hierarchy: Hierarchy, agents: List[Agent]
    ) -> HierarchyGraph:
        """Create graph with all agent nodes and edges set up."""
        graph = cls(hierarchy, agents)
        graph.generate_agent_nodes()
        return graph

    def positive_node(self, agent: Agent) -> AgentNode:
        """Return positive node corresponding to the agent."""
        return self._agent_positive_node_map[agent]

    def negative_node(self, agent) -> AgentNode:
        """Return negative node corresponding to the agent."""
        return self._agent_negative_node_map[agent]


class AllocationGraph(nx.DiGraph):
    def __init__(
        self, subgraphs: Optional[List[HierarchyGraph]] = None
    ) -> None:
        """
        Parameters
        ----------
        subgraphs:
            The hierarchy graphs are glued together by edges representing the
            preferences of each of their agents.
        """
        super(AllocationGraph, self).__init__()
        self.subgraphs = subgraphs or []
        self.flow_cost = None
        self.max_flow = None
        self.simple_flow = None
        self.allocation = []

        self._source = None
        self._sink = None

        self.flow = None
        self.flow_cost = None
        self.max_flow = None
        self.simple_flow = None

    def __str__(self) -> str:
        return f'ALLOCATION_GRAPH({len(self.subgraphs)})'

    def __repr__(self):
        str_kwargs = []
        if self.subgraphs:
            subgraph_strs = [str(subgraph) for subgraph in self.subgraphs]
            str_kwargs.append(f'subgraphs={subgraph_strs}'.replace('\'', ''))
        return parse_repr(self, str_kwargs)

    @property
    def source(self) -> AgentNode:
        """Cached property to generate source to avoid recreating objects."""
        if self._source is None:
            zero_hierarchy = Hierarchy(level=0)
            # Create source agent which equally prefers all level 1 agents.
            source_agent = Agent(
                agent_id=1,
                hierarchy=zero_hierarchy,
                preferences=[self.first_level_agents],
                name=GraphElement.SOURCE
            )
            self._source = AgentNode(source_agent, Polarity.POSITIVE)
        return self._source

    @property
    def sink(self) -> AgentNode:
        """Cached property to generate sink to avoid recreating objects."""
        if self._sink is None:
            final_hierarchy = Hierarchy(level=self.number_of_hierarchies + 1)
            sink_agent = Agent(
                agent_id=1, hierarchy=final_hierarchy, name=GraphElement.SINK
            )
            # Each agent in the last hierarchy prefers the sink agent.
            for agent in self.last_level_agents:
                agent.preferences = [sink_agent]
            self._sink = AgentNode(sink_agent, Polarity.NEGATIVE)
        return self._sink

    @property
    def first_subgraph(self) -> Optional[HierarchyGraph]:
        if self.subgraphs:
            return self.subgraphs[0]

    @property
    def last_subgraph(self) -> Optional[HierarchyGraph]:
        if self.subgraphs:
            return self.subgraphs[-1]

    @property
    def hierarchies(self) -> List[Hierarchy]:
        return [subgraph.hierarchy for subgraph in self.subgraphs]

    @property
    def number_of_hierarchies(self) -> int:
        return len(self.hierarchies)

    @property
    def first_level_agents(self) -> List[Agent]:
        return self.hierarchies[0].agents

    @property
    def last_level_agents(self) -> List[Agent]:
        return self.hierarchies[-1].agents

    @property
    def last_level(self) -> int:
        return self.hierarchies[-1].level

    @property
    def min_upper_capacity_sum(self) -> int:
        return min(
            hierarchy.upper_capacity_sum for hierarchy in self.hierarchies
        )

    def intermediate_hierarchies(self, node: AgentNode) -> List[Hierarchy]:
        """Return all hierarchies strictly between the given node and the last
        hierarchy (non-inclusive).
        """
        return self.hierarchies[node.level: -1]

    def add_edge_with_cost(
        self, out_node: AgentNode, in_node: AgentNode, cost: CostFunc
    ) -> None:
        weight = cost(out_node, in_node)
        self.add_edge(out_node, in_node, weight=weight)

    def populate_edges_from_source(self, cost: CostFunc) -> None:
        for node in self.first_subgraph.positive_agent_nodes:
            self.add_edge_with_cost(self.source, node, cost)

    def populate_edges_to_sink(self, cost: CostFunc) -> None:
        for node in self.last_subgraph.negative_agent_nodes:
            self.add_edge_with_cost(node, self.sink, cost)

    def populate_internal_edges(self) -> None:
        for subgraph in self.subgraphs:
            self.add_edges_from(subgraph.edges(data=True))

    def glue(
        self,
        subgraph1: HierarchyGraph,
        subgraph2: HierarchyGraph,
        cost: CostFunc
    ) -> None:
        for agent in subgraph1.agents:
            for preference in agent.preferences:

                # Handle preference ties.
                if isinstance(preference, Agent):
                    preference_list = [preference]
                elif isinstance(preference, list):
                    preference_list = preference
                else:
                    preference_list = []

                for other_agent in preference_list:
                    out_node = subgraph1.negative_node(agent)
                    in_node = subgraph2.positive_node(other_agent)
                    self.add_edge_with_cost(out_node, in_node, cost)

    def populate_all_edges(self, cost: CostFunc) -> None:
        self.populate_edges_from_source(cost)
        self.populate_edges_to_sink(cost)
        self.populate_internal_edges()
        for subgraph1, subgraph2 in zip(self.subgraphs, self.subgraphs[1:]):
            self.glue(subgraph1, subgraph2, cost)

    @classmethod
    def with_edges(
        cls,
        subgraphs: List[HierarchyGraph],
        cost: CostFunc
    ) -> AllocationGraph:
        graph = cls(subgraphs)
        graph.populate_all_edges(cost)
        return graph

    def compute_flow(self) -> None:
        self.flow = nx.max_flow_min_cost(self, self.source, self.sink)
        self.flow_cost = nx.cost_of_flow(self, self.flow)
        self.max_flow = nx.maximum_flow(self, self.source, self.sink)[0]

    def simplify_flow(self) -> None:
        """Create new dictionary mapping
            Agent --> OrderedDict(Agents: int)
        Map Agents to every Agent they have non-zero flow towards, and what the
        flow value is.  Assign to simple_flow attribute.
        """
        mapping = {}

        # For each agent node (except the last level):
        for subgraph in self.subgraphs[:-1]:
            for agent in subgraph.agents:
                # Assign to it the non-zero flows from negative agent nodes to
                # positive agent nodes at the next level.
                negative_node = subgraph.negative_node(agent)
                flow = self.flow[negative_node]
                items = ((k.agent, v) for k, v in flow.items() if v)
                mapping[agent] = OrderedDict(sorted(items))

        self.simple_flow = mapping

    @staticmethod
    def single_allocation(
        agent: Agent,
        flow: Dict[Agent, Dict[Agent, int]]
    ) -> List[AllocationDatum]:
        """Return a list of AllocationDatum objects describing the allocation
        of higher level agents to a given level 1 agent.
        Parameters
        ----------
        agent:
            Agent at level 1.
        flow:
            Copy of self.simple_flow where keys are deleted or values modified
            as they are encountered.
        """
        value = []
        current_agent = agent
        while current_agent in flow:
            agent_flow = flow[current_agent]
            next_agent, flow_units = next(iter(agent_flow.items()))
            rank = current_agent.preference_position(next_agent)
            value.append(AllocationDatum(next_agent, rank))
            if flow_units == 1:
                agent_flow.pop(next_agent)
            else:
                agent_flow[next_agent] -= 1
            current_agent = next_agent
        return value

    def allocate(self) -> None:
        allocation = {}

        # Make inexpensive deep copy of simple_flow.
        g = ((agent, dict(d)) for agent, d in self.simple_flow.items())
        flow = dict(g)

        for agent in self.hierarchies[0]:
            allocation[agent] = self.single_allocation(agent, flow)

        self.allocation = allocation
