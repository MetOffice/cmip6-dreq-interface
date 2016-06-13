"""top-level functionality
"""

from emit import emit_reply, emit_catastrophe
from low import InternalException, ExternalException
from parse import read_request, validate_single_request
from load import (default_dqroot, default_dqtag, valid_dqroot, valid_dqtag,
                  dqload)
from variables import compute_variables

__all__ = ('process',)

def process(input, output, debugging=False):
    """Process a request stream, emitting results on a reply stream.

    This reads a request from input, and from this generates a reply
    on output.  Basic sanity checking is done in this function, but
    detailed checking of ceach single-request takes place further down
    the stack.

    This function is the custodian of exceptions: it has handlers for
    anything which should happen and emits suitable replies in that
    case.  If debugging is true it also reraises the exception so a
    stack trace can be created.

    Anything below this should normally handle its own exceptions and
    generate a suitable per-single-request error response: anything
    which reaches this function is treated as a catastrophe (ie the
    whole process has failed).
    """

    try:
        emit_reply(tuple(process_single_request(r)
                         for r in read_request(input)),
                   output)
    except ExternalException as e:
        emit_catastrophe("{}".format(e), output,
                         note="external error")
        if debugging:
            raise
    except InternalException as e:
        emit_catastrophe("{}".format(e), output,
                         note="internal error")
        if debugging:
            raise
    except Exception as e:
        emit_catastrophe("{}".format(e), output,
                         note="unexpected internal error")
        if debugging:
            raise

class DREQLoadFailure(Exception):
    """Failure to load the DREQ: it is indeterminate whose fault this is."""
    def __init__(self, message=None, root=None, tag=None, wrapped=None):
        # I assume you don't need to call the superclass method here
        self.message = message
        self.root = root if root is not None else default_dqroot()
        self.tag = tag if tag is not None else default_dqtag()
        self.wrapped = wrapped

# This caches loaded DREQs.  There's a potential problem if a huge
# number of requests come in for different tagsL: I don't think this
# is likely in practice.]
#
dqs = {}

def ensure_dq(tag):
    """Ensure the dreq corresponding to a tag is loaded, returning it.

    Multiple requests for the same tag will return the same instance
    of the dreq.
    """
    if tag in dqs:
        return dqs[tag]
    else:
        if tag is not None:
            if valid_dqtag(tag):
                try:
                    dqs[tag] =  dqload(tag=tag)
                except Exception as e:
                    raise DREQLoadFailure(tag=tag, wrapped=e)
            else:
                raise DREQLoadFailure(message="invalid tag", tag=tag)
        else:
            try:
                dqs[None] = dqload()
            except Exception as e:
                raise DREQLoadFailure(wrapped=e)

def process_single_request(r):
    """Process a single request, returning a suitable result for JSONisation.

    This returns either the computed result, or a bad-request response
    if the request was bogus, or an error response if the dreq could
    not be loaded.
    """
    try:
        rc = validate_single_request(r)
        dq = ensure_dq(rc['dreq'] if 'dreq' in rc else None)
        reply = dict(rc)
        reply.update({'status': "ok",
                      'variables': compute_variables(dq,
                                                     rc['mip'],
                                                     rc['experiment'])})
        return reply
    except ExternalException as e:
        # if this happens then rc is not valid
        return {'mip': r['mip'] if 'mip' in r else "?",
                'experiment': r['experiment'] if 'experiment' in r else "?",
                'reply-variables': None,
                'reply-status': 'bad-request',
                'reply-status-detail': "{}".format(e)}
    except DREQLoadFailure as e:
        # rc is valid here
        reply = dict(rc)
        reply.update({'reply-variables': None,
                      'reply-status': "error",
                      'reply-status=detail':
                      ("failed to load dreq, root={} tag={}".format(e.root,
                                                                    e.tag)
                       + (": {}".format(e.message)
                          if e.message is not None
                          else ""))})
        return reply
