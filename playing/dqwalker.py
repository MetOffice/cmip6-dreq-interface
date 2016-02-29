# A walker for the dreq
#

_all_ = ['walk_dq', 'Badness']


# Exceptions
#
# It would be good to classify these by whether they are bugs in the
# request, the rules or the code, but it is vague
#

class Badness(Exception):
    pass

class MissingRule(Badness):
    # problem with rules, not request
    pass

class MutantRule(Badness):
    # problem with rules, not request
    pass

class MissingAttribute(Badness):
    # probably a problem with the rules
    pass

class BadLink(Badness):
    # could be either?
    pass

class BadDreq(Badness):
    # definitely the request
    pass

# The rules of how to walk things.  This is a dict which maps from the
# type of thing (dreq section) to a tuple, whose elements may be:
# - a string: just extract that field;
# - a two-element tuple which should be a name to use and one of:
#   - a function to call which will return the value;
#   - a two-element tuple of (id, dreq-type) which will use id to
#     extract something which is assumed to be of dreq-type if valid.
#     If dreq-type is None, then the type is inferred from the object,
#     as <object>._h.label.
#
default_rules = {'CMORvar': ('defaultPriority',
                             'positive',
                             'type',
                             'modeling_realm',
                             'frequency',
                             'prov',
                             'provNote',
                             'rowIndex',
                             ('mips',
                              (lambda cmv, rules, dq:
                                   sorted(mips_of_cmv(cmv, dq)))),
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

def walk_dq(dq, rules=None):
    # walk the dq: this constructs the top of the tree, which is a
    # dict mapping from miptable to the names of the CMORvars that
    # refer to it.
    rules = rules if rules else default_rules
    cmvs = sorted(dq.coll['CMORvar'].items,
                  cmp=lambda x,y: cmp(x.label, y.label))
    return {table: {cmv.label: walk_thing(cmv, "CMORvar", rules, dq)
                    for cmv in cmvs if cmv.mipTable == table}
            for table in sorted(set(v.mipTable for v in cmvs))}

def walk_thing(thing, dqt, rules, dq):
    # Walk the rules for thing, returning a suitable dict
    # Real Programmers would write this as a huge dict comprehension
    if dqt not in rules:
        raise MissingRule("no rule for {}".format(dqt))
    result = {}
    for rule in rules[dqt]:
        if isinstance(rule, str) or isinstance(rule, unicode):
            if hasattr(thing, rule):
                result[rule] = getattr(thing, rule)
            else:
                raise MissingAttribute("{} is missing  {}".format(dqt, rule))
        elif isinstance(rule, tuple) and len(rule) == 2:
            (name, action) = rule
            if callable(action):
                result[name] = action(thing, rules, dq)
            elif isinstance(action, tuple) and len(action) == 2:
                (child_attr, child_dqt) = action
                if not hasattr(thing, child_attr):
                    raise MissingAttribute(
                        "{} is missing {}".format(dqt, child_attr))
                child_id = getattr(thing, child_attr)
                if child_id not in dq.inx.uid:
                    raise BadLink("missing {}".format(child_id))
                child = dq.inx.uid[child_id]
                if validp(child):
                    # OK recurse
                    result[name] = walk_thing(child,
                                              child._h.label
                                              if child_dqt is None
                                              else child_dqt,
                                              rules, dq)
                else:
                    # Leave a trace that the child was invalid
                    result[name] = None
            else:
                raise MutantRule("mutant tuple {}".format(rule))
        elif isinstance(rule, tuple):
            raise MutantRule("mutant tuple {}".format(rule))
        else:
            raise MutantRule("{} is hopeless".format(rule))
    return result

def validp(item):
    # something is valid if its header isn't labelled 'remarks'
    return item._h.label != 'remarks'

def mips_of_cmv(cmv, dq):
    # Return a set of the mips of a CMORvar in dq
    #
    # This is a simplified version of vrev.checkVar.chkCmv (in
    # vrev.py) But it is simpler in the sense that I do not understand
    # what the original code really does, so I have just tried to make
    # something which is a bit less horrible and which might do
    # something useful.  In particular it does not deal with any of
    # the experiment stuff.

    # requestVar ids which refer to cmv and whose groups are valid
    rvids = set(rvid for rvid in dq.inx.iref_by_sect[cmv.uid].a['requestVar']
                if validp(dq.inx.uid[dq.inx.uid[rvid].vgid]))

    # construct a dict mapping from variable group id to the highest
    # priority in that group
    vgpri = dict()
    for rvid in rvids:
        rv = dq.inx.uid[rvid]   # the requestVar
        rvp = rv.priority       # its priority
        vgid = rv.vgid          # its group
        if vgid not in vgpri or rvp > vgpri[vgid]:
            vgpri[vgid] = rvp

    linkids = set()
    for (vgid, pri) in vgpri.iteritems():
        if dq.inx.iref_by_sect[vgid].a.has_key('requestLink'):
            for rlid in dq.inx.iref_by_sect[vgid].a['requestLink']:
                rl = dq.inx.uid[rlid] # requestLink
                if rl.opt == 'priority':
                    # if it has a priority, add it if it is high enough
                    p = int(float(rl.opar)) # this is what he does: rounding?
                    if p > pri:
                        linkids.add(rlid)
                else:
                    # no priority, just add it
                    linkids.add(rlid)

    # OK, so here is the first chunk of mips: just the mip fields of
    # all these requestLink objects
    mips = set(dq.inx.uid[rlid].mip for rlid in linkids)

    # Now deal with experiments
    #

    # The IDs of all the experiments corresponding to the
    # requestLinks, I think
    esids = set(dq.inx.uid[u].esid
                for rlid in linkids
                for u in dq.inx.iref_by_sect[rlid].a['requestItem'])

    # Empty IDs can leak in (which is looks like is a bug?)
    esids.discard('')

    for esid in esids:
        # what sort of thing is this
        label = dq.inx.uid[esid]._h.label
        if label == 'mip':
            # it's a MIP, directly
            mips.add(esid)
        elif label == 'exptgroup':
            # group of experiments: they all must belong to the same
            # MIP I think, so this just picks the first
            expt = dq.inx.uid[dq.inx.iref_by_sect[esid].a['experiment'][0]]
            exptlabel = expt._h.label
            if exptlabel == 'experiment':
                # just add its MIP
                mips.add(expt.mip)
            elif exptlabel == 'remarks':
                # something missing I think?
                pass
            else:
                raise BadDreq("{} isn't an experiment".format(exptlabel))

    return mips
