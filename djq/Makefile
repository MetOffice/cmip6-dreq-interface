# (C) British Crown Copyright 2016, Met Office.
# See LICENSE.md in the top directory for license details.
#

# This is just a bunch of shorthands
#

.PHONY: default install develop clean veryclean ready recent\
	test compare sanity

PYTHON=python

default: ready

# ready & recent mean you can use garmr to watch things
#

ready:
	@git status

recent:
	@git --no-pager log -20 --format="%h / %an / %ar / %s%d"

# clean just nukes compiled things and should be safe, veryclean
# cleans up backups which might not be.
#

clean:
	find . -type f -name '*.pyc' -print0 | xargs -0 rm -f

veryclean: clean
	find . -type f -name '*~' -print0 | xargs -0 rm -f

test: clean
	nosetests

compare: clean
	@$(MAKE) -C comparisons compare

sanity: test compare


# clean before installing or installing for development
#

install: clean
	$(PYTHON) setup.py install

develop: clean
	$(PYTHON) setup.py develop
