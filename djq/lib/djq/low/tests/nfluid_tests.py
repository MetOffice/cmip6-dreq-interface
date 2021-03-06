# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

# Tests for new fluids
#

# This doesn't test localizing, as that's never used

from djq.low.nfluid import fluid, boundp, fluids, globalize, Unbound
from threading import Thread
from nose.tools import raises

utf = globalize(fluid(), 1)

def test_global_utf_binding():
    assert utf() == 1
    utf(2)
    assert utf() == 2
    with fluids((utf, 3)):
        assert utf() == 3
        utf(4)
        assert utf() == 4
    assert utf() == 2

def test_local_binding():
    fl = fluid()
    assert not boundp(fl)
    with fluids((fl, 2)):
        assert boundp(fl)
        assert fl() == 2
        with fluids((fl, 3)):
            assert fl() == 3
        assert fl() == 2
    @raises(Unbound)
    def unbound():
        return fl()
    unbound()

tf = globalize(fluid(), 1, threaded=True)

def test_thr_binding():
    def set_tf_3():
        assert tf() == 1
        tf(3)
        assert tf() == 3
    set_tf_3()
    assert tf() == 3
    with fluids((tf, 12)):
        thr = Thread(target=set_tf_3)
        thr.start()
        thr.join()
        assert tf() == 12
    assert tf() == 3
