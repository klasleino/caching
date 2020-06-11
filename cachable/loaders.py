import pickle


class Loader(object):

    def load(self, filename):
        raise NotImplementedError()

    def save(self, filename, obj):
        raise NotImplementedError()


class PickleLoader(object):

    def load(self, filename):
        with open(filename + '.pkl', 'rb') as f:
            return pickle.load(f)

    def save(self, filename, obj):
        with open(filename + '.pkl', 'wb') as f:
            pickle.dump(obj, f)
     