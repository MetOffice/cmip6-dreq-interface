# Tests for the emitter
#

from StringIO import StringIO
from json import load
from djq.parse import *
from djq.emit import *

# This just tests that we can round-trip it: it doesn't check
# exceptions or anything yet.
#

requests = (({"mip": "test",
              "experiment": "none",
              "dreq": "latest"},),)

def string2request(s):
    # I assume that StringIO streams don't need to be closed (because
    # they don't suport with properly)
    return read_request(StringIO(s))

def request2string(r):
    stream = StringIO()
    emit_reply(r, stream)
    return stream.getvalue()

def test_round_trips():
    def test_one_round_trip(r):
        # Test one round-trip.  This is trying to not care whether
        # things come back as tuples or lists (because it doesn't
        # matter: they come back as tuples in fact).
        rt = string2request(request2string(r))
        assert len(r) == len(rt)
        for i in range(len(r)):
            assert r[i] == rt[i]
    for request in requests:
        yield (test_one_round_trip, request)

def catastrophe2string(message):
    stream = StringIO()
    emit_catastrophe(message, stream)
    return stream.getvalue()

def string2catastrophe(s):
    return load(StringIO(s))

def test_catastrophe():
    cd = string2catastrophe(catastrophe2string("doom"))
    assert isinstance(cd, dict)
    assert 'catastrophe' in cd and cd['catastrophe'] == "doom"
