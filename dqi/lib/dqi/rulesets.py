# Some rulesets for the walker
#
# These are actually used by things: it's not clear if they should be
#

from .walker import mips_of_cmv, walk_into

__all__ = ['spreadsheet', 'original']

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
                        ('var', (walk_into, 'vid')),
                        ('structure', (walk_into, 'stid'))),
            'var': ('label',
                    'title',
                    'units',
                    'description',
                    'sn'),
            'structure': ('cell_measures',
                          'cell_methods',
                          'odims',
                          ('spatialShape', (walk_into, 'spid')),
                          ('temporalShape', (walk_into, 'tmid'))),
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
                           ('var', (walk_into, 'vid')),
                           ('structure', (walk_into, 'stid'))),
               'var': ('label',
                       'title',
                       'units',
                       'description',
                       'sn'),
               'structure': ('cell_measures',
                             'cell_methods',
                             'odims',
                             ('spatialShape', (walk_into, 'spid')),
                             ('temporalShape', (walk_into, 'tmid'))),
               'spatialShape': ('dimensions',),
               'temporalShape': ('dimensions',)}
