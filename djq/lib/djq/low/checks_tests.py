# Tests for runtime checks
# Yes, really
#

from djq.low.checks import *
from djq.low.noise import verbosity_level

verbosity_level(1000)

tree = make_checktree()

@checker(tree, "one/check-one", 1)
def check_one():
    return True

@checker(tree, "two/check-two")
def check_two():
    return False

@checker(tree, "one.two/check-three", 1)
def check_three():
    return True

def test_all_checks():
    assert tree() is False

def test_one_checks():
    assert tree("one") is True

def test_no_checks():
    assert tree("none") is None

def test_high_priority_checks():
    assert tree(minpri=1) is True
    assert tree(minpri=2) is None

argtree = make_checktree()

@checker(argtree, "nine/six")
def ninesix(a, b=2):
    return a == b

def test_arg_checks():
    assert argtree(args=(1,), kwargs={'b': 1}) is True
