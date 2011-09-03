#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import copy
#from math import *


from spg import utils
from spg import CONFIG_DIR

from tools import newline_msg


def import_backends(infile):

    """ Imports the backends used in a base.ct file """  
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
                utils.newline_msg("ERR", "while unfolding line: '%s'" % (line))
                sys.exit()
            new_stuff = [
                    i.replace("%ARG%", var_name).replace("%ARG1%", var_name)
                    for i in open("%s/ctt/%s.be" % (CONFIG_DIR , backend), "r")
                  ]
            output.extend (new_stuff)
        else:
            output.append(line)
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
        ret[ var_name ] = (family, var_type, default)
    
    return ret



def load_parameters(prog_name, in_file):
    """ Loads a parameter dataset"""
    
    if prog_name[:4] == "ctx-":  prog_name = prog_name[4:]

    prog_name, ext = os.path.splitext(prog_name)
    possible_lines = import_backends("%s/spg-conf/%s.ct"%(CONFIG_DIR,prog_name))
    ret = {}
    for k in possible_lines.keys():
        (family, var_type, default)  = possible_lines[k]
        if family == "flag":
            ret[k] = False
        elif family == "val":
            eval("%s(%s)"%(var_type, default))
        elif family == "choice":
            eval("%s(%s)"%(var_type, default[0]))
            
    for line in open(in_file):
        line = line.strip()
        if not line: continue
        if line[0] == "#": continue
        vec = line.split() 
        key = vec[0]
        
        if not possible_lines.has_key(key):
            newline_msg("ERR", "key '%s' not understood"%key)
            sys.exit(2)
        (family, var_type, default)  = possible_lines[key]
        if family == "flag":
            ret[k] = True
        elif family == "val":
            ret[k] = eval("%s(%s)"%(var_type, vec[1]))
        elif family == "choice":
            if vec[1] in default:
                ret[k] = eval("%s(%s)"%(var_type, default[0]))
            else:
                newline_msg("ERR", "value '%s' not among possible values for '': %s"%(vec[1],key,default))
                sys.exit(2)
                
        
    return ret


def consistency(exec_file, miparser):
    """ Checks the consistency of a parameters.dat file """  
    consistent_param=True
  
    if exec_file[:4] == "ctx-":  exec_file = exec_file[4:]

    exec_file, ext = os.path.splitext(exec_file)
    possible_lines = import_backends("%s/spg-conf/%s.ct"%(CONFIG_DIR,exec_file))

    assert len(set(miparser.items() ) - set( possible_lines.keys() ) ) == 0 , "not all the variables are recognised: offending vars: %s"%(set( miparser.items() ) -set( possible_lines.keys() )  )

    for el in miparser.data:
    #    print el.name, 
        it = copy.copy( el )
        family, var_type, default = possible_lines[it.name]
     #   print  family, var_type, default, 
        
        values = [ i for i in it ]
        if len(values) == 0:
            values = it.data
        for val in values:
            
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

   #         print consistent_param

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
     help: a string containing an explanation of the variable"""
     
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
   




#d = {'x':pi,'y_3':1}

#v = string_evaluator("exp({x}+{y_3})",d)
#print get_variables("exp({x}+{y_3})",d)
##st='/home/tessonec/running/alpha_max_20312_3424-0.5_size-100/beta-324.3242_gamma--90.2E-4.234_fjs-1E-4.dat'

#print st
#print parameterGuess(st)




