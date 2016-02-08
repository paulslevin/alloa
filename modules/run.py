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
# This is alloa by Mante Zelvyte, Uli Kraehmer and Paul Slevin #
#                                                              #
#    ulrich.kraehmer@glasgow.ac.uk                             #
#    paul.slevin@cantab.net                                    #
#                                                              #
# Runtime with 100 agents at each hierarchy is a few ms        #
#                                                              #
################################################################\n
                '''
        for i in xrange(self.number_of_levels):
            print "{} agents of hierarchy {}".format(self.graph.hierarchies[
                                                         i].number_of_agents,
                                                     i + 1)

    def setup_allocation(self, *costs):
        assert len(costs) == len(self.data_objects) - 1
        self.graph.setup_graph(*costs)
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

    def student_project_cost(self, student, project):
        preference_position = student.preference_position(project)
        if settings.WEIGHTED_HIERARCHIES == 1:
            return self.number_of_students ** (preference_position - 1)
        elif settings.WEIGHTED_HIERARCHIES == 2:
            return self.number_of_students ** (
                preference_position - 1 +
                self.project_hierarchy.max_preferences_length - 1)

    def project_academic_cost(self, project, academic):
        if settings.WEIGHTED_HIERARCHIES in {0, 1}:
            return 0
        elif settings.WEIGHTED_HIERARCHIES == 2:
            preference_position = project.preference_position(academic)
            return self.number_of_students ** (preference_position - 1)

    @property
    def costs(self):
        return [lambda x, y: self.student_project_cost(x, y),
                lambda x, y: self.project_academic_cost(x, y)]

    def set_up(self):
        self.allocation.setup_allocation(*self.costs)


def run_project_allocation():
    example = Example()
    example.set_up()
    allocation = example.allocation
    allocation.write_allocations()
    allocation.write_profile()
    allocation.intro_string()
