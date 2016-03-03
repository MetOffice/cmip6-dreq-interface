# PathDicts are dicts (of dicts)* and can take keys which are tuples
# to search the tree.
#
# This is a case where Python is actually some good
#
# Note that, for instance, the keys method only returns the toplevel
# keys: doing anything else would be insane in fact, as there are a
# lot of key tuples.
#

class PathDict(dict):
    def __getitem__(self, key):
        if isinstance(key, tuple):
            # d[x,y,...]
            value = self
            for k in key:
                value = value[k]
            return value
        else:
            # d[x]
            return super(PathDict, self).__getitem__(key)
    
    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            # The trick is to find the last dict in the tree, and
            # update that
            self[key[0:-1]][key[-1]] = value
        else:
            super(PathDict, self).__setitem__(key, value)
        
