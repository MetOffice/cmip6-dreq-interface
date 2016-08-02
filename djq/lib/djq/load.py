"""Loading versions of the CMIP6 data request
"""

# Package interface
__all__ = ('default_dqroot', 'default_dqtag',
           'valid_dqroot', 'valid_dqtag')

# Interface
# - dqload

from os import getenv
from sys import argv
from low import fluid, globalize
from os.path import expanduser, expandvars, isdir, join, split
from dreqPy.dreq import loadDreq, defaultDreqPath, defaultConfigPath

# Thread-local fluids for the default root and tag.
#
# Either listen to environment variables, or fall back to a directory
# based on the location of the script, which is essentially
# ../data/CMIP6dreq.  This will almost always be wrong, but we have to
# try something.
#
# Python's pathname tools are annoyingly rudimentary compared to
# File::Spec, hence this arcana.
#

default_dqroot = globalize(fluid(),
                           (expandvars("$DJQ_DQROOT")
                            if getenv("DJQ_DQROOT")
                            else join(split(split(argv[0])[0])[0],
                                      "data", "CMIP6dreq")),
                           threaded=True)

default_dqtag = globalize(fluid(),
                          getenv("DJQ_DQTAG") or "latest",
                          threaded=True)

def valid_dqroot(dqroot=None):
    """Check whether dqroot smells like a dreq dqroot dir.

    The check is necessarily heuristic, not exhaustive.  Note that dqroot
    is defaulted dynamically from default_dqroot().
    """
    if dqroot is None:
        dqroot = default_dqroot()
    if isdir(dqroot) and isdir(join(dqroot, "tags")):
        return True
    else:
        return False

def valid_dqtag(dqtag=None, dqroot=None):
    """Is dqtag a valid tag for the dreq anchored at dqroot?

    This is a heuristic check.  Note that dqroot is defaulted dynamically
    from default_dqroot() and dqtag from default_dqtag()
    """
    if isdir(join(dqroot if dqroot is not None else default_dqroot(),
                  "tags",
                  dqtag if dqtag is not None else default_dqtag(),
                  "dreqPy", "docs")):
        return True
    else:
        return False

def dqload(dqtag=None, dqroot=None):
    """Load the dreq from a dqtag and dqroot, both dynamically defaulted.

    Arguments:
    - tag -- the tag, dynamically defaulted from default_dqtag()
    - dqroot -- the dreq root directory, dynamically defaulted from
      default_dqroot()

    This does no error checks itself : it will raise whatever
    exception the underlying dreq code does if things are bad.  If you
    want to check for this use the valid_* functions.
    """
    # This replicates some code in dqi.util and dqi.low, to avoid a
    # dependency on dqi as this is the only place djq relied on it.
    top = join(dqroot if dqroot is not None else default_dqroot(),
                  "tags",
                  dqtag if dqtag is not None else default_dqtag(),
                  "dreqPy", "docs")
    return loadDreq(dreqXML=join(top, split(defaultDreqPath)[1]),
                    configdoc=join(top, split(defaultConfigPath)[1]))
