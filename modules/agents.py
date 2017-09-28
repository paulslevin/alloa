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
    def __init__(self, level, agents=None):
        '''Represent a bucket of agents.'''

        self.level = level

        if agents is None:
            agents = []
        self.agents = agents

    def __str__(self):
        return str(self.level)

    def __repr__(self):
        return "HIERARCHY_{}".format(self.level)

    @property
    def _agent_name_map(self):
        return {agent: agent.name for agent in self.agents}

    @property
    def name_agent_map(self):
        if self._agent_name_map:
            return {v: k for k, v in self._agent_name_map.iteritems()}

    def add_agent(self, agent):
        if agent not in self.agents:
            self.agents.append(agent)

    @property
    def number_of_agents(self):
        return len(self.agents)

    def preferred(self, agent_subset):
        '''Return list of unique agents, sorted by id_number, that the agents
        in the given subset prefer at the next hierarchy level.'''
        all = [agent.preferences for agent in agent_subset]
        all_flattened = itertools.chain(*all)
        all_flattened_unique = set(all_flattened)
        return sorted(all_flattened_unique, key=lambda agent: agent.id)

    @property
    def all_preferred(self):
        return self.preferred(self.agents)

    @property
    def max_preferences_length(self):
        return max(len(agent.preferences) for agent in self.agents)
