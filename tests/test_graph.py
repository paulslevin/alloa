from collections import OrderedDict
from alloa.agents import Agent, Hierarchy
from alloa.graph import AgentNode, AllocationGraph
import networkx as nx
import unittest
from alloa.costs import spa_cost
from alloa.utils.enums import GraphElement, Polarity


POSITIVE = Polarity.POSITIVE
NEGATIVE = Polarity.NEGATIVE

SOURCE = GraphElement.SOURCE
SINK = GraphElement.SINK


class TestAgentNode(unittest.TestCase):
    def setUp(self):
        self.hierarchy = Hierarchy(level='1')
        self.agent = Agent(agent_id='1')
        self.positive_node = AgentNode(agent=self.agent, polarity=POSITIVE)
        self.negative_node = AgentNode(agent=self.agent, polarity=NEGATIVE)

    def test___str__(self):
        self.assertEqual(str(self.positive_node), 'AGENT_1(+)')
        self.assertEqual(str(self.negative_node), 'AGENT_1(-)')

    def test___hash__(self):
        other_positive_node = AgentNode(agent=self.agent, polarity=POSITIVE)
        self.assertEqual(hash(self.positive_node), hash(other_positive_node))

    def test___eq__(self):
        self.positive_node2 = AgentNode(agent=self.agent, polarity=POSITIVE)
        self.assertEqual(self.positive_node, self.positive_node2)
        self.negative_node2 = AgentNode(agent=self.agent, polarity=NEGATIVE)
        self.assertEqual(self.negative_node, self.negative_node2)

    def test___neq__(self):
        self.assertNotEqual(self.positive_node, self.negative_node)


