'''Module containing useful custom Exceptions.'''

class AgentExistsError(Exception):
    '''Exception raised when instantiating an agent with the same id as an
    existing agent on the hierarchy.'''
    def __init__(self, hierarchy, id):
        return super(AgentExistsError, self).__init__(
            '{} already has an agent with id {}.'.format(hierarchy, id)
        )


class AgentNotInPreferencesError(Exception):
    def __init__(self, agent, other_agent):
        return super(AgentNotInPreferencesError, self).__init__(
            '{} not in preferences of {}.'.format(other_agent, agent)    
        )