# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

"""top-level functionality
"""

__all__ = ('ensure_dq', 'invalidate_dq_cache', 'dq_info',
           'process_stream', 'process_request')

from collections import defaultdict
from low import DJQException, InternalException, ExternalException, Scram
from low import mutter, debug, verbosity_level, debug_level
from low import fluids
from emit import emit_reply, emit_catastrophe
from parse import (read_request, validate_toplevel_request,
                   validate_single_request)
from load import (default_dqroot, default_dqtag, valid_dqroot, valid_dqtag,
                  effective_dqpath, dqload)
from variables import (compute_variables, jsonify_variables,
                       cv_implementation, validate_cv_implementation,
                       jsonify_implementation, validate_jsonify_implementation,
                       NoMIP, NoExperiment, WrongExperiment)

def process_stream(input, output, backtrace=False,
                   dqroot=None, dqtag=None, dq=None,
                   dbg=None, verbosity=None,
                   cvimpl=None, jsimpl=None):
    """Process a request stream, emitting results on a reply stream.

    This reads a request from input, and from this generates a reply
    on output.  Basic sanity checking is done in this function, but
    detailed checking of ceach single-request takes place further down
    the stack.

    This function is the custodian of exceptions: it has handlers for
    anything which should happen and emits suitable replies in that
    case.  If backtrace is true it also reraises the exception so a
    stack trace can be created.

    dqroot, dqtag, dbg and verbosity, if given, will bind the dqroot,
    default tag, debug and verbose printing settings for this call,
    only. cvimpl and jsimpl will similarly bind the implementations
    for computing and jsonifying variables for this call only.

    You can explicitly pass a dreq as the dq argument, in which case
    it it used, rather than whatever dqroot and dqtag would cause to
    be loaded.

    There's no useful return value.

    Anything below this should normally handle its own exceptions and
    generate a suitable per-single-request error response: anything
    which reaches this function is treated as a catastrophe (ie the
    whole process has failed).
    """

    with fluids((debug_level, (dbg
                               if dbg is not None
                               else debug_level())),
                (verbosity_level, (verbosity
                                   if verbosity is not None
                                   else verbosity_level())),
                (default_dqroot, (dqroot
                                  if dqroot is not None
                                  else default_dqroot())),
                (default_dqtag, (dqtag
                                 if dqtag is not None
                                 else default_dqtag())),
                (cv_implementation, (validate_cv_implementation(cvimpl)
                                     if cvimpl is not None
                                     else cv_implementation())),
                (jsonify_implementation,
                 (validate_jsonify_implementation(jsimpl)
                  if jsimpl is not None
                  else jsonify_implementation()))):
        try:
            emit_reply(tuple(process_single_request(s, dq=dq)
                             for s in read_request(input)),
                       output)
        except Scram as e:
            raise
        except ExternalException as e:
            emit_catastrophe("{}".format(e), output,
                             note="external error")
            if backtrace:
                raise
        except InternalException as e:
            emit_catastrophe("{}".format(e), output,
                             note="internal error")
            if backtrace:
                raise
        except DJQException as e:
            emit_catastrophe("{}".format(e), output,
                             note="unexpected error")
            if backtrace:
                raise
        except Exception as e:
            emit_catastrophe("{}".format(e), output,
                             note="completely unexpected error")
            if backtrace:
                raise

def process_request(request, dqroot=None, dqtag=None, dq=None,
                    dbg=None, verbosity=None,
                    cvimpl=None, jsimpl=None):
    """Process a request, as a Python object, and return the results.

    Arguments:

    - request is a toplevel request, so a list or tuple of
      single-request objects.  Each single-request is a dict with
      appropriate keys.

    - dqroot, dqtag, dbg and verbosity, if given, will bind the
      dqroot, default tag, debug and verbose printing settings for
      this call.  cvimpl and jsimpl will similarly bind the
      implementations for computing and jsonifying variables.

    - if dq is given then it should be the dreq to use, and in this
      case dqroot and dqtag are ignored.

    This returns a tuple of the results for each single-request in the
    request argument.

    If anything goes seriously wrong this (or in fact things it calls)
    raises a suitable exception.  Note that it *doesn't* return a
    catastrophe response, since that's not likely to be useful in this
    context.
    """

    with fluids((debug_level, (dbg
                               if dbg is not None
                               else debug_level())),
                (verbosity_level, (verbosity
                                   if verbosity is not None
                                   else verbosity_level())),
                (default_dqroot, (dqroot
                                  if dqroot is not None
                                  else default_dqroot())),
                (default_dqtag, (dqtag
                                 if dqtag is not None
                                 else default_dqtag())),
                (cv_implementation, (validate_cv_implementation(cvimpl)
                                     if cvimpl is not None
                                     else cv_implementation())),
                (jsonify_implementation,
                 (validate_jsonify_implementation(jsimpl)
                  if jsimpl is not None
                  else jsonify_implementation()))):
        return tuple(process_single_request(s, dq=dq)
                     for s in validate_toplevel_request(request))

class DREQLoadFailure(DJQException):
    """Failure to load the DREQ: it is indeterminate whose fault this is."""
    def __init__(self, message="failed to load DREQ",
                 dqroot=None, dqtag=None, wrapped=None):
        self.message = message
        self.dqroot = dqroot if dqroot is not None else default_dqroot()
        self.dqtag = dqtag if dqtag is not None else default_dqtag()
        self.wrapped = wrapped
        super(DJQException, self).__init__(
            "{}: path {}".format(self.message,
                                 effective_dqpath(dqroot=self.dqroot,
                                                  dqtag=self.dqtag)))

