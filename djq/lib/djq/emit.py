# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

"""Emitting replies
"""

# Currently this does no checking at all
#

# Package interface
__all__ = ()

# Interface
# - EmitFailed
# - emit_reply
# - emit_catastrophe

from json import dump
from low import InternalException

class EmitFailed(InternalException):
    def __init__(self, string, wrapped=None):
        super(EmitFailed, self).__init__(string)
        self.wrapped = wrapped
    def __str__(self):
        return "{}: {}".format(super(EmitComparisonFailed, self).__str__(),
                               self.wrapped)

def emit_reply(reply, fp):
    """Emit a reply as JSON on a stream.

    No useful return value.  Raises EmitFailed if anything goes wrong.
    """
    try:
        dump(reply, fp, indent=1)
        fp.write("\n")          # prettier: I think it is safe JSON
    except Exception as e:
        raise EmitFailed("badness when emitting", e)

def emit_catastrophe(message, fp, **others):
    """Emit a reply indicating a catastrophe has happened.

    No useful return value.  Does not wrap any exceptions.
    """
    dump(dict((('catastrophe', message),), **others), fp,
         indent=2)
    fp.write("\n")              # see above
