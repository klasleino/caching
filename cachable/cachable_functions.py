from inspect import getargspec

from cached_objects import CachedObject
from file_names import Namer
from loaders import PickleLoader


class CachableDef(object):
    '''
    '''

    def __init__(
            self, 
            name=None, 
            directory=None, 
            loader=None, 
            namer=None,
            debug=False):
        '''
        Parameters
        ----------
        name : str, optional
            ...
        directory : str, optional
            ...
        loader : Loader | str, optional
            ...
        namer : Namer, optional
            ...
        debug : bool
            If set to true, prints debugging info. False by default.
        '''

        self.name = name

        self.loader = PickleLoader() if loader is None else loader

        self.namer = Namer() if namer is None else namer

        if directory is not None:
            self.namer.configure_directory(directory)

        self.debug = debug


    def __call__(self, fn):
        if self.name is None:
            self.name = fn.__name__

        self.namer.configure_name(self.name)

        argspec = getargspec(fn)
        num_defaults = 0 if argspec.defaults is None else len(argspec.defaults)
        
        self.arg_names = argspec.args
        self.defaults = {
            argspec.args[-num_defaults + i]: argspec.defaults[i] 
            for i in range(num_defaults)
        }

        def _fn(*args, **kwargs):
            # Allow the user to specify that the cached file should be 
            # refreshed.
            refresh = False
            if '_refresh' in kwargs:
                refresh = kwargs['_refresh']
                del kwargs['_refresh']

            # Allow the user to specify that the file should be refreshed and 
            # not saved. Essentially this ignores the functionality of this 
            # decorator.
            refresh_no_save = False
            if '_refresh_no_save' in kwargs:
                refresh_no_save = kwargs['_refresh_no_save']
                del kwargs['_refresh_no_save']

            # Get the args that should affect the file name.

            # Add the args if they are not taking on their default value, marked
            # to be ignored, or `self`.
            name_changing_args = {
                self.arg_names[i]: arg 
                for i, arg in enumerate(args)
                if not self.arg_names[i].startswith('_') and 
                    not self.arg_names[i] == 'self' and (
                        self.arg_names[i] not in self.defaults or 
                        self.defaults[self.arg_names[i]] != arg)
            }

            # Add the kwargs if they are not taking on their default value.
            for kw in kwargs:
                if not kw.startswith('_') and (
                        kw not in self.defaults or 
                        self.defaults[kw] != kwargs[kw]):

                    name_changing_args[kw] = kwargs[kw]

            # Also get all the args for adding to the `CachedObject`.
            all_args = {
                self.arg_names[i]: arg 
                for i, arg in enumerate(args)
                if not self.arg_names[i].startswith('_') and
                    not self.arg_names[i] == 'self'
            }

            for kw in name_changing_args:
                all_args[kw] = name_changing_args[kw]


            # Load or compute the object.

            filename = self.namer.filename_for_args(name_changing_args)
            name = self.namer.name_for_args(name_changing_args)

            if refresh or refresh_no_save:
                # Just refresh regardless of if file exists.
                if self.debug:
                    print('{} cache : just refreshing'.format(self.name))

                result = fn(*args, **kwargs)

                if not refresh_no_save:
                    self.loader.save(filename, result)

            else:
                try:
                    # Load file.
                    if self.debug:
                        print('{} cache : attempting to load'.format(self.name))

                    result = self.loader.load(filename)

                except (OSError, IOError):
                    # Actually compute the data and save the result.
                    if self.debug:
                        print(
                            '{} cache : creating and saving'.format(self.name))

                    result = fn(*args, **kwargs)

                    self.loader.save(filename, result)

            return CachedObject(result, all_args, name, filename, self.loader)

        _fn.parent = fn

        return _fn
