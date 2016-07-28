# Tests for fluid binding
#

from djq.low.fluid import fluid

variable = 3

def vacs(val=None):
    global variable
    if val is None:
        return variable
    else:
        variable = val

def test_simple_fluid_binding():
    assert vacs() == 3
    with fluid((vacs, 4)):
        assert vacs() == 4
    assert vacs() == 3

def test_not_fluid_binding():
    assert vacs() == 3
    with fluid((vacs, 100, False)):
        assert vacs() == 3

def test_nested_fluid_binding():
    with fluid((vacs, 4),
               (vacs, 5)):
        assert vacs() == 5
    assert vacs() == 3

class Bogon(Exception):
    pass

def test_fluid_exception():
    assert vacs() == 3
    try:
        with fluid((vacs, 4)):
            assert vacs() == 4
            raise Bogon()
    except Bogon:
        assert vacs() == 3
    assert vacs() == 3
