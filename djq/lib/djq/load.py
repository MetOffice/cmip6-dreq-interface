"""Loading versions of the CMIP6 data request
"""

from os import getenv
from os.path import expanduser, expandvars, isdir, join
from dqi.util import load_from_dqroot as ldq

__all__ = ('default_dqroot', 'default_dqtag', 'valid_dqroot', 'valid_dqtag',
           'dqload')

dqroot = (expandvars("$DJQ_DQROOT") if getenv("DJQ_DQROOT")
         else expanduser("~tbradsha/work/cmip6-data-request/CMIP6dreq"))

dqtag = getenv("DJQ_DQTAG") or "latest"

def default_dqroot(root=None):
    global dqroot
    if root is None:
        return dqroot
    else:
        dqroot = root

def default_dqtag(tag=None):
    global dqtag
    if tag is None:
        return dqtag
    else:
        dqtag = tag

def valid_dqroot(root=None):
    """Check whether root (defaulted from dqroot) smells like a dreq root dir.

    The check is necessarily heuristic, not exhaustive.  Note that root
    is defaulted dynamically.
    """
    if root is None:
        root = dqroot
    if isdir(root) and isdir(join(root, "tags")):
        return True
    else:
        return False

def valid_dqtag(tag=None, root=None):
    """Is tag a valid tag for the dreq anchored at root?

    This is a heuristic check.  Note that root is defaulted dynamically
    from dqroot and tag from dqtag
    """
    if isdir(join(root if root is not None else dqroot,
                  "tags",
                  tag if tag is not None else dqtag,
                  "dreqPy", "docs")):
        return True
    else:
        return False

def dqload(tag=None, root=None):
    """Load the dreq from a tag and root, both dynamically defaulted.

    Arguments:
    - tag -- the tag, dynamically defaulted from dqtag
    - root -- the dreq root directory, dynamically defaulted from dqroot

    This does no error checks itself : it will raise whatever
    exception the underlying dreq code does if things are bad.  If you
    want to check for this use the valid_* functions.
    """
    return ldq(join(root if root is not None else dqroot,
                    "tags",
                    tag if tag is not None else dqtag,
                    "dreqPy", "docs"))
