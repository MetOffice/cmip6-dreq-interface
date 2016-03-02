# Some rulesets
#

from dqwalker import mips_of_cmv

__all__ = ['spreadsheet']

spreadsheet = {'CMORvar': ('defaultPriority',
                           'positive',
                           'type',
                           'modeling_realm',
                           'frequency',
                           'prov',
                           'provNote',
                           'rowIndex',
                           ('mips',
                            (lambda cmv, rules, dq:
                                 tuple(sorted(mips_of_cmv(cmv, dq))))),
                           ('var', ('vid', 'var')),
                           ('structure', ('stid', 'structure'))),
               'var': ('label',
                       'title',
                       'units',
                       'description',
                       'sn'),
               'structure': ('cell_measures',
                             'cell_methods',
                             'odims',
                             ('spatialShape', ('spid', 'spatialShape')),
                             ('temporalShape', ('tmid', 'temporalShape'))),
               'spatialShape': ('dimensions',), # FUCK PYTHON
               'temporalShape': ('dimensions',)}
