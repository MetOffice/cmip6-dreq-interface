# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

"""Dynamic bindings for Python (New Fluids)
"""

# Fluids, or dynamic variables are functions which look themselves up
# in a stack to find or set their values.  This therefore implements
# deeply-bound dynamic variables.  The stack has a global top, and
# each thread has at least oner stack frame below that.  Fluids can be
# made such that they are automagically rebound into the thread's top
# stack frame.
#
# This is not really a general-purpose implementation, and is probably
# idiosyncractic, but it works well enough.
#
# Fluid variables are functions which can be called with zero or one
# argument: when called with no argument they return their current
# binding (or raise an Unbound exception if they are not bound), and
# when called with one argument they set their current value.  A fluid
# must be bound to set its value.  fluid() constructs fluids.
#
# boundp(v) tells you if v is bound.
#
# To locally bind fluids use the fluids context manager:
#
#  v = fluid()
#  with fluids((v, 2)):
#      assert v() == 2
#      v(3)
#      assert v() == 3
#  assert not boundp(v)
#
# To globally bind a fluid use globalize: globalize(v, val) will make
# v have the global value val.  globalize(v, val, threaded=True) will
# do the same but cause it to be rebound at the top of each thread, so
# each thread gets the default value val.  The fluid may also be
# locally bound of course (and may already be locally bound before it
# is globalized: its local value will be unchanged).  You can call
# globalize repeatedly which will alter the top-level binding and can
# alter its threadedness.
#
# localize(v) undoes everything that globalize does.  Again, if there
# is a local binding it will not be changed.
#
# There is currently no way of knowing if a fluid is threaded or, if
# it is bound, whether it has been globalized at all.
#

__all__ = ('fluid', 'boundp', 'globalize', 'localize', 'fluids',
           'Unbound')

from threading import local

class Catastrophe(Exception):
    # A horror
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

def getf(var):
    # get a fluid value (nothing to do with CL's GETF, I just liked
    # the name)
    def rv(bt):
        (car, cdr) = bt
        if var in car:
            return car[var]
        elif cdr is not None:
            return rv(cdr)
        else:
            raise Unbound(var)
    return rv(state.frame)

def setf(var, val):
    # set a fluid value (again, no relation to SETF)
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
    # is a fluid bound (this *is* related to BOUNDP)
    def bp(bt):
        (car, cdr) = bt
        if var in car:
            return True
        elif cdr is not None:
            return bp(cdr)
        else:
            return False
    return bp(state.frame)

def fluid():
    """Make a new unbound fluid variable"""
    # If Python had any coherent semantics for binding variables, this
    # would rely on letrec / labels semantics, rather than let / flet:
    # the binding corresponding to the function needs to be visible to
    # the function itself.
    var = (lambda val=None:
               (setf(var, val)
                if val is not None
                else getf(var)))
    return var

def globalize(var, val, threaded=False):
    """globalize a fluid variable.

    This makes it have a toplevel value and, if threaded is true,
    causes it to be rebound per thread.
    """
    global_frame[0][var] = val
    if threaded:
        # Note it should be rebound, and bind at thread toplevel
        thread_bound.add(var)
        state.toplevel_frame[0][var] = val
    else:
        # Remove any rebinding state
        thread_bound.discard(var)
        state.toplevel_frame[0].pop(var, None)
    return var

def localize(var):
    """Remove any toplevel binding of a fluid.

    This will make it have no global binding, no toplevel binding in
    this thread, and stop it being bound per-thread.  Existing
    bindings in other threads are not altered, and if there are
    non-toplevel bindings in the current thread they will persist
    until the stack is unwound.
    """
    thread_bound.discard(var)
    global_frame[0].pop(var, None)
    state.toplevel_frame[0].pop(var, None)
    return var

class fluids(object):
    """Context manager for fluid bindings"""

    def __init__(self, *bindings):
        self.bindings = {}
        for (var, val) in bindings:
            self.bindings[var] = val

    def __enter__(self):
        state.frame = (self.bindings, state.frame)
        return self

    def __exit__(self, ext, exv, tb):
        state.frame = state.frame[1]
        return None
