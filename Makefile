# put common definitions in here


BASEDIR         = $(HOME)/opt
LIBDIR          = $(BASEDIR)/lib/spg
BINDIR          = $(BASEDIR)/bin

.PHONY: clean all install


install:
	# scripts
	install scripts/spg-db.py ${BINDIR}
	install scripts/spg-queue.py ${BINDIR}
	install scripts/spg-run.py ${BINDIR}
	install scripts/spg-master.py ${BINDIR}
	install scripts/spg-worker.py ${BINDIR}
	install scripts/spg-results.py ${BINDIR}
	install scripts/spg-get_parameters.py ${BINDIR}
	mkdir -p ${LIBDIR}
	# library (base)
	install -m 0644 spg/__init__.py ${LIBDIR}
	mkdir -p ${LIBDIR}/base
	install -m 0644 spg/base/__init__.py ${LIBDIR}/base
	install -m 0644 spg/base/iterator.py ${LIBDIR}/base
	install -m 0644 spg/base/parser.py ${LIBDIR}/base
	# library (master)
	mkdir -p ${LIBDIR}/cmdline
	install -m 0644 spg/cmdline/__init__.py ${LIBDIR}/cmdline
	install -m 0644 spg/cmdline/ensembledb.py ${LIBDIR}/cmdline
	mkdir -p ${LIBDIR}/master
	install -m 0644 spg/master/__init__.py ${LIBDIR}/master
	install -m 0644 spg/master/exchange.py ${LIBDIR}/master
	install -m 0644 spg/master/masterdb.py ${LIBDIR}/master
	# library (parameter)
	mkdir -p ${LIBDIR}/parameter
	install -m 0644 spg/parameter/__init__.py ${LIBDIR}/parameter
	install -m 0644 spg/parameter/atom.py ${LIBDIR}/parameter
	install -m 0644 spg/parameter/ensemble.py ${LIBDIR}/parameter
	install -m 0644 spg/parameter/paramdb.py ${LIBDIR}/parameter
	# library (plot)
	mkdir -p ${LIBDIR}/plot
	install -m 0644 spg/plot/__init__.py ${LIBDIR}/plot
	install -m 0644 spg/plot/grace.py ${LIBDIR}/plot
	install -m 0644 spg/plot/spgpyplot.py ${LIBDIR}/plot
	install -m 0644 spg/plot/base.py ${LIBDIR}/plot
	# library (queue)
	mkdir -p ${LIBDIR}/queue
	install -m 0644 spg/queue/__init__.py ${LIBDIR}/queue
	install -m 0644 spg/queue/base.py ${LIBDIR}/queue
	install -m 0644 spg/queue/base.py ${LIBDIR}/queue
	install -m 0644 spg/queue/tools.py ${LIBDIR}/queue
	install -m 0644 spg/queue/torque.py ${LIBDIR}/queue
	# library (utils)
	mkdir -p ${LIBDIR}/utils
	install -m 0644 spg/utils/__init__.py ${LIBDIR}/utils
	install -m 0644 spg/utils/load_configs.py ${LIBDIR}/utils
	install -m 0644 spg/utils/check_params.py ${LIBDIR}/utils
	install -m 0644 spg/utils/tools.py ${LIBDIR}/utils


