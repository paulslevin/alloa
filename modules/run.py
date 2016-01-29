from files import FileData, DataSequence
import settings


class Allocation(object):
    def __init__(self, *paths):
        self.data_objects = []
        for i, path in enumerate(paths):
            self.data_objects.append(FileData(path, level=i + 1))
        self.sequence = DataSequence(*self.data_objects)
        self.graph = self.sequence.get_graph()

    def setup_allocation(self, *costs):
        assert len(costs) == len(self.data_objects) - 1
        self.graph.setup_graph(*costs)


# Now one can run the program using custom cost functions.
# We include the Student/Project/Academic ones in the following class.
class Example(object):
    def __init__(self):
        self.allocation = Allocation(*settings.LEVEL_PATHS)
        self.student_hierarchy = self.allocation.graph.hierarchies[0]
        self.project_hierarchy = self.allocation.graph.hierarchies[1]
        self.number_of_students = self.student_hierarchy.number_of_agents

    def student_project_cost(self, student, project):
        if settings.WEIGHTED_HIERARCHIES == 0:
            return 0
        preference_position = student.preference_position(project)
        if settings.WEIGHTED_HIERARCHIES == 1:
            return self.number_of_students ** preference_position
        elif settings.WEIGHTED_HIERARCHIES == 2:
            print preference_position, self.number_of_students ** (
                preference_position +
                self.project_hierarchy.max_preferences_length - 1)
            return self.number_of_students ** (
                preference_position +
                self.project_hierarchy.max_preferences_length - 1)

    def project_academic_cost(self, project, academic):
        if settings.WEIGHTED_HIERARCHIES in {0, 1}:
            return 0
        elif settings.WEIGHTED_HIERARCHIES == 2:
            preference_position = project.preference_position(academic)
            return self.number_of_students ** preference_position

    @property
    def costs(self):
        return [lambda x, y: self.student_project_cost(x, y),
                lambda x, y: self.project_academic_cost(x, y)]

    def set_up(self):
        self.allocation.setup_allocation(*self.costs)

c = Example()
c.set_up()
c.allocation.graph.set_flow()
print c.allocation.graph.flow_cost
