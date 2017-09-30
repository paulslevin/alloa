from   modules.agents import Agent, Hierarchy
from   modules.graph import AgentNode, HierarchyGraph
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


class TestHierarchyGraph(unittest.TestCase):
    def setUp(self):
        hierarchy = Hierarchy(level=2)
        self.agent_2_1 = Agent(id=1, hierarchy=hierarchy)
        self.agent_2_2 = Agent(id=2, hierarchy=hierarchy)
        self.agent_2_3 = Agent(id=3, hierarchy=hierarchy)
        # Suppose that only agents 1 and 3 are preferred by the level 1 agents,
        # so don't need put agent 2 on.
        self.graph = HierarchyGraph(hierarchy=hierarchy,
                                    agents=[self.agent_2_1, self.agent_2_3])

    def test___str__(self):
        self.assertEqual(str(self.graph), 'HIERARCHY_GRAPH_2')

    def test___repr__(self):
        self.assertEqual(
            repr(self.graph),
            'HierarchyGraph(hierarchy=HIERARCHY_2, agents=[AGENT_2_1, AGENT_2_3])',
        )

    def test_agents_to_nodes(self):
        self.graph.agents_to_nodes()
        self.assertEqual(self.graph.positive_dict,
                         {self.agent_2_1: AgentNode(self.agent_2_1, POSITIVE),
                          self.agent_2_3: AgentNode(self.agent_2_3, POSITIVE),})
        self.assertEqual(self.graph.negative_dict,
                         {self.agent_2_1: AgentNode(self.agent_2_1, NEGATIVE),
                          self.agent_2_3: AgentNode(self.agent_2_3, NEGATIVE),})