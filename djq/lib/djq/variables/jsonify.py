"""JSONifying variables
"""

__all__ = ('jsonify_variables', 'jsonify_implementation',
           'validate_jsonify_implementation', 'BadJSONifyImplementation')

from djq.low import fluid, boundp, globalize
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

# The fluid for the implementation, created unbound
jsonify_implementation = fluid()

def effective_jsonify_implementation():
    # return a tuple of (function, impl), where function is the
    # callable thing, and impl is the thing to key checks from. Scram
    # if there is no sane implementation
    if boundp(jsonify_implementation):
        impl = validate_jsonify_implementation(jsonify_implementation())
        return ((impl if callable(impl) else impl.jsonify_cmvids), impl)
    else:
        raise Scram("no jsonify implementation")

def validate_jsonify_implementation(impl, bootstrap=False):
    """Validate a jsonify implementation, returning it.

    Raise an exception if it is invalid.
    """
    # Note that the very first call to this with a non-None argument,
    # and with bootstrap given actually sets up the fluid.  This is
    # just a hack to bootstrap things (it can't be set here, as this
    # module should not know what the default is.
    #
    def validate(it):
        if (callable(it) or (hasattr(it, 'jsonify_cmvids')
                             and callable(it.jsonify_cmvids))):
            return it
        else:
            raise BadJSONifyImplementation("{} is no good".format(it))

    if bootstrap:
        globalize(jsonify_implementation, validate(impl), threaded=True)
        return impl
    else:
        return validate(impl)

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
