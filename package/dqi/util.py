# Some small utility functionality
#

__all__ = ['walk_from_dqroot']

from dreqPy.dreq import loadDreq, defaultDreqPath, defaultConfigPath
from .low import reroot_paths
from .walker import walk_dq

def walk_from_dqroot(dqroot=None, *args, **kws):
    (dqxml, dqconfig) = reroot_paths(dqroot,
                                     (defaultDreqPath, defaultConfigPath))
    return walk_dq(loadDreq(dreqXML=dqxml, configdoc=dqconfig), *args, **kws)
