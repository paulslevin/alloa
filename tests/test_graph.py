from   modules.agents import Agent, Hierarchy
from   modules.graph import AgentNode
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
