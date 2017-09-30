import csv
import codecs
from agents import Agent, Hierarchy
from graph import HierarchyGraph, AllocationGraph
from copy import deepcopy
from random import shuffle


class Line(object):
    def __init__(self, line):
        self.line = line
        self.raw_name = line[0]
        if self.raw_name.startswith(codecs.BOM_UTF8):
            self.raw_name = self.raw_name[3:]
        self.capacities = [int(x) for x in self.line[1:3]]
        self.raw_preferences = self.line[3:]

    def __repr__(self):
        return str(self.line)


class FileData(object):
    def __init__(self, csv_file,
                 delimiter=",", level=None, randomise=False,
                 quoting=csv.QUOTE_NONE, first_line=True,
                 higher_agent=None, agents_to_id=None):
        self.randomise = randomise
        self.delimiter = delimiter
        self.quoting = quoting
        self.level = level
        self.first_line = first_line
        self.file = csv_file
        if level:
            self.hierarchy = Hierarchy(level)
        else:
            self.hierarchy = None
        if higher_agent:
            self.higher_agent = higher_agent
        else:
            self.higher_agent = {}
        if agents_to_id:
            self.agents_to_id = agents_to_id
        else:
            self.agents_to_id = {}

    def __repr__(self):
        return "LEVEL_{}_Data".format(self.level)

    def id_to_agents(self):
        return {id: agent for agent, id in
                self.agents_to_id.iteritems()}

    def set_higher_agent(self, higher_agent):
        self.higher_agent = higher_agent

    def set_hierarchy(self, level):
        self.level = level
        self.hierarchy = Hierarchy(level)

    def results(self):
        opened_file = open(self.file, "r")
        reader = csv.reader(opened_file,
                            delimiter=self.delimiter,
                            quoting=self.quoting)
        results = []
        for i, row in enumerate(reader):
            if i == 0 and self.first_line:
                continue
            results.append(Line([x.strip() for x in row if x]))
        opened_file.close()
        return results

    def set_agents_and_ids(self):
        results_copy = deepcopy(self.results())
        if self.randomise:
            shuffle(results_copy)
        preferences = None
        for i, line in enumerate(results_copy):
            if line.raw_preferences:
                preferences = [self.higher_agent.get(preference) for
                               preference in line.raw_preferences]
            agent = Agent(i + 1,
                          self.hierarchy,
                          capacities=line.capacities,
                          preferences=preferences,
                          name=line.raw_name)
            self.agents_to_id[agent] = agent.id


class DataSequence(object):

    def __init__(self, *args):
        self.sequence = args
        self.hierarchies = []
        self.block_list = []

    def __len__(self):
        return len(self.sequence)

    def set_hierarchies(self):
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

    def set_block_list(self):
        if self.block_list:
            return None
        if not self.hierarchies:
            self.block_list = []
        for i, hierarchy in enumerate(self.hierarchies):
            if i == 0:
                first_block = HierarchyGraph(hierarchy, hierarchy.agents)
                first_block.generate_agent_nodes()
                self.block_list.append(first_block)
                continue
            previous_block = self.block_list[i - 1]
            previous_preferred_agents = previous_block.preferred_agents
            next_block = HierarchyGraph(hierarchy,
                               hierarchy.preferred(previous_preferred_agents))
            next_block.generate_agent_nodes()
            self.block_list.append(next_block)

    def get_graph(self):
        self.set_hierarchies()
        self.set_block_list()
        graph = AllocationGraph(self.block_list)
        return graph
