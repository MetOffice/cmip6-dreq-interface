# Low level

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
