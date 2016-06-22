# Exceptions

__all__ = ('InternalException', 'ExternalException', 'Disaster',
           'Scram')

class InternalException(Exception):
    """An exception which is our fault"""
    pass

class ExternalException(Exception):
    """An exception which is not out fault"""
    pass

class Disaster(InternalException):
    """A general catastrophe which is our fault"""

class Scram(Exception):
    """An exception which should not be handled anywhere"""
