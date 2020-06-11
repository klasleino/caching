
class CachedObject(object):
    '''
    Wrapper for an object that was created using the caching protocol. This 
    allows us to use cached objects as parameters to other cached objects, and
    to keep track of the parameters used to create the cached objects.
    '''

    def __init__(self, obj, params, name, file_name, loader):
        self.obj = obj
        self._params = params
        self._name = name
        self._filename = file_name
        self._loader = loader

    def _reload(self):
        '''Loads a new deep copy of this object from the cache.'''
        return CachedObject(
            self._loader(self._filename),
            self._params,
            self._name,
            self._filename,
            self._loader)

    def __getattr__(self, name):
        return getattr(self.obj, name)

    def __str__(self):
        return '[{}]'.format(self._name)

    def __repr__(self):
        return self._name
