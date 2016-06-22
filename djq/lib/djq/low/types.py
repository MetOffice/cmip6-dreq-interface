"""Some type predicates
"""

# All of these are meant to tell if something behaves in a given way
# *not considering mutability*.  They are also unlikely to be
# complete: these are just the types that are used in the code.
#

__all__ = ('arraylike', 'stringlike', 'setlike')

def arraylike(thing):
    """Is thing like an array?"""
    return isinstance(thing, list) or isinstance(thing, tuple)

def stringlike(thing):
    """Is thing like a string?"""
    return isinstance(thing, str) or isinstance(thing, unicode)

def setlike(thing):
    """Is thing like a set?"""
    return isinstance(thing, set) or isinstance(thing, frozenset)
