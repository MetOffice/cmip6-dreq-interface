# Tests for valob
#

from valob import validate_object, every_element, some_elements
from djq.low import stringlike

should_match = ((1, 1),
                ("a", "a"),
                ([1, 2, 3], [1, 2, 3]),
                (1, lambda x: isinstance(x, int)),
                ({'a': "b", 1: True},
                 {1: True, 'a': "b"}),
                ([1, 2, 3], lambda x: isinstance(x, list) and all(x)),
                ({1: [1, 2],
                  2: lambda x: x,
                  3: {'a': 1}},
                 {1: [1, lambda x: isinstance(x, int)],
                  2: callable,
                  3: {'a': 1}}),
                ([1, 2, 100, 2],
                 (lambda l:
                  isinstance(l, list) and every_element(lambda i:
                                                        isinstance(i, int),
                                                        l))),
                ([1, "a"],
                 (lambda l:
                  isinstance(l, list) and some_elements(stringlike, l))))


def test_should_match():
    def checker(ob, pattern):
        assert validate_object(ob, pattern) is True, "failed to match"
    for (ob, pattern) in should_match:
        yield (checker, ob, pattern)


should_not_match = ((1, 2),
                    ("a", "b"),
                    ([[[[[[[1, [2]]]]]]]],
                     [[[[[[[1, [3]]]]]]]]))

def test_should_not_match():
    def checker(ob, pattern):
        assert validate_object(ob, pattern) is False, "matched unexpectedly"
    for (ob, pattern) in should_not_match:
        yield (checker, ob, pattern)
