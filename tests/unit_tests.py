import os
import unittest

from unittest import TestCase

from cachable import Cachable, CachableParam


class UnitTest(TestCase):

    def setUp(self):
        self.dir = 'tests/test_cache'

        if not os.path.exists(self.dir):
            os.mkdir(self.dir)

        self.assertEqual(os.path.split(os.getcwd())[1], 'caching')

        # Start with a clean cache directory.
        for filename in os.listdir(self.dir):
            os.remove(self.dir + '/' + filename)


    def test_basic(self):

        @Cachable('f', self.dir, debug=True)
        def f(a, b, c):
            c[0] += 1
            return dict(a=a, b=b, c=c)

        c = [3]

        res = f(1, 2, c)

        self.assertEqual(res.obj['a'], 1)
        self.assertEqual(res.obj['b'], 2)
        self.assertEqual(res.obj['c'], [4])

        # Make sure the function body was run.
        self.assertEqual(c[0], 4)

        # Make sure the file was created.
        self.assertTrue(os.path.exists(res._filename + '.pkl'))

        c = [3]

        res = f(1, 2, c)

        # Make sure the file contents were correct.
        self.assertEqual(res.obj['a'], 1)
        self.assertEqual(res.obj['b'], 2)
        self.assertEqual(res.obj['c'], [4])

        # Make sure the function body was not run.
        self.assertEqual(c[0], 3)


    def test_default_args(self):

        @Cachable('f', self.dir, debug=True)
        def f(a, b, c=3):
            b[0] += 1
            return dict(a=a, b=b, c=c)

        b = [2]

        res = f(1, b, 3)

        self.assertEqual(res.obj['a'], 1)
        self.assertEqual(res.obj['b'], [3])
        self.assertEqual(res.obj['c'], 3)

        # Make sure the function body was run.
        self.assertEqual(b[0], 3)

        # Make sure the file was created without 'c' in the filename.
        self.assertTrue(os.path.exists(res._filename + '.pkl'))
        self.assertFalse('c' in res._name)

        b = [2]

        res = f(1, b)

        # Make sure the file contents were correct.
        self.assertEqual(res.obj['a'], 1)
        self.assertEqual(res.obj['b'], [3])
        self.assertEqual(res.obj['c'], 3)

        # Make sure the function body was not run.
        self.assertEqual(b[0], 2)

        b = [2]

        res = f(1, b, 5)

        # Make sure the file contents were correct.
        self.assertEqual(res.obj['a'], 1)
        self.assertEqual(res.obj['b'], [3])
        self.assertEqual(res.obj['c'], 5)

        # Make sure the function body was run.
        self.assertEqual(b[0], 3)

        # Make sure the file was created with 'c' in the filename.
        self.assertTrue(os.path.exists(res._filename + '.pkl'))
        self.assertTrue('c' in res._name)

        b = [2]

        res = f(1, b, c=5)

        # Make sure the file contents were correct.
        self.assertEqual(res.obj['a'], 1)
        self.assertEqual(res.obj['b'], [3])
        self.assertEqual(res.obj['c'], 5)

        # Make sure the function body was not run.
        self.assertEqual(b[0], 2)

        b = [2]

        res = f(a=1, b=b, c=5)

        # Make sure the file contents were correct.
        self.assertEqual(res.obj['a'], 1)
        self.assertEqual(res.obj['b'], [3])
        self.assertEqual(res.obj['c'], 5)

        # Make sure the function body was not run.
        self.assertEqual(b[0], 2)


    def test_member_function(self):

        class T(object):

            def __init__(self):
                self.counter = 0

            @Cachable('f', self.dir, debug=True)
            def f(self, a, b, c=3):
                self.counter += 1
                return dict(a=a, b=b, c=c)

        t = T()

        res = t.f(6, b=9, c=3)

        self.assertEqual(res.obj['a'], 6)
        self.assertEqual(res.obj['b'], 9)
        self.assertEqual(res.obj['c'], 3)

        # Make sure the function body was run.
        self.assertEqual(t.counter, 1)

        # Make sure the file was created without 'c' in the filename.
        self.assertTrue(os.path.exists(res._filename + '.pkl'))
        self.assertFalse('c' in res._name)

        res = t.f(6, 9)

        self.assertEqual(res.obj['a'], 6)
        self.assertEqual(res.obj['b'], 9)
        self.assertEqual(res.obj['c'], 3)

        # Make sure the function body was not run.
        self.assertEqual(t.counter, 1)

        res = t.f(b=2, c=3, a=1)

        self.assertEqual(res.obj['a'], 1)
        self.assertEqual(res.obj['b'], 2)
        self.assertEqual(res.obj['c'], 3)

        # Make sure the function body was run.
        self.assertEqual(t.counter, 2)


    def test_member_function_no_args(self):

        class T(object):

            def __init__(self):
                self.counter = 0

            @Cachable('f', self.dir, debug=True)
            def f(self):
                self.counter += 1
                return []

        t = T()

        res = t.f()

        self.assertEqual(res.obj, [])

        # Make sure the function body was run.
        self.assertEqual(t.counter, 1)

        # Make sure the file was created without 'c' in the filename.
        self.assertTrue(os.path.exists(res._filename + '.pkl'))
        self.assertTrue(res._name == 'f')

        res = t.f()

        self.assertEqual(res.obj, [])

        # Make sure the function body was not run.
        self.assertEqual(t.counter, 1)


    def test_with_cachable_params(self):

        @CachableParam()
        class P(object):
            def __init__(self, a, b, c=3):
                self.counter = 0

        class F(object):
            def __init__(self):
                self.counter = 0

            @Cachable('f', self.dir, debug=True)
            def __call__(self, p, x):
                self.counter += 1
                return []

        f = F()

        res = f(P(1, 2, 3), 4)

        self.assertEqual(res.obj, [])

        # Make sure the function body was run.
        self.assertEqual(f.counter, 1)

        # Make sure the file was created without 'c' in the filename.
        self.assertTrue(os.path.exists(res._filename + '.pkl'))
        self.assertTrue('P' in res._name)
        self.assertTrue('a-1' in res._name)
        self.assertTrue('b-2' in res._name)
        self.assertTrue('c' not in res._name)

        res = f(P(1, 2, 3), 4)

        self.assertEqual(res.obj, [])

        # Make sure the function body was not run.
        self.assertEqual(f.counter, 1)

        res = f(P(1, 2, 4), 4)

        self.assertEqual(res.obj, [])

        # Make sure the function body was run.
        self.assertEqual(f.counter, 2)


if __name__ == '__main__':
    unittest.main() 
