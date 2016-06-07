# Exceptions

__all__ = ('InternalException', 'ExternalException')

class InternalException(Exception):
    """An exception which is our fault"""
    pass

class ExternalException(Exception):
    """An exception which is not out fault"""
    pass
