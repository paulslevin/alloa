from modules.agents import Agent, Hierarchy
from unittest import TestCase


class TestAgent(TestCase):
    def test_name(self):
        hierarchy = Hierarchy(1)
        agent = Agent(1, hierarchy)
        agent.give_name("Joe Bloggs")
        self.assertEqual(agent.name, "Joe Bloggs")
