# (C) British Crown Copyright 2018, Met Office.
# See LICENSE.md in the top directory for license details.
#

# Tests for fbundle
#

from nose.tools import raises
from djq.low.fbundle import FeatureBundle

def test_feature_path_equivalence():
    fb = FeatureBundle(source={'a': {'b': 1, 'c': 2},
                               'b': 3})
    assert fb.hasfeature('a.b')
    assert fb.getfeature('a.b') == 1
    assert fb.hasfeature(('a', 'b'))
    assert fb.getfeature(('a', 'b')) == 1
    assert fb.hasfeature('b')
    assert fb.getfeature('b') == 3
    assert fb.hasfeature(['b'])
    assert fb.getfeature(['b']) == 3

def test_odd_features():
    fb = FeatureBundle(source={1: {2: 3}, 2: {3: 4}})
    assert not fb.hasfeature('1.2')
    assert fb.getfeature((1, 2)) == 3
    assert fb.hasfeature(2)
    assert fb.getfeature(2) == {3: 4}

def test_default_features():
    fb = FeatureBundle(source={'a': {'b': 1}})
    assert fb.getfeature('a.b.c') == None
    assert fb.getfeature('a.b.c', default=fb) is fb

@raises(TypeError)
def test_bad_source():
    fb = FeatureBundle(source=1)
