import itertools
from   utils.parsers import ReprParser


class Agent(object):
    def __init__(self, id, hierarchy,
                 capacities=None, preferences=None,
                 name=None):
        self.id = id
        self.capacities = capacities
        self.preferences = preferences
        self.hierarchy = hierarchy
        self.hierarchy.add_agent(self)
        self.name = name
        self.level = self.hierarchy.level
        
        # Experiment with composition.
        self.repr_parser = ReprParser(self)

    def __str__(self):
        return "AGENT_{}_{}".format(self.level, self.id)

    def __repr__(self):
        str_kwargs = ['id={}'.format(self.id),
                      'hierarchy={}'.format(self.hierarchy)]
        if self.capacities:
            str_kwargs.append('capacities={}'.format(self.capacities))
        if self.preferences:
            str_kwargs.append('preferences={}'.format(self.preferences))
        if self.name:
            str_kwargs.append('name={}'.format(self.name))

        return self.repr_parser.parse(str_kwargs)

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

        # Experiment with composition.
        self.repr_parser = ReprParser(self)

    def __str__(self):
        return 'HIERARCHY_{}'.format(str(self.level))

    def __repr__(self):
        str_kwargs = ['level={}'.format(self.level)]
        if self.agents:
            agent_strs = [str(agent) for agent in self.agents]
            str_kwargs.append('agents={}'.format(agent_strs).replace("'",'') )
        return self.repr_parser.parse(str_kwargs)

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
        '''Return list of unique agents, sorted by id, that the agents
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
