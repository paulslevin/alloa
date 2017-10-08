from   collections import OrderedDict
from   itertools import permutations
from   modules.agents import Agent, Hierarchy
from   modules.graph import AgentNode, HierarchyGraph, AllocationDatum
from   modules.graph import AllocationGraph
import networkx as nx
import unittest
from   costs import SPACosts
from   utils.enums import GraphElement, Polarity


POSITIVE = Polarity.POSITIVE
NEGATIVE = Polarity.NEGATIVE

SOURCE = GraphElement.SOURCE
SINK   = GraphElement.SINK


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

    def test___hash__(self):
        other_positive_node = AgentNode(agent=self.agent, polarity=POSITIVE)
        self.assertEqual(hash(self.positive_node), hash(other_positive_node))

    def test___eq__(self):
        self.positive_node2 = AgentNode(agent=self.agent, polarity=POSITIVE)
        self.assertEquals(self.positive_node, self.positive_node2)
        self.negative_node2 = AgentNode(agent=self.agent, polarity=NEGATIVE)
        self.assertEquals(self.negative_node, self.negative_node2)

    def test___neq__(self):
        self.assertNotEqual(self.positive_node, self.negative_node)

    def test_lexicographic_ordering(self):
        hierarchy1 = self.hierarchy
        hierarchy2 = Hierarchy(level=2)
        agent_1_1 = self.agent
        agent_1_2 = Agent(id=2, hierarchy=hierarchy1)
        agent_2_1 = Agent(id=1, hierarchy=hierarchy2)
        agent_2_2 = Agent(id=2, hierarchy=hierarchy2)
        
        agent_1_1_p = self.positive_node
        agent_1_1_n = self.negative_node
        agent_1_2_p = AgentNode(agent=agent_1_2, polarity=POSITIVE)
        agent_1_2_n = AgentNode(agent=agent_1_2, polarity=NEGATIVE)
        agent_2_1_p = AgentNode(agent=agent_2_1, polarity=POSITIVE)
        agent_2_1_n = AgentNode(agent=agent_2_1, polarity=NEGATIVE)
        agent_2_2_p = AgentNode(agent=agent_2_2, polarity=POSITIVE)
        agent_2_2_n = AgentNode(agent=agent_2_2, polarity=NEGATIVE)

        expected = [agent_1_1_p, agent_1_1_n, agent_1_2_p, agent_1_2_n,
                    agent_2_1_p, agent_2_1_n, agent_2_2_p, agent_2_2_n,]

        for permutation in permutations(expected, 8):
            self.assertEqual(sorted(permutation), expected)

    def test_level(self):
        self.assertEqual(self.positive_node.level, 1)
        self.assertEqual(self.negative_node.level, 1)


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

    def test___iter__(self):
        agents = [a for a in self.graph]
        self.assertEqual(agents, [self.agent_2_1, self.agent_2_3])

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


