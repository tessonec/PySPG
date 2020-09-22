#!/usr/bin/env python3
# -*- coding: utf-8 -*-
version_number = "1.7.0"
release_date   = "Mon Jul 21 2008"
# :::~ Author: Claudio Juan Tessone <tessonec@imedea.uib.es> (c) 2002-2008
# Distributed According to GNU Generic Purpose License (GPL) version 2
# visit www.gnu.org
################################################################################
#
# Changelog
# 1.7.0 (21/07/08) added support for renaming of files
# 1.6.1 (05/02/08) added support for non exiting if file not found
# 1.6.1 (05/02/08) replaced getopt by tclap
# 1.6.0 (05/09/07) replaced getopt by tclap
# 1.5.1 (06/08/07) added helper output function
# 1.5.0 (06/08/07) added backend configuration support
# 1.3.0 (07/07/07) added conf.in support
# 1.2.3 (05/10/07) Added randomize
# 1.2.2 (05/10/07) Added column output
# 1.2.1 (05/09/07) Added support for changelog file
# 1.2.0 (05/08/10) Now, randomseed is incremental, better htmldoc
# 1.1.2 (03/10/15) Fixed randomseed behavior
# 1.1.1 (03/08/16) added "include" keyword
# 1.1   (03/08/07) Generates simple HTML documentation, added namespaces
# 1.0   (03/02/03) Generates C++ code for parsing a .ct file
#
#
################################################################################
#
# TODO LIST
# *   Add language support
# *** documentation of .ct files
# *** cleanup of python code (too messy) to make it easily extendable
# **  generate (Python?), Ansi C, (Java?) Code
#
################################################################################
#
allow_null_config = False

safeOperation = False

included_files=[]
import os.path
def search_for_includes(com):
  for l in com:
    if l[0]=="include":

      if os.path.abspath(l[1]) in included_files:
        print("[ctt - ERROR] '%s' already included in .ct file"%l[1])
        sys.exit(4)
      print("[ctt - MESSAGE] including: %s..."%l[1])
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
    print("//:::~ ",v[2])
    print("bool ",v[1],"= false ;")
    return
  else:
    print("//:::~ ",v[4])
  if v[1] != "string":
    print(v[1],v[2],"=",v[3],";")
  else:
    print("std::"+v[1],v[2],"=",v[3].split(",")[0],";")

def externdefinition(v):

  if v[0]=="flag":
    print("//:::~ ",v[2])
    print("extern bool ",v[1],"/* = ","false","*/",";")
    return
  else:
    print("//:::~ ",v[4])
  if v[1] != "string":
    print("extern ",v[1],v[2],"/* = ",v[3],"*/",";")
  else:
    print("extern std::"+v[1],v[2],"/* = ",v[3].split(",")[0],"*/ ;")

def help(v):
  if v[0] == "flag":
    print('   std::cerr << " '+v[1]+' := tipo bool "', end=' ')
    print(" << std::endl ;")
    print('   std::cerr << "--> '+v[2]+'"',"<< std::endl;")
    print('   std::cerr << "    Valor por defecto : false" << std::endl;', end=' ')
    return
  print('   std::cerr << "'+v[2]+' := tipo ',v[1],'"', end=' ')
  print(" << std::endl ;")
  if v[0] == "val":
    print('   std::cerr << "--> '+v[4]+'"',"<< std::endl;")
    print('   std::cerr << "    Valor por defecto : ' + v[3].replace('"','\\"')+'"', end=' ')

  if v[0] == "choice":
    print('   std::cerr << "--> '+v[4]+'"',"<< std::endl;")
    posValues=v[3].split(",")
    print('   std::cerr       << "    Possible values are: " << ','<< " " <<'.join([i   for i in posValues]), end=' ')
  print(" << std::endl ;")
  print()




