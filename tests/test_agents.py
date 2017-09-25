from itertools import izip
import unittest
from modules.agents import Agent, Hierarchy


class TestHierarchy(unittest.TestCase):
    
    def setUp(self):
        self.hierarchy = Hierarchy(level=1)

    def test___str__(self):
        self.assertEqual(str(self.hierarchy), '1')

    def test___repr__(self):
        self.assertEqual(self.hierarchy.__repr__(), 'HIERARCHY_1')

    def test_add_1_agent(self):
        agent = Agent(id_number=1, hierarchy=self.hierarchy, name='Agent')
        self.hierarchy.add_agent(agent)
        self.assertEqual(self.hierarchy.agents, [agent])
        self.assertEqual(self.hierarchy.agent_to_name, {agent: 'Agent'})

    def test_add_2_agents_individually(self):
        agent1 = Agent(id_number=1, hierarchy=self.hierarchy, name='Agent 1')
        agent2 = Agent(id_number=2, hierarchy=self.hierarchy, name='Agent 2')
        self.hierarchy.add_agent(agent1)
        self.hierarchy.add_agent(agent2)
        self.assertEqual(self.hierarchy.agents, [agent1, agent2])
        self.assertEqual(self.hierarchy.agent_to_name,
                         {agent1: 'Agent 1', agent2: 'Agent 2'})

    def test_add_agents(self):
        agent1 = Agent(id_number=1, hierarchy=self.hierarchy, name='Agent 1')
        agent2 = Agent(id_number=2, hierarchy=self.hierarchy, name='Agent 2')
        self.hierarchy.add_agents(agent1, agent2)
        self.assertEqual(self.hierarchy.agents, [agent1, agent2])
        self.assertEqual(self.hierarchy.agent_to_name,
                         {agent1: 'Agent 1', agent2: 'Agent 2'})

    def test_number_of_agents(self):
        self.assertEqual(self.hierarchy.number_of_agents, 0)
        agent1 = Agent(id_number=1, hierarchy=self.hierarchy)
        self.hierarchy.add_agent(agent1)
        self.assertEqual(self.hierarchy.number_of_agents, 1)

    def test_preferred(self):

        # Level 1 agents.
        agent_1_1 = Agent(id_number=1, hierarchy=self.hierarchy)
        agent_1_2 = Agent(id_number=2, hierarchy=self.hierarchy)
        agent_1_3 = Agent(id_number=3, hierarchy=self.hierarchy)

        # Level 2 agents.
        hierarchy2 = Hierarchy(level=2)
        agent_2_4 = Agent(id_number=4, hierarchy=hierarchy2)
        agent_2_5 = Agent(id_number=5, hierarchy=hierarchy2)
        agent_2_6 = Agent(id_number=6, hierarchy=hierarchy2)
        agent_2_7 = Agent(id_number=7, hierarchy=hierarchy2)
        agent_2_8 = Agent(id_number=8, hierarchy=hierarchy2)

        agent_1_1.preferences = [agent_2_4, agent_2_5, agent_2_6]
        agent_1_2.preferences = [agent_2_5, agent_2_6, agent_2_7]
        agent_1_3.preferences = [agent_2_8]

        test_cases = [

            # Size 1 subsets.
            ({agent_1_1}, [agent_2_4, agent_2_5, agent_2_6]),
            ({agent_1_2}, [agent_2_5, agent_2_6, agent_2_7]),
            ({agent_1_3}, [agent_2_8]),

            # Size 2 subsets.
            ({agent_1_1, agent_1_2}, [agent_2_4, agent_2_5, agent_2_6, agent_2_7]),
            ({agent_1_1, agent_1_3}, [agent_2_4, agent_2_5, agent_2_6, agent_2_8]),
            ({agent_1_2, agent_1_3}, [agent_2_5, agent_2_6, agent_2_7, agent_2_8]),

            # Size 3 subset.
            ({agent_1_1, agent_1_2, agent_1_3}, 
             [agent_2_4, agent_2_5, agent_2_6, agent_2_7, agent_2_8]),
        ]

        for agent_subset, expected in test_cases:
            self.assertEqual(self.hierarchy.preferred(agent_subset), expected)
