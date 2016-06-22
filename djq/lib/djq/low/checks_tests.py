# Tests for runtime checks
# Yes, really
#

from djq.low.checks import *
from djq.low.noise import verbosity_level

verbosity_level(1000)

tree = make_checktree()

@check(tree, "one/check-one", 1)
def check_one():
    return True

@check(tree, "two/check-two")
def check_two():
    return False

@check(tree, "one.two/check-three", 1)
def check_three():
    return True

def test_all_checks():
    assert run_checks(tree) is False

def test_one_checks():
    assert run_checks(tree, "one") is True

def test_no_checks():
    assert run_checks(tree, "none") is None

def test_high_priority_checks():
    assert run_checks(tree, minpri=1) is True
    assert run_checks(tree, minpri=2) is None
