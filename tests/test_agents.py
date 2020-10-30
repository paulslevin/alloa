from itertools import permutations
import unittest
from alloa.agents import Agent, AgentExistsError, Hierarchy


class TestAgent(unittest.TestCase):

    def setUp(self):
        self.hierarchy = Hierarchy(level=1)
        self.agent = Agent(agent_id=1, hierarchy=self.hierarchy)

    def test___str__(self):
        self.assertEqual(str(self.agent), 'AGENT_1_1')

    def test_lexicographic_ordering(self):
        hierarchy1 = self.hierarchy
        hierarchy2 = Hierarchy(level=2)
        agent_1_1 = self.agent
        agent_1_2 = Agent(agent_id=2, hierarchy=hierarchy1)
        agent_2_1 = Agent(agent_id=1, hierarchy=hierarchy2)
        agent_2_2 = Agent(agent_id=2, hierarchy=hierarchy2)

        expected = [agent_1_1, agent_1_2, agent_2_1, agent_2_2]

        for permutation in permutations(expected, 4):
            self.assertEqual(sorted(permutation), expected)

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
        agent_2_1 = Agent(agent_id=1, hierarchy=hierarchy2)
        agent_2_2 = Agent(agent_id=2, hierarchy=hierarchy2)
        agent_2_3 = Agent(agent_id=3, hierarchy=hierarchy2)

        self.agent.preferences = [agent_2_1, agent_2_2, agent_2_3]

        self.assertEqual(self.agent.preference_position(agent_2_1), 1)
        self.assertEqual(self.agent.preference_position(agent_2_2), 2)
        self.assertEqual(self.agent.preference_position(agent_2_3), 3)

    def test_preference_position_tie(self):
        hierarchy2 = Hierarchy(level=2)
        agent_2_1 = Agent(agent_id=1, hierarchy=hierarchy2)
        agent_2_2 = Agent(agent_id=2, hierarchy=hierarchy2)
        agent_2_3 = Agent(agent_id=3, hierarchy=hierarchy2)
        agent_2_4 = Agent(agent_id=4, hierarchy=hierarchy2)

        self.agent.preferences = [agent_2_1, [agent_2_2, agent_2_3], agent_2_4]

        self.assertEqual(self.agent.preference_position(agent_2_1), 1)
        self.assertEqual(self.agent.preference_position(agent_2_2), 2)
        self.assertEqual(self.agent.preference_position(agent_2_3), 2)
        self.assertEqual(self.agent.preference_position(agent_2_4), 3)

    def test_preference_position_no_preference(self):
        hierarchy2 = Hierarchy(level=2)
        other = Agent(agent_id=1, hierarchy=hierarchy2)
        self.assertEqual(self.agent.preferences, [])
        self.assertEqual(self.agent.preference_position(other), 0)

    def test_agent_exists_error(self):
        """Creating additional agent with the same ID raises an Exception."""
        with self.assertRaisesRegex(
            AgentExistsError,
            r'HIERARCHY_1 already has an agent with ID 1\.',
        ):
            Agent(agent_id=1, hierarchy=self.hierarchy)


