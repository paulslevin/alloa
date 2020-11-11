import textwrap
from typing import Dict

from alloa.costs import spa_cost
from alloa.files import FileReader, FileWriter
from alloa.graph_builder import GraphBuilder
from alloa.settings import parse_config


class Runner:
    def __init__(self, config: Dict) -> None:
        self.data_objects = []
        self.config = config
        self.graph = None

    def parse_files(self) -> None:
        level_paths = self.config['level_paths']
        randomised = self.config['randomised']
        for i, path in enumerate(level_paths):
            file_data = FileReader.parse(
                path, level=i + 1, randomise=randomised
            )
            self.data_objects.append(file_data)

    def build_graph(self) -> None:
        graph_builder = GraphBuilder(self.data_objects, spa_cost)
        graph = graph_builder.build_graph()
        self.graph = graph

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
        number_of_levels = len(self.data_objects)
        for i in range(number_of_levels):
            num_of_agents = self.graph.hierarchies[i].number_of_agents
            print(f'{num_of_agents} agents of hierarchy {i + 1}')

    def run_project_allocation(self) -> None:
        self.graph.populate_all_edges()
        self.graph.compute_flow()
        self.graph.simplify_flow()
        self.graph.allocate()

    def write_output_files(self) -> None:
        first_level_agent_names = [
            x.raw_name for x in self.data_objects[0].file_content
        ]
        writer = FileWriter(self.graph, self.config, first_level_agent_names)
        writer.parse_graph()
        writer.write_allocations()
        writer.write_profile()


def run(config_filename: str) -> None:
    config = parse_config(config_filename)
    runner = Runner(config)
    runner.parse_files()
    runner.build_graph()
    runner.run_project_allocation()
    runner.write_output_files()
    runner.print_intro_string()
