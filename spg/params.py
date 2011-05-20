#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, re, os.path
from math import *

CONFIG_DIR = os.path.expanduser("~/opt/etc/")


def parameter_guess(string):
    #fp = string # os.path.abspath(string)
    regexp = re.compile(r'([a-zA-Z]\w+)-([-+]?\d*\.?\d*){1,1}([Ee][+-]?\d+)?')
    # regular expression explanation
    # r'([a-zA-Z]\w+)' matches variable name: 
    #     :::~ begins with a letter, any combination of letters, numbers and undezrscores
    # r'-' matches separator: minus sign
    # r'([-+]?\d*\.?\d*){1,1}'
    #     :::~ decimal part
    # r'([Ee][+-]?\d+)?'
    #     :::~ exponent
    ret = {}
    for var, dec, exp in regexp.findall(string):
        if "" not in [var,dec]:
            try:
                ret[var] = int(dec+exp)
            except:
                ret[var] = float(dec+exp)
    return ret


def string_evaluator(string,val_dict):
    #fp = string # os.path.abspath(string)
    rx = re.compile(r'\{([a-zA-Z]\w*)\}')
    # regular expression explanation
    # r'\{(\w)\}' matches variable name: 

    #vars = set()
    st_out = string
    for i_var in rx.findall(string):
        #vars.add(i)
        st_out = re.sub( r'\{%s\}'%i_var, str(val_dict[i_var]), st_out )
        #print st_out
    return eval(st_out)

def get_variables(string):
    #fp = string # os.path.abspath(string)
    rx = re.compile(r'\{([a-zA-Z]\w*)\}')
    # regular expression explanation
    # r'\{(\w)\}' matches variable name: 

    return rx.findall(string)


def generate_string(values, var_list, separator = "-", joining_string = "_"):
    """
      joining_string::: is the string between consecutive key,value pairs
      separator     ::: is the string separating the key, value pair
    """
    of = joining_string.join([ "%s%s%s"%(k,separator,values[k]) for k in var_list ] ) 

    return of



#d = {'x':pi,'y_3':1}

#v = string_evaluator("exp({x}+{y_3})",d)
#print get_variables("exp({x}+{y_3})",d)
##st='/home/tessonec/running/alpha_max_20312_3424-0.5_size-100/beta-324.3242_gamma--90.2E-4.234_fjs-1E-4.dat'

#print st
#print parameterGuess(st)







def backendize(infile):
  output = []
  ls_output = []
  for line in open(infile):
    if line.strip()[0] == "@":
        vec = line.strip()[1:].split()
        try:
            backend = vec[0]
            try:
                var_name = vec[1]
            except:
                var_name = ""
        except:
            newline_msg("ERR", "while unfolding line: '%s'"%(line) )
            sys.exit()
#      try:
        new_stuff = [
                i.replace("%ARG%",var_name).replace("%ARG1%",var_name)
                for i in open( "%s/ctt/%s.be"%(CONFIG_DIR ,backend), "r" )
              ]
#      except:
#        sys.stderr.write("[ctt - ERROR] when loading backend '%s' and variable '%s'\n"%(backend,var_name) )
#        sys.exit()
#      print new_stuff
        output.extend (new_stuff)
        ls_output.append( (backend, var_name)  )
    else:
        output.append(line)
 # print ls_output,output
  return ls_output,output




#:::~################################################################
#:::~ (BEGIN) checks consistency of param.dat
def check_consistency(exec_file, lines):
  consistentParam=True

  if exec_file[:4] == "ctx-": exec_file[4:]

  exec_file=exec_file[:exec_file.rfind(.)]

  lk=[]
  dk={}
  backends,lineas= backendize("%s/etc/ct-simul/%s.ct"%(CONFIG_DIR,exec_file))
  comandos = [ linea.strip()
                 for linea in
                 lineas
                 if len(linea.strip()) > 0
               ]

  for linea in comandos:
    content = [i.strip() for i in linea.split(":")]
    tipo = content[0]
    if tipo=="flag":
      dk[ content[1] ]=  (tipo, None,None)
      lk.append( content[1] )
    else:
      lk.append( content[2] )

      dk[ content[2] ]=  (tipo, content[1], content[3] )
  consistentFile = True
  for linea in lines:
    pp=ParamParser([linea])
    varName = pp.entities[0]
    iterator = pp.iterator_list[0]
    print "found variable: '%s' - "%varName,

    if isinstance(iterator,ParamIterators.ItConstant):
      print "values: ",iterator.data[0]
    if isinstance(iterator,ParamIterators.ItPunctual):
      print "values: ",iterator.data
    if isinstance(iterator, (ParamIterators.ItOperatorProduct,ParamIterators.ItOperatorPlus,
		    ParamIterators.ItOperatorMinus,ParamIterators.ItOperatorDivision,ParamIterators.ItOperatorPower)):
      print "values: #%d, [%s,%s] "%(len(iterator.data), iterator.data[0],iterator.data[-1])

    if varName in lk:
      print "  Ok! variable name"
      cttVar, typeVar,valueVar= dk[varName]
      if cttVar == "flag":
	if iterator.data > [""]:
          print "  Error! flag variable expected (cannot receive value)"
          consistentFile = False
      if cttVar == "choice":
	valV = [ i.strip(""" '" """) for i in valueVar.strip().split(",")]
	ok=True
	for iii in iterator.data:
	  if iii not in valV:
	    ok=False
	    consistentFile=False
	if not ok:
	  print "  Error! value assigned to choice is not valid. Expected among: ",valV
    else:
      consistentFile = False
      if not dummyRun:
	print "--> not known! exiting!!!"
	sys.exit(1)
      else:
	print " <---ERROR IN THIS LINE"

  if not consistentFile :
    print "Consistency check failed."
    sys.exit(2)
  else:
    print "Consistency check success.\n\n\n\n"
  if dummyRun:
    sys.exit(2)
#:::~ (END)   checks consistency of param.dat
#:::~################################################################
