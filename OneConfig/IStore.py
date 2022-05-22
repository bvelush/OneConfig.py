'''

'''

class IStore:
    '''
    '''

    def __init__(self, name: str, path: str):
        self._raise_traverse_problems = True

    def get(self, key: str) -> str:
        '''
        ***OVERRIDE IT***
        Returns the value of the key from the store.
        Can be hierarchical (via .) or flat. Hierarchy (if needed) must be implemented
        according to the logic of the store. For example, in the SQL store hierarchy could be
        table.key (always 2 levels), in JSON store -- just a path.to.the.value etc.
         '''
        pass

    @property
    def name(self) -> str:
        '''
        ***OVERRIDE IT***
        Returns the ID of the store
        '''
        pass

    @property
    def raise_traverse_problems(self) -> bool:
        return self._raise_traverse_problems

    @raise_traverse_problems.setter
    def raise_traverse_problems(self, val: bool):
        self._raise_traverse_problems = val
        