# Caching loaded DREQs.  The cache has two levels, indexed on root and
# then tag: since roots are thread-local this means there won't be
# false positives: identical tags for different roots will not be
# treated as the same.  This depends on dicts being low-level
# thread-safe: x[y] = z should never yield junk in x.  The FAQ
# (https://docs.python.org/2/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe)
# says that this is true.  Given that, this might end up overwriting
# the same cache entry due to an obvious race, but assuming the DREQ
# files don't change this is just extra work, and won't result in
# anything bad.
#
# There's a potential problem if a huge number of requests come in for
# different tags: I don't think this is likely in practice.  A fix
# would be to use weak references.
#

dqrs = defaultdict(dict)
dqinfo = {}

def invalidate_dq_cache():
    """Invalidate the cache of loaded DREQs."""
    dqrs.clear()
    dqinfo.clear()

def ensure_dq(dqtag=None, dqroot=None, force=False):
    """Ensure the dreq corresponding to a dqtag is loaded, returning it.

    Arguments:
    - dqroot is the root, defaulted from default_dqroot();
    - dqtag is the tag, which defaults from default_dqtag();
    - force, if true, will bypass the cache and force the dreq to be
      loaded, and the loaded copy to be cached.

    Multiple requests for the same dqtag will return the same instance
    of the dreq, unless force is true.

    """
    if dqroot is None:
        dqroot = default_dqroot()
    if dqtag is None:
        dqtag = default_dqtag()
    dqs = dqrs[dqroot]
    if force or (dqtag not in dqs):
        debug("missed {} for {}, loading dreq", dqtag, dqroot)
        if dqtag is not None:
            if valid_dqtag(dqtag):
                try:
                    dq = dqload(dqroot=dqroot, dqtag=dqtag)
                    dqs[dqtag] = dq
                    dqinfo[dq] = (dqroot, dqtag)
                except Exception as e:
                    raise DREQLoadFailure(wrapped=e, dqroot=dqroot, dqtag=dqtag)
            else:
                raise DREQLoadFailure(message="invalid tag",
                                      dqroot=dqroot, dqtag=dqtag)
        else:
            # dqtag is None
            try:
                dq = dqload(dqroot=dqroot)
                dqs[None] = dq
                dqinfo[dq] = (dqroot, None)
            except Exception as e:
                raise DREQLoadFailure(wrapped=e, dqroot=dqroot)
    return dqs[dqtag]

def dq_info(dq):
    """Return a tuple of (root, tag) for dq, or None if unknown.

    The dq will be unknown if it wasn't loaded with ensure_dq, or if
    the cache has been invalidated between when it was loaded and the
    call to this function.
    """
    return dqinfo[dq] if dq in dqinfo else None

def process_single_request(r, dq=None):
    """Process a single request, returning a suitable result for JSONisation.

    This returns either the computed result, or a bad-request response
    if the request was bogus, or an error response if the dreq could
    not be loaded.
    """
    # Outer try/except block catches obviously bad requests and dreq
    # load failures
    #
    try:
        rc = validate_single_request(r)
        if dq is None:
            if 'dreq' in rc:
                mutter("* single-request tag {}", rc['dreq'])
                dq = ensure_dq(rc['dreq'])
            else:
                mutter("* single-request")
                dq = ensure_dq(None)
        reply = dict(rc)
        # inner block handles semantic errors with the request and has
        # a fallback for other errors
        try:
            variables = jsonify_variables(dq,
                                          compute_variables(dq, rc['mip'],
                                                            rc['experiment']))
            reply.update({'reply-status': "ok",
                          'reply-variables': variables})
        except NoMIP as e:
            reply.update({'reply-variables': None,
                          'reply-status': "not-found",
                          'reply-status-detail': "no MIP {}".format(e.mip)})
        except NoExperiment as e:
            reply.update({'reply-variables': None,
                          'reply-status': "not-found",
                          'reply-status-detail':
                          "no experiment {}".format(e.experiment)})
        except WrongExperiment as e:
            reply.update({'reply-variables': None,
                          'reply-status': "not-found",
                          'reply-status-detail':
                          "experiment {} not in MIP {}" .format(e.experiment,
                                                                e.mip)})
        except (ExternalException, InternalException) as e:
            reply.update({'reply-variables': None,
                          'reply-status': "error",
                          'reply-status-detail': "{}".format(e)})
        return reply
    except DREQLoadFailure as e:
        # rc is valid here
        reply = dict(rc)
        reply.update({'reply-variables': None,
                      'reply-status': "error",
                      'reply-status=detail':
                      ("failed to load dreq, root={} tag={}".format(e.dqroot,
                                                                    e.dqtag)
                       + (": {}".format(e.message)
                          if e.message is not None
                          else ""))})
        return reply
    except ExternalException as e:
        # if this happens then rc is not valid
        return {'mip': r['mip'] if 'mip' in r else "?",
                'experiment': r['experiment'] if 'experiment' in r else "?",
                'reply-variables': None,
                'reply-status': 'bad-request',
                'reply-status-detail': "{}".format(e)}
