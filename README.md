# caching
Library for easily caching computations that take a long time to run, e.g., training Keras models.

## Installation
0. Optionally, create and/or activate a virtual environment to install this package in. E.g., 
```
conda create -n example_env python=3
conda activate example_env
```

1. Clone the caching repo to a location of your choice:
```
git clone https://github.com/klasleino/caching.git
```

2. Change into the repo directory and install using pip:
```
cd caching
pip install -e .
```

## Usage

Caching utility is provided via *decorators*.
The primary decorator is the `Cachable` decorator found in the `cachable` package.
This decorator is used on a function (either member or non-member) to specify that the value returned by the function should be cached.
If the function is called again with the same parameters, the result will be loaded from the cache rather than running the function again.

For example, consider the following code:
```python
from cachable import Cachable

@Cachable(directory='cache')
def f(a, b, c):
    return dict(a=a, b=b, c=c)
    
# Call 1 (body of `f` is run).
res = f(1, 2, 3)

# Call 2 (loaded from cache).
res = f(1, 2, 3)

# Call 3 (body of `f` is run).
res = f(4, 5, 6)
```
In the first call, the function, `f`, will be run, and the result will be saved in a file in a directory called "cache". 
The file name of the cached result will contain the parameters, `a`, `b`, and `c` and the values passed to them in call 1.
In the second call, the function will not be run, because an existing file with the given parameters exists; instead, the result will be loaded from the cached file.
Finally, in the third call, the parameters are different, thus the function will be run again, and a new cache entry made.

#### Cached Objects
Objects returned by `Cachable` functions are wrapped as a `cachable.cached_objects.CachedObject`.
`CachedObjects`s can mostly be used the same as their non-wrapped counterparts, but the original object returned by the non-decorated function can be obtained from the `obj` field of the `CachedObject`. 
The `CachedObject` also keeps track of the parameters used to create the object.

#### Default Parameters
Parameters taking their default values will not be included in the name of the cached file.
This keeps file names shorter, and allows backwards compatibility with previously cached files, provided the default value is chosen appropriately.

#### Non-primitive Arguments
Any argument with a canonical string representation can be passed as an argument to a `Cachable` function.
The argument, `arg`, is taken to be an unseen value if `str(arg)` does not match the string representation of any previous values passed.
This may present a problem for generic objects, as two objects may be the same, while `str(obj1) != str(obj2)`.

Any instance of `CachedObject` has a canonical string representation, so `CachedObject`s can be given as parameters to other cached objects.

For other custom objects, the `CachableParam` decorator in the `cachable` package can be used.
This gives the decorated object a canonical string representation based on the arguments passed to the object's `__init__` function.
For example, a custom object can be used as a parameter to a `Cachable` function using the following code:
```python
from cachable import Cachable, CachableParam

@CachableParam()
class P(object):
    def __init__(a, b, c):
        self.a = a
        self.b = b
        self.c = c

@Cachable(directory='cache')
def f(p):
    return dict(a=p.a, b=p.b, c=p.c)
    
# Call 1 (body of `f` is run).
res = f(P(1, 2, 3))

# Call 2 (loaded from cache).
res = f(P(1, 2, 3))
```
Note that the behavior of the caching may not be correct if the `CachableParam` is modified after it is constructed; therefore this should only be used on objects that are treated as immutable.

#### Hidden Parameters
If a `Cachable` function takes a parameter that for whatever reason should not affect the cached file name, the parameter can be hidden by beginning its name with an underscore, e.g.,
```python
from cachable import Cachable

@Cachable(directory='cache')
def f(a, b, c, _msg):
    print(_msg)
    return dict(a=a, b=b, c=c)
    
# Call 1 (body of `f` is run).
res = f(1, 2, 3, 'hello')

# Call 2 (loaded from cache).
res = f(1, 2, 3, 'world')
```

#### Refreshing
If for whatever reason, it is desired for the body of a `Cachable` function to be rerun with a set of parameters previously used, a special parameter called `_refresh` can be used, e.g.,
```python
from cachable import Cachable

@Cachable(directory='cache')
def f(a, b, c):
    return dict(a=a, b=b, c=c)
    
# Call 1 (body of `f` is run).
res = f(1, 2, 3)

# Call 2 (body of `f` is run).
res = f(1, 2, 3, _refresh=True)
```

### Loaders

By default, the results of `Cachable` functions are saved using python's `pickle` utility.
If another format is preferred, an alternative loader can be used.
Several default implementations of alternative loaders can be found in the `cachable.loaders` package.
For example, to cache a Keras model, the following could be used to save the resulting model as an `h5` file using Keras' `model.save()`:
```python
from cachable import Cachable
from cachable.loaders import KerasModelLoader

@Cachable(name='my_cached_model', directory='cache', loader=KerasModelLoader())
def create_and_train_model(**model_hyperparameters):
    # Create and train a model...
    return model
```
