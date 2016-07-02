# put common definitions in here

# Default, $HOME directory
CONFDIR         = $(HOME)/.pyspg
# Replace for this in case of global installation
BASEDIR         = ~/opt
#BASEDIR         = /opt
LIBDIR          = $(BASEDIR)/lib/
BINDIR          = $(BASEDIR)/bin/

.PHONY: clean all install


install:
	install -d ${CONFDIR}/etc/ctt
	install -d ${BINDIR}
	install -d ${LIBDIR}
	cp scripts/spg-*.py ${BINDIR}
	cp contrib/ctt.py ${BINDIR}
	cp -R spg ${LIBDIR}
	cp -R skeleton/etc/ctt ${BASEDIR}/etc
