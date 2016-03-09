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

# The rules of how to walk things.
#
# This is a dict which maps from the type of thing (dreq section) to a
# rule for that type.  There can also be a wildcard rule, whose type
# is None.
#
# Each rule is one of the following.
# - A callable, which is called and which returns the result of the
#   walk for this rule (see below for calling conventions).
# - A list of tuples of two elements: [(p, r), ...]: this is a
#   conditional, and each p is called in turn until one returns true,
#   when its r is used as the rule. It is fine if none return true.
# - A tuple of instructions, each of which is processed in turn
#
# Each instruction is one of the following.
# - A string: that field is extracted and recorded in the dictionary
#   returned;
# - A two-element tuple of (name, action): the result of action is
#   recorded under name.
# - A list of tuples [(p, i), ...]: this is a conditional, but the
#   matching i is evaluated as an instruction, not a rule.  Again, no
#   predicate needs to return true.
#
# Finally, each action in a tuple instruction is one of the following.
# - A callable: this is called, and its value recorded under the
#   instruction's name.
# - A string: the corresponding attribute is recorded.
# - A single-element tuple (attr): the attribute is retrieved, its
#   type is inferred, the rule for this type evaluated for it and the
#   result recorded.
# - A two-element tuple (attr, type): the attribute is retrieved, the
# - rule for type is then evaluated for it and the result recorded.
#
#
# Callables are called with:
# - the thing being walked;
# - its dqtype, either inferred or provided;
# - the rules;
# - the dq object;
# - for_side_effect as a keyword argument;
# - any other keyword arguments passed down
#
fallback_ruleset = {None: ()} # just enough to run it

def walk_dq(dq, ruleset=None, for_side_effect=False, **kws):
    # walk the dq: this constructs the top of the tree, which is a
    # dict mapping from miptable to the names of the CMORvars that
    # refer to it.  If for_side_effect is true the walk is done purely
    # for side effect: no result is returned and no data structure is
    # built.  Any extra keyword arguments are passed down.
    if ruleset is None:
        ruleset = fallback_ruleset
    cmvs = sorted(dq.coll['CMORvar'].items,
                  cmp=lambda x,y: cmp(x.label, y.label))
    if not for_side_effect:
        return {table: {cmv.label: walk_thing(cmv, "CMORvar", ruleset, dq,
                                              **kws)
                        for cmv in cmvs if cmv.mipTable == table}
                for table in sorted(set(v.mipTable for v in cmvs))}
    else:
        for table in sorted(set(v.mipTable for v in cmvs)):
            for cmv in cmvs:
                if cmv.mipTable == table:
                    walk_thing(cmv, "CMORvar", ruleset, dq,
                               for_side_effect=True, **kws)

def walk_thing(thing, dqt, ruleset, dq, for_side_effect=False, **kws):
    # This is just a recursive descent parser for the rules for thing
    if dqt is None:
        dqt = dqtype(thing)

    result = {} if not for_side_effect else None

    def record(name, value):
        # record a value for a name
        if not for_side_effect:
            result[name] = value

    def eval_rule(rule):
        if callable(rule):
            # function: just return its result
            result = rule(thing, dqt, ruleset, dq,
                          for_side_effect=for_side_effect, **kws)
        elif isinstance(rule, list):
            # cond
            eval_cond(rule, eval_rule)
        elif isinstance(rule, tuple):
            # a sequence of instructions
            for instruction in rule:
                eval_instruction(instruction)
        else:
            # no other sorts of rules are legal
            raise MutantRule("{} makes no sense for {}: tuple syntax lossage?"
                             .format(rules, thing))

    def eval_cond(cond, continuation):
        # evaluate a cond clause [(p,v), ...], obviously inspired by
        # http://www-formal.stanford.edu/jmc/recursive.html.  It is
        # fine for no clauses to match
        for clause in cond:
            if not ((isinstance(clause, tuple) or isinstance(clause, list))
                    and len(clause) == 2):
                raise MutantRule("bogus cond clause {}".format(clause))
            (p, v) = clause
            if not callable(p):
                raise MutantRule("{} in {} is not callable".format(p, cond))
            if p(thing, dqt, ruleset, dq,
                 for_side_effect=for_side_effect, **kws):
                return continuation(v)

    def eval_instruction(instruction):
        if isinstance(instruction, str) or isinstance(instruction, unicode):
            # trivial instruction: record a field
            if hasattr(thing, instruction):
                record(instruction, getattr(thing, instruction))
            else:
                raise MissingAttribute("{} is missing  {}"
                                       .format(dqt, instruction))
        elif isinstance(instruction, tuple) and len(instruction) == 2:
            # record something under a name
            (name, action) = instruction
            if callable(action):
                record(name, action(thing, dqt, ruleset, dq,
                                    for_side_effect=for_side_effect, **kws))
            elif isinstance(action, str) or isinstance(action, unicode):
                # record a field under a different name
                if hasattr(thing, action):
                    record(name, getattr(thing, action))
                else:
                    raise MissingAttribute("{} is missing  {}"
                                           .format(dqt, action))
            elif isinstance(action, tuple):
                if len(action) == 1:
                    # recurse with implicit dqtype
                    record(name, walk_into(action[0], None))
                elif len(action) == 2:
                    # recurse with explicit dqtype
                    record(name, walk_into(action[0], action[1]))
                else:
                    raise MutantRule("mutant recursive instruction {}"
                                     .format(instruction))
            else:
                raise MutantRule("mutant compound instruction {}"
                                 .format(instruction))
        elif isinstance(instruction, list):
            eval_cond(instruction, eval_instruction)
        else:
            raise MutantRule("instruction {} is hopeless".format(instruction))

    def walk_into(child_attr, child_dqt):
        # Recurse.  Note that child_dqt may be None which means 'to be
        # inferred by walk_thing': nothing here even cares.  This
        # doesn't care about for_side_effect as it builds no structure
        # of its own, but just passes it down.
        if not hasattr(thing, child_attr):
            raise MissingAttribute( "{} is missing {}".format(dqt, child_attr))
        child_id = getattr(thing, child_attr)
        if child_id not in dq.inx.uid:
            raise BadLink("missing {}".format(child_id))
        child = dq.inx.uid[child_id]
        if validp(child):
            # OK recurse (note that child_dqt may be None: see above)
            return walk_thing(child, child_dqt, ruleset, dq,
                              for_side_effect=for_side_effect, **kws)
        else:
            # Leave a trace that the child was invalid
            return None

    # OK, go
    if dqt not in ruleset and None not in ruleset:
        raise MissingRule("no rule for {}".format(dqt))
    eval_rule(ruleset[dqt] if dqt in ruleset else ruleset[None])

    if not for_side_effect:
        return result
    else:
        return

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
                    # if it has a priority, add it if it is high
                    # enough. This is what he does: rounding?
                    if int(float(rl.opar)) > pri:
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
            else:
                # if it's a group of experiments they all must belong
                # to the same MIP I think, so this just picks the
                # first.  Otherwiwise assume it is an experiment itself
                expt = (dq.inx.uid[dq.inx.iref_by_sect[esid].a['experiment'][0]]
                        if dqt == 'exptgroup'
                        else dq.inx.uid[esid])
                if validp(expt):
                    exptdqt = dqtype(expt)
                    if exptdqt == 'experiment':
                        # just add its MIP
                        mips.add(expt.mip)
                    else:
                        raise BadDreq("{} isn't an experiment".format(exptdqt))

    return mips
