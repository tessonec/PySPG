#! /usr/bin/python
version_number = "1.4.9"
release_date   = "Fri 30 Nov 2007"
# :::~ Author: Claudio Juan Tessone <tessonec@imedea.uib.es> (c) 2002-2003
# Distributed According to GNU Generic Purpose License (GPL)
# Please visit www.gnu.org 
# based on ctt.py 1.2.2
################################################################################
#
# Changelog
#
# 1.4.9 (30/11/07) F90 code
# 1.0   (03/01/06) Generates Fortran code for parsing a .ct file
#
#
################################################################################
#
# TODO LIST
# *   code merge with ctt.py
# *** use of getopt in order to receive parameters from command-line arguments
#
################################################################################
#

included_files=[]
import os.path
def search_for_includes(com):
  for l in com:
    if l[0]=="include":

      if os.path.abspath(l[1]) in included_files:
        print "error!!!! %s already included in .ct file"%l[1]
        sys.exit(4)
      print "including: %s..."%l[1]
      included_files.append(os.path.abspath(l[1]))

      mascoms= [ linea.strip().split(":")
                 for linea in open(l[1],"r").readlines()
                 if len(linea) > 1
               ];
      com.remove(l)
      com+=mascoms
      search_for_includes(com)



def definition(v):
  if v[0]=="flag":
    print "!\t :::~ ",v[2]
    print "\t  LOGICAL :: %s = .FALSE."%v[1] 
    return

  if v[0]=="val":
   v[1] = v[1].lower()
   if v[1] == "string" or  "character" in v[1] :
    print "!\t :::~ ",v[4]
    print '\t  CHARACTER(LEN=80) :: %s = %s'%(v[2],v[3])
   if v[1] == "int"  or v[1] == "integer" :
    print "!\t :::~ ",v[4]
    print '\t  INTEGER :: %s = %s'%(v[2],v[3])
   if v[1] == "double"  or v[1] == "real*8" :
    print "!\t :::~ ",v[4]
    print '\t  REAL*8 :: %s= %s '%(v[2],v[3])
   if v[1] == "float" or v[1] == "real*4" :
    print "!\t :::~ ",v[4]
    print '\t  REAL*4 :: %s= %s '%(v[2],v[3])
   if v[1] == "bool" or v[1] == "boolean" or v[1] == "logical":
    print "!\t :::~ ",v[4]
    print '\t  LOGICAL :: %s= %s '%(v[2],v[3])

  if v[0]=="choice":
   if v[1] == "string" or  "character" in v[1] :
    print "!\t :::~ ",v[4]
    print '\t  CHARACTER(LEN=80) :: %s = %s'%(v[2],v[3].split(",")[0])
   if v[1] == "int"  or v[1] == "integer" :
    print "!\t :::~ ",v[4]
    print '\t  INTEGER :: %s = %s'%(v[2],v[3].split(",")[0])
   if v[1] == "double"  or v[1] == "real*8" :
    print "!\t :::~ ",v[4]
    print '\t  REAL*8 :: %s= %s '%(v[2],v[3].split(",")[0])
   if v[1] == "float" or v[1] == "real*4" :
    print "!\t :::~ ",v[4]
    print '\t  REAL*4 :: %s= %s '%(v[2],v[3].split(",")[0])
   if v[1] == "bool" or v[1] == "boolean" or v[1] == "logical":
    print "!\t :::~ ",v[4]
    print '\t  LOGICAL :: %s= %s '%(v[2],v[3].split(",")[0])


def initial_value(v):
  pass
  #if v[0]=="flag":
    #print "!\t :::~ ",v[2]
    #print "\t  %s =.FALSE. "%v[1] 
  #if v[0]=="val":
    #print "!\t :::~ ",v[4]
    #print '\t  %s=%s '%(v[2],v[3])
  #if v[0]=="choice":
    #print "!\t :::~ ",v[4]
    #print '\t  %s=%s '%(v[2],v[3].split(",")[0])




def choice(v):
  if v[0]=="flag":
    print '\t    IF ( FOOSTR .EQ. "'+v[1]+'") THEN'
    print "\t     read(FOOVAL,*)%s"%v[1]
    print "\t    ENDIF"
    print
    return
    
  if v[0]=="val":
      print '\t    IF ( FOOSTR .EQ. "'+v[2]+'" ) THEN'
      #print "\t    READ (74,end=1974,fmt=*)FOOVAL"
      print "\t     read(FOOVAL,*)%s"%v[2]
      print "\t    ENDIF"
      print
      return
  if v[0]=="choice":
    print '\t    IF ( FOOSTR .EQ. "'+v[2]+'" ) THEN'
    posValues=v[3].split(",")
    #print "\t    READ (74,end=1974,fmt=*)FOOVAL"

    choclo = [" ( FOOVAL .NE. "+i+" )  " for i in posValues]
    print "\t      IF (",".AND. & \n              ".join(choclo)," ) THEN "
    print '\t          write(0,*)" {PARSE - ERR} value not found:", FOOVAL,',
    print '" not possible '+v[2],'"'
    print '\t          write(0,*)"               possible values are: " '
    for i in posValues:
      print '\t        write(0,*),%s '%str(i)
    print "\t        EXIT"
    print "\t      ENDIF"
    print "\t     read(FOOVAL,*)%s"%v[2]

    print "\t    ENDIF"
    print


