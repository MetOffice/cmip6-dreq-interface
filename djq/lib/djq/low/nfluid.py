"""Fluid (dynamic) bindings for Python
"""

# Fluid bindings are functions which look themselves up in a stack to
# find or set their values.  This therefore implements deeply-bound
# dynamic variables.  The stack has a global top, and each thread has
# at least oner stack frame below that.  Fluids can be made such that
# they are automagically rebound into the thread's top stack frame.
#
# Some operations you might want are missing: you can make new fluids
# with fluid, bind them locally with the fluids context manager and
# remove toplevel bindings with evaporate (which may go away), but
# there is no public boundp function, no way of controlling what the
# thread-default value is after creating a fluid and so on.  The
# intention is to provide enough to be useful with an interface which
# smells stable rather than to try and fail to make a language-quality
# interface.
#

__all__ = ('fluid', 'fluids', 'evaporate')

from threading import local

class Catastrophe(Exception):
    # A horror
    pass

class Silly(Exception):
    # Asking for something impossible
    pass

class Unbound(Exception):
    # Unbound fluid
    def __init__(self, var):
        self.var = var

# Each element in the stack of bindings is a two-element tuple with
# the first element being a dict mapping fluids to values and the
# second element being the rest of the stack, or None.
#
# This is the top of the stack, which contains global values for
# fluids.  Below this, all stack framnes are per-thread, and each
# thread has at least one such frame.
#
global_frame = ({}, None)

# This is a set of fluids which get rebound when a thread is created:
# whatever binding they have globally is copied into the thread's top
# stack frame
#
thread_bound = set()

class State(local):
    initialized = False
    def __init__(self):
        if self.initialized:
            raise SystemError("reinitialized")
        self.initialized = True
        try:
            frame = ({f: global_frame[0][f]
                      for f in thread_bound},
                     global_frame)
        except KeyError:
            raise Catastrophe("trying to rebind a fluid with no global value")
        self.__dict__['toplevel_frame'] = frame
        self.__dict__['frame'] = frame

state = State()

def getval(var):
    def rv(bt):
        (car, cdr) = bt
        if var in car:
            return car[var]
        elif cdr is not None:
            return rv(cdr)
        else:
            raise Unbound(var)
    return rv(state.frame)

def setval(var, val):
    def loc(bt):
        (car, cdr) = bt
        if var in car:
            return car
        elif cdr is not None:
            return loc(cdr)
        else:
            raise Unbound(var)
    loc(state.frame)[var] = val
    return val

def boundp(var):
    def bp(bt):
        (car, cdr) = bt
        if var in car:
            return True
        elif cdr is not None:
            return bp(cdr)
        else:
            return False
    return bp(state.frame)

def fluid(val=None, toplevel=False, threaded=False):
    """Make a new bound fluid variable"""
    if threaded and not toplevel:
        raise Silly("threaded fluids must be bound at toplevel")
    var = (lambda val=None:
               (setval(var, val)
                if val is not None
                else getval(var)))
    if toplevel:
        # bind globally
        global_frame[0][var] = val
        if threaded:
            # Note it should be rebound, and bind at thread toplevel
            thread_bound.add(var)
            state.toplevel_frame[0][var] = val
    else:
        # bind locally
        state.frame[0][var] = val
    return var

def evaporate(var):
    """Remove any toplevel binding of a fluid.

    This will make it have no global binding, no toplevel binding in
    this thread, and stop it being bound per-thread.  Existing
    bindings in other threads are not altered, and if there are
    non-toplevel bindings in the current thread they will persist
    until the stack is unwound.

    This function may go away.
    """
    thread_bound.discard(var)
    global_frame[0].pop(var, None)
    state.toplevel_frame[0].pop(var, None)

class fluids(object):
    """Context manager for fluid bindings"""

    def __init__(self, *bindings):
        self.bindings = {}
        for (var, val) in bindings:
            if not boundp(var):
                raise Unbound(var)
            self.bindings[var] = val

    def __enter__(self):
        state.frame = (self.bindings, state.frame)
        return self

    def __exit__(self, ext, exv, tb):
        state.frame = state.frame[1]
        return None
