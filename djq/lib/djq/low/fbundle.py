# (C) British Crown Copyright 2018, Met Office.
# See LICENSE.md in the top directory for license details.
#

"""JSON feature bundles
"""

__all__ = ('feature_bundle', 'FeatureBundle')

from json import load
from dtype import stringlike, arraylike
from exceptions import ExternalException
from nfluid import fluid, globalize

class FbundleJSONBadness(ExternalException):
    """Failure to derive something from a JSON spec"""
    def __init__(self, src=None, wrapped=None):
        self.src = src
        self.wrapped = wrapped
        super(FbundleJSONBadness, self).__init__(
            ("a badness reading JSON feature bundle from {}".format(src)
             if src is not None
             else "a badness reading JSON feature bundle"))

class FeatureBundle(dict):
    def __init__(self, source=None):
        d = None
        if source is not None:
            if stringlike(source):
                try:
                    with open(source) as json:
                        d = load(json)
                except Exception as e:
                    raise FbundleJSONBadness(src=source, wrapped=e)
            elif isinstance(source, dict):
                d = source
            else:
                raise TypeError("bogus source for feature bundle")
        if d is not None:
            for (k, v) in d.iteritems():
                super(FeatureBundle, self).__setitem__(k, v)

    # This is probably not enough to make FBs immutable, but it at
    # least makes it hard to do things to them by mistake.
    #

    def __setitem__(self, k, v):
        raise TypeError("FeatureBundles are meant to be immutable")

    def __delitem__(self, k):
        raise TypeError("FeatureBundles are meant to be immutable")

    def getfeature(self, feature, default=None):
        """Get a feature from a feature bundle

        feature is interpreted as a path, and is looked up.  If it
        isn't found then default (defaultly None) is returned.
        """
        def gf_loop(pt, e):
            if len(pt) == 0:
                return e
            elif isinstance(e, dict):
                if pt[0] in e:
                    return gf_loop(pt[1:], e[pt[0]])
                else:
                    return default
            else:
                return default

        def fpath(f):
            if stringlike(f):
                return f.split('.')
            elif arraylike(f):
                return f
            else:
                return (f,)

        return gf_loop(fpath(feature), self)

    def hasfeature(self, feature):
        """Return true if feature is known"""
        return (self.getfeature(feature, self) is not self)

    def getf(self, feat, fallback=None, default=None):
        """Get feat from a bundle, falling back progressively.

        If feat is in the bundle it is returned.  If not, and if
        fallback is given, then it's looked up there, with a default
        of default.  If fallback is not given (or is None) then
        default is returned.  default is None if not provided.
        """

        if self.hasfeature(feat):
            return self.getfeature(feat)
        elif fallback is not None:
            return fallback.getfeature(feat, default)
        else:
            return default

feature_bundle = globalize(fluid(), FeatureBundle(), threaded=True)