def print_val(v):
  if v[0]=="flag":
    print "!\t :::~ ",v[2]
    print '\t write(0,*)" {PARSE - MSG} %s =",%s '%(v[1] ,v[1] )
  else:
    print "!\t :::~ ",v[4]
    print '\t write(0,*)" {PARSE - MSG} %s =",%s '%(v[2] ,v[2] )




if __name__=="__main__":

   import getopt, sys

   import os.path

   try:
        opts, args = getopt.getopt(sys.argv[1:], "hv")
   except getopt.GetoptError:
        # print help information and exit:
        print "[CTTF - ERR] unknown option"
        print "[CTTF - ERR] help not implemented yet"
        sys.exit(2)

   if len(args)>1:
     print "[CTTF - ERR] only a file can be processed"
     sys.exit(2)


   for o, a in opts:
        if o == "-v":
          print "This is %s, version: %s\nrelease date: %s"%(os.path.split(sys.argv[0])[1],version_number,release_date)
	  sys.exit()
        if o == "-h":
          print "Usage is %s [OPTIONS] base.ct"%os.path.split(sys.argv[0])[1]
	  print "No "
	  sys.exit()

   original_stdout=sys.stdout
   print "[CTTF - MSG] generating code from:",args[0],"..."
   comandos = [ linea.strip().split(":")
                 for linea in
                 open(args[0],"r").readlines()
                 if len(linea) > 1
               ];
   import random

   comandos.append(["val","long","randomseed",str( random.randint(0,1000000000) ),"semilla de los numeros aleatorios"])
   included_files.append(os.path.abspath(args[0]))
   search_for_includes(comandos)

   fname=os.path.splitext(args[0])[0]



   sys.stdout=open(fname+".f90","w" )
   print "!     :::~ "
   print "!     :::~  File automatically generated by",os.path.split(sys.argv[0])[1]," NO EDITAR"
   print "!     :::~  "
   print
   print
   print '\t  MODULE INPUTVARS'
   print '\t  CHARACTER(LEN=80) :: FILEIN '
   print "\t  CHARACTER(LEN=80) :: BUFFER"
   print "\t  INTEGER :: randomseed = 324345345"
   print
   
   print
   #sys.stderr.write("common blocks/definitions list. Paste into fortran code, \n\n\n\n")
   for i in comandos:
     definition(i)
   print
   #sys.stderr.write('\n\t  INTEGER randomseed\n')
   print '\t  CHARACTER(LEN=80) FOOSTR, FOOVAL '
   #sys.stderr.write('\n\t  CHARACTER*50 FILEIN \n\n')
   lscoms=[i[2] for i in comandos if i[0]!="flag" and i[1]!="string" and  i[2]!="randomseed" ] + [i[1] for i in comandos if i[0]=="flag" ] 
#   sys.stderr.write(str(lscoms))
   #print '\t  COMMON/VARALL/%s'%",\n     +        ".join(lscoms)
   #sys.stderr.write('\t  COMMON/VARALL/%s\n'%",".join(lscoms))
   #print '\t  COMMON/RND/randomseed'
   #sys.stderr.write('\t  COMMON/RND/randomseed\n')
   
   lscoms=[i[2] for i in comandos if i[1]=="string" ]+["FILEIN"] 
   #print '\t  COMMON/VARSTRING/%s'%",\n     +        ".join(lscoms)
   #sys.stderr.write('\t  COMMON/VARSTRING/%s\n\n\n\n'%",".join(lscoms))
   

   #print "!     :::~  +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
   #print "!     :::~  initial values"
   #print "!     :::~  +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
   #print
   #print
   #for i in comandos:
     #initial_value(i)
   print "    CONTAINS     "
   print "    SUBROUTINE DOIT()     "
   print "!	 :::~  semilla de los numeros aleatorios"
   print "	  randomseed=SECNDS(0.0) "

   print "!       lee la command line. captura el valor del fichero de datos"

   print ' 	  CALL GETARG(1,BUFFER)'
   print ' 	  if ( BUFFER .EQ. "-i") then'
   print "               CALL GETARG(2,FILEIN)"
   print " 	  endif"
   print " 	"

   print "!	"
   print ' 	write(0,*)" {PARSE - MSG} reading:",FILEIN'
   print "!	end"
   print
   print
   print "!     :::~  +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
   print "!     :::~  Parse de las variables"
   print "!     :::~  +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
   print 
   print "\t  OPEN (UNIT = 74, FILE = FILEIN)"
   print "\t  DO WHILE (.TRUE.)"
   #print "\t    READ (74,end=1974,fmt=*)FOOSTR,FOOVAL"
   print "\t    READ (74,end=1974,fmt=*)FOOSTR,FOOVAL"
   print
   print "\t    IF (",
   valoresPosibles= ['(  FOOSTR .NE."'+i[2]+'"  )' for i in comandos if i[0]!="flag"] 
   for i in comandos:
    if i[0]=="flag":
      valoresPosibles+=['(  FOOSTR .NE."'+i[1]+'" )']

   print ".AND. & \n               ".join(valoresPosibles),
   print " )THEN"
   print '\t      PRINT*," {PARSE - MSG} key: ",FOOSTR," not found";'
   print "\t      CALL EXIT(0)"
   print "\t    ENDIF "
   print "    "
   for i in comandos:
     choice(i)

   print "\t  ENDDO"
   print "1974\t  CLOSE(74)"

   print
   print
   print "!     :::~  +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
   print "!     :::~  Prints the variables"
   print "!     :::~  +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
   for i in comandos:
     print_val(i)

   print "  END SUBROUTINE"
   print "  END MODULE "

   sys.stdout.close()
