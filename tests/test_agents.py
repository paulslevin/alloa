from itertools import izip
import unittest
from modules.agents import Agent, AgentExistsError, Hierarchy
from modules.agents import AgentNotInPreferencesError


class TestAgent(unittest.TestCase):
    
    def setUp(self):
        self.hierarchy = Hierarchy(level=1)
        self.agent = Agent(id=1, hierarchy=self.hierarchy)

    def test___str__(self):
        self.assertEqual(str(self.agent), 'AGENT_1_1')

    def test___repr__(self):
        self.assertEqual(repr(self.agent),
                         'Agent(id=1, hierarchy=HIERARCHY_1)')

    def test_upper_capacity(self):
        self.agent.capacities = [0, 1]
        self.assertEqual(self.agent.upper_capacity, 1)

    def test_lower_capacity(self):
        self.agent.capacities = [0, 1]
        self.assertEqual(self.agent.lower_capacity, 0)

    def test_capacity_difference(self):
        self.agent.capacities = [0, 1]
        self.assertEqual(self.agent.capacity_difference, 1)

    def test_preference_position(self):
        hierarchy2 = Hierarchy(level=2)
        agent_2_1 = Agent(id=1, hierarchy=hierarchy2)
        agent_2_2 = Agent(id=2, hierarchy=hierarchy2)
        agent_2_3 = Agent(id=3, hierarchy=hierarchy2)

        self.agent.preferences = [agent_2_1, agent_2_2, agent_2_3]

        self.assertEqual(self.agent.preference_position(agent_2_1), 1)
        self.assertEqual(self.agent.preference_position(agent_2_2), 2)
        self.assertEqual(self.agent.preference_position(agent_2_3), 3)

    def test_AgentExistsError(self):
        '''Test creating an additional agent with the same id raises an Exception.'''
        with self.assertRaises(AgentExistsError) as context:
            double_agent = Agent(id=1, hierarchy=self.hierarchy)
        self.assertEqual(context.exception.message,
                         'HIERARCHY_1 already has an agent with id 1.')

    def test_AgentNotInPreferencesError(self):
        hierarchy2 = Hierarchy(level=2)
        with self.assertRaises(AgentNotInPreferencesError) as context:
            other_agent = Agent(id=1, hierarchy=hierarchy2)
            self.agent.preference_position(other_agent)
        self.assertEqual(context.exception.message,
                         'AGENT_2_1 not in preferences of AGENT_1_1.')
                  

class TestHierarchy(unittest.TestCase):
    
    def setUp(self):
        self.hierarchy = Hierarchy(level=1)

    def test___str__(self):
        self.assertEqual(str(self.hierarchy), 'HIERARCHY_1')

    def test___repr__(self):
        agent_1_1 = Agent(id=1, hierarchy=self.hierarchy, name='Agent')
        agent_1_2 = Agent(id=2, hierarchy=self.hierarchy, name='Agent')
        self.assertEqual(repr(self.hierarchy),
                         "Hierarchy(level=1, agents=[AGENT_1_1, AGENT_1_2])")

    def test_add_1_agent(self):
        agent = Agent(id=1, hierarchy=self.hierarchy, name='Agent')
        self.assertEqual(self.hierarchy.agents, [agent])
        self.assertEqual(self.hierarchy._agent_name_map, {agent: 'Agent'})

    def test_add_2_agents(self):
        agent1 = Agent(id=1, hierarchy=self.hierarchy, name='Agent 1')
        agent2 = Agent(id=2, hierarchy=self.hierarchy, name='Agent 2')
        self.assertEqual(self.hierarchy.agents, [agent1, agent2])
        self.assertEqual(self.hierarchy._agent_name_map,
                         {agent1: 'Agent 1', agent2: 'Agent 2'})

    def test_number_of_agents(self):
        self.assertEqual(self.hierarchy.number_of_agents, 0)
        agent1 = Agent(id=1, hierarchy=self.hierarchy)
        self.assertEqual(self.hierarchy.number_of_agents, 1)

    def test_preferred(self):

        # Level 1 agents.
        agent_1_1 = Agent(id=1, hierarchy=self.hierarchy)
        agent_1_2 = Agent(id=2, hierarchy=self.hierarchy)
        agent_1_3 = Agent(id=3, hierarchy=self.hierarchy)

        # Level 2 agents.
        hierarchy2 = Hierarchy(level=2)
        agent_2_1 = Agent(id=1, hierarchy=hierarchy2)
        agent_2_2 = Agent(id=2, hierarchy=hierarchy2)
        agent_2_3 = Agent(id=3, hierarchy=hierarchy2)
        agent_2_4 = Agent(id=4, hierarchy=hierarchy2)
        agent_2_5 = Agent(id=5, hierarchy=hierarchy2)

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

    def test_set_agent_name(self):
        '''Test setting the agent name updates the hierarchy.'''
        agent = Agent(id=1, hierarchy=self.hierarchy, name='Agent')
        self.assertEqual(agent.name, 'Agent')
        agent.name = 'Bgent'
        self.assertEqual(agent.name, 'Bgent')
        self.assertEqual(self.hierarchy._agent_name_map, {agent: 'Bgent'})
        self.assertEqual(self.hierarchy.name_agent_map, {'Bgent': agent})

    def test_name_agent_map(self):
        agent_1_1 = Agent(id=1, hierarchy=self.hierarchy, name='Agent')
        agent_1_2 = Agent(id=2, hierarchy=self.hierarchy, name='Bgent')
        self.assertEqual(self.hierarchy.name_agent_map, 
                         {'Agent': agent_1_1, 'Bgent': agent_1_2} )

    def test_max_preference_length(self):

        # Level 1 Agents.
        agent_1_1 = Agent(id=1, hierarchy=self.hierarchy)
        agent_1_2 = Agent(id=2, hierarchy=self.hierarchy)
        agent_1_3 = Agent(id=3, hierarchy=self.hierarchy)

        # Level 2 Agents.
        hierarchy2 = Hierarchy(level=2)
        agent_2_1 = Agent(id=1, hierarchy=hierarchy2)
        agent_2_2 = Agent(id=2, hierarchy=hierarchy2)
        agent_2_3 = Agent(id=3, hierarchy=hierarchy2)
        agent_2_4 = Agent(id=4, hierarchy=hierarchy2)
        agent_2_5 = Agent(id=5, hierarchy=hierarchy2)

        agent_1_1.preferences = [agent_2_1, agent_2_2]
        agent_1_2.preferences = [agent_2_3, agent_2_4]
        agent_1_3.preferences = [agent_2_1, agent_2_3, agent_2_5]

        self.assertEqual(self.hierarchy.max_preferences_length, 3)

    def test_has_agent_with_id(self):
        agent = Agent(id=1, hierarchy=self.hierarchy)
        self.assertEqual(self.hierarchy.has_agent_with_id(1), True)
        self.assertEqual(self.hierarchy.has_agent_with_id(2), False)   
                                                             