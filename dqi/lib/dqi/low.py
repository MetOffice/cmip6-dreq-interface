# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

# Low level support for dqi
#
# Nothing here should depend on the dreq API: see util.py for that
#

__all__ = ['Badness']

from os.path import split, join

class Badness(Exception):
    pass

def reroot_paths(root, paths):
    # given a new root /d and a bunch of paths .../a, .../b return
    # /d/a, /d/b and so on
    if root is None:
        return paths
    else:
        return tuple(join(root, split(path)[1])
                     for path in paths)

class lazy(object):
    "a decorator class to produce a lazy, read-only slot"
    def __init__(self, getf):
        self.getf = getf
        self.__doc__ = getf.__doc__
        self.__name__ = getf.__name__

    def __get__(self, obj, objtype=None):
        if obj is None:         # class slot reference
            return self
        # This is depressingly dependent on the details of the
        # implementation: it essentially wedges the computed value
        # into the dictionary of obj, which means (since this is not a
        # data descriptor: no __set__ method) that next time the
        # result will come directly from there.
        name = self.__name__
        if name.startswith('__') and not name.endswith('__'):
            name = "_{}{}".format(objtype.__name__, name)
        r = self.getf(obj)
        obj.__dict__[name] = r
        return r
