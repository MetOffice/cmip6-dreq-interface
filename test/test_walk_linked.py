# This is just some test data for walk_linked

from dreqPy.dreq import loadDreq
from dqi import walk_dq, walk_linked, dqtype

ruleset = {'CMORvar': (('all', (walk_linked,)),
                       ('requestVars', (walk_linked, 'requestVar')),
                       ('links', (walk_linked, None, 'link'))),
           
           'link': ('label', 'uid',
                    ('dqtype', (lambda thing, dqt, rules, dq,
                                for_side_effect=False, **kws: dqtype(thing)))),
           None: ('label', 'uid',
                  ('flag', lambda *junk, **kws: "missed"))}
