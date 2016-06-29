"""Exceptions for djq
"""

__all__ = ('DJQException', 'InternalException', 'ExternalException',
           'Disaster', 'Scram')

class DJQException(Exception):
    """Any DJQ exception should inherit from this"""
    pass

class InternalException(DJQException):
    """An exception which is our fault"""
    pass

class ExternalException(DJQException):
    """An exception which is not out fault"""
    pass

class Disaster(InternalException):
    """A general catastrophe which is our fault"""

class Scram(DJQException):
    """An exception which should not be handled anywhere"""
    pass
