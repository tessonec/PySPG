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

PROGRAM_NAME         = "SPG-Coalesce"
PROGRAM_VERSION      = "0.1.0"
PROGRAM_AUTHOR       = "Claudio J. Tessone"
PROGRAM_RELEASE_DATE = "2011/03/25"
PROGRAM_EMAIL        = "tessonec@ethz.ch"

import spg.utils as spgu

import re, sys, shutil
import os.path, os


import numpy as n
#########################################################################################
#########################################################################################
def parse_command_line():
     from optparse import OptionParser

     parser = OptionParser()

     parser.add_option("-f","--file", type="string", action='store', dest="file_name",
                        help = "gives the name of the file to be searched for")

     parser.add_option("-o","--output", type="string", action='store', dest="output", default = None,
                        help = "name of the output file")

     parser.add_option("--var", type="string", action='store', dest="variable",
                        help = "gives the name of the variable to be stored in the merged file")

     parser.add_option("--ycol", type="int", action='store', dest="ycol",default=0,
                        help = "column to be considered containing the second independent axis")
     parser.add_option("--zcol", type="int", action='store', dest="zcol",default=1,
                        help = "column to be considered containing dependent axis")

     
     return  parser.parse_args()



opts, args = parse_command_line()




pwd = os.path.abspath(".")

ls_dirs = []
for op, dirs, files in os.walk( "." ):
  if opts.file_name in files:
    ls_dirs.append( op )


for d in ls_dirs:
    os.chdir( d )
    params = spgu.parameter_guess("%s/%s"%(d, opts.file_name))
    data = n.loadtxt(opts.file_name)
    #print "%s/%s"%(d, opts.file_name), params
    ret = [ [params[opts.variable], pt[opts.ycol]  , pt[opts.zcol] ] for pt in data]
    if not opts.output:
      fout = open("../%s"%opts.file_name,"aw")
    else:
      fout = open("../%s"%opts.output ,"aw")

    for [x,y,z] in ret:
      print >> fout, x,y,z

    fout.close()
    os.chdir(pwd)
    