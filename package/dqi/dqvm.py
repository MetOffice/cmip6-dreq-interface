# Map from MIP<->vars
#

from os.path import split, join
from collections import defaultdict
from dreqPy.dreq import loadDreq, defaultDreqPath, defaultConfigPath
from .walker import walk_dq, mips_of_cmv
from .low import lazy

__all__ = ['DQVM']

class DQVM(object):
    # I am not at all clear this is the right approach (all this laziness)
    #
    rules = {'CMORvar': (('mips', (lambda cmv, dqt, ruleset, dq, **junk:
                                       mips_of_cmv(cmv, dq, direct=False))),)}

    def __init__(self, dqroot=None):
        self.dqroot = dqroot

    @lazy
    def dq(self):
        return loadDreq(dreqXML=(defaultDreqPath
                                 if self.dqroot is None
                                 else join(self.dqroot,
                                           split(defaultDreqPath)[1])),
                        configdoc=(defaultConfigPath
                                   if self.dqroot is None
                                   else join(self.dqroot,
                                             split(defaultConfigPath)[1])))

    @lazy
    def walked(self):
        return walk_dq(self.dq, self.rules)

    @lazy
    def maps(self):
        v2m = defaultdict(set)
        m2v = defaultdict(set)
        for vt in self.walked.values():
            for (vn, vat) in vt.iteritems():
                v2m[vn].update(vat['mips'])
                for vmip in vat['mips']:
                    m2v[vmip].add(vn)
        return (v2m, m2v)

    @lazy
    def vmm(self):
        return self.maps[0]

    @lazy
    def mvm(self):
        return self.maps[1]
