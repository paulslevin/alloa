from unittest import TestCase
from modules.agents import Hierarchy, Agent


class TestHierarchy(TestCase):

    def setUp(self):
        self.hierarchy1 = Hierarchy(1)
        self.hierarchy2 = Hierarchy(1)
        self.hierarchy3 = Hierarchy(1)

    def test_init(self):
        self.assertEqual(self.hierarchy1.level, 1)
        self.assertEqual(self.hierarchy1.agents, None)

    def test_str(self):
        self.assertEqual(str(self.hierarchy2), "1")

    def test_add_agent(self):
        agent = Agent(1, self.hierarchy3)
        self.hierarchy3.add_agent(agent)
        self.assertEqual(self.hierarchy3.agents, [agent])

    def test_give_names(self):
        hierarchy = Hierarchy(1)
        self.assertRaises(ValueError, hierarchy.give_names)
        agent1 = Agent(1, hierarchy)
        agent2 = Agent(2, hierarchy)
        hierarchy.add_agent(agent1)
        hierarchy.add_agent(agent2)
        hierarchy.add_names({1: "Joe", 2: "Bloggs"})
        hierarchy.give_names()
        self.assertEqual(agent1.name, "Joe")
        self.assertEqual(agent2.name, "Bloggs")

    def test_add_names(self):
        hierarchy = Hierarchy(1)
        self.assertRaises(ValueError, hierarchy.add_names, {1: "Joe"})
        agent = Agent(1, hierarchy)
        hierarchy.add_agent(agent)
        self.assertRaises(ValueError, hierarchy.add_names, {1: "Joe",
                                                            2: "Bloggs"})
        hierarchy.add_names({1: "Joe"})
        self.assertEqual(hierarchy.names, {1: "Joe"})
