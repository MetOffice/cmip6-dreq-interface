"""Rudimentary & special-purpose dynamic binding
"""

# This is not very satisfactory, but there probably is no good
# solution to this problem in Python.
#
# This approach hides dynamic ('fluid') variables behind accessor
# functions (the idea coming from Racket's parameters), and then uses
# the code below to implement shallow binding of their values.
# However the accessor functions need to be very carefully written, as
# they need to make sure that the state they access is thread-local
# (see state.py and the documentation for threading.local).  The
# advantage of doing things like this is that naive code can just call
# the accessor functions and not care.
#
# An alternative approach would be to pass around an explicit
# deep-binding stack, so perhaps ({<varname>: <value>, ...}, <parent>)
# or something.  This might be better but it would require every
# function to know about it.  So it would not actually be better.
#
# Perhaps the best compromise would be to stash that stack in a single
# thread-local variable, and use some context-manager thing to wind
# and unwind the stack.  Accessor functions could then be written in
# some stylised way to access the stack: you could probably almost
# have Racket's make-parameter &c: p = make_parameter('p'), where
# make_parameter would do all the work of setting things up at the
# top-level of the stack, and then p would be the function which read
# the state.  That's almost rerooting (it isn't, but it smells a bit
# like it).  That's what should happen in all of this at some point.
#

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
