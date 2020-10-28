"""Contains code for parsing input files and writing output files."""
import csv
from copy import deepcopy
from random import shuffle
from typing import Dict, List, Optional

from alloa.agents import Agent, Hierarchy
from alloa.costs import spa_cost
from alloa.graph import AllocationGraph


class Line:
    """Represents a line to be written to output CSV file."""
    def __init__(self, line: List[str]) -> None:
        self.line = line
        self.raw_name = line[0]
        self.capacities = [int(x) for x in self.line[1:3]]
        self.raw_preferences = self.line[3:]

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
        higher_agent: Optional[Agent] = None,
        agents_to_id: Optional[Dict[Agent, int]] = None
    ) -> None:
        self.randomise = randomise
        self.delimiter = delimiter
        self.quoting = quoting
        self.level = level
        self.first_line = first_line
        self.file = csv_file

        self.hierarchy = Hierarchy(level) if level else None
        self.higher_agent = higher_agent or {}
        self.agents_to_id = agents_to_id or {}

    def __repr__(self) -> str:
        return f'LEVEL_{self.level}_DATA'

    def id_to_agents(self) -> Dict[int, Agent]:
        return {
            agent_id: agent for agent, agent_id in self.agents_to_id.items()
        }

    def set_higher_agent(self, higher_agent: Agent) -> None:
        self.higher_agent = higher_agent

    def set_hierarchy(self, level: int) -> None:
        self.level = level
        self.hierarchy = Hierarchy(level)

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
                results.append(Line([x.strip() for x in row if x]))
        return results

    def set_agents_and_ids(self) -> None:
        results_copy = deepcopy(self.results())
        if self.randomise:
            shuffle(results_copy)
        preferences = None
        for i, line in enumerate(results_copy):
            if line.raw_preferences:
                preferences = [
                    self.higher_agent.get(preference)
                    for preference in line.raw_preferences
                ]
            agent = Agent(
                i + 1,
                self.hierarchy,
                capacities=line.capacities,
                preferences=preferences,
                name=line.raw_name
            )
            self.agents_to_id[agent] = agent.agent_id


class DataSequence:
    """Container file data objects and joins together to create graph."""

    def __init__(self, *args: FileData) -> None:
        self.sequence = args
        self.hierarchies = []
        self.block_list = []

    def __len__(self) -> int:
        return len(self.sequence)

    def set_hierarchies(self) -> None:
        backwards = self.sequence[::-1]
        backwards[0].set_agents_and_ids()
        for i, file_data in enumerate(backwards[1:]):
            last_level = backwards[i]
            last_hierarchy = last_level.hierarchy
            name_agent_map = last_hierarchy.name_agent_map
            file_data.set_higher_agent(name_agent_map)
            file_data.set_agents_and_ids()
            self.hierarchies.append(last_hierarchy)
        self.hierarchies.append(self.sequence[0].hierarchy)
        self.hierarchies = self.hierarchies[::-1]

    def get_graph(self) -> AllocationGraph:
        self.set_hierarchies()
        graph = AllocationGraph.with_edges(self.hierarchies, cost=spa_cost)
        return graph
