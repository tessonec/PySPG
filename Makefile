# put common definitions in here


BASEDIR         = $(HOME)/opt
LIBDIR          = $(BASEDIR)/lib/
BINDIR          = $(BASEDIR)/bin/

.PHONY: clean all install


install:
	install -d ${BINDIR}
	install -d ${BASEDIR}/etc
	install -d ${LIBDIR}
	cp scripts/spg-*.py ${BINDIR}
	cp -R spg ${LIBDIR}
	cp -R skeleton/etc/ctt ${BASEDIR}/etc
