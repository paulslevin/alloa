class Agent(object):

    def __init__(self, id_number, hierarchy,
                 capacities=None, preferences=None, abilities=None):
        self.hierarchy = hierarchy
        self.id = id_number
        self.capacities = capacities
        self.preferences = preferences
        self.abilities = abilities
        self.name = None

    def __str__(self):
        return "agent at hierarchy: {}\n" \
               "id:  {}\n" \
               "capacities: {}\n" \
               "preferences: {}\n" \
               "abilities: {}".format(
                str(self.hierarchy), str(self.id), str(self.capacities),
                str(self.preferences), str(self.abilities)
                )

    def __repr__(self):
        return "AGENT_{}_{}".format(self.hierarchy, self.id)

    def give_name(self, name):
        self.name = name


class Hierarchy(object):

    def __init__(self, level, agents=None, names=None):
        self.level = level
        self.agents = agents
        self.names = names

    def __str__(self):
        return str(self.level)

    def __repr__(self):
        return "HIERARCHY_{}".format(self.level)

    def add_agent(self, agent):
        if self.agents:
            self.agents.append(agent)
        else:
            self.agents = [agent]

    def number_of_agents(self):
        if self.agents:
            return len(self.agents)
        else:
            return 0

    def add_names(self, names):
        if not self.agents:
            raise (ValueError, "Not enough agents")
        if len(names) != self.number_of_agents():
            raise (ValueError, "Incorrect number of names provided")
        self.names = names

    def give_names(self):
        if not self.names:
            raise (ValueError, "No name dictionary has been provided")
        for agent in self.agents:
            agent.give_name(self.names[agent.id])

    def largest_preferences_length(self):
        return max(len(agent.preferences) for agent in self.agents)

    def largest_abilities_length(self):
        return max(len(agent.abilities) for agent in self.agents)
