import shutil
import unittest
from datetime import datetime
from pathlib import Path

from alloa.costs import spa_cost
from alloa.files import FileReader, FileWriter, Line
from alloa.graph_builder import GraphBuilder
from alloa.settings import parse_config


class TestLine(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.input_dir = Path(
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


class TestFileReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_dir = Path(__file__).parent
        cls.input_dir = Path(
            test_dir, 'data', 'unmatched_student', 'input'
        )
        cls.student_file_data = FileReader.parse(
            csv_file=Path(cls.input_dir, 'students.csv'), level=1
        )
        cls.project_file_data = FileReader.parse(
            csv_file=Path(cls.input_dir, 'projects.csv'), level=2
        )
        cls.academic_file_data = FileReader.parse(
            csv_file=Path(cls.input_dir, 'academics.csv'), level=3
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

    def test_file_content(self):
        self.assertEqual(
            self.student_file_data.file_content,
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
            self.project_file_data.file_content,
            [
                Line(['Project1', '0', '2', 'Academic2']),
                Line(['Project2', '0', '3', 'Academic2']),
                Line(['Project3', '0', '3', 'Academic2']),
                Line(['Project4', '0', '2', 'Academic1']),
                Line(['Project5', '0', '2', 'Academic1'])
            ]
        )

        self.assertEqual(
            self.academic_file_data.file_content,
            [
                Line(['Academic1', '0', '2']),
                Line(['Academic2', '0', '7'])
            ]
        )


class TestFileWriter(unittest.TestCase):

    output_dir = ''

    @classmethod
    def setUpClass(cls):
        test_dir = Path(__file__).parent
        input_dir = Path(test_dir, 'data', 'unmatched_student', 'input')
        cls.output_dir = Path(test_dir, 'data', 'unmatched_student', 'output')

        graph_builder = GraphBuilder(
            file_data_objects=[
                FileReader.parse(
                    csv_file=Path(input_dir, 'students.csv'), level=1
                ),
                FileReader.parse(
                    csv_file=Path(input_dir, 'projects.csv'), level=2
                ),
                FileReader.parse(
                    csv_file=Path(input_dir, 'academics.csv'), level=3
                )
            ],
            cost=spa_cost
        )

        graph = graph_builder.build_graph()
        graph.populate_all_edges()
        graph.compute_flow()
        graph.simplify_flow()
        graph.allocate()

        config = parse_config('tests/data/unmatched_student/alloa.conf')
        cls.file_writer = FileWriter(
            graph,
            config,
            [
                'Firstname1 Lastname1',
                'Firstname2 Lastname2',
                'Firstname3 Lastname3',
                'Firstname4 Lastname4',
                'Firstname5 Lastname5',
                'Firstname6 Lastname6',
                'Firstname7 Lastname7',
                'Firstname8 Lastname8',
                'Firstname9 Lastname9',
                'Firstname10 Lastname10'
            ]
        )
        cls.file_writer.parse_graph()

        cls.current_datetime = datetime.today().strftime('%y%m%d_%H%M')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.output_dir)

    def test_parse_graph(self):
        output_rows = self.file_writer.output_rows
        self.assertEqual(
            output_rows[0],
            [
                'Level 1 Agent Name',
                'Level 1 Agent Name',
                'Level 2 Agent Name',
                'Level 1 Agent Rank',
                'Level 2 Agent Rank'
            ]
        )
        for i, row in enumerate(output_rows[1:]):
            self.assertEqual(
                row[0],
                f'Firstname{i + 1} Lastname{i + 1}'
            )

    def test_write_allocations(self):
        self.file_writer.write_allocations()
        allocation_filepath = Path(
            self.output_dir, f'allocation_{self.current_datetime}.csv'
        )
        self.assertTrue(allocation_filepath.exists())

    def test_write_profile(self):
        self.file_writer.write_profile()
        profile_filepath = Path(
            self.output_dir, f'allocation_profile_{self.current_datetime}.txt'
        )
        self.assertTrue(profile_filepath.exists())
