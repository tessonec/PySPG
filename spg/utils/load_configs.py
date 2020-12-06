'''
Created on Aug 30, 2011

@author: tessonec
'''

from spg import CONFIG_DIR
from .tools import * 
#from .check_params import *

from configparser import ConfigParser
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
# def load_configuration(config_filename, filter_keys = None):
#     """
#     takes a configuration file and returns the dictionary of values and the order
#     """
#
# #    possible_keys = set(["type", "label", "help", "scale", "repeat", "datatype", "lim"])
#     ret = SPGSettings()
#
#     try:
#         cfg_file = open(config_filename)
#     except:
#         cfg_file = open("%s/%s" % (CONFIG_DIR, config_filename ) )
#
#     sorted_cols = []
#     for line in cfg_file:
#         line = line.strip()
#
#         if len(line) == 0: continue
#         if line[0] == "#": continue
#
#         l = [i.strip() for i in line.split(":")]
#         name = l.pop(0)
#
#         sorted_cols.append(name)
#         values = SPGSettings()  # {"type":"xy","datatype":"float"}
#
#         for o in l:
#             # print o, l
#             [k, val] = o.split("=")
#             k = k.strip()
#             val = val.strip()
#
#             if (filter_keys is not None) and (k not in filter_keys):
#                 newline_msg("SYN", "in column '%s', unrecognised key '%s'" % (name, k))
#                 sys.exit(1)
#             else:
#                 values[k] = val
#
#         ret[name] = values
#
#     return ret, sorted_cols
#

#



def read_input_configuration(exec_file):
    """ Imports the backends used in a base.ct file """

    exec_file, ext = os.path.splitext(exec_file)
    try:
        cfgFile = f"{exec_file}.input"
    except:
        cfgFile = f"{CONFIG_DIR}/spg-conf/{exec_file}.input"



    possible_keys = set(["type", "label", "help", 'categories', 'default'])
    ret = SPGSettings()

    for l in open(cfgFile):

        l = l.strip()
        if len(l) == 0: continue
        if l[0] == "#": continue  # comment line

        l = l.split(":")

        var_name = l.pop(0).strip()
      #  print(l)

        try:
            d = {k.strip(): v.strip() for k, v in [_.split("=") for _ in l if len(_) > 0]}
        except:
            newline_msg("ERR", f"while parsing variable '{var_name}' information: >{l}<")
            sys.exit(1)

        _ = SPGSettings()

        _.var_type = d['type']

        if "categories" in d.keys():
            _.family = "choice"
            _.categories = eval(d["categories"])
            if 'default' not in d:
                _.default = _.categories[0]
        else:
            _.family = 'val'

        if "default" in d.keys():
            _.default = eval(d["default"])

        if "label" in d.keys():
            _.label = d['label']
        if "help" in d.keys():
            _.label = d['help']

        ret[var_name] = _
  #  print("----",ret)
    return ret


def read_output_configuration(exec_file):
    """
     keysColumns = ["type","label","help","scale","repeat", "lim"]
     the structure of the columns in the files are as follows:
     name of the variable, and a colon separated list of -optional- options
     type:  of the plot if xy, one column is used, xydy two columns are used
     label: to be used in the plotting script
     scale: comma separated list of minimum and maximum values
     repeat: how many columns are to be taken by the parser
     help: a string containing an explanation of the variable"""

    possible_keys = set(["type", "label", "help", "scale", "repeat", "datatype", "lim", "output_table"])
    #    if exec_file[:2] == "ct" and exec_file[3] == "-" :  exec_file = exec_file[4:]
    ret = {}
    exec_file, ext = os.path.splitext(exec_file)
    try:
        cfgFile = f"{exec_file}.stdout"
    except:
        cfgFile = f"{CONFIG_DIR}/spg-conf/{exec_file}.stdout"



    ret = SPGSettings()  # :::~ by default, results table is always created


    for l in open(cfgFile):
        l = l.strip()
        if len(l) == 0: continue
        if l[0] == "#": continue  # comment line

        l = l.split(":")

        name = l.pop(0).strip()



        values = SPGSettings({"type": "xy", "datatype": "float", "output_table":'results'})
        for o in l:
            try:
                k, v = o.split("=")
            except:
                newline_msg("FATAL", "processing '%s', line: '%s', field: '%s'" % (cfgFile, line, o))
                sys.exit(1)
            k = k.strip()
            v = v.strip()

            if k not in possible_keys:
                newline_msg("SYN", "in column '%s', unrecognised key '%s'" % (name, k))
                sys.exit(1)
            if k == "lim":
                values[k] = eval(v)
            else:
                values[k] = v

        ret[name] = values

    return ret