class TestAllocationGraph(unittest.TestCase):
    """Example from paper."""

    def setUp(self):
        self.cost = spa_cost

        self.students = Hierarchy(level=1)
        self.projects = Hierarchy(level=2)
        self.supervisors = Hierarchy(level=3)

        self.supervisor1 = Agent(
            agent_id='1',
            capacities=(1, 2),
            name='Supervisor 1'
        )
        self.supervisor2 = Agent(
            agent_id='2',
            capacities=(0, 2),
            name='Supervisor 2'
        )
        self.supervisor3 = Agent(
            agent_id='3',
            capacities=(0, 2),
            name='Supervisor 3'
        )
        self.supervisor4 = Agent(
            agent_id='4',
            capacities=(0, 2),
            name='Supervisor 4'
        )
        self.supervisors.agents = [
            self.supervisor1,
            self.supervisor2,
            self.supervisor3,
            self.supervisor4
        ]

        self.project1 = Agent(
            agent_id='5',
            capacities=(0, 2),
            preferences=[
                [self.supervisor1, self.supervisor2]
            ],
            name='Project 1'
        )
        self.project2 = Agent(
            agent_id='6',
            capacities=(0, 2),
            preferences=[
                [self.supervisor2, self.supervisor3],
                [self.supervisor1, self.supervisor4]
            ],
            name='Project 2'
        )
        self.projects.agents = [self.project1, self.project2]

        self.student1 = Agent(
            agent_id='7',
            capacities=(0, 1),
            preferences=[self.project1, self.project2],
            name='Student 1'
        )
        self.student2 = Agent(
            agent_id='8',
            capacities=(0, 1),
            preferences=[self.project2],
            name='Student 2'
        )
        self.student3 = Agent(
            agent_id='9',
            capacities=(0, 1),
            preferences=[self.project1, self.project2],
            name='Student 3'
        )
        self.students.agents = [self.student1, self.student2, self.student3]

        self.graph = AllocationGraph.with_edges(
            hierarchies=[
                self.students,
                self.projects,
                self.supervisors
            ],
            cost=self.cost
        )
        self.source = self.graph.source
        self.sink = self.graph.sink

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

    def test_hierarchies(self):
        self.assertEqual(
            self.graph.hierarchies,
            [self.students, self.projects, self.supervisors]
        )

    def test_number_of_hierarchies(self):
        self.assertEqual(self.graph.number_of_hierarchies, 3)

    def test_first_level_agents(self):
        self.assertEqual(
            self.graph.first_level_agents,
            [self.student1, self.student2, self.student3]
        )

    def test_last_level_agents(self):
        self.assertEqual(
            self.graph.last_level_agents,
            [
                self.supervisor1,
                self.supervisor2,
                self.supervisor3,
                self.supervisor4
            ]
        )

    def test_min_upper_capacity_sum(self):
        self.assertEqual(self.graph.min_upper_capacity_sum, 3)

    def test_intermediate_hierarchies(self):
        self.assertEqual(
            self.graph.intermediate_hierarchies(0),
            [self.students, self.projects]
        )
        self.assertEqual(
            self.graph.intermediate_hierarchies(self.students.level),
            [self.projects]
        )
        self.assertEqual(
            self.graph.intermediate_hierarchies(self.projects.level), []
        )
        self.assertEqual(
            self.graph.intermediate_hierarchies(self.supervisors.level), []
        )
        self.assertEqual(self.graph.intermediate_hierarchies(4), [])

    def test_populate_edges_from_source(self):
        self.graph.populate_edges_from_source()
        positive_nodes = [
            AgentNode(self.student1, POSITIVE),
            AgentNode(self.student2, POSITIVE),
            AgentNode(self.student3, POSITIVE)
        ]
        expected = {p: {'weight': 256} for p in positive_nodes}
        self.assertEqual(self.graph[self.source], expected)

    def test_populate_edges_to_sink(self):
        self.graph.populate_edges_to_sink()
        negative_nodes = [
            AgentNode(self.supervisor1, NEGATIVE),
            AgentNode(self.supervisor2, NEGATIVE),
            AgentNode(self.supervisor3, NEGATIVE),
            AgentNode(self.supervisor3, NEGATIVE)
        ]
        for n in negative_nodes:
            self.assertEqual(self.graph[n], {self.sink: {'weight': 1}})

    # def test_populate_internal_edges(self):
    #     self.graph.populate_internal_edges()
    #
    #     for subgraph in self.graph.subgraphs:
    #         # Get subgraph of allocation graph with same nodes as the
    #         # HierarchyGraph object.
    #         actual = self.graph.subgraph(subgraph.nodes)
    #
    #         # The graphs should have the same edge data.
    #         self.assertCountEqual(
    #             actual.edges(data=True),
    #             subgraph.edges(data=True)
    #         )

    def test_glue_students_to_projects(self):
        self.graph.glue(self.students)
        self.assertFalse(
            self.graph.has_edge(
                AgentNode(self.student2, NEGATIVE),
                AgentNode(self.project1, POSITIVE),
            )
        )
        test_cases = [
            (
                AgentNode(self.student1, NEGATIVE),
                AgentNode(self.project1, POSITIVE),
                {'weight': 16}
            ),
            (
                AgentNode(self.student1, NEGATIVE),
                AgentNode(self.project2, POSITIVE),
                {'weight': 64}
            ),
            (
                AgentNode(self.student2, NEGATIVE),
                AgentNode(self.project2, POSITIVE),
                {'weight': 16}
            ),
            (
                AgentNode(self.student3, NEGATIVE),
                AgentNode(self.project1, POSITIVE),
                {'weight': 16}
            ),
            (
                AgentNode(self.student3, NEGATIVE),
                AgentNode(self.project2, POSITIVE),
                {'weight': 64}
            ),
        ]
        for negative_node, positive_node, edge_data in test_cases:
            self.assertEqual(
                self.graph[negative_node][positive_node], edge_data
            )

    def test_glue_projects_to_supervisors(self):
        self.graph.glue(self.projects)

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
            (
                AgentNode(self.project1, NEGATIVE),
                AgentNode(self.supervisor1, POSITIVE),
                {'weight': 1}
            ),
            (
                AgentNode(self.project1, NEGATIVE),
                AgentNode(self.supervisor2, POSITIVE),
                {'weight': 1}
            ),
            (
                AgentNode(self.project2, NEGATIVE),
                AgentNode(self.supervisor1, POSITIVE),
                {'weight': 4}
            ),
            (
                AgentNode(self.project2, NEGATIVE),
                AgentNode(self.supervisor2, POSITIVE),
                {'weight': 1}
            ),
            (
                AgentNode(self.project2, NEGATIVE),
                AgentNode(self.supervisor3, POSITIVE),
                {'weight': 1}
            ),
            (
                AgentNode(self.project2, NEGATIVE),
                AgentNode(self.supervisor4, POSITIVE),
                {'weight': 4}
            ),
        ]

        for negative_node, positive_node, edge_data in test_cases:
            self.assertEqual(
                self.graph[negative_node][positive_node],
                edge_data
            )

    def test_graph_consists_of_agent_nodes(self):
        self.graph.populate_all_edges()
        self.assertEqual(len(self.graph.nodes), 20)
        for node in self.graph.nodes:
            self.assertIsInstance(node, AgentNode)

    def test_compute_flow(self):
        self.graph.populate_all_edges()
        self.graph.compute_flow()
        self.assertEqual(self.graph.flow_cost, 822)
        self.assertEqual(self.graph.max_flow, 3)

    def test_simplify_flow(self):
        """Use example flow from paper."""

        # Make sure this flow satisfies the constraints.
        self.graph.populate_all_edges()
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
            self.project1: OrderedDict([
                (self.supervisor1, 1), (self.supervisor2, 1)
            ]),
            self.project2: OrderedDict([
                (self.supervisor3, 1)
            ]),
        }
        self.assertEqual(self.graph.simple_flow, expected)

    def test_allocate(self):
        self.graph.populate_all_edges()
        self.graph.flow = self.example_flow
        self.graph.simplify_flow()
        self.graph.allocate()
        # Every agent in this example got their first choice.
        self.assertEqual(
            self.graph.allocation,
            {
                self.student1: [
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
                ],
            }
        )

    def test_single_allocation(self):
        self.graph.populate_all_edges()
        self.graph.flow = self.example_flow
        self.graph.simplify_flow()
        flow = {
            agent: dict(d) for agent, d in self.graph.simple_flow.items()
        }

        self.assertEqual(
            self.graph.single_allocation(self.student1, flow),
            [(self.project1, 1), (self.supervisor1, 1)]
        )
        self.assertEqual(
            self.graph.single_allocation(self.student2, flow),
            [(self.project2, 1), (self.supervisor3, 1)]
        )
        self.assertEqual(
            self.graph.single_allocation(self.student3, flow),
            [(self.project1, 1), (self.supervisor2, 1)]
        )

    def test_costs(self):

        for agent in [self.student1, self.student2, self.student3]:
            self.assertEqual(
                self.cost(
                    self.source, AgentNode(agent, POSITIVE), self.graph
                ),
                256
            )

            self.assertEqual(
                self.cost(
                    AgentNode(agent, POSITIVE),
                    AgentNode(agent, NEGATIVE),
                    self.graph
                ),
                0
            )

        # self.assertEqual(
        #     self.costs.exponent(
        #         AgentNode(self.student1, NEGATIVE),
        #         AgentNode(self.project1, POSITIVE)
        #     ),
        #     2
        # )
        #
        # self.assertEqual(
        #     self.costs.exponent(
        #         AgentNode(self.student1, NEGATIVE),
        #         AgentNode(self.project2, POSITIVE)
        #     ),
        #     3
        # )
        #
        # self.assertEqual(
        #     self.costs.exponent(
        #         AgentNode(self.project1, NEGATIVE),
        #         AgentNode(self.supervisor1, POSITIVE)
        #     ),
        #     0
        # )
        #
        # self.assertEqual(
        #     self.costs.exponent(
        #         AgentNode(self.project1, NEGATIVE),
        #         AgentNode(self.supervisor2, POSITIVE)
        #     ),
        #     0
        # )
        #
        # self.assertEqual(
        #     self.costs.exponent(
        #         AgentNode(self.project1, NEGATIVE),
        #         AgentNode(self.supervisor3, POSITIVE)
        #     ),
        #     -1
        # )
