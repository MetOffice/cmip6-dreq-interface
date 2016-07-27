"""JSONifying variables
"""

__all__ = ('jsonify_variables', 'jsonify_implementation',
           'BadJSONifyImplementation')

from djq.low import State
from djq.low import whisper, ExternalException, Scram, Disaster
from djq.low import make_checktree, checker
from djq.low import validate_object, every_element, one_of, all_of, stringlike

class BadJSONifyImplementation(ExternalException):
    pass

# checkers (which are not, yet, per backend) are run on the way out,
# and are called with the dq, cmvids, and the JSON structure resulting
#
checks = make_checktree()

@checker(checks, "variables.jsonify/validate-results")
def validate_results(dq, cmvids, results):
    # This checker looks at results and checks they smell basically
    # good: it could actually just be in jsonify itself, since any
    # implementation should pass this.
    number = one_of((int, float)) # a JSON number
    return validate_object(
        results,
        every_element({'uid': all_of((stringlike,
                                      lambda u: u in cmvids)),
                       'label': stringlike,
                       'miptable': stringlike,
                       'priority': number,
                       'mips': every_element(
                           {'mip': stringlike,
                            'priority': number,
                            'objectives': every_element(stringlike)})}))

state = State(implementation=None)
fallback_implementation = None

def effective_jsonify_implementation():
    # return a tuple of (function, impl), where function is the
    # callable thing, and impl is the thing to key checks from. Scram
    # if there is no sane implementation
    impl = jsonify_implementation()
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
    # Note that the very first call to this with a non-None argument
    # will also set the fallback. This is done in the package init.
    global fallback_implementation
    if impl is None:
        # read
        impl = (state.implementation
                if state.implementation is not None
                else fallback_implementation)
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
            if fallback_implementation is None:
                fallback_implementation = impl
        else:
            raise BadJSONifyImplementation("{} is no good".format(impl))

def jsonify_variables(dq, cmvids):
    """Return a suitable dict for a bunch of cmv uids"""
    (jsonify_cmvids, impl) = effective_jsonify_implementation()
    results = sorted(jsonify_cmvids(dq, cmvids),
                     key=lambda j: j['label'])
    if checks(args=(dq, cmvids, results)) is False:
        raise Disaster("failed JSONify checks")
    for r in results:
        whisper("     {}", r['label'])
    return results
