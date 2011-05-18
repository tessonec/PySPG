#!/usr/bin/python
# -*- coding: utf-8 -*-

# :::~ Author: Claudio Juan Tessone <tessonec@ethz.ch> (c) 2010
###
### 
###
###
# Distributed According to GNU Generic Purpose License (GPL) version 3
# Please visit www.gnu.org
###############################################################################

PROGRAM_NAME         = "SPG-Edit-Param"
PROGRAM_VERSION      = "0.1.0"
PROGRAM_AUTHOR       = "Claudio J. Tessone"
PROGRAM_RELEASE_DATE = "2010/05/29"
PROGRAM_EMAIL        = "tessonec@ethz.ch"

import spg.utils as spgu

import re, sys, shutil

#########################################################################################
#########################################################################################
def parse_command_line():
     from optparse import OptionParser

     parser = OptionParser()

     parser.add_option("-e","--edit", type="string", action='append', dest="edit",
                        help = "Replaces a given iterator. Its name is grabbed directly from the argument")

     parser.add_option("-s","--swap", type="string", nargs=2, action='append', dest="swap",
                        help = "Swaps two variables in the param.dat file")

     parser.add_option("-i","--insert", type="string", nargs=2, action='append', dest="insert",
                        help = "Inserts the given iterator before the first variable. The second argument is usually enclosed between quotes")

     parser.add_option("-a","--append", type="string", nargs=2, action='append', dest="append",
                        help = "Appends the second iterator after the first variable. The second argument is usually enclosed between quotes")

     parser.add_option("-d","--delete", type="string", action='append', dest="delete",
                        help = "Deletes the second whose variables are those named")

     parser.add_option("-m","--move", type="string", nargs=2, action='append', dest="move",
                        help = "Moves the iterator to the position given as second argument")

     
     return  parser.parse_args()



def parse_param_dat(fin):
  regex = re.compile(r'(?P<iter>[*+.:/])(?P<var>[a-zA-Z]\w*)\s*(?P<values>.*)')
  vec_entities = []
  dict_iters = {}
  for l in fin:
    l = l.strip()
    if l[:2] == "%!":
      vec_entities.append( l )
      continue
    if l[:2] == "#":
      vec_entities.append( l )
      continue
    
    match = regex.match( l )
    iter = match.group( 'iter' )
    var  = match.group( 'var' )
    values = match.group( 'values' )

    vec_entities.append( var )
    dict_iters[var] = (iter, values)

  return vec_entities, dict_iters

def out_param_dat(fout, vec_ents, dict_iters):

  for ent in vec_ents:
    if ent in dict_iters.keys():
      (iter, values) = dict_iters[ent] 
      print >> fout, '%s%s %s'%(iter, ent, values)
    else:
      print >> fout, '%s'%(ent)


def find_var(vec_ents, var):
  try:
    return vec_ents.index(var)
  except:
    spgu.newline_msg("ERR","variable '%s' not found "%var1)
    sys.exit(1)

#----------------------------------------------------- from spg import SPGParser
#===============================================================================
#  
# parser = SPGParser()
# 
# vec_param_dat = glob.glob()
#===============================================================================

#--------------------------------------------- parser.fetch( open("param.dat") )

#-------------------------------------------------------------- for i in parser:
        #--------------------------------------------------------------- print i


opts, args = parse_command_line()

#print opts
for i_arg in args:
    spgu.newline_msg("MSG","parsing... '%s' "%i_arg)
    vec_entities, dict_iters = parse_param_dat( open(i_arg) ) 
    
    if opts.swap is not None:
      for var1, var2 in opts.swap:
        pos1 = find_var(vec_entities, var1)
        pos2 = find_var(vec_entities, var2)
        vec_entities[pos1], vec_entities[pos2] = vec_entities[pos2], vec_entities[pos1] 

    if opts.edit is not None:
      for ed in opts.edit:
        var, dil = parse_param_dat( [ed] )
        var = var[0]
        (iter, values) = dil[ var ]

        dict_iters[var] = (iter, values)

    if opts.insert is not None:
      for var1, oth in opts.insert:
        pos1 = find_var(vec_entities, var1)

        var2, dil = parse_param_dat( [oth] )
        var2 = var2[0]
        dict_iters[var2] = dil[ var2 ]

        vec_entities.insert( pos1, var2 )

    if opts.append is not None:
      for var1, oth in opts.append:
        pos1 = find_var(vec_entities, var1)+1

        var2, dil = parse_param_dat( [oth] )
        var2 = var2[0]
        dict_iters[var2] = dil[ var2 ]

        vec_entities.insert( pos1, var2 )

    if opts.delete is not None:
      for var1 in opts.delete:
        vec_entities.remove( var1 )

    if opts.move is not None:
      for var1, shift in opts.move:
        pos1 = find_var(vec_entities, var1)
        vec_entities.remove( var1 )
       
        vec_entities.insert( pos1+int(shift) , var1 )
        
    shutil.copy( i_arg, "%s-"%i_arg )
    out_param_dat(open(i_arg,"w"), vec_entities, dict_iters)
    