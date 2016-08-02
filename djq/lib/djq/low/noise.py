"""Talking
"""

__all__ = ('verbosity_level', 'debug_level',
           'chatter', 'mutter', 'mumble', 'whisper', 'think',
           'debug')

from sys import stderr
from nfluid import fluid, globalize
from traceback import format_stack

verbosity_level = globalize(fluid(), 0, threaded=True)
debug_level = globalize(fluid(), 0, threaded=True)

def maybe_talk(level, message, *arguments):
    if level > 0:
        print >>stderr, message.format(*arguments)

def chatter(message, *arguments):
    """Talk"""
    maybe_talk(1, message, *arguments)

def mutter(message, *arguments):
    """Talk if verbose"""
    maybe_talk(verbosity_level(), message, *arguments)

def mumble(message, *arguments):
    """Talk if very verbose"""
    maybe_talk(verbosity_level() - 1, message, *arguments)

def whisper(message, *arguments):
    """Talk if extremely verbose"""
    maybe_talk(verbosity_level() - 2, message, *arguments)

def think(message, *arguments):
    """Talk if ludicrously verbose"""
    maybe_talk(verbosity_level() - 3, message, *arguments)

def debug(message, *arguments):
    """Talk if debugging"""
    try:
        maybe_talk(debug_level(), message, *arguments)
    except Exception as e:
        print >>stderr, "mutant bug horror: {}\n{}".format(e,
                                                           format_stack()[-2]),
