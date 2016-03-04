# A walker for the dreq
#

# Nothing is private here, but just export the toplevel for simple use
__all__ = ['walk_dq']


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
#   - an id, which will be extracted and whose type will be inferred
#     (see dqtype)
#   - a two-element tuple of (id, dreq-type) which will use id to
#     extract something which is assumed to be of dreq-type if valid.
#     If dreq-type is None, then the type is inferred from the object
#     by dqtype
#
# Additionally there can be a rule for None which will match anything:
# you can use this as a fallback rule
#
fallback_rules = {None: ()} # just enough to run it

def walk_dq(dq, rules=None):
    # walk the dq: this constructs the top of the tree, which is a
    # dict mapping from miptable to the names of the CMORvars that
    # refer to it.
    rules = rules if rules else fallback_rules
    cmvs = sorted(dq.coll['CMORvar'].items,
                  cmp=lambda x,y: cmp(x.label, y.label))
    return {table: {cmv.label: walk_thing(cmv, "CMORvar", rules, dq)
                    for cmv in cmvs if cmv.mipTable == table}
            for table in sorted(set(v.mipTable for v in cmvs))}

def walk_thing(thing, dqt, rules, dq):
    # Walk the rules for thing, returning a suitable dict
    # Real Programmers would write this as a huge dict comprehension

    def walk_into(child_attr, child_dqt):
        # Recurse.  Note that child_dqt may be None which means 'to be
        # inferred by walk_thing': nothing here even cares.
        if not hasattr(thing, child_attr):
            raise MissingAttribute( "{} is missing {}".format(dqt, child_attr))
        child_id = getattr(thing, child_attr)
        if child_id not in dq.inx.uid:
            raise BadLink("missing {}".format(child_id))
        child = dq.inx.uid[child_id]
        if validp(child):
            # OK recurse (note that child_dqt may be None: see above)
            return walk_thing(child, child_dqt, rules, dq)
        else:
            # Leave a trace that the child was invalid
            return None

    if dqt is None:             # no type given for thing
        dqt = dqtype(thing)     # so infer
    if dqt not in rules and None not in rules:
        raise MissingRule("no rule for {}".format(dqt))
    rules_for_dqt = rules[dqt] if dqt in rules else rules[None]
    if not (isinstance(rules_for_dqt, list)
            or isinstance(rules_for_dqt, tuple)):
        # ('x') is a really common mistake for ('x',) because Python is crap
        raise MutantRule("ruleset {} isn't: tuple syntax lossage?"
                         .format(rules_for_dqt))
    result = {}
    for rule in rules_for_dqt:
        if isinstance(rule, str) or isinstance(rule, unicode):
            if hasattr(thing, rule):
                result[rule] = getattr(thing, rule)
            else:
                raise MissingAttribute("{} is missing  {}".format(dqt, rule))
        elif isinstance(rule, tuple) and len(rule) == 2:
            (name, action) = rule
            if callable(action):
                result[name] = action(thing, rules, dq)
            elif isinstance(action, str) or isinstance(action, unicode):
                result[name] = walk_into(action, None)
            elif isinstance(action, tuple) and len(action) == 2:
                result[name] = walk_into(action[0], action[1])
            else:
                raise MutantRule("mutant tuple rule {}".format(rule))
        else:
            raise MutantRule("rule {} is hopeless".format(rule))
    return result

def dqtype(item):
    # an item's type in the request
    return item._h.label

def validp(item):
    # something is valid if its dqt is not 'remarks'
    return dqtype(item) != 'remarks'

def mips_of_cmv(cmv, dq, direct=False):
    # Return a set of the mips of a CMORvar in dq.  If direct is true,
    # only use the MIP directly, not its experiments
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

    if not direct:
        # Now deal with experiments, if asked
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
            dqt = dqtype(dq.inx.uid[esid])
            if dqt == 'mip':
                # it's a MIP, directly
                mips.add(esid)
            elif dqt == 'exptgroup':
                # group of experiments: they all must belong to the
                # same MIP I think, so this just picks the first
                expt = dq.inx.uid[dq.inx.iref_by_sect[esid].a['experiment'][0]]
                if validp(expt):
                    exptdqt = dqtype(expt)
                    if exptdqt == 'experiment':
                        # just add its MIP
                        mips.add(expt.mip)
                    else:
                        raise BadDreq("{} isn't an experiment".format(exptdqt))

    return mips
