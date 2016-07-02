# put common definitions in here

TARGET          = random-walk

CONFIGFILE      = 

BASEDIR         = $(HOME)/opt
CPP             = g++
CPPFLAGS        = -O2
FORTRAN         = gfortran
CC              = gcc
LD              = g++
CTT             = ~/opt/bin/ctt.py
LDFLAGS         = -L${BASEDIR}/lib -lm -ldranxor
RM              = rm
SHELL           = /bin/bash
INCLUDES        = -I${BASEDIR}/include
EXEEXT          = .p4
EXEPREFIX       = ctx-
OBJS            = base.o main.o 

.PHONY: clean all install



all:  ${EXEPREFIX}${TARGET}${EXEEXT}


${EXEPREFIX}${TARGET}${EXEEXT}: ${OBJS}
	${LD} ${OBJS} -o $@ ${CPPFLAGS} ${LDFLAGS}

%.o : %.cxx
	${CPP} ${INCLUDES} ${CPPFLAGS} -c $<

base.o : ${EXEPREFIX}${TARGET}.cxx
	${CPP} ${INCLUDES} ${CPPFLAGS}  -c -o base.o ${EXEPREFIX}${TARGET}.cxx

%.cxx : %.ct
	${CTT} -n -i $<

clean:
	${RM} -f *.o ${EXEPREFIX}*${EXEEXT}

