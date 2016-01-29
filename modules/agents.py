import itertools


class Agent(object):
    def __init__(self, id_number, hierarchy,
                 capacities=None, preferences=None, abilities=None,
                 name=None):
        self.hierarchy = hierarchy
        self.id = id_number
        self.capacities = capacities
        self.preferences = preferences
        self.abilities = abilities
        self.name = name

    def __str__(self):
        return "AGENT_{}_{}".format(self.hierarchy, self.id)
        return "agent at hierarchy: {}\n" \
               "id:  {}\n" \
               "capacities: {}\n" \
               "preferences: {}\n" \
               "abilities: {}\n" \
               "name: {}\n".format(
                str(self.hierarchy), str(self.id), str(self.capacities),
                str(self.preferences), str(self.abilities), str(self.name))

    def __repr__(self):
        return "AGENT_{}_{}".format(self.hierarchy, self.id)

    def give_name(self, name):
        self.name = name

    def upper_capacity(self):
        if self.capacities:
            return self.capacities[1]
        else:
            return None

    def preference_position(self, higher_agent):
        return self.preferences.index(higher_agent)

    def lower_capacity(self):
        if self.capacities:
            return self.capacities[0]
        else:
            return None

    def capacity_difference(self):
        if self.capacities:
            return self.upper_capacity() - self.lower_capacity()


class Hierarchy(object):
    def __init__(self, level, agents=None, names=None):
        self.level = level
        self.agents = agents
        if names:
            self.agent_to_name = names
        else:
            self.agent_to_name = {}

    def __str__(self):
        return str(self.level)

    def __repr__(self):
        return "HIERARCHY_{}".format(self.level)

    def add_agent(self, agent):
        if self.agents:
            self.agents.append(agent)
        else:
            self.agents = [agent]
        self.agent_to_name[agent] = agent.name

    @property
    def number_of_agents(self):
        if self.agents:
            return len(self.agents)
        else:
            return 0

    def preferred(self, agent_subset):
        preferred_set = set(itertools.chain.from_iterable(
                agent.preferences for agent in agent_subset))
        return sorted(preferred_set, key=lambda x: x.id)

    @property
    def all_preferred(self):
        return self.preferred(self.agents)

    def set_name(self, agent, name):
        agent.name = name
        self.agent_to_name[agent] = name

    @property
    def name_to_agent(self):
        if self.agent_to_name:
            return dict((v, k) for k, v in self.agent_to_name.iteritems())

    def add_names(self, names):
        if not self.agents:
            raise (ValueError, "Not enough agents")
        if len(names) != self.number_of_agents():
            raise (ValueError, "Incorrect number of names provided")
        self.agent_to_name = names

    def give_names(self):
        if not self.agent_to_name:
            raise (ValueError, "No name dictionary has been provided")
        for agent in self.agents:
            agent.give_name(self.agent_to_name[agent.id])

    @property
    def max_preferences_length(self):
        return max(len(agent.preferences) for agent in self.agents)

    @property
    def max_abilities_length(self):
        return max(len(agent.abilities) for agent in self.agents)
