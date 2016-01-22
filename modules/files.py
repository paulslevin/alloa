import csv
import codecs
from agents import Agent, Hierarchy


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
    def __init__(self, csv_file, level=0, delimiter=",",
                 quoting=csv.QUOTE_NONE, first_line=True,
                 higher_agent=None):
        self.first_line = first_line
        self.opened = open(csv_file, "r")
        self.reader = csv.reader(self.opened,
                                 delimiter=delimiter,
                                 quoting=quoting)
        self.hierarchy = Hierarchy(level)
        self.higher_agent = higher_agent

    def results(self):
        results = []
        for i, row in enumerate(self.reader):
            if i == 0 and self.first_line:
                continue
            results.append(Line([x.strip() for x in row if x]))
        return results

    def set_agents(self):
        for i, line in enumerate(self.results()):
            agent = Agent(i + 1,
                          self.hierarchy,
                          capacities=line.capacities,
                          preferences=[self.higher_agent[preference] for
                                       preference in line.raw_preferences])
            self.hierarchy.add_agent(agent)


f = FileData("C:/Programming/alloa/test/students.csv", level=1)

print f.results()
