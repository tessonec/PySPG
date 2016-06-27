# put common definitions in here


BASEDIR         = $(HOME)/opt
LIBDIR          = $(BASEDIR)/lib/spg
BINDIR          = $(BASEDIR)/bin

.PHONY: clean all install


install:
	# scripts
	install scripts/spg-db.py ${BINDIR}
	install scripts/spg-run-standalone.py ${BINDIR}
	install scripts/spg-run-threaded.py ${BINDIR}
	install scripts/spg-table.py ${BINDIR}
	#library
	mkdir -p ${LIBDIR}
	install -D spg/*.py ${LIBDIR}
	install -d ${LIBDIR}/base
	install -D spg/base/*.py ${LIBDIR}/base
	install -d ${LIBDIR}/cmdline
	install -D spg/cmdline/*.py ${LIBDIR}/cmdline
	install -d ${LIBDIR}/master
	install -D spg/master/*.py ${LIBDIR}/master
	install -d ${LIBDIR}/simulation
	install -D spg/simulation/*.py ${LIBDIR}/simulation
	install -d ${LIBDIR}/runner
	install -D spg/runner/*.py ${LIBDIR}/runner
	install -d ${LIBDIR}/utils
	install -D spg/utils/*.py ${LIBDIR}/utils


