"""Finding variables
"""

# This is where we actually compute the variables.  There is no
# abstraction from the dreq interface at all here, and you need to be
# reasonably familiar with it to make any sense of this.  Pretty much
# everything works in terms of UIDs since they uniquely define objects
# (the UIDs of MIPs are the same as their names, but this isn't true
# for anything else, and things like experiment names don't need to be
# unique).  All the functions that do work get a first argument which
# is the dreq object, called dq, and do a lot of grovelling around in
# dq.inx.* as you'd expect.
#

from djq.low import ExternalException, InternalException, Disaster
from djq.low import mutter, make_checktree, check, run_checks
from jsonify import jsonify_cmvids

__all__ = ('compute_variables', 'NoMIP', 'WrongExperiment', 'NoExperiment')

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

checks = make_checktree()

def compute_variables(dq, mip, experiment):
    """Compute the variables for a MIP and generalised experiment name.

    This is the only public function in this module.
    """
    mutter("* mip {} experiment {}", mip, experiment)
    validate_mip_experiment(dq, mip, experiment)

    if (isinstance(experiment, str) or isinstance(experiment, unicode)
        or experiment is None or isinstance(experiment, bool)):
        cmvids = compute_cmvids(dq, mip, exids_of_mip(dq, mip, experiment))
        mutter("  -> {} variables", len(cmvids))
        return jsonify_cmvids(dq, cmvids)
    else:
        raise Disaster("this can't happen")

def validate_mip_experiment(dq, mip, experiment):
    """Validate a MIP and an experiment if it is stringy.

    Raise suitable exceptions on failure, return value undefined.
    """
    if mip not in dq.inx.uid or dq.inx.uid[mip]._h.label != 'mip':
        raise NoMIP(mip)
    if isinstance(experiment, str) or isinstance(experiment, unicode):
        if experiment not in dq.inx.experiment.label:
            raise NoExperiment(experiment)
        for ei in dq.inx.experiment.label[experiment]:
            if mip == dq.inx.uid[ei].mip:
                if run_checks(checks, args=(dq, mip, experiment)) is False:
                    raise Disaster("failed sanity checks")
                return
        raise WrongExperiment(experiment, mip)

def compute_cmvids(dq, mip, exids):
    """Compute the cmvids for a MIP and a set of experiment ids."""
    cmvids = set(cmvids_of_mip(dq, mip))
    for exid in exids:
        cmvids.update(cmvids_of_exid(dq, exid))
    return cmvids

def exids_of_mip(dq, mip, match):
    """Find all the names of the experiments of mip matched by match.

    match may be a string, a list of strings, a set or frozenset of
    strings, or something truthy or falsy.

    This is more general than the system needs (you never get lists or
    sets of experiments, currently).

    """

    def expt_matches(expt):
        # there must be a more idiomatic way of doing type dispatch
        if isinstance(match, str) or isinstance(match, unicode):
            return expt.label == match
        elif (isinstance(match, list) or isinstance(match, tuple)
              or isinstance(match, set) or isinstance(match, frozenset)):
            return True if expt.label in match else False
        else:
            return True if match else False

    return set(expt.uid for expt in dq.coll['experiment'].items
               if expt.mip == mip and expt_matches(expt))


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

@check(checks, "variables.compute/preset-safety")
def preset_safety_check(dq, mip, experiment):
    # The aim of this is to check that the preset value of all the
    # requestitem objects are less than or equal to zero, which means
    # nothing will be filtered by the pmax setting which is inherited
    # from the scope.py code.
    for ex in (dq.inx.experiment.uid[exid]
               for exid in exids_of_mip(dq, mip, experiment)):
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
