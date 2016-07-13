# Package tests for djq
#

from types import ModuleType, FunctionType
import djq.variables as variables
from djq.low import validate_package_interface, report_package_interface

categories = {'instances': {FunctionType: ('compute_variables',
                                           'jsonify_variables',
                                           'cv_implementation',
                                           'jsonify_implementation')},
              'types': {Exception: ('NoExperiment', 'NoMIP',
                                    'WrongExperiment', 'BadCVImplementation')}}

def test_interface():
    if not validate_package_interface(variables, categories):
        report_package_interface(variables, categories)
        raise Exception("djq.variable package interface trouble")

if __name__ == '__main__':
    report_package_interface(variables, categories)
