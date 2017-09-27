import itertools


class Agent(object):
    def __init__(self, id_number, hierarchy,
                 capacities=None, preferences=None,
                 name=None):
        self.id = id_number
        self.capacities = capacities
        self.preferences = preferences
        self.hierarchy = hierarchy
        self.hierarchy.add_agent(self)
        self.name = name
        self.level = self.hierarchy.level

    def __str__(self):
        return "AGENT_{}_{}".format(self.hierarchy, self.id)

    def __repr__(self):
        return "AGENT_{}_{}".format(self.hierarchy, self.id)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name):
        '''Update the name dict on the hierarchy.'''
        self.__name = new_name
        self.hierarchy.agent_to_name[self] = new_name

    @property
    def upper_capacity(self):
        if self.capacities:
            return self.capacities[1]
    
    @property
    def lower_capacity(self):
        if self.capacities:
            return self.capacities[0]

    @property
    def capacity_difference(self):
        if self.capacities:
            return self.upper_capacity - self.lower_capacity

    def preference_position(self, higher_agent):
        return self.preferences.index(higher_agent) + 1


class Hierarchy(object):
    def __init__(self, level, agents=None, names=None):

        self.level = level

        if agents is None:
            agents = []
        self.agents = agents

        if names is None:
            names = {}
        self.agent_to_name = names

    def __str__(self):
        return str(self.level)

    def __repr__(self):
        return "HIERARCHY_{}".format(self.level)

    def add_agent(self, agent):
        '''Add agent to list and update agent name dictionary.'''
        if agent not in self.agents:
            self.agents.append(agent)

    @property
    def number_of_agents(self):
        return len(self.agents)

    def preferred(self, agent_subset):
        preferred_set = set(itertools.chain.from_iterable(
                agent.preferences for agent in agent_subset))
        return sorted(preferred_set, key=lambda x: x.id)

    @property
    def all_preferred(self):
        return self.preferred(self.agents)

    # TODO: Remove once test coverage increases.
    def set_name(self, agent, name):
        agent.name = name
        self.agent_to_name[agent] = name

    @property
    def name_to_agent(self):
        if self.agent_to_name:
            return {v: k for k, v in self.agent_to_name.iteritems()}

    @property
    def max_preferences_length(self):
        return max(len(agent.preferences) for agent in self.agents)
