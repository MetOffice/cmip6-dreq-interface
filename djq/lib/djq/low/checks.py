"""Runtime check framework
"""

# A check is a function, which may have any arguments, which should
# return true or false.  Checks live in a tree and have priorities and
# names.  You can pass arguments and keyword arguments to functions
# when running them but the default is not to.  All functions in a
# given tree get the same arguments.  The tree is run by calling it.
#

__all__ = ('make_checktree', 'checker', 'enable_checks')

from collections import defaultdict
from noise import chatter, mumble, debug
from types import stringlike

checks_enabled = True
checks_minpri = 0

def enable_checks(enabled=None, minpri=None):
    """Globally control which checks run.

    If enabled is False, then checks are disabled, if minpri is a
    number then it is used to set the minimum priority.
    """
    global checks_enabled
    global checks_minpri

    if enabled is None:
        enabled = checks_enabled
    checks_enabled = enabled if enabled is not None else checks_enabled
    checks_minpri = minpri if minpri is not None else checks_minpri
    debug("enabled {} minpri {}", checks_enabled, checks_minpri)

class CheckNode(object):
    """An object which can run a tree of checks.

    After creating an instance, add checks with the add method, and
    run them by calling the object.
    """

    def __init__(self):
        self.subnodes = defaultdict(CheckNode)
        self.checks = defaultdict(list)

    def add(self, branch, priority, name, check):
        """Add a check.

        - branch is where to add it: either an arraylike object or a
          dotted stringlike object: "foo.bar" is equivalent to ("foo",
          "bar").

        - priority is the priority of the check: higher priority
          checks run first and are harder to suppress.

        - name is the name of the check, a stringlike object.

        - check is the check function itself, which should return a
          true value if it passes.

         Return value is the check function.
         """
        if stringlike(branch):
            self.add(branch.split("."), priority, name, check)
        elif len(branch) == 0:
            self.checks[priority].append((name, check))
        else:
            self.subnodes[branch[0]].add(branch[1:], priority, name, check)
        return check

    def __call__(self, path=None, minpri=None, enabled=None,
                 args=(), kwargs={}):
        """Run some or all checks for tree

        If path is given run only checks under it.  If minpri is given
        (fallback is 0 but this can be contolled with enable_checks)
        run only checks with priority greater than or equal to
        it. enabled can be used to override what enable_checks would
        say.

        args and kwargs are passed to the check functions if given.

        If you give a path where there are no checks, or no checks
        have a high enough priority, then no checks will run and the
        function will return None.  Otherwise it returns True if all
        the checks pass and False otherwise.
        """
        if minpri is None:
            minpri = checks_minpri
        if enabled is None:
            enabled = checks_enabled

        if enabled:
            node = self if path is None else self.find(path)
            # The string here determines how paths get printed: in
            # particular whether there is a leading dot (with () there
            # isn't, with "" there would be).
            if node:
                return node.run(() if path is None else path,
                                minpri, args, kwargs)
            else:
                return None
        else:
            return None

    # Everything below is implementation
    #

    def find(self, branch):
        if stringlike(branch):
            return self.find(branch.split("."))
        elif len(branch) == 0:
            return self
        elif branch[0] in self.subnodes:
            return self.subnodes[branch[0]].find(branch[1:])
        else:
            return None

    def run(self, path, minpri, args, kwargs):
        if stringlike(path):
            return self.run(path.split("."), minpri, args, kwargs)
        else:
            ok = None
            # checks further up the tree run first, and higher
            # priority checks run first
            for pri in sorted((pri
                               for pri in self.checks.keys()
                               if pri >= minpri),
                              reverse=True):
                for (name, check) in self.checks[pri]:
                    if check(*args, **kwargs):
                        mumble("[passed {}/{}/{}]", ".".join(path), pri, name)
                        ok = True
                    else:
                        chatter("[failed {}/{}/{}]", ".".join(path), pri, name)
                        ok = False
            for (pathelt, subnode) in sorted(self.subnodes.iteritems(),
                                             key=lambda i: i[0]):
                snok = subnode.run(tuple(path) + (pathelt,), minpri,
                                   args, kwargs)
                if ok is not False and snok is not None:
                    ok = snok
            return ok

def make_checktree():
    """Make a check tree"""
    return CheckNode()

def checker(tree, spec, priority=0):
    """A decorator to install a check function:

        @check(tree, "foo/bar")
        def my_check():
            ...

    will install my_check as a check under "foo" called "bar" in tree.
    Optionally privide the priority as the third argument (default is
    0).

    """
    assert "/" in spec
    (path, name) = spec.split("/")
    return lambda f: tree.add(path, priority, name, f)
