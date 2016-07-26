"""Validate objects against patterns
"""

__all__ = ('validate_object', 'every_element', 'one_of', 'all_of')

def equal(x, y):
    # Python doesn't have a proper eql predicate: '==' is pretty much
    # EQUAL, while 'is' is EQ.  This is just one of Python's many
    # uselessnesses.
    return x == y

def validate_object(ob, pattern, eql=equal):
    """Return True if ob matches pattern, otherwise False.

    ob matches pattern if:
    - they are both dictionaries of the same size, ob is an instance
      of pattern's type, they have the same keys, and the values of
      the keys match;
    - they are both lists or tuples, ob is an instance of pattern's
      type, they are the same length and their entries match;
    - pattern is a type and ob is an instance of that type;
    - pattern is a predicate (a function) which returns true on ob;
    - eql(ob, pattern) is true, where eql defaultly compares with ==.

    Note there is no occurs check: if ob or pattern is circular this
    will fail to terminate.

    See every_element, which is a function which returns suitable
    predicates for checking that every element of an iterable matches
    some pattern.
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
    elif isinstance(pattern, type):
        return True if isinstance(ob, pattern) else False
    elif callable(pattern):
        # if the pattern is a function simply call it on the object
        # and return True if its result is true.  Note this means you
        # can't directly compare functions in the object: you need to
        # use something like lambda x: x == <fn>
        return True if pattern(ob) else False
    else:
        # just use eql
        return True if eql(ob, pattern) else False

def every_element(pattern, tp=None, eql=equal):
    """Return a predicate which will check every element in an iterable.

    - pattern is the pattern to check each element against;
    - tp, if given, is a type which the iterable should be an instance
      of;
    - eql, if given, is the equality predicate for validate_object;

    This then returns a function of one argument which validate_object
    will use to check the object.
    """
    def eep(ob):
        if tp is None or isinstance(ob, tp):
            for e in ob:
                if not validate_object(e, pattern, eql=eql):
                    return False
            return True
        else:
            return False
    return eep

def one_of(patterns, eql=equal):
    """Return a predicate which checks an object matches one of the patterns.
    """
    def oop(ob):
        for p in patterns:
            if validate_object(ob, p, eql=eql):
                return True
        return False
    return oop

def all_of(patterns, eql=equal):
    """Return a predicate which checks an object matches all of the patterns.
    """
    def aop(ob):
        for p in patterns:
            if not validate_object(ob, p, eql=eql):
                return False
        return True
    return aop
