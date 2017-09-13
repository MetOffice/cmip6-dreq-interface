# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

"""Loading versions of the CMIP6 data request
"""

# Package interface
__all__ = ('default_dqroot', 'default_dqtag',
           'valid_dqroot', 'valid_dqtag')

# Interface
# - dqload
# - effective_dqpath

from os import getenv
from sys import argv
from low import fluid, globalize
from low import debug
from os.path import expanduser, expandvars, isdir, join, split
from dreqPy.dreq import loadDreq, defaultDreqPath, defaultConfigPath
from dreqPy import __path__ as dreqPy_path

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
    return (isdir(dqroot)
            and isdir(join(dqroot, "tags"))
            and isdir(join(dqroot, "trunk")))

def valid_dqtag(dqtag=None, dqroot=None):
    """Is dqtag a valid tag for the dreq anchored at dqroot?

    This is a heuristic check.  Note that dqroot is defaulted dynamically
    from default_dqroot() and dqtag from default_dqtag()
    """
    if dqtag is not False:
        if isdir(join(dqroot if dqroot is not None else default_dqroot(),
                      "tags",
                      dqtag if dqtag is not None else default_dqtag(),
                      "dreqPy", "docs")):
            return True
        else:
            return False
    else:
        if isdir(join(dqroot if dqroot is not None else default_dqroot(),
                      "trunk", "dreqPy", "docs")):
            return True
        else:
            return False

def effective_dqpath(dqtag=None, dqroot=None):
    """Return the effective path to the DREQ.

    Arguments:
    - tag -- the tag, dynamically defaulted from default_dqtag()
    - dqroot -- the dreq root directory, dynamically defaulted from
      default_dqroot()
    """
    debug("dqroot    = {}\n  default = {}", dqroot, default_dqroot())
    debug("dqtag     = {}\n  default = {}", dqtag, default_dqtag())
    return (join(dqroot if dqroot is not None else default_dqroot(),
                 "tags",
                 dqtag if dqtag is not None else default_dqtag(),
                 "dreqPy", "docs")
            if dqtag is not False
            else join(dqroot if dqroot is not None else default_dqroot(),
                      "trunk", "dreqPy", "docs"))

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
    debug("dreqPy from {}", dreqPy_path[0])
    top = effective_dqpath(dqtag, dqroot)
    debug("effective = {}", top)
    xml = join(top, split(defaultDreqPath)[1])
    config = join(top, split(defaultConfigPath)[1])
    debug("XML       = {}\nconfig    = {}", xml, config)
    dreq = loadDreq(dreqXML=xml, configdoc=config, manifest=None)
    debug("loaded dreq version {}", dreq.version)
    return dreq
