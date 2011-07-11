#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:37:27 2011

@author: Claudio Tessone - <tessonec@ethz.ch>
"""

from spg.pool import ResultsDBQuery
import os.path, sys


#########################################################################################
#########################################################################################
def parse_command_line():
     from optparse import OptionParser

     parser = OptionParser()

     parser.add_option("--table-depth", type="int", action='store', dest="table_depth",
                        default = None, help = "The depth of the table to be created")

     parser.add_option("--coalesce", type="string", action='store', dest="coalesce",
                        default = None, help = "comma separated list -with no blanks- ")

     parser.add_option("--prefix", type="string", action='store', dest="prefix",
                        default= "out", help = "prefix for the output")

#     parser.add_option("--filter","--insert", type="string", action='store', dest="insert",
#                        help = "Inserts the given iterator before the first variable. The second argument is usually enclosed between quotes")

     return  parser.parse_args()


if __name__ == "__main__":
#    print params.CONFIG_DIR

    opts, args = parse_command_line()
    
    for iarg in args:
    
       db_name = os.path.abspath( iarg )
    
       rq = ResultsDBQuery(db_name)
       
       if opts.coalesce is not None:
          rq.coalesce = opts.coalesce.split(",")
       elif opts.table_depth is not None:
          rq.coalesce = rq.variables [:-opts.table_depth]
          
       
       for i in rq:
          print i
  #  r1 = rq.result_table("ordprm_kuramoto")
  #  n.savetxt("ordprm_kuramoto",r1)
    
  #  r2 = rq.full_result_table()
  #  n.savetxt("output.dat",r2) 