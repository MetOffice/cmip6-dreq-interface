"""Finding variables
"""

# This is where we actually compute the variables.  There is no
# abstraction from the dreq interface at all here.

from low import ExternalException, InternalException, Scram
from low import mutter

__all__ = ('compute_variables', 'NoMIP', 'NoExperiment')

class NoMIP(ExternalException):
    def __init__(self, mip):
        self.mip = mip

class NoExperiment(ExternalException):
    def __init__(self, experiment):
        self.experiment = experiment

class WrongExperiment(ExternalException):
    def __init__(self, experiment, mip):
        self.experiment = experiment
        self.mip = mip

class NotImplemented(InternalException):
    pass

def compute_variables(dq, mip, experiment):
    """Compute the for a MIP and experiment name.

    This first checks the experiment is valid and belongs to the MIP,
    finds the experiment UID, then computes a set of CMV UIDs
    corresponding to the MIP and the experiment, turns them into
    something suitable for JSON, and returns them.
    """

    if not (isinstance(experiment, str)
            or isinstance(experiment, unicode)):
        raise  NotImplemented("can't do experiment special cases yet")
    if mip not in dq.inx.uid or dq.inx.uid[mip]._h.label != 'mip':
        raise NoMIP(mip)
    if experiment not in dq.inx.experiment.label:
        raise NoExperiment(experiment)
    exid = None
    for ei in dq.inx.experiment.label[experiment]:
        if mip == dq.inx.uid[ei].mip:
            exid = ei
    if exid is None:
        raise WrongExperiment(experiment, mip)
    return jsonify_cmvids(dq, (cmvids_of_mip(dq, mip)
                               | cmvids_of_exid(dq, exid)))

# Finding the cmvids for MIPS
# This is not insanely hard
#

def cmvids_of_mip(dq, mipname):
    """Ids of CMORvars which link to mipname.

    This is taken from the examples in the dreq
    """
    # request groups that link to the MIP
    rgs = set(dq.inx.uid[l.refid]
              for l in (dl for dl in dq.coll['requestLink'].items
                        if dl.mip == mipname))
    # and the variable names of those groups
    return set(dq.inx.uid[rv].vid
               for rvs in (dq.inx.iref_by_sect[vg.uid].a['requestVar']
                           for vg in rgs)
               for rv in rvs)

# Finding the CMVids for exids
# This is much more hairy
#

def rqlids_of_exid(dq, exid, pmax=2):
    """Find a the request link UIDs for an experiment UID.

    This is approximately from rqlByExpt in scope.py.

    I am not sure what pmax is for (but it is not used in calls).
    """
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

# Converting things to something JSONable
# This is extremely incomplete
#

def jsonify_cmvids(dq, cmvids):
    """Return a suitable dict for a bunch of cmv uids.:"""
    return tuple(jsonify_cmvid(dq, cmvid)
                 for cmvid in cmvids)

def jsonify_cmvid(dq, cmvid):
    cmv = dq.inx.uid[cmvid]
    return {'uid': cmvid,
            'label': cmv.label}
