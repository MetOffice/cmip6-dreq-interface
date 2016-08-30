# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

# Package tests for djq.low
#
# This will only work if djq.low is basically there.
#

from types import FunctionType
import djq.low
from djq.low import validate_package_interface, report_package_interface

categories = {'types': {Exception: ('DJQException', 'InternalException',
                                    'ExternalException', 'Disaster', 'Scram',
                                    'Unbound'),
                        object: ('fluids',)},
              'instances': {FunctionType:
                            (('arraylike', 'stringlike', 'setlike')
                             + ('verbosity_level', 'debug_level',
                                'chatter', 'mutter', 'mumble', 'whisper',
                                'think', 'debug')
                             + ('make_checktree', 'checker',
                                'checks_enabled', 'checks_minpri')
                             + ('validate_object', 'every_element', 'one_of',
                                'all_of')
                             + ('fluid', 'boundp', 'globalize', 'localize')
                             + ('validate_package_interface',
                                'report_package_interface'))}}

def test_interface():
    if not validate_package_interface(djq.low, categories):
        report_package_interface(djq.low, categories)
        raise Exception("djq.low package interface trouble")

if __name__ == '__main__':
    report_package_interface(djq.low, categories)
