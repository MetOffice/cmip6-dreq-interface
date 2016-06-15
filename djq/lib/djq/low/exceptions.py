# Exceptions

__all__ = ('InternalException', 'ExternalException', 'Scram')

class InternalException(Exception):
    """An exception which is our fault"""
    pass

class ExternalException(Exception):
    """An exception which is not out fault"""
    pass

class Scram(Exception):
    """An exception which should not be handled anywhere"""
