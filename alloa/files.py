"""Contains code for parsing input files and writing output files."""
import csv
from copy import deepcopy
from random import shuffle
from typing import List, Optional

from alloa.agents import Agent, Hierarchy
from alloa.costs import spa_cost
from alloa.graph import AllocationGraph


class Line:
    """Represents a line to be written to output CSV file."""
    def __init__(self, line: List[str]) -> None:
        self.line = [x.strip() for x in line]
        self.raw_name = line[0]
        self.capacities = [int(x) for x in self.line[1:3]]
        self.raw_preferences = self.line[3:]

    def __eq__(self, other) -> bool:
        return self.line == other.line

    def __repr__(self) -> str:
        return str(self.line)


class FileData:
    """Contains data parsed from input CSV file."""
    def __init__(
        self,
        csv_file: str,
        delimiter: str = ',',
        level: Optional[int] = None,
        randomise: bool = False,
        quoting: int = csv.QUOTE_NONE,
        first_line: bool = True,
    ) -> None:
        self.randomise = randomise
        self.delimiter = delimiter
        self.quoting = quoting
        self.level = level
        self.first_line = first_line
        self.file = csv_file

        self.hierarchy = Hierarchy(level) if level else None

    def __repr__(self) -> str:
        return f'LEVEL_{self.level}_DATA'

    def create_agents(
        self, next_hierarchy: Optional[Hierarchy] = None
    ) -> None:
        results_copy = deepcopy(self.results())
        if self.randomise:
            shuffle(results_copy)
        for i, line in enumerate(results_copy):
            preferences = [
                next_hierarchy.name_agent_map.get(preference)
                for preference in line.raw_preferences
            ] if next_hierarchy else []
            agent = Agent(
                capacities=line.capacities,
                preferences=preferences,
                name=line.raw_name
            )
            self.hierarchy.agents.append(agent)

    def results(self) -> List[Line]:
        with open(self.file, 'r') as opened_file:
            reader = csv.reader(
                opened_file,
                delimiter=self.delimiter,
                quoting=self.quoting
            )
            results = []
            for i, row in enumerate(reader):
                if i == 0 and self.first_line:
                    continue
                results.append(Line(row))
        return results


class DataSequence:
    """Container for file data objects and joins together to create graph."""
    def __init__(self, *args: FileData) -> None:
        self.sequence = args
        self.hierarchies = []
        self.block_list = []

    def __len__(self) -> int:
        return len(self.sequence)

    def get_graph(self) -> AllocationGraph:
        self._set_hierarchies()
        graph = AllocationGraph.with_edges(self.hierarchies, cost=spa_cost)
        return graph

    def _set_hierarchies(self) -> None:
        backwards = self.sequence[::-1]
        backwards[0].create_agents()
        for i, file_data in enumerate(backwards[1:]):
            last_level = backwards[i]
            last_hierarchy = last_level.hierarchy
            file_data.create_agents(last_hierarchy)
            self.hierarchies.append(last_hierarchy)
        self.hierarchies.append(self.sequence[0].hierarchy)
        self.hierarchies = self.hierarchies[::-1]
