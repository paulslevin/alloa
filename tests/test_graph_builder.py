import unittest
from pathlib import Path

from alloa.costs import spa_cost
from alloa.files import FileReader
from alloa.graph_builder import GraphBuilder


class TestGraphBuilder(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.input_dir = Path(
            self.test_dir, 'data', 'unmatched_student', 'input'
        )
        self.student_file_data = FileReader.parse(
            csv_file=Path(self.input_dir, 'students.csv'), level=1
        )
        self.project_file_data = FileReader.parse(
            csv_file=Path(self.input_dir, 'projects.csv'), level=2
        )
        self.academic_file_data = FileReader.parse(
            csv_file=Path(self.input_dir, 'academics.csv'), level=3
        )
        self.graph_builder = GraphBuilder(
            file_data_objects=[
                self.student_file_data,
                self.project_file_data,
                self.academic_file_data
            ],
            cost=spa_cost
        )

    def test_create_agents(self):
        self.graph_builder.create_agents()
        academic_hierarchy = self.graph_builder.hierarchies[2]
        self.assertEqual(len(academic_hierarchy.agents), 2)
        academic_test_cases = [
            ('Academic1', [], [0, 2]),
            ('Academic2', [], [0, 7]),
        ]
        for academic, test_case in zip(
            academic_hierarchy.agents, academic_test_cases
        ):
            self.assertEqual(academic.name, test_case[0])
            self.assertEqual(academic.preferences, test_case[1])
            self.assertEqual(academic.capacities, test_case[2])
        academic1, academic2 = academic_hierarchy.agents

        project_hierarchy = self.graph_builder.hierarchies[1]
        self.assertEqual(len(project_hierarchy.agents), 5)
        project_test_cases = [
            ('Project1', [academic2], [0, 2]),
            ('Project2', [academic2], [0, 3]),
            ('Project3', [academic2], [0, 3]),
            ('Project4', [academic1], [0, 2]),
            ('Project5', [academic1], [0, 2]),
        ]
        for project, test_case in zip(
            project_hierarchy.agents, project_test_cases
        ):
            self.assertEqual(project.name, test_case[0])
            self.assertEqual(project.preferences, test_case[1])
            self.assertEqual(project.capacities, test_case[2])
        project1, project2, project3, project4, project5 = (
            project_hierarchy.agents
        )

        student_hierarchy = self.graph_builder.hierarchies[0]
        self.assertEqual(len(student_hierarchy.agents), 10)
        student_test_cases = [
            ('Firstname1 Lastname1', [project2, project3, project1], [0, 1]),
            ('Firstname2 Lastname2', [project2, project3, project4], [0, 1]),
            ('Firstname3 Lastname3', [project2, project1, project4], [0, 1]),
            ('Firstname4 Lastname4', [project3, project2, project1], [0, 1]),
            ('Firstname5 Lastname5', [project1, project2, project3], [0, 1]),
            ('Firstname6 Lastname6', [project1, project2, project4], [0, 1]),
            ('Firstname7 Lastname7', [project4, project5, project3], [0, 1]),
            ('Firstname8 Lastname8', [project4, project2, project3], [0, 1]),
            ('Firstname9 Lastname9', [project1, project4, project5], [0, 1]),
            ('Firstname10 Lastname10', [project1, project2, project5], [0, 1]),
        ]
        for project, test_case in zip(
            student_hierarchy.agents, student_test_cases
        ):
            self.assertEqual(project.name, test_case[0])
            self.assertEqual(project.preferences, test_case[1])
            self.assertEqual(project.capacities, test_case[2])

    def test_build_graph(self):
        graph = self.graph_builder.build_graph()
        graph.populate_all_edges()
        graph.compute_flow()
        self.assertEqual(graph.flow_cost, 90288)
