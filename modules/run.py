from costs import SPACosts
from files import FileData, DataSequence
import settings
import csv


class Allocation(object):
    def __init__(self, *paths, **kwargs):
        self.data_objects = []
        self.randomised = kwargs.get('randomised', {})
        for i, path in enumerate(paths):
            randomise = self.randomised.get(i + 1, False)
            self.data_objects.append(FileData(path,
                                              level=i + 1,
                                              randomise=randomise))
        self.sequence = DataSequence(*self.data_objects)
        self.number_of_levels = len(self.sequence)
        self.graph = self.sequence.get_graph()

    def intro_string(self):
        print '''
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
################################################################\n
                '''
        for i in xrange(self.number_of_levels):
            print "{} agents of hierarchy {}".format(self.graph.hierarchies[
                                                         i].number_of_agents,
                                                     i + 1)

    def setup_allocation(self, cost):
        self.graph.setup_graph(cost)
        self.graph.set_flow()
        self.graph.simplify_flow()
        self.graph.allocate()

    def write_allocations(self):
        allocation = open(settings.ALLOCATION_PATH, "wb")
        writer = csv.writer(allocation, delimiter=",")
        for row in self.allocation:
            writer.writerow(row)
        allocation.close()

    def write_profile(self):
        profile = open(settings.ALLOCATION_PROFILE_PATH, "wb")
        writer = csv.writer(profile, delimiter="\n")
        writer.writerow(["Total number of assigned level 1 agents is " +
                         str(self.graph.max_flow),
                         "Total cost of assignment is " + str(
                             self.graph.flow_cost)])
        for i in xrange(self.number_of_levels - 1):
            writer.writerow(["", "Level {} Preference Count".format(i + 1)])
            for j in xrange(self.graph.hierarchies[i].max_preferences_length):
                split_point = self.number_of_levels
                column = [row[split_point + i] for row in self.allocation]
                count = str(column.count(j + 1))
                writer.writerow(["Number of level {} agents that were "
                                 "choice #".format(i + 2) + str(j + 1) + ": " +
                                 count])
        profile.close()

    @property
    def allocation(self):
        unnamed = self.graph.allocation
        split_point = self.number_of_levels
        rows = [[agent.name for agent in row[:split_point]] + row[split_point:]
                for row in unnamed]
        rows = sorted(rows,
                      key=lambda r: r[0][len(r[0]) - r[0][::-1].index(" "):])
        return rows


# Now one can run the program using custom cost functions.
# Include the Student/Project/Academic ones in the following class.
class Example(object):
    def __init__(self):
        self.allocation = Allocation(*settings.LEVEL_PATHS,
                                     randomised={1: True})
        self.student_hierarchy = self.allocation.graph.hierarchies[0]
        self.project_hierarchy = self.allocation.graph.hierarchies[1]
        self.number_of_students = self.student_hierarchy.number_of_agents

    def set_up(self):
        costs = SPACosts(self.allocation.graph)
        self.allocation.setup_allocation(costs.cost)


def run_project_allocation():
    example = Example()
    example.set_up()
    allocation = example.allocation
    allocation.write_allocations()
    allocation.write_profile()
    allocation.intro_string()
