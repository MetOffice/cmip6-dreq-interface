"""JSONifying variables
"""

__all__ = ('jsonify_variables', 'jsonify_implementation')

from threading import local
from djq.low import whisper, ExternalException, Scram, Disaster

class BadJSONifyImplementation(ExternalException):
    pass

state = local()
state.implementation = None

def effective_jsonify_implementation():
    # return a tuple of (function, impl), where function is the
    # callable thing, and impl is the thing to key checks from. Scram
    # if there is no sane implementation
    impl = state.implementation
    if callable(impl):
        return (impl, impl)
    elif (hasattr(impl, 'jsonify_cmvids')
          and callable(impl.jsonify_cmvids)):
        return (impl.jsonify_cmvids, impl)
    else:
        raise Scram("no implementation")

def jsonify_implementation(impl=None):
    """Get or set a back end for computing variables.
    """
    if impl is None:
        # read
        impl = state.implementation
        if (callable(impl) or (hasattr(impl, 'jsonify_cmvids')
                               and callable(impl.jsonify_cmvids))):
            return impl
        elif impl is None:
            return None
        else:
            raise Disaster("mutant cv implementation")
    else:
        # set
        if (callable(impl) or (hasattr(impl, 'jsonify_cmvids')
                               and callable(impl.jsonify_cmvids))):
            state.implementation = impl
        else:
            raise BadJSONifyImplementation("{} is no good".format(impl))


def jsonify_variables(dq, cmvids):
    """Return a suitable dict for a bunch of cmv uids"""
    (jsonify_cmvids, impl) = effective_jsonify_implementation()
    results = sorted(jsonify_cmvids(dq, cmvids),
                     key=lambda j: j['label'])
    for r in results:
        whisper("     {}", r['label'])
    return results
