"""Computing variables by inverting the map from variables to mips
"""

__all__ = ()

from sys import modules
from collections import defaultdict
from dqi import mips_of_cmv
from djq.low import checker
from djq.variables.compute import pre_checks, post_checks

impl = modules[__name__]
pre_checktree = pre_checks[impl]
post_checktree = post_checks[impl]

def compute_cmvids_for_exids(dq, mip, exids):
    """Compute the cmvids for a MIP and a set of experiment ids.

    This is the interface function for the back end.

    This is an extremely rudimentary hack: ignore the experiments and
    just use dqi to compute *all* the variables for all the MIPs.
    """
    mipcmvids = defaultdict(set)
    for cmv in dq.coll['CMORvar'].items:
        for m in mips_of_cmv(cmv, dq):
            mipcmvids[m].add(cmv.uid)
    return mipcmvids[mip]
