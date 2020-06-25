from inspect import getargspec

from cachable import Cachable
from cachable.file_names import Namer


class CachableParam(Cachable):
    '''
    Class decorator that specifies that the class can be used as a parameter to
    a cachable function. Overrides the `str` and `repr` methods on the class.
    '''

    def __init__(self, name=None, namer=None):
        self.name = name
        self.namer = Namer() if namer is None else namer
        
    def __call__(self, cls):
        if self.name is None:
            self.name = cls.__name__

        self.namer.configure_name(self.name)

        this = self
        original_init = cls.__init__

        argspec = getargspec(original_init)
        num_defaults = 0 if argspec.defaults is None else len(argspec.defaults)
        
        self.arg_names = argspec.args[1:]
        self.defaults = {
            argspec.args[-num_defaults + i] : argspec.defaults[i] 
            for i in range(num_defaults)
        }

        def _init(self, *args, **kwargs):

            # Get the args that should affect the name.
            name_changing_args, all_args = this._get_relevant_args(args, kwargs)

            name = this.namer.name_for_args(name_changing_args)

            self._name = name
            self._params = all_args

            original_init(self, *args, **kwargs)

        # Replace the init function and modify the str and repr functions.
        cls.__init__ = _init
        cls.__str__ = lambda slf : '[{}]'.format(slf._name)
        cls.__repr__ = lambda slf : slf._name

        return cls
