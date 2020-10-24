import csv
import textwrap
from typing import Dict, List, Union

import alloa.settings as settings
from alloa.costs import CostFunc, SPACosts
from alloa.files import DataSequence, FileData


class Allocation:
    def __init__(self, *paths: str, **kwargs: Dict[int, bool]) -> None:
        self.data_objects = []
        self.randomised = kwargs.get('randomised', {})
        for i, path in enumerate(paths):
            randomise = self.randomised.get(i + 1, False)
            self.data_objects.append(
                FileData(path, level=i + 1, randomise=randomise)
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

    def setup_allocation(self, cost: CostFunc) -> None:
        self.graph.populate_all_edges(cost)
        self.graph.compute_flow()
        self.graph.simplify_flow()
        self.graph.allocate()

    def write_allocations(self) -> None:
        allocation = open(settings.ALLOCATION_PATH, 'w', newline='')
        writer = csv.writer(allocation, delimiter=',')
        for row in self.allocation:
            writer.writerow(row)
        allocation.close()

    def write_profile(self) -> None:
        with open(settings.ALLOCATION_PROFILE_PATH, 'w') as profile:
            writer = csv.writer(profile, delimiter='\n')
            writer.writerow([
                f'Total number of assigned level 1 agents '
                f'is {self.graph.max_flow}',
                f'Total cost of assignment is {self.graph.flow_cost}'
            ])
            for i in range(self.number_of_levels - 1):
                writer.writerow([
                    '', 'Level {} Preference Count'.format(i + 1)
                ])
                for j in range(
                        self.graph.hierarchies[i].max_preferences_length
                ):
                    split_point = self.number_of_levels
                    column = [row[split_point + i] for row in self.allocation]
                    count = column.count(j + 1)
                    writer.writerow([
                        f'Number of level {i + 2} agents that were '
                        f'choice #{j + 1}: {count}'
                    ])

    @property
    def allocation(self) -> List[List[Union[str, int]]]:
        unnamed = self.graph.allocation
        rows = []
        for agent in self.graph.first_level_agents:
            row = [agent.name]
            row.extend(
                dude.agent.name for dude in unnamed[agent]
            )
            row.extend(
                dude.rank for dude in unnamed[agent]
            )
            rows.append(row)

        rows = sorted(
            rows,
            key=lambda r: r[0][len(r[0]) - r[0][::-1].index(' '):]
        )
        return rows


# Now one can run the program using custom cost functions.
# Include the Student/Project/Academic ones in the following class.
class Example:
    def __init__(self) -> None:
        self.allocation = Allocation(
            *settings.LEVEL_PATHS, randomised={1: True}
        )
        self.student_hierarchy = self.allocation.graph.hierarchies[0]
        self.project_hierarchy = self.allocation.graph.hierarchies[1]
        self.number_of_students = self.student_hierarchy.number_of_agents

    def set_up(self) -> None:
        costs = SPACosts(self.allocation.graph)
        self.allocation.setup_allocation(costs.cost)


def run_project_allocation() -> None:
    example = Example()
    example.set_up()
    allocation = example.allocation
    allocation.write_allocations()
    allocation.write_profile()
    allocation.print_intro_string()
