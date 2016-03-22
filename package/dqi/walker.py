# A walker for the dreq
#

__all__ = ['MissingRule', 'MutantRule', 'MissingAttribute', 'BadLink',
           'walk_dq', 'walk_thing', 'walk_into', 'walk_linked',
           'dqtype', 'validp', 'mips_of_cmv']

from collections import defaultdict
from .low import Badness

# Things to think about.
#
# There are a lot of places where this knows about (documented)
# details of the data request object: in particular it knows about the
# various indices.  I thought about abstracting all of this away with
# accessor functions but I'm not actually sure it is helpful to do
# that.  It might become so if the language became richer: it might be
# useful to be able to say 'walk everyone which links to me' for
# instance.  However that probabably will not happen (in fact: that
# particular case has happened: see walk_linked below)
#

# Exceptions
#
# It would be good to classify these by whether they are bugs in the
# request, the rules or the code, but it is vague
#

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
# A ruleset is a dict which maps from the type of thing (dreq section)
# to a rule for that type.  There can also be a wildcard rule, whose
# type is None, and which matches any type if there is no more
# specific rule for that type.
#
# Each rule is one of the following.
# - A callable, which is called with v conventions (see below)
#   and which returns the result of the walk for this rule.
# - A list of tuples of two elements: [(p, r), ...]: this is a
#   conditional, and each p is called with v conventions in
#   turn until one returns true, when its r is used as the rule. It is
#   fine if none return true.
# - A tuple of instructions, each of which is processed in turn
#
# Each instruction is one of the following.
# - A string: that field is extracted and recorded in the dictionary
#   returned (a string instruction s is shorthand for a tuple of (s,
#   s): see actions below).
# - A two-element tuple of (name, action): the result of action is
#   recorded under name.
# - A list of tuples [(p, i), ...]: this is a conditional as before,
#   but the matching i is evaluated as an instruction, not a rule.
#   Again, no predicate needs to return true, and in this case nothing
#   at all is done for this instruction.
#
# Finally, each action in a tuple instruction is one of the following.
# - A callable: this is called (v convention), and its value recorded
#   under the instruction's name.
# - A string: the corresponding attribute is recorded.
# - A tuple (f, ...): f should be a callable and is called with f
#   conventions (see below) and its result is the value recorded.
# - a list of tuples which is a conditional, as before, the result
#   being None if no clause matches.
#
# There are two calling conventions depending on whether a callable is
# being used as a variable (v convention) or function (f convention):
#
# V convention arguments:
# - the thing being walked;
# - its dqtype, either inferred or provided;
# - the ruleset;
# - the dq object;
# - for_side_effect as a keyword argument;
# - any other keyword arguments passed down.
#
# F convention arguments:
# - a tuple consisting of the arguments to the function in the action,
#   so in (f, a, b), f gets (a, b) as its first argument;
# - the thing being walked;
# - its dqtype, either inferred or provided;
# - the ruleset;
# - the dq object;
# - for_side_effect as a keyword argument;
# - any other keyword arguments passed down
# F convention is the same as V convention but with an additional
# first argument.
#

# What the walker builds.
#
# walk_dq walks each CMORvar in the request. If not called for side
# effect it builds a structure which looks like
#
#  {mt: {cmv: (walk, ...), ...}, ...}
#
# In other words a dict mapping from mip table names to a dict mapping
# from CMORvar names to a tuple of the walks of all the CMORvars
# belonging to the mip table with that name.  We think there should
# only be one element in each tuple (so the tuple of (mip table name,
# CMORvar name) should uniquely identify a CMORvar, but this has not
# always been true and may not need to be true in fact.  An earlier
# version of this code built structures like
#
#  {mt: {cmv: walk, ...}, ...}
#
# which simply lost any duplicate CMORvar names: this at least does
# not do that.
#
# If called for side effect, walk_dq simply walks all the CMORvars.
#
# In both cases the order the walk happens in is undefined, but each
# CMORvar is walked only once.  (There used to be all sorts of
# spurious sorting, which was never needed and is now gone.)
#
# walk_thing normally constructs a dict mapping between
# instruction-name and result-of-instruction (see above), which may
# (and does in practice) happen recursively, via walk_into.  However
# in the case where the rule for a typeis a function, then it can
# actually construct anything at all.
#

