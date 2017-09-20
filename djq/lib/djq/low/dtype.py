# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

"""Some (duck) type predicates
"""

# All of these are meant to tell if something behaves in a given way
# *not considering mutability*.  They are also unlikely to be
# complete: these are just the types that are used in the code.
#

__all__ = ('arraylike', 'stringlike', 'setlike')

def arraylike(thing):
    """Is thing like an array?"""
    return isinstance(thing, (list, tuple))

def stringlike(thing):
    """Is thing like a string?"""
    return isinstance(thing, (str, unicode))

def setlike(thing):
    """Is thing like a set?"""
    return isinstance(thing, (set, frozenset))

def numberlike(thing):
    """Is thing some kind of number?"""
    return isinstance(thing, (int, float, long, complex))
