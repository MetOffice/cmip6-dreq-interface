"""Loading versions of the CMIP6 data request
"""

from os import getenv
from os.path import expanduser, expandvars, isdir, join
from dqi.util import load_from_dqroot as ldq

__all__ = ('dqtop', 'dqtag', 'valid_dqtop', 'valid_dqtag',
           'dqload', 'ldq')

dqtop = (expandvars("$DJQ_DQTOP") if getenv("DJQ_DQTOP")
         else expanduser("~tbradsha/work/cmip6-data-request/CMIP6dreq"))

dqtag = getenv("DJQ_DQTAG") or "latest"

def valid_dqtop(top=None):
    """Check whether top (defaulted from dqtop) smells like a dreq top dir.

    The check is necessarily heuristic, not exhaustive.  Note that top
    is defaulted dynamically.
    """
    if top is None:
        top = dqtop
    if isdir(top) and isdir(join(top, "tags")):
        return True
    else:
        return False

def valid_dqtag(tag=None, top=None):
    """Is tag a valid tag for the dreq anchored at top?

    This is a heuristic check.  Note that top is defaulted dynamically
    from dqtop and tag from dqtag
    """
    if isdir(join(top if top is not None else dqtop,
                  "tags",
                  tag if tag is not None else dqtag,
                  "dreqPy", "docs")):
        return True
    else:
        return False

def dqload(tag=None, top=None):
    """Load the dreq from a tag and top, both dynamically defaulted.

    Arguments:
    - tag -- the tag, dynamically defaulted from dqtag
    - top -- the dreq top directory, dynamically defaulted from dqtop

    This does no error checks itself : it will raise whatever
    exception the underlying dreq code does if things are bad.  If you
    want to check for this use the valid_* functions.
    """
    return ldq(join(top if top is not None else dqtop,
                    "tags",
                    tag if tag is not None else dqtag,
                    "dreqPy", "docs"))
