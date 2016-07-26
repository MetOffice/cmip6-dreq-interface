# This is just a bunch of shorthands
#

.PHONY: default install develop test clean veryclean ready recent

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
	find . -type f -name '*.pyc' -print0 | xargs -0 -r rm

veryclean: clean
	find . -type f -name '*~' -print0 | xargs -0 -r rm

test: clean
	nosetests

# clean and test before installing, just clean before installing for
# development
#

install: clean test
	$(PYTHON) setup.py install

develop: clean
	$(PYTHON) setup.py develop