def choice(v):
  if v[0]=="flag":
    print('  if (foo == "'+v[1]+'")')
    print("  {")
    print("     ", v[1], "=true;")
    print('      std::cerr << " +  {ctt - SETTING} " << "'+v[1]+' = true" << std::endl;')
    print("  }")
    return
  print('  if (foo == "'+v[2]+'")')
  print("  {")

  if v[0]=="val":
    print("    fin >> ", v[2], ";")
    print('      std::cerr << " +  {ctt - SETTING} " << "'+v[2]+' = " <<', v[2],' << std::endl;')

  if v[0]=="choice":
    posValues=v[3].split(",")
    print("    {")
    print("      fin >> ",v[2],";")
    choclo = ["("+v[2]+"!="+i+")" for i in posValues]
    print("      if ( ","&&".join(choclo),")")
    print("      {")
    print('        std::cerr << " +  {ctt - ERROR} \'" <<',v[2], end=' ')
    print(' << "\' not between possible values of '+v[2]+'"', " << std::endl;")
    print('        std::cerr << " +  {ctt - ERROR} Possible values are: " << ','<< " " <<'.join([i   for i in posValues]),' << std::endl;')
    print("        exit(EXIT_FAILURE);")
    print("      }")
    print("    }")
    print('    std::cerr << " +  {ctt - SETTING} " << "'+v[2]+' = " <<', v[2],' << std::endl;')

  print()
  print("  }")


def backendize(infile):
  fin = open(infile, "r")
  output = []
  ls_output = []
  for line in fin.readlines():
    if line.strip()[0] == "@":
      vec = line.strip()[1:].split()
      var_name_2 = ""
      try:
        backend = vec[0]
	try:
          var_name = vec[1]
        except:
	  var_name = ""
	try:
          var_name_2 = vec[2]
	except:
	  var_name_2 = ""
      except:
        sys.stderr.write("[ctt - ERROR] when unfolding line '%s'\n"%(line) )
        sys.exit()
      try:
        #print >> sys.stderr,var_name ,var_name_1 ,var_name_2
        new_stuff = [
                    i.replace("%ARG%",var_name).replace("%ARG1%",var_name).replace("%ARG2%",var_name_2)
                    for i in open( os.path.expanduser("~/opt/etc/ctt/%s.be"%backend), "r" ).readlines()
                  ]
      except:
        sys.stderr.write("[ctt - ERROR] when loading backend '%s' and variable '%s'\n"%(backend,var_name) )
        sys.exit()
      #print >> sys.stderr,new_stuff
      output.extend (new_stuff)
      ls_output.append( (backend, var_name, var_name_2)  )
    else:
      output.append(line)
  return ls_output,output




if __name__=="__main__":

   import getopt, sys

   import os.path

   useNamespaces=False
   createInit=False

   try:
        opts, args = getopt.getopt(sys.argv[1:], "nihvus")
   except getopt.GetoptError:
        # print help information and exit:
        print("[ctt - ERROR] unknown option")
        #print "[ctt - ERROR] Help and getopt not implemented yet! "
        sys.exit(2)

   if len(args)>1:
     print("[ctt - ERROR] can only parse once at a time")
     sys.exit(2)


   for o, a in opts:
        if o == "-u":
          allow_null_config = True
        if o == "-n":
          useNamespaces=True
        if o == "-i":
          createInit=True
        if o == "-v":
          print("This is %s, version: %s\nrelease date: %s"%(os.path.split(sys.argv[0])[1],version_number,release_date))
	  sys.exit()
        if o == "-h":
          print("Usage is %s [OPTIONS] base.ct"%os.path.split(sys.argv[0])[1])
	  print("  -d: creates documentation")
	  print("  -n: generates namespace inside de code")
          print("  -i: generates initialization routine ")
          print("  -u: allows nUll config files ")

	  sys.exit()

   fname=os.path.splitext(args[0])[0]

   ifname = "input.dat"

   release_date = '""'
   version      = '""'
   try:
     l1 = open("Changelog").readline().split()
     version      = '"%s"'%l1[1]
     release_date = '"%s"'%l1[3]

   except:
     sys.stderr.write("[ctt - WARNING] 'Changelog' file not found/bad permissions/could not parse it\n")
     sys.stderr.write("[ctt - WARNING] not setting release date, nor version\n")

   original_stdout=sys.stdout
   print("[ctt - MESSAGE] generating code from:",args[0],"...")
   backends,lineas= backendize(args[0])
#   print lineas
   comandos = [ linea.strip().split(":")
                 for linea in
                 lineas
                 if len(linea) > 1
               ];
   comandos.append(["val","long","randomseed","0","semilla de los numeros aleatorios"])
   included_files.append(os.path.abspath(args[0]))
   search_for_includes(comandos)

   sys.stdout=open(fname+".h","w")
   print("//:::~ ")
   print("//:::~ File automaticamente generado por",os.path.split(sys.argv[0])[1]," NO EDITAR")
   print("//:::~ ")
   print()
   print("#ifndef __CTTBASE_H")
   print("#define __CTTBASE_H")
   print("#include <cstdlib>")
   print("#include <string>")
   print("#include <iostream>")
   print("#include <ctime>")
   print("#include <sys/time.h>")
   #print "#include <sys/stat.h>"
   print("#include <fstream>")
   print('#include <dranxor.h>')

   print()

   includes = set()
   vars_from_be = []
   for backend, var_name, var_name_2 in backends:
 #    print backend
     for linea_h in open(os.path.expanduser("~/.pyspg/ctt/%s.be.h"%backend)):
       if "#include" in linea_h.strip():
         includes.add(linea_h.strip())
       else:
#         sys.stderr.write("%s\n"%linea_h.strip())
         vars_from_be.append(linea_h.strip().replace("%ARG%",var_name).replace("%ARG1%",var_name).replace("%ARG2%",var_name))

   print('//:::~ includes found in backends')
   for inc in includes:
      print(inc)
   print()
   print("#define VERSION_NUMBER %s"%version)
   print("#define RELEASE_DATE %s"%release_date)

   print()
   print()
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print("//:::~ Definiciones de las variables seteables desde el infile")
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print()
#   if useNamespaces:
   print("namespace CTGlobal")
   print("{")
   print()
#   print '  extern  long randomseed; /* = 0*/'
   print('  extern std::string filein /* = "%s" */ ;'%ifname)
   print()
   print('  extern std::string prog_name /*  */ ;')
   print()
   # print '  extern int verbosityLevel /* = 0*/;'
   # print '  extern bool quietRun /* = false*/;'
   print()
   for i in comandos:
     #print >> sys.stderr, i
     externdefinition(i)
   print()
   print("// from backends")
   for i in vars_from_be:
     if i.strip() != '':
       print("extern ",i.split("=")[0], ";")
   print()
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print("//:::~ Parse de las variables")
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print("void input_variables(std::istream &fin);")

   print()
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print("//:::~ Asking for output")
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print()
   print('void query_output(std::string type, std::string msg , std::string opening_closing = "<>",int indent=0);')
   print()
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print("//:::~ Small Help")
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print()
   print("void help_available();")
   if createInit:
     print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
     print("//:::~ Option reading")
     print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
     print("bool initialize_program(int &argc, char** & argv);")
#   if useNamespaces:
   print("};")
   print()
   print("#endif")
   print()
   sys.stdout.close()

   sys.stdout=open(fname+".cxx","w" )
   print("//:::~ ")
   print("//:::~ File automatically generated by", end=' ')
   print(os.path.basename( sys.argv[0] ), end=' ')
   print(" NO EDITAR")
   print("//:::~ ")
   print()
   # if createInit:
#     print '#include <util/ctgetopt.h>'
#      print '#include <tclap/CmdLine.h>'
   print('#include "%s.h"'%os.path.splitext( os.path.basename( fname ) )[0])
   print()
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print("//:::~ Definiciones de las variables seteables desde el infile")
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print()
#   if useNamespaces:
   print("namespace CTGlobal")
   print("{")
   print()
   print('  std::string filein = "%s";'%ifname)
   print()
   # print '  int verbosityLevel  = 0;'
   # print '  bool quietRun = false;'

   print('  std::string prog_name = "" ;')
   #   print '  long randomseed = 0;'
   print()
   for i in comandos:
     definition(i)
   print()
   print("// from backends")
   for i in vars_from_be:
     print(i)

   print()