class TestAllocationGraph(unittest.TestCase):
    '''Example from paper.'''
    def setUp(self):
        self.students    = Hierarchy(level=1)
        self.projects    = Hierarchy(level=2)
        self.supervisors = Hierarchy(level=3)

        self.supervisor1 = Agent(id=1, hierarchy=self.supervisors, 
                                 capacities=(1,2), name='Supervisor 1')
        self.supervisor2 = Agent(id=2, hierarchy=self.supervisors,
                                 capacities=(0,2), name='Supervisor 2')
        self.supervisor3 = Agent(id=3, hierarchy=self.supervisors,
                                 capacities=(0,2), name='Supervisor 3')
        self.supervisor4 = Agent(id=4, hierarchy=self.supervisors,
                                 capacities=(0,2), name='Supervisor 4')

        self.project1 = Agent(id=1, hierarchy=self.projects, 
                              capacities=(0,2), 
                              preferences=[[self.supervisor1, self.supervisor2]],
                              name='Project 1')
        self.project2 = Agent(id=2, hierarchy=self.projects, 
                              capacities=(0,2),
                              preferences=[[self.supervisor2, self.supervisor3],
                                           [self.supervisor1, self.supervisor4]],
                              name='Project 2')

        self.student1 = Agent(id=1, hierarchy=self.students, capacities=(0,1),
                              preferences=[self.project1, self.project2],
                              name='Student 1')
        self.student2 = Agent(id=2, hierarchy=self.students, capacities=(0,1),
                              preferences=[self.project2],
                              name='Student 2')
        self.student3 = Agent(id=3, hierarchy=self.students, capacities=(0,1),
                              preferences=[self.project1, self.project2],
                              name='Student 3')

        self.student_subgraph = HierarchyGraph.full_subgraph(
            self.students, [self.student1, self.student2, self.student3],
        )
        self.project_subgraph = HierarchyGraph.full_subgraph(
            self.projects, [self.project1, self.project2],
        )
        self.supervisor_subgraph = HierarchyGraph.full_subgraph(
            self.supervisors, [self.supervisor1, self.supervisor2,
                               self.supervisor3, self.supervisor4],
        )

        self.graph = AllocationGraph([self.student_subgraph,
                                      self.project_subgraph,
                                      self.supervisor_subgraph])
        self.source = self.graph.source
        self.sink   = self.graph.sink

        self.costs = SPACosts(self.graph)

        self.example_flow = {
            self.source: OrderedDict((
                (AgentNode(self.student1, POSITIVE), 1),
                (AgentNode(self.student2, POSITIVE), 1),
                (AgentNode(self.student3, POSITIVE), 1),
            )),
            AgentNode(self.student1, POSITIVE): OrderedDict((
                (AgentNode(self.student1, NEGATIVE), 1),
            )),
            AgentNode(self.student2, POSITIVE): OrderedDict((
                (AgentNode(self.student2, NEGATIVE), 1),
            )),
            AgentNode(self.student3, POSITIVE): OrderedDict((
                (AgentNode(self.student3, NEGATIVE), 1),
            )),
            AgentNode(self.student1, NEGATIVE): OrderedDict((
                (AgentNode(self.project1, POSITIVE), 1),
                (AgentNode(self.project2, POSITIVE), 0),
            )),
            AgentNode(self.student2, NEGATIVE): OrderedDict((
                (AgentNode(self.project2, POSITIVE), 1),
            )),
            AgentNode(self.student3, NEGATIVE): OrderedDict((
                (AgentNode(self.project1, POSITIVE), 1),
                (AgentNode(self.project2, POSITIVE), 0),
            )),
            AgentNode(self.project1, POSITIVE): OrderedDict((
                (AgentNode(self.project1, NEGATIVE), 2),
            )),
            AgentNode(self.project2, POSITIVE): OrderedDict((
                (AgentNode(self.project2, NEGATIVE), 1),
            )),
            AgentNode(self.project1, NEGATIVE): OrderedDict((
                (AgentNode(self.supervisor1, POSITIVE), 1),
                (AgentNode(self.supervisor2, POSITIVE), 1),
            )),
            AgentNode(self.project2, NEGATIVE): OrderedDict((
                (AgentNode(self.supervisor1, POSITIVE), 0),
                (AgentNode(self.supervisor2, POSITIVE), 0),
                (AgentNode(self.supervisor3, POSITIVE), 1),
                (AgentNode(self.supervisor4, POSITIVE), 0),
            )),
            AgentNode(self.supervisor1, POSITIVE): OrderedDict((
                (AgentNode(self.supervisor1, NEGATIVE), 0),
            )),
            AgentNode(self.supervisor2, POSITIVE): OrderedDict((
                (AgentNode(self.supervisor2, NEGATIVE), 1),
            )),
            AgentNode(self.supervisor3, POSITIVE): OrderedDict((
                (AgentNode(self.supervisor3, NEGATIVE), 1),
            )),
            AgentNode(self.supervisor4, POSITIVE): OrderedDict((
                (AgentNode(self.supervisor4, NEGATIVE), 0),
            )),
            AgentNode(self.supervisor1, NEGATIVE): OrderedDict((
                (self.sink, 1),
            )),
            AgentNode(self.supervisor2, NEGATIVE): OrderedDict((
                (self.sink, 1),
            )),
            AgentNode(self.supervisor3, NEGATIVE): OrderedDict((
                (self.sink, 1),
            )),
            AgentNode(self.supervisor4, NEGATIVE): OrderedDict((
                (self.sink, 0),
            )),
        }

    def test___str__(self):
        self.assertEqual(str(self.graph), 'ALLOCATION_GRAPH(3)')

    def test___repr__(self):
        self.assertEqual(
            repr(self.graph), 
            'AllocationGraph(subgraphs=[HIERARCHY_GRAPH_1, HIERARCHY_GRAPH_2, HIERARCHY_GRAPH_3])'
        )

    def test_level_nodes_map(self):
        student_nodes    = self.student_subgraph.nodes
        supervisor_nodes = self.supervisor_subgraph.nodes
        project_nodes    = self.project_subgraph.nodes
        self.assertEqual(
            self.graph.level_nodes_map, 
            {0: [self.source],
             1: list(student_nodes),
             2: list(project_nodes),
             3: list(supervisor_nodes),
             4: [self.sink]}
        )

    def test_first_subgraph(self):
        self.assertEqual(self.graph.first_subgraph,
                         self.student_subgraph)

    def test_last_subgraph(self):
        self.assertEqual(self.graph.last_subgraph, self.supervisor_subgraph)

    def test_hierarchies(self):
        self.assertEqual(self.graph.hierarchies,
                         [self.students, self.projects, self.supervisors])

    def test_number_of_hierarchies(self):
        self.assertEqual(self.graph.number_of_hierarchies, 3)

    def test_first_level_agents(self):
        self.assertEqual(self.graph.first_level_agents,
                         [self.student1, self.student2, self.student3])

    def test_last_level_agents(self):
        self.assertEqual(self.graph.last_level_agents,
                         [self.supervisor1, self.supervisor2, 
                          self.supervisor3, self.supervisor4])

    def test_last_level(self):
        self.assertEqual(self.graph.last_level, 3)

    def test_min_upper_capacity_sum(self):
        self.assertEqual(self.graph.min_upper_capacity_sum, 3)
        
    def test_intermediate_hierarchies(self):
        self.assertEqual(self.graph.intermediate_hierarchies(self.source),
                         [self.students, self.projects])
        for node in self.graph.level_nodes_map[1]:
            self.assertEqual(self.graph.intermediate_hierarchies(node),
                             [self.projects])
        for node in self.graph.level_nodes_map[2]:
            self.assertEqual(self.graph.intermediate_hierarchies(node), [])
        for node in self.graph.level_nodes_map[3]:
            self.assertEqual(self.graph.intermediate_hierarchies(node), [])
        for node in self.graph.level_nodes_map[4]:
            self.assertEqual(self.graph.intermediate_hierarchies(node), [])
        
    def test_populate_edges_from_source(self):
        self.graph.populate_edges_from_source(self.costs.cost)
        positive_nodes = [AgentNode(self.student1, POSITIVE),
                          AgentNode(self.student2, POSITIVE),
                          AgentNode(self.student3, POSITIVE)]
        expected = {p: {'weight': 256} for p in positive_nodes}
        self.assertEqual(self.graph[self.source], expected)

    def test_populate_edges_to_sink(self):
        self.graph.populate_edges_to_sink(self.costs.cost)
        negative_nodes = [AgentNode(self.supervisor1, NEGATIVE),
                          AgentNode(self.supervisor2, NEGATIVE),
                          AgentNode(self.supervisor3, NEGATIVE),
                          AgentNode(self.supervisor3, NEGATIVE)]
        for n in negative_nodes:
            self.assertEqual(self.graph[n], {self.sink: {'weight': 1}})

    def test_populate_internal_edges(self):
        self.graph.populate_internal_edges()

        for subgraph in self.graph.subgraphs:
            # Get subgraph of allocation graph with same nodes as the
            # HierarchyGraph object.
            actual = self.graph.subgraph(subgraph.nodes)

            # The graphs should have the same edge data.
            self.assertItemsEqual(actual.edges(data=True),
                                  subgraph.edges(data=True))

    def test_glue_students_to_projects(self):
        self.graph.glue(
            self.student_subgraph, self.project_subgraph, self.costs.cost
        )
        self.assertFalse(
            self.graph.has_edge(
                AgentNode(self.student2, NEGATIVE),
                AgentNode(self.project1, POSITIVE),
             )
        )
        test_cases = [
            (AgentNode(self.student1, NEGATIVE),
             AgentNode(self.project1, POSITIVE),
             {'weight': 16}),
            (AgentNode(self.student1, NEGATIVE),
             AgentNode(self.project2, POSITIVE),
             {'weight': 64 }),
            (AgentNode(self.student2, NEGATIVE),
             AgentNode(self.project2, POSITIVE),
             {'weight': 16}),
            (AgentNode(self.student3, NEGATIVE),
             AgentNode(self.project1, POSITIVE),
             {'weight': 16}),
            (AgentNode(self.student3, NEGATIVE),
             AgentNode(self.project2, POSITIVE),
             {'weight': 64}),
        ]
        for negative_node, positive_node, edge_data in test_cases:
            self.assertEqual(self.graph[negative_node][positive_node],
                             edge_data)

    def test_glue_projects_to_supervisors(self):
        self.graph.glue(
            self.project_subgraph, self.supervisor_subgraph, self.costs.cost
        )

        self.assertFalse(
            self.graph.has_edge(
                AgentNode(self.project1, NEGATIVE),
                AgentNode(self.supervisor3, POSITIVE),
             ),
        )
        self.assertFalse(
            self.graph.has_edge(
                AgentNode(self.project1, NEGATIVE),
                AgentNode(self.supervisor4, POSITIVE),
             ),
        )

        test_cases = [
            (AgentNode(self.project1, NEGATIVE),
             AgentNode(self.supervisor1, POSITIVE),
             {'weight': 1}),
            (AgentNode(self.project1, NEGATIVE),
             AgentNode(self.supervisor2, POSITIVE),
             {'weight': 1}),
            (AgentNode(self.project2, NEGATIVE),
             AgentNode(self.supervisor1, POSITIVE),
             {'weight': 4}),
            (AgentNode(self.project2, NEGATIVE),
             AgentNode(self.supervisor2, POSITIVE),
             {'weight': 1}),
            (AgentNode(self.project2, NEGATIVE),
             AgentNode(self.supervisor3, POSITIVE),
             {'weight': 1}),
            (AgentNode(self.project2, NEGATIVE),
             AgentNode(self.supervisor4, POSITIVE),
             {'weight': 4}),
        ]

        for negative_node, positive_node, edge_data in test_cases:
            self.assertEqual(self.graph[negative_node][positive_node],
                             edge_data)

    def test_graph_consists_of_AgentNodes(self):
        self.graph.populate_all_edges(self.costs.cost)
        self.assertEqual(len(self.graph.nodes), 20)
        for node in self.graph.nodes:
            self.assertIsInstance(node, AgentNode)

    def test_compute_flow(self):
        self.graph.populate_all_edges(self.costs.cost)
        self.graph.compute_flow()
        self.assertEqual(self.graph.flow_cost, 822)
        self.assertEqual(self.graph.max_flow, 3)

    def test_simplify_flow(self):
        '''Use example flow from paper.'''

        # Make sure this flow satisfies the constraints.
        self.graph.populate_all_edges(self.costs.cost)
        self.assertEqual(nx.cost_of_flow(self.graph, self.example_flow), 822)

        # Simplify the test flow.
        self.graph.flow = self.example_flow
        self.graph.simplify_flow()
        expected = {
            # Students 1 and 3 both get Project 1, and Student 2 gets Project 2.
            self.student1: OrderedDict([(self.project1, 1)]),
            self.student2: OrderedDict([(self.project2, 1)]),
            self.student3: OrderedDict([(self.project1, 1)]),
            # Project 1 has two students on it, and will be supervised by
            # Supervisors 1 and 2. Supervisor 3 will supervise Project 2.
            self.project1: OrderedDict([(self.supervisor1, 1),
                                        (self.supervisor2, 1)]),
            self.project2: OrderedDict([(self.supervisor3, 1)]),
        }
        self.assertEqual(self.graph.simple_flow, expected)

    def test_allocate(self):
        self.graph.populate_all_edges(self.costs.cost)
        self.graph.flow = self.example_flow
        self.graph.simplify_flow()
        self.graph.allocate()
        # Every agent in this example got their first choice.
        self.assertEqual(
            self.graph.allocation,
            {self.student1: [
                (self.project1, 1),
                (self.supervisor1, 1),
             ],
             self.student2: [
                 (self.project2, 1),
                 (self.supervisor3, 1),
             ],
             self.student3: [
                 (self.project1, 1),
                 (self.supervisor2, 1),
             ],}
        )

    def test_single_allocation(self):
        self.graph.populate_all_edges(self.costs.cost)
        self.graph.flow = self.example_flow
        self.graph.simplify_flow()
        g = ((agent, dict(d)) for agent, d in self.graph.simple_flow.iteritems())
        flow = dict(g)

        self.assertEqual(
            self.graph.single_allocation(self.student1, flow),
            [(self.project1, 1), (self.supervisor1, 1)],
        )
        self.assertEqual(
            self.graph.single_allocation(self.student2, flow),
            [(self.project2, 1), (self.supervisor3, 1)],
        )
        self.assertEqual(
            self.graph.single_allocation(self.student3, flow),
            [(self.project1, 1), (self.supervisor2, 1)],
        )
