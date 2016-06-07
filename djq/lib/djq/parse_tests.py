# Tests for the parser
#

from StringIO import StringIO
from nose.tools import raises
from djq.parse import *

def parse_stringy_request(s):
    # I assume that StringIO streams don't need to be closed (because
    # they don't suport with properly)
    return parse_request(StringIO(s))

# Both lexically and syntactically fine
#
good_jsons = (
    "[]",
    """
[
 {"mip": "FOO",
  "experiment": "BAR"}]""",
    """
[
 {"mip": "FOO",
  "experiment": "BAR",
  "dreq": "BINE"}]""",
    """
[
 {"MIP": "FOO",
  "experiment": "BAR",
  "Dreq": "BINE"}]""")

def test_good_jsons():
    for j in good_jsons:
        yield (parse_stringy_request, j)

# Lexically OK, syntactically bad
#
bad_jsons = (
    "{}",
    """
[
 [1, 2]]""",
    """
[
 {"MIP": "FOO",
  "UNKNOWN": "KEY"}]""")

def test_bad_jsons():
    @raises(BadSyntax)
    def parse_bad(json):
        parse_stringy_request(json)
    for j in bad_jsons:
        yield (parse_bad, j)

# Not even lexically OK
#
# (note that the Python JSON module accepts repeated keys, so there's
# nothing we can do about that (they are legal by the standard,
# although implementations are allowed to reject them as an
# extension).
#
malformed_jsons = (
    "[",
    "",
    "just completely bogus rubbish here")

def test_malformed_jsons():
    @raises(BadJSON)
    def parse_malformed(json):
        parse_stringy_request(json)
    for j in malformed_jsons:
        yield (parse_malformed, j)
