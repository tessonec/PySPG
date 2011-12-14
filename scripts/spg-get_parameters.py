#!/usr/bin/python
'''
Created on Sep 21, 2011

@author: tessonec
'''


import spg.utils as utils 
import optparse

import math as m
import random as rnd
import sys




def load_parameters(argv):
    """ Loads a parameter dataset. other_params is an array of tuples (cmd_line_arg, type, dest, default, help) """

    parser = optparse.OptionParser()
    parser.add_option("--input", '-i', type="string", action='store', dest="input_filename",
                        default = "in.dat" , help = "Input file parameter" )
    parser.add_option("--parameter", '-p', type="string", action='store', dest="parameters",
                        default = "" , help = "Set of parameters (comma separated, no blanks) to be printed, from the " )
        
    options, args = parser.parse_args()
    set_of_parameters = options.parameters.split(",") 
    dict_of_vals = {}

    for line in open(options.input_filename):
        line = line.strip()
        if not line: continue
        if line[0] == "#": continue
        
        vec = line.split() 
        key = vec[0]
        if len(vec) == 1:
            dict_of_vals[key] = True
        elif len(vec) == 2:
            dict_of_vals[key] = vec[1]
        else:
            utils.newline_msg("ERR", "line '%s' does not contain a pair of values, nor a flag " %(line) )
            return

    ret = ""
    
    for i in set_of_parameters:
        if i not in dict_of_vals.keys():
            utils.newline_msg("ERR", "requested parameter '%s' not in input file " %(i) )
            return
        ret += "%s\t"%dict_of_vals[i]

    return ret






if __name__ == "__main__":
    

    
    parameters = load_parameters(sys.argv)
    print parameters

    
    
