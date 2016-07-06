"""Package namespace control
"""

__published__ = ('validate_package_interface', 'publish')

__all__ = __published__

from sys import modules
from types import ModuleType

# Publishing names
#

def publish(into, *mods):
    """Publish names into a module from some modules.

    - into is the *name* of a module to publish into (because it is
      ludicrously hard to find the current module, so this function
      does it.
    - mods is modules to publish.

    Typically invoke this as publish(__name__, mod, ...)

    What should be published is any name mentioned in
    mod.__published__: these names are imported into whatever module
    is named by __name__'s dictionary.

    This is a horrible hack.
    """
    ivars = vars(modules[into])
    for mod in mods:
        for var in getattr(mod, '__published__',
                           getattr(mod, '__all__', ())):
            ivars[var] = getattr(mod, var)


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

def validate_package_interface(pkg, categories):
    """Validate a package interface.

    This needs documentation.
    """
    (filtered, missing) = filter_names(pkg, categories)
    return len(filtered) == 0 and len(missing) == 0

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