def walk_dq(dq, ruleset={None: ()}, for_side_effect=False, **kws):
    # walk the dq: this constructs the top of the tree, which is a
    # dict mapping from miptable to the names of the CMORvars that
    # refer to it.  If for_side_effect is true the walk is done purely
    # for side effect: no result is returned and no data structure is
    # built.  Any extra keyword arguments are passed down.
    #
    # The ruleset {None: ()} is what you need to minimally run the
    # walker.
    if not for_side_effect:
        results = defaultdict(lambda: defaultdict(list))
        for cmv in dq.coll['CMORvar'].items:
            results[cmv.mipTable][cmv.label].append(
                walk_thing(cmv, "CMORvar", ruleset, dq,
                           for_side_effect=False, **kws))
        return {mt: {name: tuple(walks)
                      for (name, walks) in mt_cmvs.iteritems()}
                for (mt, mt_cmvs) in results.iteritems()}
    else:
        for cmv in dq.coll['CMORvar'].items:
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

    def eval_cond(cond, continuation, fallback_continuation=None):
        # evaluate a conditional [(p, v), ...], obviously inspired by
        # http://www-formal.stanford.edu/jmc/recursive.html.  It is
        # fine for no clauses to match: the fallback is called in that
        # case if it is defined.
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
        if fallback_continuation:
            return fallback_continuation()

    def eval_instruction(instruction):
        if isinstance(instruction, str) or isinstance(instruction, unicode):
            # trivial instruction: record a field
            record(instruction, eval_action(instruction))
        elif isinstance(instruction, tuple) and len(instruction) == 2:
            record(instruction[0], eval_action(instruction[1]))
        elif issinstance(instruction, list):
            eval_cond(instruction, eval_instruction)
        else:
            raise MutantRule("instruction {} is hopeless".format(instruction))

    def eval_action(action):
        # Finally do something.  This is unlike the other eval_*
        # functions as it returns a useful value which is stored by
        # eval_instruction rather than doing its own recording.
        if callable(action):
            return action(thing, dqt, ruleset, dq,
                          for_side_effect=for_side_effect, **kws)
        elif isinstance(action, str) or isinstance(action, unicode):
            if hasattr(thing, action):
                return getattr(thing, action)
            else:
                raise MissingAttribute("{} is missing  {}".format(dqt, action))
        elif isinstance(action, tuple) and len(action) >= 1:
            (f, args) = (action[0], action[1:])
            if callable(f):
                return f(args, thing, dqt, ruleset, dq,
                         for_side_effect=for_side_effect, **kws)
            else:
                raise MutantRule("no callable in {}".format(action))
        elif isinstance(action, list):
            return eval_cond(action, eval_action, lambda: None)
        else:
            raise MutantRule("mutant action {}".format(action))

    # OK, go
    if dqt not in ruleset and None not in ruleset:
        raise MissingRule("no rule for {}".format(dqt))
    eval_rule(ruleset[dqt] if dqt in ruleset else ruleset[None])

    if not for_side_effect:
        return result
    else:
        return

def walk_into(args, thing, dqt, ruleset, dq, for_side_effect=False, **kws):
    # F convention walker to walk into a slot
    if not 1 <= len(args) <= 2:
        raise MutantRule("walk_into needs one or two arguments")
    child_attr = args[0]
    child_dqt = args[1] if len(args) == 2 else None
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

def walk_linked(args, thing, dqt, ruleset, dq, for_side_effect=False, **kws):
    # F convention walker to walk elements which link to this one,
    # returning a tuple.  If no args are given walk all sections as
    # their normal types; if one, walk single section as its own
    # dqtype; if two, then if the first is not None walk that section
    # with the type given by the second argument, and if the first is
    # None walk all sections with the type given by the second
    # argument.

    def walk_all(as_type=None):
        # walk all sections, optionally with a type (note that
        # walk_thing defaults types given as None to be right).
        #
        # Martin's description implies that dq.inx.iref_by_uid returns
        # tuples of (section, identifier): it doesn't, it returns
        # (linking_field_name, identifier).
        linked = (link for link in (dq.inx.uid[l[1]]
                                    for l in dq.inx.iref_by_uid[thing.uid])
                  if validp(link))
        if not for_side_effect:
            return tuple(walk_thing(link, as_type, ruleset, dq,
                                    for_side_effect=False, **kws)
                         for link in linked)
        else:
            for link in linked:
                walk_thing(link, as_type, ruleset, dq,
                           for_side_effect=True, **kws)

    def walk_sect(sect, as_type=None):
        # walk one section
        sects = dq.inx.iref_by_sect[thing.uid].a
        if sect in sects:
            linked = (link for link in (dq.inx.uid[l] for l in sects[sect])
                      if validp(link))
            if not for_side_effect:
                return (tuple(walk_thing(link, as_type, ruleset, dq,
                                         for_side_effect=False, **kws)
                              for link in linked))
            else:
                for link in linked:
                    walk_thing(link, as_type, ruleset, dq,
                               for_side_effect=True, **kws)
        else:
            return None

    if len(args) == 0:
        return walk_all(None)
    elif len(args) == 1:
        return walk_sect(args[0], args[0])
    elif len(args) == 2:
        if args[0] is None:
            return walk_all(args[1])
        else:
            return walk_sect(args[0], args[1])
    else:
        raise MutantRule("walk_linked: need 0-2 args but got {}?"
                         .format(args))

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
