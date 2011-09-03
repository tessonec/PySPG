'''
Created on Aug 30, 2011

@author: tessonec
'''


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
    