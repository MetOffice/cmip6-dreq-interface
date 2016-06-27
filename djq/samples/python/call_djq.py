#!/usr/bin/env python
# -*- mode: Python -*-
#

"""Call djq
"""

from subprocess import Popen, PIPE
from json import dumps, loads
from pprint import pprint

def djq_from_structure(json, cmd="djq", options=()):
    argv = [cmd]
    argv.extend(options)
    p = Popen(argv, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (result, noise) = p.communicate(dumps(json))
    if p.returncode != 0:
        raise Exception("Badness: {} (exit {})".format(noise, p.returncode))
    return loads(result)

if __name__ == '__main__':
    sample = [{'dreq': 'latest',
               'mip': 'DECK',
               'experiment': 'control'}]
    result = djq_from_structure(sample)
    pprint(result)
