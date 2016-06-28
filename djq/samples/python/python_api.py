#!/usr/bin/env python
# -*- mode: Python -*-
#

"""Python-level API to djq
"""

from djq import process_request
from djq.low import chatter, ExternalException
from pprint import pprint

if __name__ == '__main__':
    try:
        chatter("(invalid request)")
        pprint(process_request([1]))
    except ExternalException as e:
        chatter("(expected) {}", e)
    except Exception as e:
        exit("oops: {}".format(e))
    try:
        chatter("(valid request)")
        pprint(process_request([{'dreq': 'latest',
                                 'mip': 'DECK',
                                 'experiment': 'control'},
                                {'mip': 'invalid-mip-name'}]))
    except Exception as e:
        exit(e)
