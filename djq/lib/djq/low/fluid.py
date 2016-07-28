"""Rudimentary & special-purpose dynamic binding
"""

__all__ = ('fluid',)

from dtype import arraylike

class fluid(object):
    """A context manager class to support fluid bindings.

    Use as:
     with fluid((accessor, value[, bindp]), ...) [as ...]:
         ...

    Each accessor is a function which:
    - when called with no arguments will return the state of something
    - when called with a single argument will set the state of that thing.

    On entry, for each binding, if bindp is not present, or is present
    and is true, this will:
    - record the value of accessor();
    - call accessor(value) to set the new value.

    On exit this will, for each accessor recorded above, and in
    reverse order of bindings:
    - call accessor(saved_value) to reset the value.

    Note the this is not general purpose: apart from anything else
    proper dynamic scope needs support from the runtime of the
    language. This just implements a cheap-and-nasty shallow-binding
    model, assuming suitably-written accessors.

    If accessor functions raise exceptions then bad things will
    follow.

    The lower-case name is deliberate.
    """

    def __init__(self, *bindings):
        for binding in bindings:
            if not (arraylike(binding)
                    and (2 <= len(binding) <= 3)
                    and callable(binding[0])):
                raise Exception("bad bindings")
        self.bindings = bindings
        self.state = None

    def __enter__(self):
        if self.state is not None:
            # you can only use an instance once
            raise Exception("recursive doom")
        self.state = []
        for binding in self.bindings:
            if (len(binding) == 2
                or (len(binding) == 3 and binding[2])):
                accessor = binding[0]
                value = binding[1]
                self.state.insert(0, (accessor, accessor()))
                accessor(value)
        return self

    def __exit__(self, ext, exv, tb):
        for (accessor, value) in self.state:
            accessor(value)
        return None
