# (C) British Crown Copyright 2018, Met Office.
# See LICENSE.md in the top directory for license details.
#

# Tests for memoize
#
# These tests take a significant amount of time (at least 10s) to run,
# and if you have an absurdly fast machine (*absurdly* fast) they
# might spuriously pass.  They might spuriously pass on a quantum
# computer I suppose.
#
# This is also hopelessly unsafe in a threaded environment
#

from signal import signal, alarm, SIGALRM
from nose.tools import raises
from djq.low.memoize import memoizable, memos, Memos
from djq.low.nfluid import fluids

class Timeout(Exception):
    pass

def timeout(signum, frame):
    raise Timeout("timeout")

# Tests of simple versions
#

@memoizable
def fib(n):
    if n <= 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)

f30 = 1346269
# fib(60) is not effectively computable without memoizing
f70 = 308061521170129

def test_fib30_unmemoized():
    assert fib(30) == f30

def test_fib30_memoized():
    with fluids((memos, Memos())):
        assert fib(30) == f30

@raises(Timeout)
def test_fib70_unmemoized():
    prev_handler = signal(SIGALRM, timeout)
    try:
        alarm(10)
        assert fib(70) == f70
    finally:
        alarm(0)
        signal(SIGALRM, prev_handler)

def test_fib70_memoized():
    prev_handler = signal(SIGALRM, timeout)
    try:
        with fluids((memos, Memos())):
            alarm(120)              # this is absurdly too long
            assert fib(70) == f70
    finally:
        alarm(0)
        signal(SIGALRM, prev_handler)

# Tests of spread argument versions
#

def test_simple_memoized_spread():
    @memoizable(spread=True)
    def addup(x, y):
        return x + y

    assert addup(1, 2) == 3
    assert addup(2, 2) == 4
    with fluids((memos, Memos())):
        assert addup(1, 2) == 3
        assert addup(2, 3) == 5

@memoizable(spread=True)
def fiblike(n, a, b):
    if n <= 1:
        return 1
    else:
        return a * fiblike(n - 1, a, b) + b * fiblike(n - 2, a, b)

def test_fiblike30_unmemoized():
    assert fiblike(30, 1, 1) == f30

def test_fiblike30_memoized():
    with fluids((memos, Memos())):
        assert fiblike(30, 1, 1) == f30

@raises(Timeout)
def test_fiblike70_unmemoized():
    prev_handler = signal(SIGALRM, timeout)
    try:
        alarm(10)
        assert fiblike(70, 1, 1) == f70
    finally:
        alarm(0)
        signal(SIGALRM, prev_handler)

def test_fiblike70_memoized():
    prev_handler = signal(SIGALRM, timeout)
    try:
        with fluids((memos, Memos())):
            alarm(120)              # this is absurdly too long
            assert fiblike(70, 1, 1) == f70
    finally:
        alarm(0)
        signal(SIGALRM, prev_handler)

# Tests of key extraction & jash failure
#

def test_key_extraction():
    @memoizable(key=lambda a: a[0])
    def silly_fact(a):
        return 1 if a[0] == 1 else a[0] * silly_fact([a[0] - 1])
    fact10 = 3628800
    assert silly_fact([10]) == fact10
    with fluids((memos, Memos())):
        assert silly_fact([10]) == fact10

@raises(TypeError)
def test_unhashable():
    @memoizable
    def f(a):
        return a
    with fluids((memos, Memos())):
        f([])
