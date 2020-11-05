import csv
import textwrap
from typing import Dict, List, Union

from alloa.files import DataSequence, FileData
from alloa.settings import parse_config


class Allocation:
    def __init__(self, config: Dict) -> None:
        self.config = config

        self.level_paths = self.config['level_paths']
        self.allocation_path = self.config['allocation_path']
        self.allocation_profile_path = self.config['allocation_profile_path']
        self.randomised = self.config['randomised']

        self.data_objects = []

        for i, path in enumerate(self.level_paths):
            self.data_objects.append(
                FileData(path, level=i + 1, randomise=self.randomised)
            )

        self.sequence = DataSequence(*self.data_objects)
        self.number_of_levels = len(self.sequence)
        self.graph = self.sequence.get_graph()

    def print_intro_string(self) -> None:
        print(textwrap.dedent('''
            ################################################################
            #                                                              #
            # This is alloa by:                                            #
            #   Mante Zelvyte                                              #
            #   Uli Kraehmer                                               #
            #       ulrich.kraehmer@tu-dresden.de                          #
            #       https://tu-dresden.de/mn/math/geometrie/kraehmer       #
            #   Paul Slevin                                                #
            #       pt.slevin@gmail.com                                    #
            #                                                              #
            # Runtime with 100 agents at each hierarchy is a few ms        #
            #                                                              #
            ################################################################
        '''))
        for i in range(self.number_of_levels):
            num_of_agents = self.graph.hierarchies[i].number_of_agents
            print(f'{num_of_agents} agents of hierarchy {i + 1}')

    def setup_and_run_allocation(self) -> None:
        self.graph.populate_all_edges()
        self.graph.compute_flow()
        self.graph.simplify_flow()
        self.graph.allocate()

    def write_allocations(self) -> None:
        with open(self.allocation_path, 'w') as allocation:
            writer = csv.writer(allocation, delimiter=',')
            for row in self.allocation:
                writer.writerow(row)

    def write_profile(self) -> None:
        with open(self.allocation_profile_path, 'w') as profile:
            profile.writelines([
                f'Total number of assigned level 1 agents '
                f'is {self.graph.max_flow}\n',
                f'Total cost of assignment is {self.graph.flow_cost}\n'
            ])
            for i in range(self.number_of_levels - 1):
                profile.write(
                    f'\nLevel {i + 1} Preference Count\n'
                )
                for j in range(
                    self.graph.hierarchies[i].max_preferences_length
                ):
                    split_point = self.number_of_levels
                    column = [row[split_point + i] for row in self.allocation]
                    count = column.count(j + 1)
                    profile.write(
                        f'Number of level {i + 2} agents that were '
                        f'choice #{j + 1}: {count}\n'
                    )

    @property
    def allocation(self) -> List[List[Union[str, int]]]:

        if not self.graph.first_level_agents:
            return []

        allocation = self.graph.allocation

        first_agent = self.graph.first_level_agents[0]
        num_of_agents = len(allocation[first_agent]) // 2 + 1
        name_columns, rank_columns = [], []
        for i in range(num_of_agents):
            name_columns.append(f'Level {i + 1} Agent Name')
            rank_columns.append(f'Level {i + 1} Agent Rank')
        column_names = ['Level 1 Agent Name'] + name_columns + rank_columns

        number_of_columns = len(column_names)

        rows = []

        for agent in self.graph.first_level_agents:
            row = [agent.name]
            row.extend(
                datum.agent.name for datum in allocation[agent]
            )
            row.extend(
                datum.rank for datum in allocation[agent]
            )

            # Extend row to correct length in case agent is not allocated.
            row.extend(None for _ in range(number_of_columns - len(row)))

            rows.append(row)

        # Sort so the output CSV file has the same order as the input CSV file
        # for first level agents.
        first_level_agent_names = [
            x.raw_name for x in self.data_objects[0].results()
        ]

        def _key(_row):
            return first_level_agent_names.index(_row[0])

        rows = sorted(rows, key=_key)
        return [column_names] + rows


def run_project_allocation(config_filename: str) -> None:
    config = parse_config(config_filename)
    allocation = Allocation(config)
    allocation.setup_and_run_allocation()
    allocation.write_allocations()
    allocation.write_profile()
    allocation.print_intro_string()
