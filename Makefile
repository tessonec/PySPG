# put common definitions in here


BASEDIR         = $(HOME)/opt

.PHONY: clean all install


install:
	# scripts
	install scripts/spg-db.py ${BASEDIR}/bin
	install scripts/spg-run.py ${BASEDIR}/bin
	install scripts/spg-cmd.py ${BASEDIR}/bin
	install scripts/spg-master.py ${BASEDIR}/bin
	install scripts/spg-worker.py ${BASEDIR}/bin
	install scripts/spg-results.py ${BASEDIR}/bin
	# library (base)
	install -m 0644 spg/__init__.py ${BASEDIR}/lib/spg
	install -m 0644 spg/utils.py ${BASEDIR}/lib/spg
	install -m 0644 spg/base/__init__.py ${BASEDIR}/lib/spg/base
	install -m 0644 spg/base/iterator.py ${BASEDIR}/lib/spg/base
	install -m 0644 spg/base/parser.py ${BASEDIR}/lib/spg/base
	install -m 0644 spg/base/checks.py ${BASEDIR}/lib/spg/base
	# library (parameter)
	install -m 0644 spg/parameter/__init__.py ${BASEDIR}/lib/parameter
	install -m 0644 spg/parameter/atom.py ${BASEDIR}/lib/parameter
	install -m 0644 spg/parameter/ensemble.py ${BASEDIR}/lib/parameter
	install -m 0644 spg/parameter/db.py ${BASEDIR}/lib/parameter
	# library (pool)
	install -m 0644 spg/pool/__init__.py ${BASEDIR}/lib/spg/pool
	install -m 0644 spg/pool/exchange.py ${BASEDIR}/lib/spg/pool
	install -m 0644 spg/pool/process.py ${BASEDIR}/lib/spg/pool


