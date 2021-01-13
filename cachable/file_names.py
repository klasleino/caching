from hashlib import blake2b


class Namer(object):

    def __init__(
            self, 
            directory=None,
            name=None,
            max_length=128, 
            hash_digits=8,
            abbreviate=False, 
            abbrev_hash_digits=4):

        self.directory = directory
        self.name = name

        self.max_length = max_length
        self.hash_digits = hash_digits
        self.abbreviate = abbreviate
        self.abbrev_digits = abbrev_hash_digits


    def configure_name(self, name):
        if self.name is None:
            self.name = name

        return self


    def configure_directory(self, directory):
        if self.directory is None:
            self.directory = directory

        return self


    def filename_for_args(self, args):
        if self.directory is None:
            raise ValueError('Need to configure `directory`.')

        return '{}/{}'.format(self.directory, self.name_for_args(args))


    def name_for_args(self, args):
        if self.name is None:
            raise ValueError('Need to configure `name`.')

        name = [self.name]

        for arg in sorted(args):
            arg_name = (
                arg if not self.abbreviate else 
                ''.join([s[0] for s in arg.split('_')]))

            if isinstance(args[arg], list) or isinstance(args[arg], tuple):
                name.append('{}-{}'.format(
                    arg_name, ','.join(str(a) for a in args[arg])))
            else:
                name.append('{}-{}'.format(arg_name, args[arg]))

        name = '.'.join(name)

        # If we abbreviated the name, it may not be unique, so we add a hash to
        # the end of the name to better ensure uniqueness.
        if self.abbreviate:
            name += '.' + (
                blake2b(name.encode('utf-8'), digest_size=self.abbrev_digits)
                    .hexdigest())

        # Check if the file name is too long. In this case, we need to replace
        # it with the hash of the name. We only do this when the name is too
        # long because this format is not preferred as it is not human-readable.
        if len(name) > self.max_length:
            name = '{}.{}'.format(
                self.name,
                blake2b(name.encode('utf-8'), digest_size=self.hash_digits)
                    .hexdigest())

        return name
        