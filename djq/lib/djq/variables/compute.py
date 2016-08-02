"""Finding variables, top level
"""

# This is the top level part of finding variables.  It deals with
# sanity checking everything, finding the experiment IDs (exids)
# corresponding to an experiment, and then dispatching to a back end.
# The back end can be selected, using cv_implementation.  A back end
# is either itself function, or a module with a function named
# compute_cmvids_for_exids (in which case the actual back end
# implementation is set to that function).
#
# The back end function is called with:
#  - the dreq
#  - the MIP name
#  - a set of experiment ids belonging to that MIP
# and should return an iterable of cmvids
#
# There is no abstraction from the dreq interface at all here
#

__all__ = ('cv_implementation', 'validate_cv_implementation',
           'compute_variables',
           'NoMIP', 'WrongExperiment', 'NoExperiment',
           'BadCVImplementation')

from collections import defaultdict
from djq.low import fluid, boundp, globalize
from djq.low import ExternalException, InternalException, Disaster, Scram
from djq.low import mutter, mumble, make_checktree
from djq.low import stringlike, arraylike, setlike

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

class BadCVImplementation(ExternalException):
    pass

# Pre and post checks: back ends can know about these.  These are
# indexed by the back end, and only the checks for the current back
# end run (see below).
#
# pre checkers are responsible for checking that things going in are
# sane, and get called with dq, mip, exids.
#
# post checkers are responsible for checking that things coming out
# are sane, and get called with dq, mip cmvids
#
pre_checks = defaultdict(make_checktree)
post_checks = defaultdict(make_checktree)

# The fluid for the implementation: created unbound
cv_implementation = fluid()

def effective_cv_implementation():
    # return a tuple of (function, impl), where function is the
    # callable thing, and impl is the thing to key checks from. Scram
    # if there is no sane implementation
    if boundp(cv_implementation):
        impl = validate_cv_implementation(cv_implementation())
        return ((impl if callable(impl) else impl.compute_cmvids_for_exids),
                impl)
    else:
        raise Scram("no cv implementation")

def validate_cv_implementation(impl, bootstrap=False):
    """Validate a back end for computing variables, returning it.

    Raise an exception if it is invalid.
    """
    # Note that the very first call to this with a non-None argument,
    # and with bootstrap given actually sets up the fluid.  This is
    # just a hack to bootstrap things (it can't be set here, as this
    # module should not know what the default is.
    #
    def validate(it):
        if (callable(it) or (hasattr(it, 'compute_cmvids_for_exids')
                             and callable(it.compute_cmvids_for_exids))):
            return it
        else:
            raise BadCVImplementation("{} is no good".format(impl))

    if bootstrap:
        globalize(cv_implementation, validate(impl), threaded=True)
        return impl
    else:
        return validate(impl)

def compute_variables(dq, mip, experiment):
    """Compute the variables for a MIP and generalised experiment name.

    This is the only public function in this module.

    returns a set of cmvids suitable for JSONification.

    See cv_implementation for selecting a back end.
    """
    (cv, impl) = effective_cv_implementation()
    mutter("  mip {} experiment {} implementation {}",
           mip, experiment, (impl.__name__
                             if hasattr(impl, '__name__')
                             else impl))
    validate_mip_experiment(dq, mip, experiment, impl)

    if (stringlike(experiment) or experiment is None
        or isinstance(experiment, bool)):
        exids = exids_of_mip(dq, mip, experiment)
        for label in sorted(dq.inx.uid[exid].label for exid in exids):
            mumble("      {}", label)
        cmvids = cv(dq, mip, exids)
        mutter("  -> {} variables", len(cmvids))
        for v in cmvids:
            if v not in dq.inx.uid:
                raise Disaster("uid {} unfound".format(v))
            elif dq.inx.uid[v]._h.label != 'CMORvar':
                raise Disaster("{} ({}) is {} not CMORvar".format(
                        dq.inx.uid[v].label, v, dq.inx.uid[v]._h.label))
        if (post_checks[impl](args=(dq, mip, cmvids))
            is False):
            raise Disaster("failed post checks")
        return cmvids
    else:
        raise Disaster("this can't happen")

def validate_mip_experiment(dq, mip, experiment, impl):
    """Validate a MIP and an experiment if it is stringy.

    Raise suitable exceptions on failure, return value undefined.
    """
    if mip not in dq.inx.uid or dq.inx.uid[mip]._h.label != 'mip':
        raise NoMIP(mip)
    if stringlike(experiment):
        # a literal experiment
        if experiment not in dq.inx.experiment.label:
            # No experiment at all with that name
            raise NoExperiment(experiment)
        exids = exids_of_mip(dq, mip, experiment)
        if len(exids) == 0:
            # Nothing matched
            raise WrongExperiment(experiment, mip)
    else:
        # True, False or None
        exids = exids_of_mip(dq, mip, experiment)
    if pre_checks[impl](args=(dq, mip, exids)) is False:
        raise Disaster("failed pre checks")

def exids_of_mip(dq, mip, match):
    """Find all the names of the experiments of mip matched by match.

    match may be a string, a list of strings, a set or frozenset of
    strings, or something truthy or falsy.

    This is more general than the system needs (you never get lists or
    sets of experiments, currently).

    """
    def expt_matches(expt):
        # there must be a more idiomatic way of doing type dispatch
        if stringlike(match):
            return expt.label == match
        elif arraylike(match) or setlike(match):
            return True if expt.label in match else False
        else:
            return True if match else False

    return set(expt.uid for expt in dq.coll['experiment'].items
               if expt.mip == mip and expt_matches(expt))
