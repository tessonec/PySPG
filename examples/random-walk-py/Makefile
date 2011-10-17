# put common definitions in here


BASEDIR         = $(HOME)/opt
LIBDIR          = $(BASEDIR)/lib/spg
BINDIR          = $(BASEDIR)/bin
CONFDIR         = $(BASEDIR)/etc/spg-conf

.PHONY: clean all install

SCRIPT_NAME=random-walk

install:
	# scripts
	install cts-${SCRIPT_NAME}.py ${BINDIR}/
	install -m 0644 base.ct ${CONFDIR}/${SCRIPT_NAME}.ct
	install -m 0644 conf.stdout ${CONFDIR}/${SCRIPT_NAME}.stdout
	install -m 0644 conf.params ${CONFDIR}/${SCRIPT_NAME}.params
	install -m 0644 conf.in ${CONFDIR}/${SCRIPT_NAME}.in
