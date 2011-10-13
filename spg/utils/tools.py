#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, re, os.path
from math import *


def generate_string(values, var_list, separator = "-", joining_string = "_"):
    """Replaces a list of variables with its value into a string"""
#    print values, var_list
    thisstr = joining_string.join( [
                         "%s%s%s"%(k, separator, values[k] )
                         for k in var_list if k
                     ] )

    return thisstr.replace("'","").replace('"',"")



# :::~ DEPRACTED FUNCTION, it is duplicated functionality from replace_values
#def replace_in_string(sss,dict_of_values):
#    """replaces -within in a string- a dictionary of values"""
#
#    thisstr=str(sss)
#    for varname in dict_of_values.keys():
#        thisstr=thisstr.replace(
#                   "[%s]"%varname,
#                   "%s"%( dict_of_values[varname] )
#                )
#        thisstr=thisstr.replace(
#                   "{%s}"%varname,
#                   "%s-%s"%( varname, dict_of_values[varname] )
#                )
#    return thisstr



def parameters_from_string(string):
    """guesses the values of parameters  from the string the format is expected to be key-value.
    values are expected to be numeric"""

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


def evaluate_string(string,val_dict, ):
    """evaluates an expression with the values given in the dictionary.
    The variable names are to be enclosed in square-brackets.
    automatic type conversion is attemped"""
    
    #fp = string # os.path.abspath(string)
    rx = re.compile(r'\[([a-zA-Z0-9_]\w*)\]')
    # regular expression explanation
    # r'\{(\w)\}' matches variable name: 
    st_out = string
    try:
        for i_var in rx.findall(string):
            st_out = re.sub( r'\[%s\]'%i_var, str(val_dict[i_var]), st_out )
        return eval( st_out ) 
        #print st_out
    except:
        try:
            return eval(str( string ) )
        except:
            return str(string) 


def replace_values(string,val_dict):
    """replaces a set of values (given in val_dict) into a string.
    Square-bracketed keys are changed into its value
    Curly-bracketed keys are changed into its key-value. 
    Attempts to evaluate the result to give a type conversion"""
    
    string = str(string).strip()
    
    st_out = string.strip()
    #fp = string # os.path.abspath(string)
    
    # regular expression explanation
    # r'\{(\w)\}' matches variable name: 
    
   # try:

    if not st_out: return "" 
         
    rx_s = re.compile(r'\[([a-zA-Z]\w*)\]')
    for i_var in rx_s.findall(string):
            st_out = re.sub( r'\[%s\]'%i_var, str( val_dict[i_var] ), st_out )
            
    rx_c = re.compile(r'\{([a-zA-Z]\w*)\}')
    for i_var in rx_c.findall(string):
            st_out = re.sub( r'\{%s\}'%i_var, "%s-%s"%(i_var, str( val_dict[i_var] ) ), st_out )
        
    try:
        ret = eval( st_out) 
    except:
        ret =  str( st_out ) 
    return ret



def get_variables(string):
    """gets all the variable names from a string"""
    #:::~ FIXME: UNUSED, is it worth?
    
    #fp = string # os.path.abspath(string)
    rx = re.compile(r'\{([a-zA-Z]\w*)\}')
    # regular expression explanation
    # r'\{(\w)\}' matches variable name: 
    return rx.findall(string)

#d = {'x':pi,'y_3':1}


def parse_to_dict(string, allowed_keys = None):
    """parses a string into a dictionary. Blanks or colons can be used as separator.
    The function attempts to guess the type, otherwise a string is assigned.
    allowed_keys gives the possible list of keys that will be accepted by the parsing. Otherwise None is returned """
    #:::~ FIXME: Convoluted code
    
    string = ":".join( string.split() )
    
    ret = {}
    for i in string.split(":"):
        try:
            [k,v] = i.split("=")
        except:
            newline_msg("SYN", "error while parsing pair key, value: '%s'"%i)
            return None
        if allowed_keys and k not in allowed_keys:
            newline_msg("SYN", "error key: '%s' not allowed -allowed values are %s-"%(k,allowed_keys))
            return None
        try:
            ret[k] = int(v)
        except: 
            try:
                ret[k] = float(v)
            except:
                if v.lower()  == "true":
                    ret[k] = True
                elif v.lower()  == "false":
                    ret[k] = False
                else:
                    ret[k] = v
    return ret


#v = eevaluate_stringexp({x}+{y_3})",d)
#print get_variables("exp({x}+{y_3})",d)
##st='/home/tessonec/running/alpha_max_20312_3424-0.5_size-100/beta-324.3242_gamma--90.2E-4.234_fjs-1E-4.dat'

#print st
#print parameterGuess(st)

#########################################################################################
#########################################################################################
def inline_msg( type, msg, indent = 0 , stream = sys.stderr):
    print >> stream, "%s[%s - %5s ] %s...\r"%(" "*indent, os.path.split(sys.argv[0])[1], type, msg),
    stream.flush()

def newline_msg( type, msg, indent = 0 , stream = sys.stderr ):
    print >> stream, "%s[%s - %5s ] %s"%(" "*indent, os.path.split(sys.argv[0])[1], type, msg)
    stream.flush()
#########################################################################################
#########################################################################################



