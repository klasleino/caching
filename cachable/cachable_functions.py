from inspect import getargspec

from cachable.cached_objects import CachedObject
from cachable.file_names import Namer
from cachable.loaders import PickleLoader


class Cachable(object):
    '''
    Decorator for a function that insturments the function to cache its result
    based on the "name-changing" args that are passed to it. Name-changing args
    are the arguments that (1) do not have a name beginning with '_', (2) are
    not `self`, and (3) are not being given values equal to their default value
    in the function signature.

    The instrumented funciton will return the object that would have been 
    returned using the given parameters (note that this means the function
    should not have side-effects, and will be made implicitly deterministic),
    wrapped as a `CachedObject`, which stores the parameters used to create the
    object.
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
            The base name of the `CachedObject` that will be returned from the
            function this decorator instruments. This will also be the prefix to
            the file name used to cache the object.
        directory : str, optional
            Path to the directory to store the cached objects in. The directory
            can optionally be configured in `namer`, in which case this will be
            ignored.
        loader : Loader | str, optional
            Oject that loads and saves cached objects. By default `PickleLoader`
            is used so results will be stored using python's `pickle`.
        namer : Namer, optional
            Object that creates the file names based on the name-changing args.
            If None, a default namer is used, but the namer can be configured if
            desired.
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

        # Get the argument names and defaults from the argspec.
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
            name_changing_args, all_args = self._get_relevant_args(args, kwargs)
            
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
                        print(
                            '{} cache : attempting to load from {}'
                            .format(self.name, filename))

                    result = self.loader.load(filename)

                except (OSError, IOError):
                    # Actually compute the data and save the result.
                    if self.debug:
                        print(
                            '{} cache : creating and saving to {}'
                            .format(self.name, filename))

                    result = fn(*args, **kwargs)

                    self.loader.save(filename, result)

            return CachedObject(result, all_args, name, filename, self.loader)

        _fn.parent = fn

        return _fn


    def _get_relevant_args(self, args, kwargs):
        # Add the args if they are not taking on their default value, marked to
        # be ignored, or `self`.
        name_changing_args = {
            self.arg_names[i]: arg 
            for i, arg in enumerate(args)
            if not self.arg_names[i].startswith('_') and 
                not self.arg_names[i] == 'self' and (
                    self.arg_names[i] not in self.defaults or 
                    self.defaults[self.arg_names[i]] != arg)
        }

        # Add the kwargs if they are not taking on their default value or marked
        # to be ignored.
        for kw in kwargs:
            if not kw.startswith('_') and (
                    kw not in self.defaults or 
                    self.defaults[kw] != kwargs[kw]):

                name_changing_args[kw] = kwargs[kw]

        # Also get all the args for adding to the `CachedObject`. This includes
        # all the args that were used to create this object, even if they took
        # their default values.
        all_args = {
            self.arg_names[i]: arg 
            for i, arg in enumerate(args)
            if not self.arg_names[i].startswith('_') and
                not self.arg_names[i] == 'self'
        }

        for kw in name_changing_args:
            all_args[kw] = name_changing_args[kw]

        return name_changing_args, all_args
