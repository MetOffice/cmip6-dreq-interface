#!/usr/bin/env python -
# -*- mode: Python -*-
#

"""An example of using two different implementations in the same code,
in order to compare their results.
"""

from djq import process_request, ensure_dq
from djq.variables import cv_implementation, validate_cv_implementation
import djq.variables.cv_dreq_example as cde
import djq.variables.cv_invert_varmip as civ

request = [{'mip': "AerChemMIP",
            'experiment': "HISTghg"}]

# Check them, just in case (this will raise an exception if anything
# goes wrong)
validate_cv_implementation(cde)
validate_cv_implementation(civ)

for impl in (cv_implementation(), cde, civ):
    print ("with {}: {} variables"
           .format(impl.__name__,
                   len(process_request(request,
                                       cvimpl=impl)[0]['reply-variables'])))
