# (C) British Crown Copyright 2016-2018, Met Office.
# See LICENSE.md in the top directory for license details.
#

"""Loading versions of the CMIP6 data request
"""

# Package interface
__all__ = ('default_dqroot', 'default_dqtag',
           'valid_dqroot', 'valid_dqtag',
           'default_dqpath')

# Interface
# - dqload
# - effective_dqpath

from os import getenv
from sys import argv
from low import fluid, globalize
from low import debug
from metadata import note_reply_metadata
from os.path import isdir, join, split
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
                           (getenv("DJQ_DQROOT")
                            or join(split(split(argv[0])[0])[0],
                                    "data", "CMIP6dreq")),
                           threaded=True)

default_dqtag = globalize(fluid(),
                          getenv("DJQ_DQTAG") or "latest",
                          threaded=True)

default_dqpath = globalize(fluid(), None, threaded=True)

def valid_dqroot(dqroot=None):
    """Check whether dqroot smells like a dreq dqroot dir.

    The check is necessarily heuristic, not exhaustive.  Note that dqroot
    is defaulted dynamically from default_dqroot().
    """
    if dqroot is None:
        dqroot = default_dqroot()
    return ((dqroot is not None)
            and isdir(dqroot)
            and isdir(join(dqroot, "tags"))
            and isdir(join(dqroot, "trunk")))

def valid_dqtag(dqtag=None, dqroot=None):
    """Is dqtag a valid tag for the dreq anchored at dqroot?

    This is a heuristic check.  Note that dqroot is defaulted dynamically
    from default_dqroot() and dqtag from default_dqtag()
    """
    if dqtag is None:
        dqtag = default_dqtag()
    if dqtag is None:
        return False
    elif dqtag is not False:
        if isdir(join(dqroot if dqroot is not None else default_dqroot(),
                      "tags", dqtag, "dreqPy", "docs")):
            return True
        else:
            return False
    else:
        if isdir(join(dqroot if dqroot is not None else default_dqroot(),
                      "trunk", "dreqPy", "docs")):
            return True
        else:
            return False

def effective_dqpath(dqtag=None, dqroot=None, dqpath=None):
    """Return the effective path to the DREQ.

    Arguments:
    - tag -- the tag, dynamically defaulted from default_dqtag()
    - dqroot -- the dreq root directory, dynamically defaulted from
      default_dqroot()
    - dqpath -- the path, dynamically defaulted from default_dqpath()

    If either dqpath is given or default_dqpath is not None, then
    return that, alse construct a suitable path using the root & tag.
    """
    note_reply_metadata(dqroot=dqroot, default_dqroot=default_dqroot(),
                        dqtag=dqtag, default_dqtag=default_dqtag(),
                        dqpath=dqpath, default_dqpath=default_dqpath())
    if dqpath is None:
        dqpath = default_dqpath()
    if dqtag is None:
        dqtag = default_dqtag()
    if dqroot is None:
        dqroot = default_dqroot()
    if dqpath is not None:
        return dqpath
    elif dqtag is not False:
        return join(dqroot, "tags", dqtag, "dreqPy", "docs")
    else:
        return join(dqroot, "trunk", "dreqPy", "docs")

def dqload(dqtag=None, dqroot=None, dqpath=None):
    """Load the dreq from a dqtag and dqroot and dpath, all defaulted.

    Arguments:
    - tag -- the tag, dynamically defaulted from default_dqtag()
    - dqroot -- the dreq root directory, dynamically defaulted from
      default_dqroot()
    - dqpath -- the path to the XML directory, dynamically-defaulted from
      default_dqpath.

    This does no error checks itself : it will raise whatever
    exception the underlying dreq code does if things are bad.  If you
    want to check for this use the valid_* functions.

    """
    # This replicates some code in dqi.util and dqi.low, to avoid a
    # dependency on dqi as this is the only place djq relied on it.
    note_reply_metadata(dreqpy_path=dreqPy_path)
    top = effective_dqpath(dqtag=dqtag, dqroot=dqroot, dqpath=dqpath)
    xml = join(top, split(defaultDreqPath)[1])
    config = join(top, split(defaultConfigPath)[1])
    note_reply_metadata(dreq_top=top,
                        dreq_xml=xml,
                        dreq_config=config)
    dreq = loadDreq(dreqXML=xml, configdoc=config, manifest=None)
    note_reply_metadata(dreq_loaded_version=dreq.version)
    return dreq
