<!-- (C) British Crown Copyright 2016, Met Office.
     See LICENSE.md in the top directory for license details. -->

# Using `djq` from Python
This document describes how to use the Python interface to `djq`. It
does not describe the details of request and reply objects: these
correspond directly to the JSON objects in the [JSON
interface](JSON-spec.md) however.  There is also a stream interface,
whch is used by the `djq` command-line interface, which is not
described here at all.

This is also not a complete API specification: I haven't described
everything in the interface, although I don't think I've left out
anything important.


## Requirements to use the interface
To do anything at all the interface needs access to a DREQ checkout
which it can load, and to a working version of the `dreqPy` interface.  [This](http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/) is what you should check out, *not* the `.../tags/latest/` link that various web pages point you to.

If `dreqPy` is not available then any attempt to `import djq` will
fail altogether.  If `dreqPy` *is* available but the DREQ can't be
found then any queries of the DREQ will fail.  As described in [the
installation instructions](Installation.md) you can specify where the
DREQ checkout is using the `DJQ_DQROOT` environment variable, which
should point at the root of a checkout of the DREQ toplevel (not a
branch or tag).

If you want to, you can check whether the DREQ can be found and also
tell it where to look.

```python
>>> from djq import default_dqroot, valid_dqroot
>>> default_dqroot()
'/tmp/silly/dqroot'
>>> valid_dqroot()
False
>>> valid_dqroot("/home/h04/tbradsha/work/cmip6-data-request/CMIP6dreq")
True
>>> default_dqroot("/home/h04/tbradsha/work/cmip6-data-request/CMIP6dreq")
'/home/h04/tbradsha/work/cmip6-data-request/CMIP6dreq'
>>> valid_dqroot()
True
```

You can do equivalent things for the tag, although if you get thwe
root right then the default tag is usually right.

These checks are not definitive: the only way to know if there's
really a valid DREQ there is to try to load it:

```python
>>> from djq import ensure_dq
>>> ensure_dq()
<dreqPy.dreq.loadDreq object at 0x7f1a4b571090>
```

If `ensure_dq()` raises an exception then things are definitely not
right, even if `valid_dqroot()` thinks they are.


## An example
This example can be found in `samples/python/djq_interface.py`.  The
functions and exceptions used are explained in the following
sections.

```python
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

Running this example should produce a great deal of output on standard
output, as well as some noise on standard error.  The standard output
begin something like this:

```python
({'experiment': None,
  'mip': 'DCPP',
  'reply-status': 'ok',
  'reply-variables': [{'label': 'alb',
                       'mips': ({'mip': 'DCPP',
                                 'objectives': ('Origin, mechanisms and predictability of long timescale variations including the current hiatus and similar variations of both signs',
                                                'Decadal predictability and forecast skill of forced and internally generated climate components',
                                                'Effect of volcanoes on decadal variability,  predictability and skill',
                                                'Quasi-operational decadal predictions and their utility for the GFCS and for applications in general'),
                                 'priority': 1},),
                       'miptable': 'emMon',
                       'priority': 1,
                       'uid': '8b9212ec-4a5b-11e6-9cd2-ac72891c3257'},
                       ...]})
```

## Packages
There are three packages you may need to use.

* `djq.low` is the low-level interface: it defines things like the
  top-level exception classes and provides ways of printing verbose
  output and some general utilities.  Nothing in this package depends
  on the DREQ at all.   A great deal of `djq.low` exists so that
  higher-level things can use it and isn't relevant to the interface,
  so there are lots of things in it I'm not going to describe.
* `djq` is the high-level interface: it provides the interface to
  query the DREQ itself, some tools to set and check the location of
  the DREQ and the default tag, and some more specific types of
  exception.
* `djq.variables` contains the implementation of computing variables
  and JSONifying the results, and supports switching the back ends for
  these processes, possibly to user-provided ones.

In almost all cases you probably want to just import some basic
exceptions from `djq.low` and the actual interface from `djq`.  You
might possibly want to check some of the more specific exceptions
which are exported from `djq` but probably you don't.  If you want to
write your own back end for computing variables or compare existing
back ends then you may need to use some things from `djq.variables`,
but you don't need to do that for simple use.

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
is bogus: this is an `ExternalException`.  There are other exceptions
related to the stream interface.

Finally note that some things which perhaps ought to be exceptions
aren't: for instance the DREQ can't be loaded when processing a
request you get back a reply saying that, rather than an exception.
This is because a request consists of a list of single-requests, and
the DREQ may be loadable for only some of them (depending on their
tags), so the system wants to be able to return the list of responses,
even though some of them failed.  If you try to explicitly load the
DREQ you *do* get an exception if it fails however.

## Functions in the interface
All of these functions are exported from `djq` except where otherwise
stated.

### Querying the DREQ
This is the aim of the whole thing, and there is a single function
which does this.

```python
process_request(request,
                dqroot=None, dqtag=None, dq=None,
                dbg=None, verbosity=None,
                cvimpl=None, jsimpl=None)
