'''
Created on Aug 30, 2011

@author: tessonec
'''

from tools import * 
from check_params import *

from ConfigParser import ConfigParser
import os.path 


def load_config(config_name, key):
    ret  = {}
    for l in open(config_name):
        l = l.strip()
        if not l: continue
        if l[0] == "#": continue
        v = l.split(":")
        for kp in v[1:]:
            kpv = kp.split("=")
            if kpv[ 0 ].strip() == key:
                ret[ v[0] ] =  kpv[ 1 ].strip()
    return ret
    
    
    
def get_root_directory():
    ret = os.path.expanduser( "~/opt" )
    try:
        cp = ConfigParser( os.path.expanduser("~/.spg/config") )
        cp.get("Global", "root_dir")
    except:
        pass
    
    return os.path.expanduser(ret)






class Parameters(dict):
    # :::~ class that allows to take the values as items
     
    # :::~ http://stackoverflow.com/questions/1325673/python-how-to-add-property-to-a-class-dynamically
    __getattr__= dict.__getitem__
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__
            
    def __str__(self):
        ret = ""
        for k in self.keys():
            ret += "%s = %s\n"%(k,self[k])
        return ret



def load_parameters(argv):
    """ Loads a parameter dataset. other_params is an array of tuples (cmd_line_arg, type, dest, default, help) """
    
    prog_name = os.path.split(argv[0])[-1]
    if prog_name[:2] == "ct" and prog_name[3] == "-" :  prog_name = prog_name[4:]

    prog_name, ext = os.path.splitext(prog_name)
        
    default_input_file = open("%s/spg-conf/%s.in"%(CONFIG_DIR, prog_name)  ).readline().strip()
    
    
    parser = optparse.OptionParser()
    parser.add_option("--input", '-i', type="string", action='store', dest="input_filename",
                        default = default_input_file , help = "Input file parameter" )
    
    options, args = parser.parse_args()
    
    possible_lines = import_backends("%s/spg-conf/%s.ct"%(CONFIG_DIR,prog_name))
    ret = Parameters()
    
    for k in possible_lines.keys():
        (family, var_type, default)  = possible_lines[k]
        if family == "flag":
            ret[k] = False
        elif family == "val":
            if var_type == "str":
                ret[k] =  default
            else:
                ret[k] = eval("%s('%s')"%(var_type, default))
        elif family == "choice":
            ret[k] = eval("%s('%s')"%(var_type, default[0]))
            
    for line in open(options.input_filename):
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
            ret[key] = True
        elif family == "val":
 #           print k, "%s(%s)"%(var_type, vec[1])
            if var_type == "str":
                ret[key] =  vec[1]
            else:
                ret[key] = eval("%s('%s')"%(var_type, vec[1]))
#            print ret[k]
        elif family == "choice":
            if vec[1] in default:
                ret[key] = eval("%s('%s')"%(var_type, default[0]))
            else:
                newline_msg("ERR", "value '%s' not among possible values for '': %s"%(vec[1],key,default))
                sys.exit(2)
        #print ret
                
    return ret
