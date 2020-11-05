import csv
import os.path
import shutil
import textwrap
import unittest
from datetime import datetime

from alloa.run import run_project_allocation


class TestRun(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.output_dir = os.path.join(
            self.test_dir, 'data', 'unmatched_student', 'output'
        )
        self.current_date = datetime.today().strftime('%d%m%y')

    def tearDown(self):
        shutil.rmtree(self.output_dir)

    def test_run_project_allocation_unmatched_student(self):
        run_project_allocation('tests/data/unmatched_student/alloa.conf')
        allocation_filepath = os.path.join(
            self.output_dir, f'allocation_{self.current_date}.csv'
        )
        profile_filepath = os.path.join(
            self.output_dir, f'allocation_profile_{self.current_date}.txt'
        )
        self.assertTrue(os.path.isfile(allocation_filepath))
        self.assertTrue(os.path.isfile(profile_filepath))

        with open(allocation_filepath, 'r') as allocation:
            reader = csv.reader(allocation)
            rows = list(reader)
            column_names = rows.pop(0)
            self.assertEqual(
                column_names,
                [
                    'Level 1 Agent Name',
                    'Level 1 Agent Name',
                    'Level 2 Agent Name',
                    'Level 1 Agent Rank',
                    'Level 2 Agent Rank'
                ]
            )
            # Nine students should be assigned a project.
            # One student is left out.
            self.assertEqual(len(rows), 10)
            number_of_assigned_students = len([row for row in rows if row[1]])
            self.assertEqual(number_of_assigned_students, 9)

        with open(profile_filepath, 'r') as profile:
            profile_content = profile.read()

        self.assertEqual(
            profile_content,
            textwrap.dedent(
                '''\
                Total number of assigned level 1 agents is 9
                Total cost of assignment is 90288
            
                Level 1 Preference Count
                Number of level 2 agents that were choice #1: 7
                Number of level 2 agents that were choice #2: 2
                Number of level 2 agents that were choice #3: 0
            
                Level 2 Preference Count
                Number of level 3 agents that were choice #1: 9
                '''
            )
        )
