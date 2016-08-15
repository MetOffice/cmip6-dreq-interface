#!/usr/bin/env python -
# -*- mode: Python -*-
#

"""Writing a simple backend which uses a union of two existing ones.
"""

from djq import process_request, ensure_dq
from djq.variables import cv_implementation, validate_cv_implementation
from djq.variables.cv_dreq_example import compute_cmvids_for_exids as cvde
from djq.variables.cv_invert_varmip import compute_cmvids_for_exids as cviv

request = [{'mip': "AerChemMIP",
            'experiment': "HISTghg"}]

def cv_union(dq, mip, exids):
    # Compute the union of two implementations
    return cvde(dq, mip, exids) | cviv(dq, mip, exids)

cv_implementation(validate_cv_implementation(cv_union))

print ("{} variables"
       .format(len(process_request(request)[0]['reply-variables'])))
