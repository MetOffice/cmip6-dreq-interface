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
    try:
        return compute_variables_1(dq, mip, experiment)
    except (ExternalException, InternalException):
        raise
    except Exception as e:
        raise Scram(e)

def compute_variables_1(dq, mip, experiment):
    if mip not in dq.inx.uid or dq.inx.uid[mip]._h.label != 'mip':
        raise NoMIP(mip)
    if isinstance(experiment, str) or isinstance(experiment, unicode):
        if experiment not in dq.inx.experiment.label:
            raise NoExperiment(experiment)
        if mip not in (dq.inx.uid[u].mip
                       for u in dq.inx.experiment.label[experiment]):
            raise WrongExperiment(experiment, mip)
        return ()
    else:
        raise NotImplemented("can't hack the special cases for experiment yet")
