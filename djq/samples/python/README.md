<!-- (C) British Crown Copyright 2016, 2018 Met Office.
     See LICENSE.md in the top directory for license details. -->

# Python samples for `djq`
These are some small samples of how to use the `djq` Python interface.
They are all scripts and can be run directly.

## `python_api.py`
This demonstrates a simple use of the Python interface: it simply
calls `process_request` on a few different requests, and handles some
expected exception types.

## `djq_interface.py`
This is a more advanced example: it demonstrates verbosity control,
checking that the tag is valid, and all the exceptions you might want
to handle when calling `process_request`.

## `compare_backends.py`
This demonstrates how you can select implementations ('back ends'),
and switch between them within one program.  The program itself uses
two explicit backends as well as the default one (which is the same as
one of the explicit ones) and compares variable counts for a specific
query.

## `union_backend.py`
This demonstrates how to write a simple backend, by implementing one
which computes the union of the results of two existing backends.  The
function to do this is a single line of code.

## `reply_labelsets.py`
This is a Python module which contains a single function,
`reply_labelsets`: this takes the same arguments as `process_request`
but simplifies its return value to a tuple of tuples of MIP,
experiment, and a set of variable labels.  This can be useful for
detailed comparison of two backends, for instance: take differences
between the sets of labels they return for the same requests.

## `call_djq.py` (obsolescent)
Originally the only documented interface to `djq` was through the
command line `djq` tool.  This demonstrates how to call it from
Python.  This is now not needed as there is a proper Python interface
which is much preferable.