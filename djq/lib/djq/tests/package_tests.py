# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

# Package tests for djq
#

from types import ModuleType, FunctionType
import djq
from djq.low import validate_package_interface, report_package_interface

categories = {'instances': {FunctionType: ('process_stream', 'process_request',
                                           'read_request',
                                           'default_dqroot', 'valid_dqroot',
                                           'default_dqtag','valid_dqtag',
                                           'default_dqpath',
                                           'ensure_dq', 'invalidate_dq_cache',
                                           'dq_info'),
                            ModuleType: ('low', 'variables')},
              'types': {Exception: ('BadJSON', 'BadParse', 'BadSyntax')}}

def test_interface():
    if not validate_package_interface(djq, categories):
        report_package_interface(djq, categories)
        raise Exception("djq package interface trouble")

if __name__ == '__main__':
    report_package_interface(djq, categories)
