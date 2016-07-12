# Using `djq` from Python
This document describes how to use the Python interface to `djq`. It
does not describe the details of requests and reply objects (they're
JSON-compatible `dict`s), or the stream interface, which is really
only intended to be used by the `djq` program itself.

## An example
This example can be found in `samples/python/djq_interface.py`.  The
functions and exceptions used by this sample are explained in the
following sections.

```
#!/usr/bin/env python
# -*- mode: Python -*-
#

"""A fragment of code as an example
"""

sample_request = [{'mip': "DCPP",
                   'experiment': None}]

from sys import argv
from pprint import pprint
from djq import process_request, BadParse
from djq import valid_dqtag, default_dqroot, default_dqtag
from djq.low import InternalException, ExternalException, Scram

class InvalidTag(ExternalException):
    pass

def query(request, verbosity=1, dqroot=None):
    """Query the request, doing some checks and handling errors.

    Arguments:
    - request is the request
    - verbosity is how verbose to be
    - dqroot is the root to use for this query, if any

    Result is the result.

    If anything goes wrong exit with a suitable message.
    """
    try:
        if not valid_dqtag(dqroot=dqroot):
            raise InvalidTag("{} wrong in {}"
                             .format(default_dqtag(),
                                     dqroot or default_dqroot()))
        return process_request(request,
                               verbosity=verbosity,
                               dqroot=dqroot)
    except InternalException as e:
        # something happened in djq, handle it here?
        # note this will catch Disaster as well
        exit("badness in djq: {}".format(e))
    except ExternalException as e:
        # this was our fault
        exit("badness outside djq: {}".format(e))
    except Scram as e:
        # Something terrible happened
        exit("a very bad thing: {}".format(e))
    except Exception as e:
        # Tentacles
        exit("mutant horror: {}".format(e))

if __name__ == '__main__':
    if len(argv) == 1:
        pprint(query(sample_request))
    elif len(argv) == 2:
        pprint(query(sample_request, dqroot=argv[1]))
    else:
        exit("zero or one argument")
```

## Packages
There are three packages you may need to use.

* `djq.low` is the low-level interface: it defines things like the
  top-level exception classes and provides ways of printing verbose
  output and some general utilities.  Nothing in this package depends
  on the DREQ at all.
* `djq` is the high-level interface: it provides the interface to
  query the DREQ itself, some tools to set and check the location of
  the DREQ and the default tag, and some more specific types of
  exception.
* `djq.variables` contains the implementation of computing variables,
  and supports switching the back end for this, possibly to a
  user-provided one.

In almost all cases you probably want to just import some basic
exceptions from `djq.low` and the actual interface from `djq`.  You
might possibly want to check some of the more specific exceptions
which are exported from `djq` but probably you don't.

## Exceptions
`djq.low` defines several classes of exception.

* `DJQException` is the top of the tree: any exception consciously
  raised by `djq` will be a subclass of this.  Conversely, any
  exception which is *not* a subclass of this is completely unexpected
  and due to something horrible happening.
* `InternalException` is the class of exceptions that it thinks are
  its fault: problems with the program rather than problems with data
  it has been given.
* `ExternalException` is the class of exceptions which it thinks are
  not its fault: it it has been fed incorrect data or something like
  that.
* `Disaster` is an `InternalException` and covers some serious
  internal problem otherwise unknown.  Generally these are 'this can't
  happen' checks or other sanity checks.
* `Scram` is a `DJQException` and is a serious problem where the blame
  is unknown.  Generally the right response to a `Scram` is to stop
  immediately.

Both `Disaster` and `Scram` represent things which should never happen.

`djq` defines several more exceptions built on these.  The only one
that matters is `BadParse` which means that something in the request
is bogus: this is an `ExternalException`.

Finally note that some things which perhaps ought to be exceptions
aren't: for instance if it can't load the DREQ you get back a reply
saying that, rather than an exception.  This is because a request
consists of a list of single-requests, and the DREQ may be loadable
for only some of them (depending on their tags), so the system wants
to be able to return the list of responses, even though some of them
failed.

## Functions in the interface
All of these functions are exported from `djq` except where otherwise stated.

### Querying the DREQ
There is a single function which does this.

```
process_request(request,
                dqroot=None, dqtag=None,
                dbg=None, verbosity=None)
```

This processes the request `request` and returns the reply.  It deals
with loading the DREQ if need be.

* `request` is the request object;
* `dqroot` is the root of the DREQ if given, otherwise a default will
  be used;
* `dqtag` is the DREQ tag if given, otherwise a default will be used;
* `dbg` is the debug level for this request if given, otherwise a
  default will be used;
* `verbosity` is the verbosity level for this request if given,
  otherwise a default will be used.

This function does not raise exceptions itself, but does not catch any
that are raised below it.

### Utilities
There are some functions to get and set the default DREQ root and tag,
and to check it.

* `default_dqroot(dqroot=None)` will return the default root if `root`
  is not given, and set it if it is.
* `valid_dqroot(dqroot=None)` will return true if the given root, or
  the default root if none is given, is probably valid.
* `default_dqtag(dqtag=None)` will return or set the default tag.
* `valid_dqtag(dqtag=None, dqroot=None)` will check the given or
  default tag within the given or default root.

These functions set and get the default values used by
`process_request`.  The checks are heuristic: what they do is to check
that the provided paths (and the paths constructed for the tag) smell
like DREQ checkouts, but they don't actually try and load a DREQ from
them.  All the default values are thread-local.

`ensure_dq(dqtag=None, dqroot=None)` will return an instance of the
DREQ, loading it if needed.  By default `dqtag` and `dqroot` are the
values set by `default_dqtag` and `default_dqroot`.  This is the
function that `process_request` calls to get hold of the DREQ, but it
can be called directly to get hold of an instance to explore.

`invalidate_dq_cache()` will obliterate any cached DREQs that have
been loaded.  This will save some memory, and might be useful if you
think that the wrong version of the DREQ has been loaded for some
reason.  The first subsequent call to `process_request`, or to
`ensure_dq` explicitly, will reload the DREQ.

There are some functions for noise control, exported from `djq.low`.

* `verbosity_level(l=None)` will get or set the default verbosity
  level, with higher levels being more verbose.  The fallback default
  is `0`.
* `debug_level(l=None)` will get or set the default debug-noise level,
  with the fallback being `0`.  Currently it only matters whether is
  is zero or more than zero.

### Switching back ends
(This section is preliminary.)

`djq.variables` contains a single function which allows you to select
a different back end for computing variables:

```
cv_implemementation(impl)
```

will select `impl` as the implementation.  `impl` can be either:

* a function, which is the implementation;
* an object with an attribute named `compute_cmvids_for_exids`, which
  names a function which will do the work.

This allows you, for instance, to pass it a module, in which is
defined a suitable function -- this is the common case in fact.

The implementation function takes three arguments:

1. an instance of the DREQ;
2. the name of the MIP;
3. a set of experiment Ids.

These will have been checked: the experiment IDs will name real
experiments and those experiments will belong to the MIP.

Its return value should be a set of `CMORvar` IDs.

You can also call `cv_implementation` with no arguments to return the
current back end: in the attribute case, this is the thing with the
attribute, not the function (so
`cv_implementation(cv_implementation())` does nothing if an
implementation is set, for instance).