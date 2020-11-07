from alloa.agents import Agent
from alloa.files import FileData, Line
import unittest
import os.path


class TestLine(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.input_dir = os.path.join(
            self.test_dir, 'data', 'unmatched_student', 'input'
        )

    def test_line(self):
        input_line = [
            'Agent1', '0', '1 ', '\nProject3', 'Project1\t', ' Project2'
        ]
        line = Line(input_line)
        self.assertEqual(
            line.line, ['Agent1', '0', '1', 'Project3', 'Project1', 'Project2']
        )
        self.assertEqual(line.raw_name, 'Agent1')
        self.assertEqual(line.capacities, [0, 1])
        self.assertEqual(
            line.raw_preferences, ['Project3', 'Project1', 'Project2']
        )


class TestFileData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.input_dir = os.path.join(
            cls.test_dir, 'data', 'unmatched_student', 'input'
        )
        cls.student_file_data = FileData(
            csv_file=os.path.join(cls.input_dir, 'students.csv'), level=1
        )
        cls.project_file_data = FileData(
            csv_file=os.path.join(cls.input_dir, 'projects.csv'), level=2
        )
        cls.academic_file_data = FileData(
            csv_file=os.path.join(cls.input_dir, 'academics.csv'), level=3
        )

    def test___eq__(self):
        line1 = Line([
            'Agent1', '0', '1 ', '\nProject3', 'Project1\t', ' Project2'
        ])
        line2 = Line([
            'Agent1', '0\n', ' 1', 'Project3\t', '\nProject1', 'Project2 '
        ])
        self.assertEqual(line1, line2)

    def test___repr__(self):
        self.assertEqual(repr(self.student_file_data), 'LEVEL_1_DATA')
        self.assertEqual(repr(self.project_file_data), 'LEVEL_2_DATA')
        self.assertEqual(repr(self.academic_file_data), 'LEVEL_3_DATA')

    def test_create_agents(self):
        self.academic_file_data.create_agents()
        academic_hierarchy = self.academic_file_data.hierarchy
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

        self.project_file_data.create_agents(
            next_hierarchy=self.academic_file_data.hierarchy
        )
        project_hierarchy = self.project_file_data.hierarchy
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

        self.student_file_data.create_agents(
            next_hierarchy=self.project_file_data.hierarchy
        )
        student_hierarchy = self.student_file_data.hierarchy
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

    def test_results(self):
        self.assertEqual(
            self.student_file_data.results(),
            [
                Line([
                    'Firstname1 Lastname1',
                    '0', '1',
                    'Project2', 'Project3', 'Project1'
                ]),
                Line([
                    'Firstname2 Lastname2',
                    '0', '1',
                    'Project2', 'Project3', 'Project4'
                ]),
                Line([
                    'Firstname3 Lastname3',
                    '0', '1',
                    'Project2', 'Project1', 'Project4'
                ]),
                Line([
                    'Firstname4 Lastname4',
                    '0', '1',
                    'Project3', 'Project2', 'Project1'
                ]),
                Line([
                    'Firstname5 Lastname5',
                    '0', '1',
                    'Project1', 'Project2', 'Project3'
                ]),
                Line([
                    'Firstname6 Lastname6',
                    '0', '1',
                    'Project1', 'Project2', 'Project4'
                ]),
                Line([
                    'Firstname7 Lastname7',
                    '0', '1',
                    'Project4', 'Project5', 'Project3'
                ]),
                Line([
                    'Firstname8 Lastname8',
                    '0', '1',
                    'Project4', 'Project2', 'Project3'
                ]),
                Line([
                    'Firstname9 Lastname9',
                    '0', '1',
                    'Project1', 'Project4', 'Project5'
                ]),
                Line([
                    'Firstname10 Lastname10',
                    '0', '1',
                    'Project1', 'Project2', 'Project5'
                ]),
            ]
        )

        self.assertEqual(
            self.project_file_data.results(),
            [
                Line(['Project1', '0', '2', 'Academic2']),
                Line(['Project2', '0', '3', 'Academic2']),
                Line(['Project3', '0', '3', 'Academic2']),
                Line(['Project4', '0', '2', 'Academic1']),
                Line(['Project5', '0', '2', 'Academic1'])
            ]
        )

        self.assertEqual(
            self.academic_file_data.results(),
            [
                Line(['Academic1', '0', '2']),
                Line(['Academic2', '0', '7'])
            ]
        )
