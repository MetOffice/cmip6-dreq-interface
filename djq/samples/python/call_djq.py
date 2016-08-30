#!/usr/bin/env python -
# -*- mode: Python -*-
#
# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
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
        raise Exception(noise)
    return loads(result)

if __name__ == '__main__':
    try:
        sample = [{'dreq': 'latest',
                   'mip': 'DECK',
                   'experiment': 'control'}]
        result = djq_from_structure(sample)
        pprint(result)
    except Exception as e:
        exit(e)
