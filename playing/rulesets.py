# Some rulesets
#

from dqwalker import mips_of_cmv

__all__ = ['spreadsheet']

original = {'CMORvar': ('defaultPriority',
                        'positive',
                        'type',
                        'modeling_realm',
                        'frequency',
                        'prov',
                        'provNote',
                        'rowIndex',
                        ('mips',
                         (lambda cmv, dqt, rules, dq, for_side_effect=False,
                                 **junk:
                              (tuple(sorted(mips_of_cmv(cmv, dq)))
                               if not for_side_effect
                               else None))),
                        ('var', ('vid',)),
                        ('structure', ('stid',)),
                        ('self', (lambda cmv, dqt, rules, dq, **junk: cmv))),
               'var': ('label',
                       'title',
                       'units',
                       'description',
                       'sn'),
               'structure': ('cell_measures',
                             'cell_methods',
                             'odims',
                             ('spatialShape', ('spid',)),
                             ('temporalShape', ('tmid',))),
               'spatialShape': ('dimensions',),
               'temporalShape': ('dimensions',)}

spreadsheet = {'CMORvar': ('label',
                           'defaultPriority',
                           'positive',
                           'type',
                           'modeling_realm',
                           'frequency',
                           'prov',
                           'provNote',
                           'rowIndex',
                           ('direct_mips',
                            (lambda cmv, dqt, rules, dq, for_side_effect=False,
                                    **junk:
                                 (tuple(sorted(mips_of_cmv(cmv, dq,
                                                           direct=True)))
                                  if not for_side_effect
                                  else None))),
                           ('all_mips',
                            (lambda cmv, dqt, rules, dq, for_side_effect=False,
                                    **junk:
                                 (tuple(sorted(mips_of_cmv(cmv, dq,
                                                          direct=False)))
                                  if not for_side_effect
                                  else None))),
                           ('var', ('vid',)),
                           ('structure', ('stid',)),
                           ('self', (lambda cmv, dqt, rules, dq, **junk: cmv))),
               'var': ('label',
                       'title',
                       'units',
                       'description',
                       'sn'),
               'structure': ('cell_measures',
                             'cell_methods',
                             'odims',
                             ('spatialShape', ('spid',)),
                             ('temporalShape', ('tmid',))),
               'spatialShape': ('dimensions',),
               'temporalShape': ('dimensions',)}
