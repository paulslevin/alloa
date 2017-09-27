from itertools import izip
import unittest
from modules.agents import Agent, Hierarchy


class TestAgent(unittest.TestCase):
    
    def setUp(self):
        self.hierarchy = Hierarchy(level=1)
        self.agent = Agent(id_number=1, hierarchy=self.hierarchy)

    def test___str__(self):
        self.assertEqual(str(self.agent), 'AGENT_1_1')

    def test___repr__(self):
        self.assertEqual(self.agent.__repr__(), 'AGENT_1_1')

    def test_upper_capacity(self):
        self.agent.capacities = [0, 1]
        self.assertEqual(self.agent.upper_capacity, 1)

class TestHierarchy(unittest.TestCase):
    
    def setUp(self):
        self.hierarchy = Hierarchy(level=1)

    def test___str__(self):
        self.assertEqual(str(self.hierarchy), '1')

    def test___repr__(self):
        self.assertEqual(self.hierarchy.__repr__(), 'HIERARCHY_1')

    def test_add_1_agent(self):
        agent = Agent(id_number=1, hierarchy=self.hierarchy, name='Agent')
        self.assertEqual(self.hierarchy.agents, [agent])
        self.assertEqual(self.hierarchy.agent_to_name, {agent: 'Agent'})

    def test_add_2_agents(self):
        agent1 = Agent(id_number=1, hierarchy=self.hierarchy, name='Agent 1')
        agent2 = Agent(id_number=2, hierarchy=self.hierarchy, name='Agent 2')
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
        agent_2_1 = Agent(id_number=1, hierarchy=hierarchy2)
        agent_2_2 = Agent(id_number=2, hierarchy=hierarchy2)
        agent_2_3 = Agent(id_number=3, hierarchy=hierarchy2)
        agent_2_4 = Agent(id_number=4, hierarchy=hierarchy2)
        agent_2_5 = Agent(id_number=5, hierarchy=hierarchy2)

        agent_1_1.preferences = [agent_2_1, agent_2_2, agent_2_3]
        agent_1_2.preferences = [agent_2_2, agent_2_3, agent_2_4]
        agent_1_3.preferences = [agent_2_5]

        test_cases = [

            # Size 1 subsets.
            ({agent_1_1}, [agent_2_1, agent_2_2, agent_2_3]),
            ({agent_1_2}, [agent_2_2, agent_2_3, agent_2_4]),
            ({agent_1_3}, [agent_2_5]),

            # Size 2 subsets.
            ({agent_1_1, agent_1_2}, [agent_2_1, agent_2_2, agent_2_3, agent_2_4]),
            ({agent_1_1, agent_1_3}, [agent_2_1, agent_2_2, agent_2_3, agent_2_5]),
            ({agent_1_2, agent_1_3}, [agent_2_2, agent_2_3, agent_2_4, agent_2_5]),

            # Size 3 subset.
            ({agent_1_1, agent_1_2, agent_1_3}, 
             [agent_2_1, agent_2_2, agent_2_3, agent_2_4, agent_2_5]),
        ]

        for agent_subset, expected in test_cases:
            self.assertEqual(self.hierarchy.preferred(agent_subset), expected)

        self.assertEqual(
            self.hierarchy.all_preferred, 
            [agent_2_1, agent_2_2, agent_2_3, agent_2_4, agent_2_5],
        )

    # TODO: Remove once test coverage increases.
    def test_set_name(self):
        agent = Agent(id_number=1, hierarchy=self.hierarchy, name='Agent')
        self.assertEqual(agent.name, 'Agent')
        self.hierarchy.set_name(agent, 'Bgent')
        agent.name = 'Bgent'
        self.assertEqual(agent.name, 'Bgent')
        self.assertEqual(self.hierarchy.agent_to_name, {agent: 'Bgent'})
        self.assertEqual(self.hierarchy.name_to_agent, {'Bgent': agent})

    def test_set_agent_name(self):
        '''Test setting the agent name updates the hierarchy.'''
        agent = Agent(id_number=1, hierarchy=self.hierarchy, name='Agent')
        self.assertEqual(agent.name, 'Agent')
        agent.name = 'Bgent'
        self.assertEqual(agent.name, 'Bgent')
        self.assertEqual(self.hierarchy.agent_to_name, {agent: 'Bgent'})
        self.assertEqual(self.hierarchy.name_to_agent, {'Bgent': agent})

    def test_name_to_agent(self):
        agent_1_1 = Agent(id_number=1, hierarchy=self.hierarchy, name='Agent')
        agent_1_2 = Agent(id_number=2, hierarchy=self.hierarchy, name='Bgent')
        self.assertEqual(self.hierarchy.name_to_agent, {'Agent': agent_1_1,
                                                        'Bgent': agent_1_2, } )

    def test_max_preference_length(self):

        # Level 1 Agents.
        agent_1_1 = Agent(id_number=1, hierarchy=self.hierarchy)
        agent_1_2 = Agent(id_number=2, hierarchy=self.hierarchy)
        agent_1_3 = Agent(id_number=3, hierarchy=self.hierarchy)

        # Level 2 Agents.
        hierarchy2 = Hierarchy(level=2)
        agent_2_1 = Agent(id_number=1, hierarchy=hierarchy2)
        agent_2_2 = Agent(id_number=2, hierarchy=hierarchy2)
        agent_2_3 = Agent(id_number=3, hierarchy=hierarchy2)
        agent_2_4 = Agent(id_number=4, hierarchy=hierarchy2)
        agent_2_5 = Agent(id_number=5, hierarchy=hierarchy2)

        agent_1_1.preferences = [agent_2_1, agent_2_2]
        agent_1_2.preferences = [agent_2_3, agent_2_4]
        agent_1_3.preferences = [agent_2_1, agent_2_3, agent_2_5]

        self.assertEqual(self.hierarchy.max_preferences_length, 3)
        