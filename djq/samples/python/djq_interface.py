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
