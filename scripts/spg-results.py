#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:37:27 2011

@author: Claudio Tessone - <tessonec@ethz.ch>
"""

from spg.pool import ResultsDBQuery
from spg.params import generate_string

import os.path, os

import numpy as n


#########################################################################################
#########################################################################################
def parse_command_line():
     from optparse import OptionParser

     parser = OptionParser()

     parser.add_option("--table-depth", type="int", action='store', dest="table_depth",
                        default = 1, help = "The depth (how many independent variables) on the table are to be created")

     parser.add_option("--coalesce", type="string", action='store', dest="coalesce",
                        default = None, help = "comma separated list -with no blanks- ")

     parser.add_option("--prefix", type="string", action='store', dest="prefix",
                        default= "output", help = "prefix for the output")

     parser.add_option("--expand-dirs", action='store_true', dest="expand_dirs",
                        help = "whether to expand dirs instead of appending names to the output name")

     parser.add_option("--by-val", action='store_true', dest="by_val",
                        help = "whether to coalesce tableby var -useful if repeated-")

#     parser.add_option("--filter","--insert", type="string", action='store', dest="insert",
#                        help = "Inserts the given iterator before the first variable. The second argument is usually enclosed between quotes")

     return  parser.parse_args()


if __name__ == "__main__":
    opts, args = parse_command_line()
    
    for iarg in args:
    
       db_name = os.path.abspath( iarg )
    
       rq = ResultsDBQuery(db_name)
       
       if opts.coalesce is not None:
          rq.coalesce = opts.coalesce.split(",")
       elif opts.table_depth is not None:
          rq.coalesce = rq.variables[:-opts.table_depth]
#       print rq.coalesce
       for i in rq:
    #      print i
          if not opts.by_val:
            data = rq.full_result_table_restricted(restrict_to_values = i)
          else:
            data = rq.full_result_table_restricted_byval(restrict_to_values = i)
          
          if not opts.expand_dirs:
              gen_s = generate_string(i, rq.coalesce )
              output_fname = "%s-%s.dat"%(opts.prefix, gen_s )
          else:
              gen_s = generate_string(i, rq.coalesce, joining_string = "/" )
              
              output_fname = "%s/%s.dat"%(gen_s, opts.prefix  )
          d,f = os.path.split(output_fname)
          if d != "" and not os.path.exists(d):
              os.makedirs(d)
          n.savetxt( output_fname, data)
  #  r1 = rq.result_table("ordprm_kuramoto")
  #  n.savetxt("ordprm_kuramoto",r1)
    
  #  r2 = rq.full_result_table()
  #  n.savetxt("output.dat",r2) 