class TestHierarchy(unittest.TestCase):

    def setUp(self):
        self.hierarchy = Hierarchy(level=1)

    def test___str__(self):
        self.assertEqual(str(self.hierarchy), 'HIERARCHY_1')

    def test___iter__(self):
        agent1 = Agent(agent_id=1, hierarchy=self.hierarchy)
        agent2 = Agent(agent_id=2, hierarchy=self.hierarchy)
        agent3 = Agent(agent_id=3, hierarchy=self.hierarchy)
        agents = [a for a in self.hierarchy]
        self.assertEqual(agents, [agent1, agent2, agent3])

    def test_add_1_agent(self):
        agent = Agent(agent_id=1, hierarchy=self.hierarchy, name='Agent')
        self.assertEqual(self.hierarchy.agents, [agent])
        self.assertEqual(self.hierarchy._agent_name_map, {agent: 'Agent'})

    def test_add_2_agents(self):
        agent1 = Agent(agent_id=1, hierarchy=self.hierarchy, name='Agent 1')
        agent2 = Agent(agent_id=2, hierarchy=self.hierarchy, name='Agent 2')
        self.assertEqual(self.hierarchy.agents, [agent1, agent2])
        self.assertEqual(
            self.hierarchy._agent_name_map,
            {agent1: 'Agent 1', agent2: 'Agent 2'}
        )

    def test_number_of_agents(self):
        self.assertEqual(self.hierarchy.number_of_agents, 0)
        Agent(agent_id=1, hierarchy=self.hierarchy)
        self.assertEqual(self.hierarchy.number_of_agents, 1)

    def test_preferred(self):

        # Level 1 agents.
        agent_1_1 = Agent(agent_id=1, hierarchy=self.hierarchy)
        agent_1_2 = Agent(agent_id=2, hierarchy=self.hierarchy)
        agent_1_3 = Agent(agent_id=3, hierarchy=self.hierarchy)

        # Level 2 agents.
        hierarchy2 = Hierarchy(level=2)
        agent_2_1 = Agent(agent_id=1, hierarchy=hierarchy2)
        agent_2_2 = Agent(agent_id=2, hierarchy=hierarchy2)
        agent_2_3 = Agent(agent_id=3, hierarchy=hierarchy2)
        agent_2_4 = Agent(agent_id=4, hierarchy=hierarchy2)
        agent_2_5 = Agent(agent_id=5, hierarchy=hierarchy2)

        agent_1_1.preferences = [agent_2_1, agent_2_2, agent_2_3]
        agent_1_2.preferences = [agent_2_2, agent_2_3, agent_2_4]
        agent_1_3.preferences = [agent_2_5]

        test_cases = [

            # Size 1 subsets.
            ({agent_1_1}, [agent_2_1, agent_2_2, agent_2_3]),
            ({agent_1_2}, [agent_2_2, agent_2_3, agent_2_4]),
            ({agent_1_3}, [agent_2_5]),

            # Size 2 subsets.
            (
                {agent_1_1, agent_1_2},
                [agent_2_1, agent_2_2, agent_2_3, agent_2_4]
            ),
            (
                {agent_1_1, agent_1_3},
                [agent_2_1, agent_2_2, agent_2_3, agent_2_5]
            ),
            (
                {agent_1_2, agent_1_3},
                [agent_2_2, agent_2_3, agent_2_4, agent_2_5]
            ),

            # Size 3 subset.
            (
                {agent_1_1, agent_1_2, agent_1_3},
                [agent_2_1, agent_2_2, agent_2_3, agent_2_4, agent_2_5]
            ),
        ]

        for agent_subset, expected in test_cases:
            self.assertEqual(self.hierarchy.preferred(agent_subset), expected)

        self.assertEqual(
            self.hierarchy.all_preferred,
            [agent_2_1, agent_2_2, agent_2_3, agent_2_4, agent_2_5],
        )

    def test_set_agent_name(self):
        """Setting the agent name updates the hierarchy."""
        agent = Agent(agent_id=1, hierarchy=self.hierarchy, name='Agent')
        self.assertEqual(agent.name, 'Agent')
        agent.name = 'Bgent'
        self.assertEqual(agent.name, 'Bgent')
        self.assertEqual(self.hierarchy._agent_name_map, {agent: 'Bgent'})
        self.assertEqual(self.hierarchy.name_agent_map, {'Bgent': agent})

    def test_name_agent_map(self):
        agent_1_1 = Agent(agent_id=1, hierarchy=self.hierarchy, name='Agent')
        agent_1_2 = Agent(agent_id=2, hierarchy=self.hierarchy, name='Bgent')
        self.assertEqual(
            self.hierarchy.name_agent_map,
            {'Agent': agent_1_1, 'Bgent': agent_1_2}
        )

    def test_max_preference_length(self):

        # Level 1 Agents.
        agent_1_1 = Agent(agent_id=1, hierarchy=self.hierarchy)
        agent_1_2 = Agent(agent_id=2, hierarchy=self.hierarchy)
        agent_1_3 = Agent(agent_id=3, hierarchy=self.hierarchy)

        # Level 2 Agents.
        hierarchy2 = Hierarchy(level=2)
        agent_2_1 = Agent(agent_id=1, hierarchy=hierarchy2)
        agent_2_2 = Agent(agent_id=2, hierarchy=hierarchy2)
        agent_2_3 = Agent(agent_id=3, hierarchy=hierarchy2)
        agent_2_4 = Agent(agent_id=4, hierarchy=hierarchy2)
        agent_2_5 = Agent(agent_id=5, hierarchy=hierarchy2)

        agent_1_1.preferences = [agent_2_1, agent_2_2]
        agent_1_2.preferences = [agent_2_3, agent_2_4]
        agent_1_3.preferences = [agent_2_1, agent_2_3, agent_2_5]

        self.assertEqual(self.hierarchy.max_preferences_length, 3)

    def test_has_agent_with_id(self):
        Agent(agent_id=1, hierarchy=self.hierarchy)
        self.assertEqual(self.hierarchy.has_agent_with_id(1), True)
        self.assertEqual(self.hierarchy.has_agent_with_id(2), False)

    def test_upper_capacity_sum(self):
        Agent(agent_id=1, hierarchy=self.hierarchy, capacities=[0, 1])
        Agent(agent_id=2, hierarchy=self.hierarchy, capacities=[0, 10])
        Agent(agent_id=3, hierarchy=self.hierarchy, capacities=[0, 100])
        self.assertEqual(self.hierarchy.upper_capacity_sum, 111)
