#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, re
import os.path
import copy
from math import *


import utils

CONFIG_DIR = os.path.expanduser("~/opt/etc")


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
#  ls_output = []
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
#        ls_output.append( (backend, var_name)  )
    else:
        output.append(line)
#  utils.newline_msg( "INF", "%s --> %s"%(ls_output,output) )
  ret = {}
  for l in output:
      l = [ i.strip() for i in l.split(":")]
      family = l[0]
      if family == "flag":
          var_type = None
          var_name = l[1]
          default = False
      else:
          var_type = l[1]
          var_name = l[2]
          default = l[3]
          if family == "choice":
              default = [ i.strip('"') for i in  default.split(",") ]
      ret[ var_name ] = ( family, var_type, default )

  return ret



def check_consistency(exec_file, miparser):
  consistent_param=True
  
  if exec_file[:4] == "ctx-":  exec_file = exec_file[4:]

  exec_file, ext = os.path.splitext(exec_file)

  possible_lines = backendize("%s/spg-conf/%s.ct"%(CONFIG_DIR,exec_file))

#  print miparser.items(), possible_lines.keys()
  assert len(set(miparser.items() ) - set( possible_lines.keys() ) ) == 0 , "not all the variables are recognised: offending vars: %s"%(set( miparser.items() ) -set( possible_lines.keys() )  )


  for el in miparser.data:
      
      it = copy.copy( el )
#      print it.name, " ", 
      family, var_type, default = possible_lines[it.name]
      values = [ i for i in it ]
      if len(values) == 0:
          values = it.data
#      print it.name, values
      for val in values:
#          print it.name, val, family, var_type, default
          # print val, default
          if family == "flag" : 
              utils.newline_msg("VAL", "flag can not contain a value")
          elif family == "choice" and str(val) not in default: 
              utils.newline_msg("VAL", "choice value '%s' not recognised: possible values: %s"%(val, default))
              consistent_param = False
          elif var_type in set(["float","double"]): 
              try: 
                  float(val) 
              except:
                  utils.newline_msg("VAL", "wrong type for '%s' expected '%s' "%(it.name, var_type))
                  consistent_param = False
          elif var_type in set(["int","unsigned", "long int", "long"]): 
              try: 
                  int(val) 
              except:
                  utils.newline_msg("VAL", "wrong type for '%s' expected '%s' "%(it.name, var_type))
                  consistent_param = False
          elif var_type == "string":
              try: 
                  str(val) 
              except:
                  utils.newline_msg("VAL", "wrong type for '%s' expected '%s' "%(it.name, var_type))
                  consistent_param = False

 

  return consistent_param






  
def contents_in_output(exec_file):
   """
     keysColumns = ["type","label","help","scale","repeat"]
     the structure of the columns in the files are as follows:
     name of the variable, and a colon separated list of -optional- options
     type:  of the plot if xy, one column is used, xydy two columns are used
     label: to be used in the plotting script
     scale: comma separated list of minimum and maximum values 
     repeat: how many columns are to be taken by the parser
     help: a string containing an explanation of the variable
   """
   possible_keys = set(["type","label","help","scale","repeat"])
   if exec_file[:4] == "ctx-":  exec_file = exec_file[4:]
   ret = []
   exec_file,ext=os.path.splitext(exec_file)

   cfgFile = "%s/spg-conf/%s.stdout"%(CONFIG_DIR,exec_file)
   for line in open(cfgFile):
       if len(line.strip()) == 0: continue
       l = [ i.strip() for i in line.split(":")]
       
       name = l[0]
       values = {"type":"xy"}
       for o in l[1:]:
           k,v = o.split("=")
           k=k.strip()
           v=v.strip()
           
           if k not in possible_keys:
               utils.newline_msg("SYN","in column '%s', unrecognised key '%s'"%(name,k))
               sys.exit(1)
           values[k]=v
       ret.append((name,values))    
       
   return ret 