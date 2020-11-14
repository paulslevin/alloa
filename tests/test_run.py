import csv
import shutil
import textwrap
import unittest
from datetime import datetime
from pathlib import Path

from alloa.run import run


class TestRun(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.current_datetime = datetime.today().strftime('%y%m%d_%H%M')

    def test_run_unmatched_student(self):
        run('tests/data/unmatched_student/alloa.conf')
        output_dir = Path(self.test_dir, 'data', 'unmatched_student', 'output')
        allocation_filepath = Path(
            output_dir, f'allocation_{self.current_datetime}.csv'
        )
        profile_filepath = Path(
            output_dir, f'allocation_profile_{self.current_datetime}.txt'
        )
        self.assertTrue(allocation_filepath.exists())
        self.assertTrue(profile_filepath.exists())

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
        shutil.rmtree(output_dir)

    def test_run_large_input(self):
        run('tests/data/large_input/alloa.conf')
        output_dir = Path(self.test_dir, 'data', 'large_input', 'output')
        allocation_filepath = Path(
            output_dir, f'allocation_{self.current_datetime}.csv'
        )
        profile_filepath = Path(
            output_dir, f'allocation_profile_{self.current_datetime}.txt'
        )
        self.assertTrue(allocation_filepath.exists())
        self.assertTrue(profile_filepath.exists())

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
            self.assertEqual(len(rows), 100)
            number_of_assigned_students = len([row for row in rows if row[1]])
            self.assertEqual(number_of_assigned_students, 83)

        with open(profile_filepath, 'r') as profile:
            profile_content = profile.read()

        very_large_integer = (
            '114109468242080764452269530495003366017637053027074349994495524662'
            '84452883331884019686997136321502542'
        )

        self.assertEqual(
            profile_content,
            textwrap.dedent(
                f'''\
                Total number of assigned level 1 agents is 83
                Total cost of assignment is {very_large_integer}

                Level 1 Preference Count
                Number of level 2 agents that were choice #1: 70
                Number of level 2 agents that were choice #2: 11
                Number of level 2 agents that were choice #3: 2
                Number of level 2 agents that were choice #4: 0
                Number of level 2 agents that were choice #5: 0
                Number of level 2 agents that were choice #6: 0
                Number of level 2 agents that were choice #7: 0
                Number of level 2 agents that were choice #8: 0
                Number of level 2 agents that were choice #9: 0
                Number of level 2 agents that were choice #10: 0
                Number of level 2 agents that were choice #11: 0
                Number of level 2 agents that were choice #12: 0
                Number of level 2 agents that were choice #13: 0
                Number of level 2 agents that were choice #14: 0
                Number of level 2 agents that were choice #15: 0
                Number of level 2 agents that were choice #16: 0
                Number of level 2 agents that were choice #17: 0
                Number of level 2 agents that were choice #18: 0
                Number of level 2 agents that were choice #19: 0
                Number of level 2 agents that were choice #20: 0
                Number of level 2 agents that were choice #21: 0
                Number of level 2 agents that were choice #22: 0
                Number of level 2 agents that were choice #23: 0
                Number of level 2 agents that were choice #24: 0
                Number of level 2 agents that were choice #25: 0
                Number of level 2 agents that were choice #26: 0
                Number of level 2 agents that were choice #27: 0
                Number of level 2 agents that were choice #28: 0
                Number of level 2 agents that were choice #29: 0
                Number of level 2 agents that were choice #30: 0
                Number of level 2 agents that were choice #31: 0
                Number of level 2 agents that were choice #32: 0
                Number of level 2 agents that were choice #33: 0
                Number of level 2 agents that were choice #34: 0
                Number of level 2 agents that were choice #35: 0
                Number of level 2 agents that were choice #36: 0
                Number of level 2 agents that were choice #37: 0
                Number of level 2 agents that were choice #38: 0
                Number of level 2 agents that were choice #39: 0
                Number of level 2 agents that were choice #40: 0
                Number of level 2 agents that were choice #41: 0
                Number of level 2 agents that were choice #42: 0
                Number of level 2 agents that were choice #43: 0
                Number of level 2 agents that were choice #44: 0
                Number of level 2 agents that were choice #45: 0
                Number of level 2 agents that were choice #46: 0
                Number of level 2 agents that were choice #47: 0
                Number of level 2 agents that were choice #48: 0
                Number of level 2 agents that were choice #49: 0
                Number of level 2 agents that were choice #50: 0

                Level 2 Preference Count
                Number of level 3 agents that were choice #1: 83
                '''
            )
        )
        shutil.rmtree(output_dir)
