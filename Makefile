# put common definitions in here


BASEDIR         = $(HOME)/opt

.PHONY: clean all install



install:
	install scripts/spg-init.py ${BASEDIR}/bin
	install scripts/spg-run.py ${BASEDIR}/bin
	install -m 0644 spg/__init__.py ${BASEDIR}/lib/spg
	install -m 0644 spg/iterator.py ${BASEDIR}/lib/spg
	install -m 0644 spg/load.py ${BASEDIR}/lib/spg
	install -m 0644 spg/params.py ${BASEDIR}/lib/spg
	install -m 0644 spg/parser.py ${BASEDIR}/lib/spg
	install -m 0644 spg/utils.py ${BASEDIR}/lib/spg


