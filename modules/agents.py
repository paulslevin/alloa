'''Module containing Agent and Hierarchy classes. Agents represent nodes on the
graph and are bucketed into a hierarchy of multiple agents, with a given level.
Each agent has an (ordered) list of preferences of agents at the next level.

Example
-------
Three students Paul, Michael and Patricia each have a list of three projects
they'd like to work on, ordered by preference
Paul:     [Spheres, Circles, Lines]
Michael:  [Circles, Algebra, Cones]
Patricia: [Triangles, Mechanics, Algebra]
Then 
[Paul, Michael, Patricia] would be represented by three agent objects at a
level 1 hierarchy, and the projects 
[Spheres, Circles, Lines, Algebra, Cones, Triangles, Mechanics, Algebra]
would be represented by eight agent objects at a level 2 hierachy.
'''

import itertools
from   utils.parsers import ReprParser
from   utils.exceptions import AgentExistsError, AgentNotInPreferencesError


class Agent(object):
    '''Represent an individual agent e.g. student/project/supervisor.'''
    def __init__(self, id, hierarchy,
                 capacities=None, preferences=None,
                 name=None):
        '''
        Parameters
        ----------
        id: int
            Unique number identifying the agent at each hierarchy.
        hierarchy: Hierarchy object
        name: str
            Name of agent e.g. Paul. This is not unique.
        capacities: tuple of int
            The minimum and maximum amount this agent can take on, e.g.
            a project supervisor with capacities (1, 3) would mean she must
            supervise one project as a minimum, but can supervise up to three
            in total.
        preferences: list of Agent
            The agents at the next hierarchy level that this agent prefers.
        '''

        self.id = id
        self.hierarchy = hierarchy
        self.name = name
        self.level = self.hierarchy.level
        self.capacities = capacities
        self.preferences = preferences

        # Experiment with composition.
        self.repr_parser = ReprParser(self)

    def __str__(self):
        return "AGENT_{}_{}".format(self.level, self.id)

    def __repr__(self):
        str_kwargs = []
        for attr in [ 'id', 'hierarchy', 'capacities', 'preferences', 'name']:
            value = getattr(self, attr)
            if value is not None:
                str_kwargs.append('{}={}'.format(attr, value))
        return self.repr_parser.parse(str_kwargs)

    @property
    def hierarchy(self):
        return self._hierarchy

    @hierarchy.setter
    def hierarchy(self, value):
        self._hierarchy = value
        self._hierarchy.add_agent(self)

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

    def preference_position(self, other):
        '''Position of another agent in the preference list.'''
        if self.preferences:
            if other in self.preferences:
                return self.preferences.index(other) + 1
        raise AgentNotInPreferencesError(self, other)


class Hierarchy(object):
    '''Represent a bucket of agents.'''

    def __init__(self, level, agents=None):

        self.level = level
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
    def agents(self):
        return self._agents

    @agents.setter
    def agents(self, value):
        if value is None:
            self._agents = []
        else:
            self._agents = value

    @property
    def _agent_name_map(self):
        return {agent: agent.name for agent in self.agents}

    @property
    def name_agent_map(self):
        if self._agent_name_map:
            return {v: k for k, v in self._agent_name_map.iteritems()}

    def add_agent(self, agent):
        if self.has_agent_with_id(agent.id):
            raise AgentExistsError(self, agent.id)
        self.agents.append(agent)

    def has_agent_with_id(self, id):
        for agent in self.agents:
            if agent.id == id:
                return True
        return False

    @property
    def number_of_agents(self):
        return len(self.agents)

    def preferred(self, agent_subset):
        '''Return list of unique agents, sorted by id, that the agents
        in the given subset prefer at the next hierarchy level.'''
        all_unflattened = [agent.preferences for agent in agent_subset]
        all_flattened = itertools.chain(*all_unflattened)
        all_flattened_unique = set(all_flattened)
        return sorted(all_flattened_unique, key=lambda agent: agent.id)

    @property
    def all_preferred(self):
        return self.preferred(self.agents)

    @property
    def max_preferences_length(self):
        return max(len(agent.preferences) for agent in self.agents)
