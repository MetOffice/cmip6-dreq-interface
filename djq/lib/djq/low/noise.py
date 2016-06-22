"""Talking
"""

__all__ = ('verbosity_level', 'debug_level',
           'chatter', 'mutter', 'mumble', 'whisper', 'think',
           'debug')

from sys import stderr
from traceback import format_stack

verbosity = 0

def verbosity_level(l=None):
    """Get or set the verbosity level"""
    global verbosity
    if l is None:
        return verbosity
    else:
        verbosity = l

debugity = 0

def debug_level(l=None):
    """Get or set the debug level """
    global debugity
    if l is None:
        return debugity
    else:
        debugity = l

def maybe_talk(level, message, *arguments):
    if level > 0:
        print >>stderr, message.format(*arguments)

def chatter(message, *arguments):
    """Talk"""
    maybe_talk(1, message, *arguments)

def mutter(message, *arguments):
    """Talk if verbose"""
    maybe_talk(verbosity, message, *arguments)

def mumble(message, *arguments):
    """Talk if very verbose"""
    maybe_talk(verbosity - 1, message, *arguments)

def whisper(message, *arguments):
    """Talk if extremely verbose"""
    maybe_talk(verbosity - 2, message, *arguments)

def think(message, *arguments):
    """Talk if ludicrously verbose"""
    maybe_talk(verbosity - 3, message, *arguments)

def debug(message, *arguments):
    """Talk if debugging"""
    try:
        maybe_talk(debugity, message, *arguments)
    except Exception as e:
        print >>stderr, "mutant bug horror: {}\n{}".format(e,
                                                           format_stack()[-2]),
