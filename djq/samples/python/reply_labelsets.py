# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

"""An example of simplifying responses
"""

__all__ = ('reply_labelsets',)

from djq import process_request

def reply_labelsets(rq, **args):
    # Return tuples with MIP, experiment, labelset for each request
    return tuple((r['mip'],
                  r['experiment'],
                  set(v['label'] for v in r['reply-variables']))
                 for r in process_request(rq, **args))
