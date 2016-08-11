"""Computing variables by inverting the map from variables to mips
"""

__all__ = ('compute_cmvids_for_exids',)

from sys import modules
from collections import defaultdict
from djq.low import checker, mumble, mutter
from compute import pre_checks, post_checks
from varmip import mips_of_cmv, validp

impl = modules[__name__]
pre_checktree = pre_checks[impl]
post_checktree = post_checks[impl]

def compute_cmvids_for_exids(dq, mip, exids):
    """Compute the cmvids for a MIP and a set of experiment ids.

    This is the interface function for the back end.

    This is a fairly rudimentary hack.
    """
    mipcmvids = defaultdict(set)
    bads = set()
    for cmv in dq.coll['CMORvar'].items:
        if validp(dq.inx.uid[cmv.vid]):
            mips = mips_of_cmv(dq, cmv, exids)
            if len(mips) > 0:
                for m in mips:
                    mipcmvids[m].add(cmv.uid)
            else:
                mumble("[{} ({}) belongs to no MIPs?]", cmv.label, cmv.uid)
        else:
            bads.add(cmv)
            mumble("[pruned {} ({}): var not valid]", cmv.label, cmv.uid)
    if len(bads) > 0:
        mutter("[pruned {} invalid vars]", len(bads))
    return mipcmvids[mip]
