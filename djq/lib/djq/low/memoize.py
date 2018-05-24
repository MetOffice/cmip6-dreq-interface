# (C) British Crown Copyright 2018, Met Office.
# See LICENSE.md in the top directory for license details.
#

"""Memoizing functions in a thread-safe way
"""

# A memoized function is a function, usually of one argument (see
# 'spread' below), which, when called, looks up that argument in a
# table, and if it's there returns what it finds.  If it's not there
# it computes a value and stores it in the table under the argument
# before returning.  Computationally expensive functions can be hugely
# sped up this way if the number of possible arguments is small in
# practice.
#
# This code works by having a fluid variable which may be bound to a
# Memos object.  Memos is a subclass of defaultdict, which maps from
# functions to the dicts where they keep their memoized results.  (The
# only reason for Memos to be a subclass of defaultdict is that I
# wanted to abstract the implementation slightly: it would probably
# work as well to just have a make_memos() function.).  The fluid
# (memos) is by default bound to None, so memoization does not happen.
#
# There is then a decorator, memoizable, which suitably wraps a
# function with the memoization code.  It has an optional argument,
# key, which, if given, should be a function which, when applied to
# the argument of the memoized function, returns a suitable key for
# the table.  This can be used to create hashable keys for arguments
# which aren't themselves hashable or (for instance) to quantize float
# arguments into buckets.
#
# In fact it's possible to have memoizable functions of more than one
# argument, using the 'spread' option to memoizable.  If this is
# given them the wrapper function gets a tuple of all the arguments
# which it looks up in the table (it's a 'nospread' function), before,
# if needing, calling the wrapped function with tuple as separate
# arguments ('spreading' them).  For this to work the tuple of
# arguments must be hashable (or you need to use a key option), which
# means that all its elements must be hashable.
#
# The decorator is called 'memoizable' not 'memoized' because it only
# says that a function *may* be memoized: unless the memos fluid if
# bound it won't be.
#
# The use of a fluid means that you can isolate memoized usage of a
# function, that the code is thread-safe, and also that the memos
# table (which can potentially be large can be disposed of
# automagically when the stack is unwound.
#

__all__ = ('memos', 'Memos', 'memoizable')

from collections import defaultdict
from nfluid import fluid, globalize

memos = globalize(fluid(), None, threaded=True)

class Memos(defaultdict):
    def __init__(self):
        super(Memos, self).__init__(dict)

def memoizable(function=None, key=None, spread=False):
    def memoized(f):
        def memoized_single(x):
            stashes = memos()
            if stashes is not None:
                stash = stashes[f]
                k = x if key is None else key(x)
                if k in stash:
                    return stash[k]
                else:
                    v = f(x)
                    stash[k] = v
                    return v
            else:
                return f(x)
        def memoized_spread(*args):
            stashes = memos()
            if stashes is not None:
                stash = stashes[f]
                k = args if key is None else key(args)
                if k in stash:
                    return stash[k]
                else:
                    v = f(*args)
                    stash[k] = v
                    return v
            else:
                return f(*args)
        return memoized_single if not spread else memoized_spread
    return (memoized(function) if function is not None
            else lambda f: memoized(f))
