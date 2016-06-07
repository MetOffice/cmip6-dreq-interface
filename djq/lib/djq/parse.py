from json import load
from djq.low import ExternalException

# A request is an array of single-requests
# a single-request is a dictionary with keys:
#  - mip: string naming a MIP
#  - experiment: string naming an experiment
#  - dreq (optional): string specifying a DREQ version
#  - (other keys which must begin with "request-")
#
# This reads the JSON and does syntactic, but no semantic, validation.
#

__all__ = ('BadParse', 'BadJSON', 'BadSyntax',
           'parse_request')

class BadParse(ExternalException):
    pass

class BadJSON(BadParse):
    def __init__(self, string, wrapped=None):
        super(BadJSON, self).__init__(string)
        self.wrapped = wrapped

class BadSyntax(BadParse):
    pass

def parse_request(fp):
    """Parse a JSON request, returning the parsed object.

    fp is the file-like object to read the request from.

    This does syntactic, but no semantic validation on the request.
    """
    def parse_request(r):
        # Parse requests
        if not (isinstance(r, list) or isinstance(r, tuple)):
            raise BadSyntax("JSON request should be a list of single-requests")
        return tuple(parse_single_request(s) for s in r)

    def parse_single_request(s):
        # Parse a single request:
        #
        # it should be a dict;
        if not isinstance(s, dict):
            raise BadSyntax("single JSON request should be a dict")
        # all the keys should be stringy (I think this is always true
        # for JSON);
        if not all(lambda k: isinstance(k, str) or isinstance(k, unicode)
                   for k in s.keys()):
            raise BadSyntax("non-stringy keys in single JSON request?")
        # now canonicalize keys to lowercase;
        cs = {k.lower(): v for (k, v) in s.iteritems()}
        # it needs to have mip and experiment keys;
        if 'mip' not in cs or 'experiment' not in cs:
            raise BadSyntax("both 'mip' and 'experiment' must be specified")
        # and validate all te keys
        return {key: val
                for (key, val) in (validate_sr_entry(k, v)
                                   for (k, v) in cs.iteritems())}

    def validate_sr_entry(k, v):
        # Validate a single entry (keys are known to be stringy by
        # now):
        #
        # known keys need to have stringy values;
        if k == 'mip' or k == 'experiment' or k == 'dreq':
            if isinstance(v, str) or isinstance(v, unicode):
                return (k, v)
            else:
                raise BadSyntax("not a string in {}: {}".format(k, v))
        # and unknown keys need to start with the right prefix.
        elif k.startswith("request-"):
            return (k, v)
        else:
            raise BadSyntax("bad key {}".format(k))

    try:
        request = load(fp)
    except Exception as e:
        raise BadJSON("bad JSON request", e)
    return parse_request(request)
