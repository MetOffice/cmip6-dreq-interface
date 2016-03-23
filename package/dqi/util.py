# Utilities for dqi
#
# This can depend on the dreq API
#

__all__ = ['load_from_dqroot', 'walk_from_dqroot']

from dreqPy.dreq import loadDreq, defaultDreqPath, defaultConfigPath
from .low import reroot_paths
from .walker import walk_dq

def load_from_dqroot(dqroot=None):
    (dqxml, dqconfig) = reroot_paths(dqroot,
                                     (defaultDreqPath, defaultConfigPath))
    return loadDreq(dreqXML=dqxml, configdoc=dqconfig)

def walk_from_dqroot(dqroot=None, *args, **kws):
    return walk_dq(load_from_dqroot(dqroot=dqroot), *args, **kws)
