"""An attempt at computing variables based on examples in the dreq.
"""

# This is a back end for djq.variables.compute, and is where we
# actually compute the variables.  There is no abstraction from the
# dreq interface at all here, and you need to be reasonably familiar
# with it to make any sense of this.  Pretty much everything works in
# terms of UIDs since they uniquely define objects (the UIDs of MIPs
# are the same as their names, but this isn't true for anything else,
# and things like experiment names don't need to be unique).  All the
# functions that do work get a first argument which is the dreq
# object, called dq, and do a lot of grovelling around in dq.inx.* as
# you'd expect.
#
# This implementation, djq.variables.cv_dreq_example, is based on
# examples in the dreq documentation.  In particular it is based on
# the material which can be found at
# http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/trunk/dreqPy/docs/dreqExamples.pdf,
# or equivelently in CMIP6dreq/trunk/dreqPy/docs/dreqExamples.pdf in a
# checkout, or equivalent places for branches & tags.  Some of the
# code is also based on
# http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/trunk/dreqPy/scope.py.
#

__all__ = ('compute_cmvids_for_exids',)

from sys import modules
from djq.low import checker
from djq.low import mutter, mumble
from compute import pre_checks, post_checks

impl = modules[__name__]
pre_checktree = pre_checks[impl]
post_checktree = post_checks[impl]

def compute_cmvids_for_exids(dq, mip, exids):
    """Compute the cmvids for a MIP and a set of experiment ids.

    This is the interface function for the back end.
    """
    cmvids = set(cmvids_of_mip(dq, mip))
    for exid in exids:
        cmvids.update(cmvids_of_exid(dq, exid))
    # There can be bogons in the result (things which are not
    # CMORvars), so grovel over the answer and remove them, reporting
    # if any were removed fairly vigorously.
    #
    bads = set()
    for v in cmvids:
        l = dq.inx.uid[v]._h.label
        if l != 'CMORvar':
            bads.add(v)
            mumble("[pruned {}: {} not CMORvar]", v, l)
    if len(bads) > 0:
        mutter("[pruned {} bogons]", len(bads))
    return cmvids - bads

# Finding the cmvids for MIPS
# This is not insanely hard
#

def cmvids_of_mip(dq, mipname):
    """Ids of CMORvars which link to mipname.

    This is taken from the examples in the dreq
    """
    # request groups that link to the MIP
    rgs = set(dq.inx.uid[l.refid]
              for l in (rl for rl in dq.coll['requestLink'].items
                        if rl.mip == mipname))
    # and the variable names of those groups
    return set(dq.inx.uid[rv].vid
               for rvs in (dq.inx.iref_by_sect[rg.uid].a['requestVar']
                           for rg in rgs)
               for rv in rvs)


# Finding the CMVids for exids
# This is much more hairy
#

def rqlids_of_exid(dq, exid, pmax=2):
    """Find a the request link UIDs for an experiment UID.

    This is approximately from rqlByExpt in scope.py.

    I am not sure what pmax is for although nothing uses it.  There is
    a check that nothing is excluded by it below.
    """
    assert pmax > 0
    ex = dq.inx.experiment.uid[exid]   # the experiment object
    assert ex._h.label == 'experiment' # it must be an experiment
    exset = set((exid, ex.egid, ex.mip)) # set of ids of things to look for
    riids = riids_of_mip(dq, ex.mip) # set of request item UIDs for the mip

    # xris is a set of request items which we like
    xris = set(i for i in (dq.inx.uid[ri] for ri in riids)
               if i.preset <= pmax and i.esid in exset)
    # xrqlids is the ids of rqls we like (remove the remarks without noise)
    xrqlids = set(xri.rlid for xri in xris
                  if dq.inx.uid[xri.rlid]._h.label != 'remarks')
    # And this is the answer we are looking for
    return xrqlids

@checker(pre_checktree, "variables.compute/preset-safety")
def preset_safety_check(dq, mip, exids):
    # The aim of this is to check that the preset value of all the
    # requestitem objects are less than or equal to zero, which means
    # nothing will be filtered by the pmax setting which is inherited
    # from the scope.py code.
    for exid in exids:
        ex = dq.inx.experiment.uid[exid]
        for ri in (dq.inx.uid[riid]
                   for riid in riids_of_mip(dq, ex.mip)):
            if ri.preset > 0:
                return False
    return True

def riids_of_mip(dq, mip):
    """Request item ids that link to the mip."""
    return set(ri
               for rlid in (rl.uid
                            for rl in dq.coll['requestLink'].items
                            if rl.mip == mip)
               for ri in dq.inx.iref_by_sect[rlid].a['requestItem'])

def rgids_of_rqlids(dq, rqlids):
    """Return the request group Ids for a bunch of request link ids.

    This is close to part of mipcmvids above and should be made the
    same thing.
    """
    return set(dq.inx.uid[l.refid]
               for l in (dq.inx.uid[rqlid]
                         for rqlid in rqlids))

def cmvids_of_rgids(dq, rgids):
    """Return the CMORvar ids (note not labels) for a bunch of rgids."""
    return set(dq.inx.uid[rv].vid
               for rvs in (dq.inx.iref_by_sect[vg.uid].a['requestVar']
                           for vg in rgids)
               for rv in rvs)

def cmvids_of_exid(dq, exid):
    """Return the CMORvar uids for an exid."""
    return cmvids_of_rgids(dq, rgids_of_rqlids(dq, rqlids_of_exid(dq, exid)))
