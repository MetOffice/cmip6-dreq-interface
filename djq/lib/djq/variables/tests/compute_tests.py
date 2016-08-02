# Minimal tests of compute
#

from sys import modules
from nose.tools import raises
from djq.variables.compute import (cv_implementation,
                                   validate_cv_implementation,
                                   BadCVImplementation)
from djq.variables import cv_dreq_example

# Check implementation switching

me = modules[__name__]

@raises(BadCVImplementation)
def test_switch_to_me():
    cv_implementation(validate_cv_implementation(me))

def test_switch_to_good():
    cv_implementation(cv_dreq_example)
    assert cv_implementation() is cv_dreq_example

def test_switch_to_fn():
    def impl(dq, mip, exids):
        return set()
    cv_implementation(impl)
    assert cv_implementation() is impl
