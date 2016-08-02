# Notes
## Python style
I've read [PEP 8](https://www.python.org/dev/peps/pep-0008/) but don't
always follow its advice.

### Avoiding spot plague
Rather than `import foo` and then a lot of `foo.bar()`s I always say
`from foo import bar` and then `bar()`.  This makes code less visually
noisy, makes it clear exactly what you are asking for, and means that
`foo.bar()` always means 'call the method `bar` in the `foo` object'
and similarly for attribute access.

The argument against this is that it means that there are multiple
bindings to the same value in different modules, and this means
assignment breaks:

```
from low import verbosity, mutter

verbosity = 4

mutter(...)
```

Doesn't do what you expect, if you expect it to do anything useful.
The answer to that is not to muck around with global variables which
you don't own: anything which wants to let you modify some global
state does so by exposing a functional interface to do so:

```
from low import verbosity_level, mutter

verbosity_level(4)

mutter(...)
```

In practice there is almost no mutable global state where this would
matter.

### Packages as conduits
Packages are conduits for their modules: `__init__.py` looks like
this:

```
from . import m1
from .m1 import *

from . import m2
from .m2 import *
```

This trick comes from NumPy, although other people must use it.  This
is the only place where `from x import *` is OK other than in test
modules.

This means that `__all__` in a module is the list of names that should
be visible *from its package*: there may be additional names which
should be visible to other modules *within the package*, and there is
no way of enforcing what they should be other than convention.

Packages generally don't do `from <subpackage> import *` for
subpackages: this would mean that packages extended all their
subpackages and that's not what you normally want I think (I don't
want `djq` to be an extension of `djq.low`).

### Short module names in packages

Modules in a package which need other modules in the same package use
short names.  So in `djq.variables`, `cv_invert_varmip.py` says

```
from varmip import mips_of_cmv
```

and not

```
from djq.variables.varmip import mips_of_cmv
```

I only do this for modules in the current package or subpackages, not
upwards (so the same module says `from djq.low import ...`).

I don't understand [relative
names](https://www.python.org/dev/peps/pep-0328/) very well, and I'm
not sure if I should use them here as well: it has always been obscure
to me just how `sys.path` gets set up.

### Tests
Test modules should live in subdirectories called `tests` but have not
always done so.  They always use fully-qualified names for imports so
they don't depend on where they are in the tree.

### Single and double quotes
I use both `'single quotes'` and `"double quotes"` for strings (as
well as `"""triple double quotes"""` for docstrings).

* Single quotes are where a string is being used as a poor-person's
  symbol: for instance where it is a key in a `dict` or something like
  that, or when it is one of a small set of values.  For instance
  `{'return-code': 'error'}`.
* Double quotes are where a string is just a string.  For instance
  `{'message': "a bad thing has happened"}`.
