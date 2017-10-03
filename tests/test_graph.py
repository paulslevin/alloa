from   modules.agents import Agent, Hierarchy
from   modules.graph import AgentNode, HierarchyGraph
import networkx as nx
import unittest
from   utils.enums import Polarity


POSITIVE = Polarity.POSITIVE
NEGATIVE = Polarity.NEGATIVE


class TestAgentNode(unittest.TestCase):
    def setUp(self):
        self.hierarchy = Hierarchy(level=1)
        self.agent = Agent(id=1, hierarchy=self.hierarchy)
        self.positive_node = AgentNode(agent=self.agent, polarity=POSITIVE)
        self.negative_node = AgentNode(agent=self.agent, polarity=NEGATIVE)

    def test___str__(self):
        self.assertEqual(str(self.positive_node), 'AGENT_1_1(+)')
        self.assertEqual(str(self.negative_node), 'AGENT_1_1(-)')

    def test___repr__(self):
        self.assertEqual(repr(self.positive_node),
                         'AgentNode(agent=AGENT_1_1, polarity=+)')
        self.assertEqual(repr(self.negative_node),
                         'AgentNode(agent=AGENT_1_1, polarity=-)')

    def test___eq__(self):
        self.positive_node2 = AgentNode(agent=self.agent, polarity=POSITIVE)
        self.assertEquals(self.positive_node, self.positive_node2)
        self.negative_node2 = AgentNode(agent=self.agent, polarity=NEGATIVE)
        self.assertEquals(self.negative_node, self.negative_node2)

    def test___neq__(self):
        self.assertNotEqual(self.positive_node, self.negative_node)


class TestHierarchyGraph(unittest.TestCase):
    def setUp(self):
        self.hierarchy = Hierarchy(level=2)
        self.agent_2_1 = Agent(id=1, hierarchy=self.hierarchy, capacities=(2,5))
        self.agent_2_2 = Agent(id=2, hierarchy=self.hierarchy, capacities=(0,1))
        self.agent_2_3 = Agent(id=3, hierarchy=self.hierarchy, capacities=(1,1))

        # Suppose that only agents 1 and 3 are preferred by the level 1 agents,
        # so don't need put agent 2 on.
        self.agents = [self.agent_2_1, self.agent_2_3]
        self.graph = HierarchyGraph(self.hierarchy, self.agents)

        self.agent_node_2_1_p = AgentNode(self.agent_2_1, POSITIVE)
        self.agent_node_2_1_n = AgentNode(self.agent_2_1, NEGATIVE)
        self.agent_node_2_3_p = AgentNode(self.agent_2_3, POSITIVE)
        self.agent_node_2_3_n = AgentNode(self.agent_2_3, NEGATIVE)

    def test___str__(self):
        self.assertEqual(str(self.graph), 'HIERARCHY_GRAPH_2')

    def test___repr__(self):
        self.assertEqual(
            repr(self.graph),
            'HierarchyGraph(hierarchy=HIERARCHY_2, agents=[AGENT_2_1, AGENT_2_3])',
        )

    def test___eq__(self):
        '''Generating nodes and agents by hand results in an equivalent graph.'''
        self.graph.assign_agents_to_nodes()
        self.graph.generate_agent_nodes()

        graph = HierarchyGraph(hierarchy=self.hierarchy, agents=[])
        graph.add_nodes_from([
            (self.agent_node_2_1_p, {'demand': 2}),
            (self.agent_node_2_1_n, {'demand': -2}),
            (self.agent_node_2_3_p, {'demand': 1}),
            (self.agent_node_2_3_n, {'demand': -1}),
        ])
        graph.add_edges_from([(self.agent_node_2_1_p,
                               self.agent_node_2_1_n,
                               {'weight': 0, 'capacity': 3}),
                              (self.agent_node_2_3_p,
                               self.agent_node_2_3_n,
                               {'weight': 0, 'capacity': 0}),])
        graph.agents = self.agents
        self.assertEqual(graph, self.graph)

    def test___neq__(self):
        self.graph.assign_agents_to_nodes()
        self.graph.generate_agent_nodes()

        graph = HierarchyGraph(hierarchy=self.hierarchy, agents=[])
        graph.add_nodes_from([
            (self.agent_node_2_1_p, {'demand': 3}), # Differs only here.
            (self.agent_node_2_1_n, {'demand': -2}),
            (self.agent_node_2_3_p, {'demand': 1}),
            (self.agent_node_2_3_n, {'demand': -1}),
        ])
        graph.add_edges_from([(self.agent_node_2_1_p, 
                               self.agent_node_2_1_n,
                               {'weight': 0, 'capacity': 3}),
                              (self.agent_node_2_3_p,
                               self.agent_node_2_3_n,
                               {'weight': 0, 'capacity': 0}),])
        graph.agents = self.agents

        self.assertNotEqual(graph, self.graph)

    def test_assign_agents_to_nodes(self):
        self.graph.assign_agents_to_nodes()
        self.assertEqual(self.graph._agent_positive_node_map,
                         {self.agent_2_1: self.agent_node_2_1_p,
                          self.agent_2_3: self.agent_node_2_3_p,})
        self.assertEqual(self.graph._agent_negative_node_map,
                         {self.agent_2_1: self.agent_node_2_1_n,
                          self.agent_2_3: self.agent_node_2_3_n,})

    def test_agent_to_positive_node(self):
        self.graph.assign_agents_to_nodes()
        self.assertEqual(self.graph.positive_node(self.agent_2_1),
                         self.agent_node_2_1_p)
        self.assertEqual(self.graph.positive_node(self.agent_2_3),
                         self.agent_node_2_3_p)

    def test_agent_to_negative_node(self):
        self.graph.assign_agents_to_nodes()
        self.assertEqual(self.graph.negative_node(self.agent_2_1),
                         self.agent_node_2_1_n)
        self.assertEqual(self.graph.negative_node(self.agent_2_3),
                         self.agent_node_2_3_n)

    def test_positive_agent_nodes(self):
        self.graph.assign_agents_to_nodes()
        self.assertEqual(self.graph.positive_agent_nodes,
                         [self.agent_node_2_1_p, self.agent_node_2_3_p])

    def test_negative_agent_nodes(self):
        self.graph.assign_agents_to_nodes()
        self.assertEqual(self.graph.negative_agent_nodes,
                         [self.agent_node_2_1_n, self.agent_node_2_3_n])

    def test_generate_agent_nodes(self):
        self.graph.assign_agents_to_nodes()
        self.graph.generate_agent_nodes()

        # data=True will get the nodes with demand data.
        nodes = self.graph.nodes(data=True)
        expected_nodes = [
            (self.agent_node_2_1_p, {'demand': 2}),
            (self.agent_node_2_1_n, {'demand': -2}),
            (self.agent_node_2_3_p, {'demand': 1}),
            (self.agent_node_2_3_n, {'demand': -1}),
        ]
        self.assertItemsEqual(expected_nodes, nodes)

        # data=True will get the edges with capacity and weight data.
        edges = self.graph.edges(data=True)
        expected_edges = [
            (self.agent_node_2_1_p, self.agent_node_2_1_n, 
             {'capacity': 3, 'weight': 0}),
            (self.agent_node_2_3_p, self.agent_node_2_3_n,
             {'capacity': 0, 'weight': 0}),
        ]
        self.assertItemsEqual(expected_edges, edges)

    def test_full_subgraph(self):
        full_graph = HierarchyGraph.full_subgraph(self.hierarchy, self.agents)
        self.graph.assign_agents_to_nodes()
        self.graph.generate_agent_nodes()
        self.assertEqual(full_graph, self.graph)
