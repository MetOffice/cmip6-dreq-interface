# Tests for the toplevel
#
# This only currently tests failures of various kinds, and is also a
# bit messy
#

from StringIO import StringIO
from json import loads, dumps
from nose.tools import raises
from djq.toplevel import process_stream, process_request
from djq.low import ExternalException

# These should result in a catastrophe and perhaps raise an exception
# if debugging
#
catastrophic_inputs = (
    "[",
    "1",
    "[1]",
    "[[]]")

def stream_test_catastrophic_inputs():
    def check_catastrophe(s):
        out = StringIO()
        process_stream(StringIO(s), out)
        jsn = loads(out.getvalue())
        assert isinstance(jsn, dict) and 'catastrophe' in jsn
    for i in catastrophic_inputs:
        yield (check_catastrophe, i)

def stream_test_catastrophic_inputs_raising():
    @raises(ExternalException)
    def check_catastrophe(s):
        out = StringIO()
        process_stream(StringIO(s), out, backtrace=True)
    for i in catastrophic_inputs:
        yield (check_catastrophe, i)

# These are objects which are not valid requests
#
invalid_requests = (
    1,
    {},
    [1],
    "a")

def object_test_invalid_requests():
    @raises(ExternalException)
    def check_invalid(r):
        process_request(r)
    for r in invalid_requests:
        yield (check_invalid, r)

# This request should result in a list of bad-request returns
#
bad_request = ({'mip': "ok",
                'experiment': "ok",
                'extra': 'not allowed'},
               {'mip': 1,
                'experiment': "ok"},
               {'mip': "ok",
                'experiment': "ok",
                'dreq': 1},
               {})

def stream_test_bad_request():
    def check_bad_reply(reply):
        assert (isinstance(reply, dict)
                and 'reply-status' in reply
                and reply['reply-status'] == "bad-request")
    out = StringIO()
    process_stream(StringIO(dumps(bad_request)), out)
    for r in loads(out.getvalue()):
        yield (check_bad_reply, r)

def object_test_bad_request():
    def check_bad_reply(reply):
        assert (isinstance(reply, dict)
                and 'reply-status' in reply
                and reply['reply-status'] == "bad-request")
    for r in process_request(bad_request):
        yield (check_bad_reply, r)

# This request should elicit error responses (this is slightly relying
# on an 'obviously absurd' tag name
#
error_request = ({'mip': "ok",
                  'experiment': "ok",
                  'dreq': "premadness-hegelian-Eu-top-dog-Spartacan"},
                 {'mip': "ok",
                  'experiment': None,
                  'dreq': "premadness-hegelian-Eu-top-dog-Spartacan"})

def stream_test_error_request():
    def check_error_reply(reply):
        assert (isinstance(reply, dict)
                and 'reply-status' in reply
                and reply['reply-status'] == "error")
    out = StringIO()
    process_stream(StringIO(dumps(error_request)), out)
    for r in loads(out.getvalue()):
        yield (check_error_reply, r)

def object_test_error_request():
    def check_error_reply(reply):
        assert (isinstance(reply, dict)
                and 'reply-status' in reply
                and reply['reply-status'] == "error")
    for r in process_request(error_request):
        yield (check_error_reply, r)
