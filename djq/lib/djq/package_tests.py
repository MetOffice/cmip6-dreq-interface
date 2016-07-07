# Package tests for djq
#

from types import ModuleType, FunctionType
import djq
from djq.low import validate_package_interface, report_package_interface

categories = {'instances': {FunctionType: ('process_stream', 'process_request',
                                           'default_dqroot', 'default_dqtag',
                                           'valid_dqroot', 'valid_dqtag',
                                           'invalidate_dq_cache'),
                            ModuleType: ('low',)},
              'types': {Exception: ('BadJSON', 'BadParse', 'BadSyntax')}}

def test_interface():
    if not validate_package_interface(djq, categories):
        report_package_interface(djq, categories)
        raise Exception("djq package interface trouble")

if __name__ == '__main__':
    report_package_interface(djq, categories)
