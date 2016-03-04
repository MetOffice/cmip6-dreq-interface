# PathDicts are dicts (of dicts)* and can take keys which are tuples
# to search the tree.
#
# This is a case where Python is actually some good: being able to
# just subclass dict is a win and would not be possible in CL, say.
#
# However note that, for instance, the keys method only returns the
# toplevel keys: doing anything else would be insane in fact, as there
# are a lot of key tuples.  However, __contains__ *is* implemented,
# which means things are not consistent although they are useful in
# practice.
#
# There is a problem with recursion here, which this tries to
# overcome: x[(1, 2), 3] ends up as x.__getitem(((1, 2), 3)), and then
# the first step would, naively, end up as x.__getitem[(1, 2)], which
# isn't right.  So instead this makes sure that the first step calls
# the superclass method.  Hence all the checks for things being self.
# However I am not sure this is completely right.
#

class PathDict(dict):
    def __getitem__(self, key):
        if isinstance(key, tuple):
            # d[x,y,...]
            value = self
            for k in key:
                value = (super(PathDict, self).__getitem__(k)
                         if value is self
                         else value[k])
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

    def __contains__(self, key):
        # This is just a mess since it needs to deal with preventing
        # recursion and with crashing into things which aren't dicts
        # or anything like them.  Note that __contains__ means
        # semantically *different* things in Python for different
        # types: [1,2,3].__contains__(3) does not mean that [1,2,3][3]
        # is valid.  Oh, Python.
        if isinstance(key, tuple):
            found = self
            for k in key:
                if found is self:
                    s = super(PathDict, self)
                    if s.__contains__(k):
                        found = s.__getitem__(k)
                    else:
                        return False
                elif hasattr(found, '__contains__') and  k in found:
                    found = found[k]
                else:
                    return False
            return True
        else:
            return super(PathDict, self).__contains__(key)
