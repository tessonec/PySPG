'''
Created on Aug 30, 2011

@author: tessonec
'''

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


