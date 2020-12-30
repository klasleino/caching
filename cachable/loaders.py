import pickle


class Loader(object):

    def load(self, filename):
        raise NotImplementedError()

    def save(self, filename, obj):
        raise NotImplementedError()


class PickleLoader(Loader):

    def load(self, filename):
        with open(filename + '.pkl', 'rb') as f:
            return pickle.load(f)

    def save(self, filename, obj):
        with open(filename + '.pkl', 'wb') as f:
            pickle.dump(obj, f)


try:
    import numpy as np

    class NumpyLoader(Loader):

        def load(self, filename):
            return np.load(filename + '.npy')

        def save(self, filename, array):
            np.save(filename + '.npy', array)

except:
    # Only include if numpy is installed.
    pass


try:
    try:
        from keras.models import load_model

    except:
        from tensorflow.keras.models import load_model

    class KerasModelLoader(Loader):

        def __init__(self, custom_objects=None):
            self.custom_objects = (
                {} if custom_objects is None else custom_objects)

        def load(self, filename):
            return load_model(
                filename + '.h5', 
                custom_objects=self.custom_objects)

        def save(self, filename, model):
            model.save(filename + '.h5')

except:
    # Only include if keras is installed.
    pass


try:
    from tensorflow.keras.models import load_model

    class TfKerasModelLoader(Loader):

        def __init__(self, custom_objects=None):
            self.custom_objects = (
                {} if custom_objects is None else custom_objects)

        def load(self, filename):
            return load_model(
                filename + '.h5', 
                custom_objects=self.custom_objects)

        def save(self, filename, model):
            model.save(filename + '.h5')

except:
    # Only include if tensorflow is installed.
    pass
     