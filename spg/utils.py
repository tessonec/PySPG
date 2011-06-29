#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re, os, os.path
from math import *


def replace_list(list_of_vars, dict_of_values, separator = "_"):
     """
       defines how the actual value of the parameter set is printed out.
       A good candidate to be overwritten in inheriting classes.
     """

     thisstr = separator.join( [
                         "%s%s%s"%(k,"-",dict_of_values[k] )
                         for k in list_of_vars if k
                     ] )

     return thisstr



def replace_string(sss,dict_of_values):
     thisstr=str(sss)
     for varname in dict_of_values.keys():
        
        thisstr=thisstr.replace(
                   "{{%s}}"%varname,
                   "%s"%( dict_of_values[varname] )
                )
        thisstr=thisstr.replace(
                   "{%s}"%varname,
                   "%s-%s"%( varname, dict_of_values[varname] )
                )
     return thisstr



def parameter_guess(string):
      #fp = string # os.path.abspath(string)
      regexp = re.compile(r'([a-zA-Z]\w*)-([-+]?\d*\.?\d*){1,1}([Ee][+-]?\d+)?')
      # regular expression explanation
      # r'([a-zA-Z]\w+)' matches variable name: 
      #     :::~ begins with a letter, any combination of letters, numbers and underscores
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

#d = {'x':pi,'y_3':1}

#v = string_evaluator("exp({x}+{y_3})",d)
#print get_variables("exp({x}+{y_3})",d)
##st='/home/tessonec/running/alpha_max_20312_3424-0.5_size-100/beta-324.3242_gamma--90.2E-4.234_fjs-1E-4.dat'

#print st
#print parameterGuess(st)

#########################################################################################
#########################################################################################
def inline_msg( type, msg, indent = 0 ):
  print >> sys.stderr, "%s[%s - %5s ] %s...\r"%(" "*indent, os.path.split(sys.argv[0])[1], type, msg),
  sys.stderr.flush()

def newline_msg( type, msg, indent = 0 ):
  print >> sys.stderr, "%s[%s - %5s ] %s"%(" "*indent, os.path.split(sys.argv[0])[1], type, msg)
  sys.stderr.flush()
#########################################################################################
#########################################################################################



