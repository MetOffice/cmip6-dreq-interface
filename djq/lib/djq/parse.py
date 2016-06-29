"""Parsing JSON requests
"""

__published__ = ('BadParse', 'BadJSON', 'BadSyntax')

__all__ = __published__ + ('read_request', 'validate_toplevel_request',
                            'validate_single_request')

from json import load
from low import ExternalException
from low import stringlike, arraylike

# A request is an array of single-requests
# a single-request is a dictionary with keys:
#  - mip: string naming a MIP
#  - experiment: string naming an experiment
#  - dreq (optional): string specifying a DREQ version
#  - (other keys which must begin with "request-")
#
# This reads the JSON and does syntactic, but no semantic, validation.
#

class BadParse(ExternalException):
    pass

class BadJSON(BadParse):
    def __init__(self, message, wrapped=None):
        super(BadJSON, self).__init__(message)
        self.wrapped = wrapped

class BadSyntax(BadParse):
    pass

def read_request(fp):
    """Read a JSON request from a stream and do some validation.

    Return the request read, or raise an exception.

    fp is the file-like object to read the request from.

    See validate_toplevel_request for the validation this does.
    """
    try:
        request = load(fp)
    except Exception as e:
        raise BadJSON("bad JSON request", e)
    return validate_toplevel_request(request)

def validate_toplevel_request(r):
    """Check an object is valid as a request at toplevel.

    Return the request if it is valid, otherwise raise a BadSyntax
    exception.

    Note that this only checks the toplevel of the request: use
    validate_single_request to check each single-request.  This is
    done so that callers can process a list of single-requests, only
    some of which are valid, without just giving up altogether.
    """
    if not (arraylike(r) and all(isinstance(s, dict) for s in r)):
        raise BadSyntax("JSON request should be a list of objects")
    return r

def validate_single_request(s):
    """Validate a single-request.

    Either return a canonicalised (lower-case keys) version, or raise
    an exception if it is invalid.
    """

    def validate_sr_entry(k, v):
        # Validate a single entry (keys are known to be stringy by
        # now):
        #
        # Check known keys
        if k == 'mip' or k == 'dreq':
            # 'mip' and 'dreq' must be stringy
            if stringlike(v):
                return (k, v)
            else:
                raise BadSyntax("not a string in {}: {}".format(k, v))
        elif k == 'experiment':
            # 'experiment' must be stringy, None, or a boolean
            if stringlike(v) or v is None or isinstance(v, bool):
                return (k, v)
            else:
                raise BadSyntax(
                    "experiment isn't string, boolean or null: {}".format(k, v))
        # Check unknown keys start with the right prefix.
        elif k.startswith("request-"):
            return (k, v)
        else:
            raise BadSyntax("bad key {}".format(k))

    if not isinstance(s, dict):
        raise BadSyntax("single JSON request should be a dict")
    # all the keys should be stringy (I think this is always true
    # for JSON);
    if not all(stringlike for k in s.keys()):
        raise BadSyntax("non-stringy keys in single JSON request?")
    # now canonicalize keys to lowercase;
    cs = {k.lower(): v for (k, v) in s.iteritems()}
    # it needs to have mip and experiment keys;
    if 'mip' not in cs or 'experiment' not in cs:
        raise BadSyntax("both 'mip' and 'experiment' must be specified")
    # and validate all the keys
    return {key: val
            for (key, val) in (validate_sr_entry(k, v)
                               for (k, v) in cs.iteritems())}
