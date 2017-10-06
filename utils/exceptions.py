'''Module containing useful custom Exceptions.'''

class AgentExistsError(Exception):
    '''Exception raised when instantiating an agent with the same id as an
    existing agent on the hierarchy.'''
    def __init__(self, hierarchy, id):
        return super(AgentExistsError, self).__init__(
            '{} already has an agent with id {}.'.format(hierarchy, id)
        )