```

This processes the request `request` and returns the reply.  It deals
with loading the DREQ if need be.

* `request` is the request object;
* `dqroot` is the root of the DREQ if given, otherwise a default will
  be used;
* `dqtag` is the DREQ tag if given, otherwise a default will be used;
* `dq`, if given, is an instance of the loaded DREQ -- if it is
  provided then `dqroot` and `dqtag` don't do anything;
* `dbg` is the debug level for this request if given, otherwise a
  default will be used;
* `verbosity` is the verbosity level for this request if given,
  otherwise a default will be used;
* `cvimpl` and `jsimpl`, if given, should be implemementations of the
  back ends for computing and JSONifying variables respectively, for
  this call.

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

`dq_info(dq)` will return a tuple of `(root, tag)` for `dq`, or `None`
if it is unknown.  It will be unknown if it was not loaded with
`ensure_dq`, or if the cache has been invalidated between the time it
was loaded the time this function was called (or, in fact, if `dq` is
just some random object).

There are some functions for noise control, exported from `djq.low`.

* `verbosity_level(l=None)` will get or set the default verbosity
  level, with higher levels being more verbose.  The fallback default
  is `0`.
* `debug_level(l=None)` will get or set the default debug-noise level,
  with the fallback being `0`.  Currently it only matters whether is
  is zero or more than zero.

Both of these settings are thread-local.

### A note on tags and the trunk
Normally the system loads the DREQ from a tagged release.  However it
can also be useful to load from the trunk, to get the absolute latest
version.  So when specifying tags there are three options:

* if the tag is a string, then it simply specifies the tag to load
  from;
* if the tag is `None` then the ambient default tag is used -- the
  value of which can be retrieved or set with `default_dqtag`;
* if the tag is `False` then the DREQ is loaded from the trunk.

Note that you can specify the trunk as the ambient default tag with a
call to `default_dqtag(False)` for instance.

### Controlling how variables are computed
There are several possible approaches to computing the variables
corresponing to a MIP and experiment and I could not work out which
one is right. So `djq.variables` contains tools which allow you to
select different implementations for computing variables.
[Implementations](Implementations.md) describes which ones exist.

Everything below is in `djq.variables`.

`cv_implementation` will either select an implementation for computing
variables or return the current one: `cv_implementation(impl)` selects
`impl` as the implementation, while `cv_implementation()` returns the
current one.  An implementation is either:

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

`validate_cv_implementation(impl)` will check that `impl` looks like a
good implementation.  Note that this check is really only that it is
either callable or has an attribute named `compute_cmvids_for_exids`
which is callable: it doesn't do any more deep checking than that.  It
is just a sanity check.  The system itself calls it before an
implementation is used, but `cv_implementation(impl)` does not.

If the implementation is not good then `BadCVImplementation` is raised
(this is an `ExternalException`).

Once set, an implementation is thread-local.

### Controlling JSONifiers
There is a similar implementation switch for JSONifiers.  Again the
functions below are in `djq.variables`.  There is currently only one
implementation, although nothing stops you from writing your own.

`jsonify_implementation` either sets or returns the current
implementation: `jsonify_implementation(impl)` sets it,
`jsonify_implementation()` returns it.  An implementation can be
either:

* a function, which is the implementation;
* an object with an attribute named `jsonify_cmvids`, which names a
  function which will do the work.

The implementation function takes two arguments:

1. the DREQ;
2. a set of `CMORvar` IDs.

It should return suitable structure to be converted into JSON.

The elements of the structures that it returns should be `dict`s (or a
compatible type) with entries for `'label'`: these are used for
sorting them.  Things will blow up if the `x['label']` doesn't work
for each element.  They also need to be something that the standard
Python JSON interface knows how to turn into JSON.

`validate_jsonify_implementation(impl)` does basic sanity checking on
an implementation.  Again this is called by the system before the
implementation is used.

If the implementation is no good then `BadJSONIFYImplementation` is
raised, and again this is an `ExternalException`.

The implementation, once set, is thread-local.

### Selecting default implementations
`djq.variables` selects default implementations when it is imported
(which happens when `djq` is imported).  It does this by importing
modules -- `cv_default` for computing variables and `jsonify_default`
for JSONification -- and then configuring them as defaults using some
secret magic.  `cv_default.py` is in turn a symlink to
`cv_dreq_example.py` which provides the current default
implementation: changing this symlink would change which
implementation was selected with no code change.  As there's only one
implementation of JSONification there's no symlink currently, but the
same mechanism could be used if there was more than one.

Quite probably the default implementation will change to
`cv_invert_varmip` at some point as it seems to give better results in
general.

## An example: comparing the results from two implementations
Here is some example code which compares two provided implementations
for computing variables. This code can be found in
`samples/python/compare_backends.py`.

```python
#!/usr/bin/env python -
# -*- mode: Python -*-
#

