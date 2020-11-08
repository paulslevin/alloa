"""Contains code for parsing input files and writing output files."""
import csv
from random import shuffle
from typing import Dict, List, Optional

from alloa.agents import Hierarchy
from alloa.graph import AllocationGraph


class Line:
    """Represents a line of data read from input CSV file."""
    def __init__(self, line: List[str]) -> None:
        self.line = [x.strip() for x in line]
        self.raw_name = line[0]
        self.capacities = [int(x) for x in self.line[1:3]]
        self.raw_preferences = self.line[3:]

    def __eq__(self, other) -> bool:
        return self.line == other.line

    def __repr__(self) -> str:
        return str(self.line)


class FileReader:
    """Contains data parsed from input CSV file."""
    def __init__(
        self,
        csv_file: str,
        delimiter: str = ',',
        level: Optional[int] = None,
        randomise: bool = False,
        quoting: int = csv.QUOTE_NONE,
    ) -> None:
        self.randomise = randomise
        self.delimiter = delimiter
        self.quoting = quoting
        self.level = level
        self.file = csv_file

        self.hierarchy = Hierarchy(level) if level else None

        self.file_content = []

    @classmethod
    def parse(cls, *args, **kwargs):
        file_data = cls(*args, **kwargs)
        file_data.parse_file()
        return file_data

    def __repr__(self) -> str:
        return f'LEVEL_{self.level}_DATA'

    def parse_file(self) -> None:
        with open(self.file, 'r') as opened_file:
            reader = csv.reader(
                opened_file,
                delimiter=self.delimiter,
                quoting=self.quoting
            )
            file_content = []
            for i, row in enumerate(reader):
                # Ignore header with columns.
                if i == 0:
                    continue
                file_content.append(Line(row))
        if self.randomise:
            shuffle(file_content)
        self.file_content = file_content


class FileWriter:
    """Writes output allocation and profile files."""
    def __init__(
        self,
        graph: AllocationGraph,
        config: Dict,
        first_level_agent_names: List[str]
    ) -> None:
        self.graph = graph
        self.number_of_levels = len(config['level_paths'])
        self.allocation_path = config['allocation_path']
        self.allocation_profile_path = config['allocation_profile_path']
        self.first_level_agent_names = first_level_agent_names
        self.output_rows = []

    def parse_graph(self) -> None:

        if not self.graph.first_level_agents:
            return

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
        def _key(_row):
            return self.first_level_agent_names.index(_row[0])

        rows = sorted(rows, key=_key)
        self.output_rows = [column_names] + rows

    def write_allocations(self) -> None:
        with open(self.allocation_path, 'w') as allocation:
            writer = csv.writer(allocation, delimiter=',')
            for row in self.output_rows:
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
                    column = [row[split_point + i] for row in self.output_rows]
                    count = column.count(j + 1)
                    profile.write(
                        f'Number of level {i + 2} agents that were '
                        f'choice #{j + 1}: {count}\n'
                    )
