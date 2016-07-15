"""thread-local objects with defaults"""

__all__ = ('State',)

from threading import local

class State(local):
    """Local state with initialisation"""
    initialized = False
    def __init__(self, **kws):
        if self.initialized:
            raise SystemError("multiple local init?")
        self.initialized = True
        self.__dict__.update(kws)