"""An example of using two different implementations in the same code,
in order to compare their results.
"""

from djq import process_request, ensure_dq
from djq.variables import validate_cv_implementation
import djq.variables.cv_dreq_example as cde
import djq.variables.cv_invert_varmip as civ

request = [{'mip': "AerChemMIP",
            'experiment': "HISTghg"}]

# Check them, just in case (this will raise an exception if anything
# goes wrong)
validate_cv_implementation(cde)
validate_cv_implementation(civ)

for impl in (cde, civ):
    print ("with {}: {} variables"
           .format(impl.__name__,
                   len(process_request(request,
                                       cvimpl=impl)[0]['reply-variables'])))
```

Running this:

```
$ python samples/python/compare_backends.py
[pruned 34 bogons]
with djq.variables.cv_dreq_example: 732 variables
with djq.variables.cv_invert_varmip: 798 variables
```

(The exact results will obviously depend on the exact DREQ version.
The text in \[square brackets\] is noise from one of the backends on
standard error.)

## An example: writing a trivial implementation
It's very easy to write a simple implementation: here is the code you
need to write one which computes the union of the variables returned
by the two implementations above.

```python
from djq.variables import cv_implementation, validate_cv_implementation
from djq.variables.cv_dreq_example import compute_cmvids_for_exids as cvde
from djq.variables.cv_invert_varmip import compute_cmvids_for_exids as cviv

def cv_union(dq, mip, exids):
    # Compute the union of two implementations
    return cvde(dq, mip, exids) | cviv(dq, mip, exids)

# Install cv_union as the implementation in this thread
cv_implementation(validate_cv_implementation(cv_union))
```

A script which uses this implementation is in
`samples/python/union_backend.py`.

---

## A note on dynamic variables
I've described things such as the as verbosity levels above as being
'thread-local', and `process_request` has a lot of arguments which
allow values for these things to be set for a single call:

```python
process_request(request, verbosity=100, cvimpl=myimpl)
```

will set the value of `verbosity_level` and `cv_implementation` for
this call only.

These things are in fact implemented as dynamically-scoped variables:
variables whose bindings have indefinite scope (they can be referenced
anywhere, not just where they are lexically visible) and definite
extent (the bindings only exist until the end of the form that
establishes them).  Python doesn't have such variables (and indeed
habitually conflates binding and assignment in a horrid way), so there
is an implementation in `djq.low.nfluids`, where they are called
'fluid variables'.  They are implemented as functions which look up
values on a secret binding stack, together with a context manager
which pushes and pops stack frames.  This is why, for instance
`cv_implementation` doesn't check its argument for sanity: it's just a
fluid variable.  Fluid bindings are per-thread (each thread has its
own stack) and there's an option of causing them to be automatically
rebound for each thread, so setting (as opposed to binding) verbosity
in one thread does not alter its value in another thread.

The implementation of `process_request` then looks, in part, like
this:

```python
def process_request(... verbosity=None):
    ...
    with fluids((verbosity_level, (verbosity
                                   if verbosity is not None
                                   else verbosity_level())),
                ...):
        ...
```
