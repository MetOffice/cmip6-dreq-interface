# Package tests for djq
#

from types import ModuleType, FunctionType
import djq
from djq.low import validate_package_interface

djq_cats = {'instances': {FunctionType: ('process_stream', 'process_request',
                                         'default_dqroot', 'default_dqtag',
                                         'valid_dqroot', 'valid_dqtag',
                                         'invalidate_dq_cache'),
                          ModuleType: ('low',)},
            'types': {Exception: ('BadJSON', 'BadParse', 'BadSyntax')}}

def test_djq_interface():
    assert validate_package_interface(djq, djq_cats), "package interface bogon"