#   if useNamespaces:
   print("};")
   print()
   print()
  # if useNamespaces:
   # print
   # print
   # if createInit:
   print("""//:::~ :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::""")
   print("""//:::::::::::::: OPTION READING (BEGIN) ::::::::::::::::::::::::::::::::::::::::""")
   print("""//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::""")
   print("""//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::""")
   print("""//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::""")
   print("bool CTGlobal::initialize_program(int &argc, char** & argv){")
   print(""" using namespace std;""")
     # print """ """
     # print """ 	  TCLAP::CmdLine cmd(string( " release date: ")+RELEASE_DATE, ' ', VERSION_NUMBER);"""
     # print
     # print """    TCLAP::ValueArg<string> nameArg("i","input","configuration input file name",false,filein,"string"); """
     # print """    cmd.add( nameArg );"""
     # print
     # print """    TCLAP::SwitchArg quietSwitch("q","quiet","Quietly runs the program", false);"""
     # print """    cmd.add( quietSwitch );"""
     # print
     # print """    TCLAP::MultiSwitchArg verboseMSwitch("v","verbose", "Increases verbosity level");"""
     # print """    cmd.add( verboseMSwitch );"""
   if os.path.exists("cmdline.pre"):
       for i in open("cmdline.pre"):
         print(i)
   print()
   print(" struct timeval tv;")
   print(" gettimeofday(&tv, NULL); ")
   print(" randomseed=tv.tv_usec;")
   print(" rt_rand_init(randomseed);")

   print("""    if (argc == 1){
                      return false;
                   }""")


     # print """ try {  """
     # print """    cmd.parse( argc, argv );"""
   print(""" filein = string(argv[1]);""")

   print(""" std::fstream * sin = new std::fstream( filein.c_str(), std::ios::in);""")

   print(""" if( !sin->fail() )""")
   print("""    input_variables(*sin);""")
   if not allow_null_config:
       print("""  else{""")
       print("""    std:: cerr << "< " << argv[0] << " - ERROR > " ;""")
       print("""    std::cerr << "could not read input from file '" << filein << "'"  << std::endl;""")
       print("""    exit( EXIT_FAILURE );""")
       print("""  } """)

   if os.path.exists("cmdline.post"):
       for i in open("cmdline.post"):
         print(i)


   print(""" return true;""")
   print("""} """)

   print()
  #    ####################### BACKENDS
  #  for backend, var_name, var_name_2 in backends:
  # #     print backend
  #      cxx_content = "".join(open(os.path.expanduser("~/opt/etc/ctt/%s.be.cxx"%backend)).readlines() ).replace("%ARG%",var_name).replace("%ARG1%",var_name).replace("%ARG2%",var_name_2)
  #      print cxx_content

   print()
   print("""//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::""")
   print("""//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::""")
   print("""//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::""")
   print("""//:::::::::::::: OPTION READING ( END ) ::::::::::::::::::::::::::::::::::::::::""")
   print("""//:::~ :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::""")

#     print "}"
   print()
   print("void CTGlobal::query_output(std::string type, std::string msg , std::string oc, int indent){")
   print('  for(int i=0;i<indent;i++) std::cerr << " ";')
   print('  std::cerr << oc[0] << " ";')
   print('  std::cerr << prog_name << " - "<< type << " ";')
   print('  std::cerr << oc[1] << " ";')
   print('  std::cerr << msg << std::endl;')
   print("}")
   print()
   print()
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print("//:::~ Parse de las variables")
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print()
   print("void CTGlobal::input_variables(std::istream &fin)")
   print("{")
   print()
   print(" struct timeval tv;")
   print(" gettimeofday(&tv, NULL); ")
   print(" randomseed=tv.tv_usec;")
   print(" rt_rand_init(randomseed);")
   print()
   print(" std::string foo;")
   print(" fin >> foo;")
   print(' while( (!fin.eof()) &&  (foo != "end") )')
   print(" {")
   print("    ")
   print("  if (", end=' ')
   valoresPosibles=[' (foo !="'+i[2]+'") ' for i in comandos if i[0]!="flag"]
   for i in comandos:
    if i[0]=="flag":
      valoresPosibles+=[' (foo !="'+i[1]+'") ']

   print("&&".join(valoresPosibles), end=' ')
   print(")")
   print("  {  ")
   print('    std::cerr << " +  {ctt - ERROR} command " <<  foo << " not understood";')
   print('    std::cerr << std::endl;')
   print("    exit(EXIT_FAILURE);")
   print("    ")
   print("    ")
   print("  }  ")
   for i in comandos:
     choice(i)
   print("  fin >> foo;")
   print(" }")
   print("  if(randomseed)")
#   print "    srand(randomseed);"
   print("    rt_rand_init(randomseed);")
   print("    ")
   # print "  else"
   # print "  {"
   # print "      struct timeval tv;"
   # print "     gettimeofday(&tv, NULL); "
   # print "    randomseed=tv.tv_usec;"
   # print "    rt_rand_init(randomseed);"
   # print "  }"
   print('  std::fstream frandom("random.seed",std::ios::app | std::ios::out );')
   print("  frandom << randomseed  << std::endl ;  ")
   print("  frandom.close();  ")
   #print "  std::cerr << std::endl;  "
   print("    ")

   print("}")

   print()
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print("//:::~ Pequegno Help")
   print("//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
   print()
   print("void CTGlobal::help_available()")
   print("{")
   print()
   print(" ")
   for i in comandos:
     help(i)
   print(" exit(EXIT_FAILURE);")
   print("}")
   print()

   sys.stdout.close()




