# This is just a bunch of shorthands
#
# ready & recent mean you can use garmr to watch things
#

.PHONY: default install develop clean ready recent

PYTHON=python

default: ready

ready:
	@git status

recent:
	@git --no-pager log -20 --format="%h / %an / %ar / %s%d"

clean:
	find . -type f -name '*.pyc' -print0 | xargs -0 -r rm
	find . -type f -name '*~' -print0 | xargs -0 -r rm

install:
	$(PYTHON) setup.py install

develop:
	$(PYTHON) setup.py develop
