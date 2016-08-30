# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

"""Package namespace control
"""

# Package interface
__all__ = ('validate_package_interface', 'report_package_interface')

from sys import modules, stdout
from types import ModuleType

# Checking namespaces for packages
#

# The category map is a dict mapping category -> tmap, where category
# is used to look up the filter for tmap.
#
# tmap in turn looks maps thing -> names-for-thing where thing is
# whatever names-for-thing should match against.
#
# So for instance, a map like
#  {'instances': {FunctionType: ('one', 'two')}}
# says that the 'instances' filter should be used with a tmap of
#  {FunctionType: ('one', 'two')}
# and this means that one and two should exist and be functions
#

def validate_package_interface(pkg, categories, details=False):
    """Validate a package interface.

    This needs documentation.
    """
    (filtered, missing) = filter_names(pkg, categories)
    if details:
        return (filtered, missing)
    else:
        return len(filtered) == 0 and len(missing) == 0

def report_package_interface(package, categories, stream=stdout):
    (filtered, missing) = validate_package_interface(package, categories,
                                                     details=True)
    if len(filtered) > 0:
        print "* extras"
        for f in sorted(filtered, key=lambda x: getattr(package, x).__module__):
            print "  {} from {}".format(f, getattr(package, f).__module__)
    if len(missing) > 0:
        print "* missing"
        for m in sorted(missing):
            print "  {}".format(m)

filters = {}

def filter_names(pkg, categories):
    names = set(dir(pkg))
    missing = set()
    for (category, cmap) in categories.iteritems():
        (names, missing) = tuple(filters[category](pkg, names, missing, cmap))
    return filter_ignoreable(pkg, names, missing)

def filter(category):
    # decorator.  A filter needs to return (filtered, unseen)
    def install_filter(f):
        filters[category] = f
        return f
    return install_filter

def parameterized_filter(predicate, pkg, names, missing, tmap):
    # A filter which uses a general predicate
    nmap = {}                   # name -> thing to test
    unseen = set(missing)
    filtered = set()
    for (tp, tnames) in tmap.iteritems():
        unseen |= set(tnames)
        for name in tnames:
            nmap[name] = tp
    for name in names:
        if not (name in nmap
                and predicate(getattr(pkg, name), nmap[name])):
            filtered.add(name)
        else:
            unseen.discard(name)
    return (filtered, unseen)

@filter('instances')
def filter_instances(pkg, names, missing, tmap):
    # filter instances
    return parameterized_filter(isinstance, pkg, names, missing, tmap)

@filter('types')
def filter_types(pkg, names, missing, tmap):
    # filter types
    return parameterized_filter(issubclass, pkg, names, missing, tmap)

def filter_ignoreable(pkg, names, missing):
    # names beginning with _ and names which refer to modules are
    # ignoreable
    return (set(name for name in names
                if not (name.startswith("_")
                        or isinstance(getattr(pkg, name), ModuleType))),
            missing)