def read_parameter_atom(argv):
    """ Loads a parameter atom, compares it with the list of possible keys and returns the actual values"""

    prog_name = os.path.split(argv[0])[-1]
    # if prog_name[:2] == "ct" and prog_name[3] == "-" :  prog_name = prog_name[4:]

    prog_name, ext = os.path.splitext(prog_name)

    input_filename = argv[1]

    #  possible_lines = import_backends("%s.ct"%(prog_name))
    #    try:
    possible_lines = read_input_configuration("%s.input" % (prog_name))
    #    except:
    #        possible_lines = import_backends("%s/spg-conf/%s.input"%(CONFIG_DIR,prog_name))
    ret = SPGSettings()
    #    print(possible_lines)

    for k in list(possible_lines.keys()):
        (family, var_type, default) = possible_lines[k]
        if family == "val":
            if var_type == "str":
                ret[k] = default
            else:
                ret[k] = eval("%s(%s)" % (var_type, default))
        elif family == "choice":
            if var_type == "str":
                ret[k] = default[0]
            else:
                ret[k] = eval("%s(%s)" % (var_type, default[0]))

    for line in open(input_filename):
        line = line.strip()
        if not line: continue
        if line[0] == "#": continue
        vec = line.split()
        key = vec[0]
        if key not in possible_lines:
            newline_msg("ERR", "key '%s' not understood" % key)
            sys.exit(2)
        (family, var_type, default) = possible_lines[key]
        if family == "flag":
            ret[key] = True
        elif family == "val":
            #           print k, "%s(%s)"%(var_type, vec[1])
            if var_type == "str":
                ret[key] = vec[1]
            else:
                ret[key] = eval("%s('%s')" % (var_type, vec[1]))
        #            print ret[k]
        elif family == "choice":
            if vec[1] in default:
                ret[key] = eval("%s('%s')" % (var_type, vec[1]))
            else:
                newline_msg("ERR", "value '%s' not among possible values for '': %s" % (vec[1], key, default))
                sys.exit(2)
        # print ret

    return ret































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
#
#
# def read_configuration(exec_file, additional_keys, extension):
#     """
#      keysColumns = ["type","label","help","scale","repeat", "lim"]
#      the structure of the columns in the files are as follows:
#      name of the variable, and a colon separated list of -optional- options
#      type:  of the plot if xy, one column is used, xydy two columns are used
#      label: to be used in the plotting script
#      scale: comma separated list of minimum and maximum values
#      repeat: how many columns are to be taken by the parser
#      help: a string containing an explanation of the variable"""
#
#     possible_keys = set(["type", "label", "help"])
#     if len(additional_keys) > 0:
#         possible_keys.update(additional_keys)
#     #    if exec_file[:2] == "ct" and exec_file[3] == "-" :  exec_file = exec_file[4:]
#     ret = {}
#     exec_file, ext = os.path.splitext(exec_file)
#
#     try:
#         cfgFile = "%s.%s" % (exec_file, extension)
#     except:
#         cfgFile = "%s/spg-conf/%s.%s" % (CONFIG_DIR, exec_file, extension)
#
#     ret['results'] = []  # :::~ by default, results table is always created
#
#     for line in open(cfgFile):
#         if len(line.strip()) == 0: continue
#         l = [i.strip() for i in line.split(":")]
#
#         if l[0][0] == "@":
#             table = l.pop(0)[1:]
#         else:
#             table = "results"
#
#         if table not in list(ret.keys()):
#             ret[table] = []
#
#         name = l.pop(0)
#         values = {"plot_type": "xy", "type": "float"}
#         for o in l:
#
#             try:
#                 k, v = o.split("=")
#             except:
#
#                 newline_msg("FATAL", "processing '%s', line: '%s', field: '%s'" % (cfgFile, line, o))
#                 sys.exit(1)
#             k = k.strip()
#             v = v.strip()
#
#             if k not in possible_keys:
#                 newline_msg("SYN", "in column '%s', unrecognised key '%s'" % (name, k))
#                 sys.exit(1)
#             if k == "lim":
#                 values[k] = eval(v)
#             else:
#                 values[k] = v
#
#         ret[table].append((name, values))
#
#     return ret




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