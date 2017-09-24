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