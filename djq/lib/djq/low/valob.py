"""Validate objects against patterns
"""

__all__ = ('validate_object', 'every_element', 'some_elements')

def validate_object(ob, pattern, eql=lambda x, y: x == y):
    """Return True if ob matches pattern, otherwise False.

    ob matches pattern if:
    - they are both dictionaries of the same size, ob is an instance
      of pattern's type, they have the same keys, and the values of
      the keys match;
    - they are both lists or tuples, ob is an instance of pattern's
      type, they are the same length and their entries match;
    - pattern is a function which returns true on ob;
    - eql(ob, pattern) is true, where eql defaultly compares with ==.

    Note there is no occurs check: if ob or pattern is circular this
    will fail to terminate.
    """
    if isinstance(pattern, dict):
        # dictionaries should have matching keys and each value should
        # match
        if isinstance(ob, type(pattern)) and len(ob) == len(pattern):
            for (pk, pp) in pattern.iteritems():
                if pk not in ob or not validate_object(ob[pk], pp, eql):
                    return False
            return True
        else:
            return False
    elif isinstance(pattern, list) or isinstance(pattern, tuple):
        # arraylike things should have matching types, be the same
        # length, and each entry should match
        if isinstance(ob, type(pattern)) and len(ob) == len(pattern):
            for i in range(len(pattern)):
                if not validate_object(ob[i], pattern[i], eql):
                    return False
            return True
        else:
            return False
    elif callable(pattern):
        # if the pattern is a function simply call it on the object
        # and return True if its result is true.  Note this means you
        # can't directly compare functions in the object: you need to
        # use something like lambda x: x == <fn>
        return True if pattern(ob) else False
    else:
        # just use eql
        return True if eql(ob, pattern) else False

# CL's EVERY and SOME
#

def every_element(predicate, iterable):
    """Return True if predicate is true for every element of iterable."""
    for elt in iterable:
        if not predicate(elt):
            return False
    return True

def some_elements(predicate, iterable):
    """Return True if predicate is true for at least one element of iterable."""
    for elt in iterable:
        if predicate(elt):
            return True
    return False
