import itertools


class Agent(object):
    def __init__(self, id_number, hierarchy,
                 capacities=None, preferences=None, abilities=None,
                 name=None):
        self.id = id_number
        self.capacities = capacities
        self.preferences = preferences
        self.abilities = abilities
        self.name = name
        self.hierarchy = hierarchy
        self.hierarchy.add_agent(self)
        self.level = self.hierarchy.level

    def __str__(self):
        return "AGENT_{}_{}".format(self.hierarchy, self.id)

    def __repr__(self):
        return "AGENT_{}_{}".format(self.hierarchy, self.id)

    def give_name(self, name):
        self.name = name

    def upper_capacity(self):
        if self.capacities:
            return self.capacities[1]

    def preference_position(self, higher_agent):
        return self.preferences.index(higher_agent) + 1

    def lower_capacity(self):
        if self.capacities:
            return self.capacities[0]

    def capacity_difference(self):
        if self.capacities:
            return self.upper_capacity() - self.lower_capacity()


class Hierarchy(object):
    def __init__(self, level, agent_to_name_map=None):

        self.level = level

        if agent_to_name_map is None:
            agent_to_name_map = {}
        self.agent_to_name_map = agent_to_name_map

    def __str__(self):
        return str(self.level)

    def __repr__(self):
        return "HIERARCHY_{}".format(self.level)

    def add_agent(self, agent):
        '''Add agent to list and update agent name dictionary.'''
        if agent not in self.agent_to_name_map:
            self.agent_to_name_map[agent] = agent.name

    @property
    def agents(self):
        return self.agent_to_name_map().keys()
    
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

    def add_or_set_name(self, agent, name):
        '''
        Set the name attribute of the supplied agent to input name variable. Overwrites the agent: name
        mapping in the agent_to_name_map if it exists, otherwise adds the key value pair to the mapping.
        '''
        agent.name = name
        self.agent_to_name_map[agent] = name

    @property
    def name_to_agent(self):
        if self.agent_to_name_map:
            return {v: k for k, v in self.agent_to_name_map.iteritems()}

    @property
    def max_preferences_length(self):
        return max(len(agent.preferences) for agent in self.agents)

    @property
    def max_abilities_length(self):
        return max(len(agent.abilities) for agent in self.agents)
