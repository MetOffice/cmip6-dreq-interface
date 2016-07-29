#!/usr/bin/env python -
# -*- mode: Python -*-
#

"""An example of using two different implementations in the same code,
in order to compare their results.
"""

from djq import process_request, ensure_dq
import djq.variables.cv_dreq_example as cde
import djq.variables.cv_invert_varmip as civ

request = [{'mip': "AerChemMIP",
            'experiment': "HISTghg"}]

for impl in (cde, civ):
    print ("with {}: {} variables"
           .format(impl.__name__,
                   len(process_request(request,
                                       cvimpl=impl)[0]['reply-variables'])))
