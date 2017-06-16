'''
Created on Aug 30, 2011

@author: tessonec
'''

from tools import * 
from check_params import *

from ConfigParser import ConfigParser
import os.path, sys


class SPGSettings(dict):
    # :::~ class that allows to take the values as items

    # :::~ http://stackoverflow.com/questions/1325673/python-how-to-add-property-to-a-class-dynamically
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __str__(self):
        ret = ":\n"
        for k in self.keys():
            ret += "%s = %s\n" % (k, self[k])
        return ret

#
# def load_config(config_name, key):
#     ret  = SPGParameters()
#     for l in open(config_name):
#         l = l.strip()
#         if len(l) == 0: continue
#         if l[0] == "#": continue
#         v = l.split(":")
#         for kp in v[1:]:
#             kpv = kp.split("=")
#             if kpv[ 0 ].strip() == key:
#                 ret[ v[0] ] =  kpv[ 1 ].strip()
#     return ret

def load_configuration(config_filename, filter_keys = None):
    """
    keysColumns = ["type","label","help","scale","repeat", "lim"]
    the structure of the columns in the files are as follows:
    name of the variable, and a colon separated list of -optional- options
    type:  of the plot if xy, one column is used, xydy two columns are used
    label: to be used in the plotting script
    scale: comma separated list of minimum and maximum values
    repeat: how many columns are to be taken by the parser
    help: a string containing an explanation of the variable"""

#    possible_keys = set(["type", "label", "help", "scale", "repeat", "datatype", "lim"])
    ret = SPGSettings()
#    print config_filename

    try:
        cfg_file = open(config_filename)
    except:
        cfg_file = open("%s/%s" % (CONFIG_DIR, config_filename ) )

    sorted_cols = []
    for line in cfg_file:
        line = line.strip()

        if len(line) == 0: continue
        if line[0] == "#": continue

        l = [i.strip() for i in line.split(":")]
        name = l.pop(0)

        sorted_cols.append(name)
        values = SPGSettings()  # {"type":"xy","datatype":"float"}

        for o in l:
            # print o, l
            [k, val] = o.split("=")
            k = k.strip()
            val = val.strip()

            if (filter_keys is not None) and (k not in filter_keys):
                newline_msg("SYN", "in column '%s', unrecognised key '%s'" % (name, k))
                sys.exit(1)
            else:
                values[k] = val

        ret[name] = values

    return ret, sorted_cols


#
#
# def get_root_directory():
#     ret = os.path.expanduser( "~/opt" )
#     try:
#         cp = ConfigParser( os.path.expanduser("~/.spg/config") )
#         cp.get("Global", "root_dir")
#     except:
#         pass
#
#     return os.path.expanduser(ret)
#



def load_parameters(argv):
    """ Loads a parameter dataset. other_params is an array of tuples (cmd_line_arg, type, dest, default, help) """
    
    prog_name = os.path.split(argv[0])[-1]
   # if prog_name[:2] == "ct" and prog_name[3] == "-" :  prog_name = prog_name[4:]

    prog_name, ext = os.path.splitext(prog_name)
        
    default_input_file = "input.dat" #open("%s/spg-conf/%s.in"%(CONFIG_DIR, prog_name)  ).readline().strip()
#    default_input_file = open("%s/spg-conf/%s.in"%(CONFIG_DIR, prog_name)  ).readline().strip()

    # parser = optparse.OptionParser()
    # parser.add_option("--input", '-i', type="string", action='store', dest="input_filename",
    #                     default = default_input_file , help = "Input file parameter" )
    #
    # options, args = parser.parse_args()
    input_filename = argv[1]

  #  possible_lines = import_backends("%s.ct"%(prog_name))
    try:
        possible_lines = import_backends("%s.ct"%(prog_name))
    except: 
        possible_lines = import_backends("%s/spg-conf/%s.ct"%(CONFIG_DIR,prog_name))
    ret = SPGSettings()

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
            
    for line in open(input_filename):
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
                ret[key] = eval("%s('%s')"%(var_type, vec[1]))
            else:
                newline_msg("ERR", "value '%s' not among possible values for '': %s"%(vec[1],key,default))
                sys.exit(2)
        #print ret
                
    return ret
