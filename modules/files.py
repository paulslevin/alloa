import csv
import codecs
from agents import Agent, Hierarchy
from copy import deepcopy


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

    def __init__(self, csv_file, delimiter=",", level=None,
                 quoting=csv.QUOTE_NONE, first_line=True,
                 higher_agent=None, agents_to_id=None):
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

    def id_to_agents(self):
        return {id_number: agent for agent, id_number in self.agents_to_id}

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
        preferences = None
        for i, line in enumerate(results_copy):
            if line.raw_preferences:
                preferences = [self.higher_agent.get(preference) for
                               preference in line.raw_preferences]
            agent = Agent(i + 1,
                          self.hierarchy,
                          capacities=line.capacities,
                          preferences=preferences)
            agent.give_name(line.raw_name)
            self.hierarchy.add_agent(agent)
            self.agents_to_id[agent] = agent.id


class DataSequence(object):

    def __init__(self, *args):
        backwards = args[::-1]
        backwards[0].set_agents_and_ids()
        for i, file_data in enumerate(backwards[1:]):
            file_data.set_higher_agents(backwards[i-1].id_to_agents())
            file_data.set_agents_and_ids()


print [1, 2, 3][:-1]

# f = FileData("C:/Programming/alloa/test/academics.csv", level=1)
# print f.results()
# f.set_agents_and_ids()
#
# agents = f.agents_to_id.keys()
# for agent in sorted(agents):
#     print agent
