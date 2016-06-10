# Tests for the parser
#

from StringIO import StringIO
from nose.tools import raises
from djq.parse import *

# Tests of the top-level reader
#
def read_stringy_request(s):
    # I assume that StringIO streams don't need to be closed (because
    # they don't suport with properly)
    return read_request(StringIO(s))

good_toplevels = (
    "[]",
    "[{}]",
    """
[{"mip": "one",
  "experiment": "two"}]""",
    """[{"one": 2}]""")

def test_good_toplevels():
    for j in good_toplevels:
        yield (read_stringy_request, j)

bad_toplevels = (
    "1",
    "[1]",
    "[[]]")

def test_bad_toplevels():
    @raises(BadSyntax)
    def read_bad(json):
        return read_stringy_request(json)
    for j in bad_toplevels:
        yield (read_bad, j)

hopeless_toplevels = (
    "",
    "["
    "{1:}",
    "not even trying")

def test_hopless_toplevels():
    @raises(BadJSON)
    def read_hopeless(json):
        return read_stringy_request(json)
    for j in hopeless_toplevels:
        yield (read_hopeless, j)

# tests of single requests
#

good_single_requests = (
    {'mip': "a",
     'experiment': "b"},
    {'mip': "c",
     'experiment': "d",
     'dreq': "e"},
    {'MIP': "a",
     'ExpeRiMENT': "b"},
    {'mip': "a",
     'experiment': "b",
     'request-optional': "c"})

def test_good_single_requests():
    for s in good_single_requests:
        yield (validate_single_request, s)

bad_single_requests = (
    {'mip': 1,
     'experiment': "ok"},
    {'unknown': "key"},
    1,
    [1, 2],
    {})

def test_bad_single_requests():
    @raises(BadSyntax)
    def validate_bad(s):
        return validate_single_request(s)
    for s in bad_single_requests:
        yield(validate_bad, s)
