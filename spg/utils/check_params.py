#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
import copy
import optparse
#from math import *

from .load_configs import *

from spg import CONFIG_DIR

from .tools import newline_msg, evaluate_string


############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################


def consistency(exec_file, miparser):
    """ Checks the consistency of a spg simulation file """
    consistent_param=True
  
    # if exec_file[:2] == "ct" and exec_file[3] == "-" :  exec_file = exec_file[4:]

    exec_file, ext = os.path.splitext(exec_file)

    try:
        possible_lines = read_input_configuration("%s.input" % (exec_file))
    except:
        possible_lines = read_input_configuration("%s/spg-conf/%s.input" % (CONFIG_DIR, exec_file))

    assert len(set(miparser.items() ) - set( possible_lines.keys() ) ) == 0 , "not all the variables are recognised: offending vars: %s"%(set( miparser.items() ) -set( possible_lines.keys() )  )
  #  print(possible_lines)
  #  print(miparser.data)

    for el in miparser.data:
    #    print el.name, 
        it = copy.copy( el )
        pc = possible_lines[it.name]
  #      print(pc)
#   print  family, var_type, default, 
#        print it.name
        values = [ i for i in it ]
        if len(values) == 0:
            values = it.data
        for val in values:
            if pc.family == "choice" and str(val) not in pc.categories:
                newline_msg("VAL", "choice value '%s' not recognised: possible values: %s"%(val, pc.categories))
                consistent_param = False
            elif pc.var_type == 'str':
                try:
                    str( "%s(%s)" %(pc.var_type, evaluate_string(val, miparser ) ) )
                except:
                    newline_msg("VAL", "wrong type for '%s' expected '%s' "%(it.name, pc.var_type))
                    consistent_param = False



            elif pc.var_type in set( [ "float", 'int', 'bool'] ): # in set(["float","double"]):
            #    print it.name, var_type, val, evaluate_string(val, miparser)  
                try: 
                    eval( "%s(%s)" %(pc.var_type, evaluate_string(val, miparser ) ) )
                except:
                    newline_msg("VAL", "wrong type for '%s' expected '%s' "%(it.name, pc.var_type))
                    consistent_param = False

    return consistent_param



#d = {'x':pi,'y_3':1}

#v = string_evaluator("exp({x}+{y_3})",d)
#print get_variables("exp({x}+{y_3})",d)
##st='/home/tessonec/running/alpha_max_20312_3424-0.5_size-100/beta-324.3242_gamma--90.2E-4.234_fjs-1E-4.dat'

#print st
#print parameterGuess(st)




