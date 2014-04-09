#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:37:27 2011

@author: Claudio Tessone - <tessonec@ethz.ch>
"""

from spg import VAR_PATH, RUN_DIR, CONFIG_DIR
import spg.utils as utils
from spg.cmdline import BaseDBCommandParser
from spg.master import MasterDB
from spg.parameter import ResultsDBQuery


import numpy as np
import math as m
#from matplotlib import rc
#import matplotlib.pyplot as plt
#import matplotlib.pylab as plb
import sqlite3 as sql
import sys, optparse
import os, os.path
import fnmatch

class ResultCommandParser(BaseDBCommandParser):
    """Results command handler"""

    def __init__(self):
        BaseDBCommandParser.__init__(self, EnsembleConstructor = ResultsDBQuery)
        self.prompt = "| spg-results :::~ "
        
        self.possible_keys = set( [ "raw_data", "split_colums", "restrict_by_val", "table", "split_columns"] )
        self.output_column = []
        self.raw_data = False
        self.split_columns = False
        self.restrict_by_val = False # was True
        self.table  = "results" # default value

        self.autoscale = None

#        self.figures = {}
#        self.values = {'repeat': 1, 'sql_retries': 1, 'timeout' : 60, 'weight': 1}
#        self.doc_header = "default values: %s"%(self.values )

    def do_load(self,c):
        """loads a results_database"""
        BaseDBCommandParser.do_load(self, c)
        self.output_column = self.current_param_db.output_column['results'][1:]
        
        os.chdir( self.current_param_db.path )


    def do_save_table(self,c):
       """save_table [-flag1 -flag2] 
          saves the table values in ascii format
          FLAGS::: -header:        the first row is the column name
                   -append:      appends the output, instead of rewriting the file        
       """
       
       
       flags,c = self.parse_command_line(c)
       if "append" in flags:
          open_type = "aw"
       else:
          open_type = "w" 
       
       for i in self.current_param_db:
         if self.split_columns:
           for column in self.output_column:
          #    print ":::", self.output_column
              gen_d = utils.generate_string(i, self.current_param_db.separated_vars, joining_string = "/" )
              if gen_d :  gen_d+= "/"
              gen_s = utils.generate_string(i, self.current_param_db.coalesced_vars, joining_string = "_" )
              output_fname = utils.fix_filename(  "%s%s-%s-%s.dat"%(gen_d, self.table, column, gen_s) )
              d,f = os.path.split(output_fname)
              if d != "" and not os.path.exists(d): os.makedirs(d)
              output_file = open(output_fname , open_type)
            #  print "1:::~",output_fname
              if "header" in flags:
                  output_file.write(  self.current_param_db.table_header( [column] ) )
                  output_file.flush()

              data = self.current_param_db.result_table(restrict_to_values = i, table = self.table, raw_data = self.raw_data, restrict_by_val = self.restrict_by_val, output_column = [column] )

              np.savetxt( output_file, data)
         else:
           data = self.current_param_db.result_table(restrict_to_values = i, table = self.table, raw_data = self.raw_data, restrict_by_val = self.restrict_by_val, output_column = self.output_column )
           gen_s = self.current_param_db.full_name.split("/")[-1][:-len(".sqlite")][len('results'):]
           
           
           gen_d = utils.generate_string(i, self.current_param_db.separated_vars, joining_string = "/" )
           if gen_d:  gen_d+= "/"
           
#           gen_s = utils.generate_string(i, self.current_param_db.coalesced_vars, joining_string = "_" )
           output_fname = utils.fix_filename( "%s%s%s.dat"%(gen_d, self.table, gen_s) )
           #print "2:::~",output_fname , "%s%s%s.dat"%(gen_d, self.table, gen_s), gen_d, self.table, gen_s
           d,f = os.path.split(output_fname)
           if d != "" and not os.path.exists(d): os.makedirs(d)
           output_file = open(output_fname , open_type)
           if "header" in flags:
                 output_file.write(  self.current_param_db.table_header(table = self.table, output_column= self.output_column ) )
                 output_file.flush()
           np.savetxt( output_file, data )

    def do_setup_vars_in_table(self,c):
        """sets up the variables that output into the table as independent columns"""
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return
        self.current_param_db.setup_vars_in_table(c)

    def do_setup_vars_separated(self,c):
        """sets up which variables are going to have a separated directory"""
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return
        self.current_param_db.setup_vars_separated(c)

    def do_setup_vars_coalesced(self,c):
        """sets up which variables are coalesced into the same file"""
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return
        self.current_param_db.setup_vars_coalesced(c)
        

    def do_setup_output_column(self,c):
        """sets which columns to generate output from"""
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return
        c = c.split(",")
        if not set(c).issubset(  self.current_param_db.output_column[self.table] ):
            utils.newline_msg("ERR", "the column(s) is (are) not in the output: %s"%( set(c) - set(  self.current_param_db.output_column[self.table] )) )
        self.output_column = c

    def do_set_as_var(self,c):
        """ Sets a (set of) non-variables as variable """
        if not self.current_param_db: 
            utils.newline_msg("WRN", "current db not set... skipping")
            return 
        ls_vars = c.split(",")
        if not set(ls_vars).issubset( set(self.current_param_db.entities) ):
            utils.newline_msg("VAR", "the variables '%s' are not recognised"%set(ls_vars)-set(self.current_param_db.entities) )
            return
        for v in ls_vars:
            self.current_param_db.execute_query( 'UPDATE entities SET varies=1 WHERE name = ?', v)
        self.current_param_db.init_db()

    def do_set(self, c):
        """sets a VAR1=VALUE1[:VAR2=VALUE2]
        sets a value in the currently loaded database """

        if c == "help":
            utils.newline_msg("HELP", " possible_keys = %s"%self.possible_keys )
            return 
        
        if not self.current_param_db: 
            utils.newline_msg("WRN", "current db not set... skipping")
            return 
        
        ret = utils.parse_to_dict(c, allowed_keys=self.possible_keys)
        if not ret: 
            return
        for k in ret.keys():
            if k == "table":
                 if ret[k] not in self.current_param_db.output_column.keys():
                     utils.newline_msg("ERR", "table '%s' not among the ones found in the DB: (%s)"%(ret[k], ", ".join(self.current_param_db.output_column.keys())) )
                     return
                 self.output_column = self.current_param_db.output_column[ ret[k] ][1:]
            self.__dict__[k] = ret[k]

    def do_conf(self,c):
        """prints the current configuration"""
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return
        print " -- db: %s"%( self.shorten_name( self.current_param_db.full_name ) )
        print "  + variables = %s "%( ", ".join(self.current_param_db.variables ) )
        print "  + entities = %s "%( ", ".join(self.current_param_db.entities ) )
        
        print "  + table   = %s (tables found: %s) "%(self.table, ", ".join(self.current_param_db.output_column.keys())) 
        print "  + columns = %s "%( ", ".join( self.current_param_db.output_column[self.table]  ) )
        print "  + split_columns = %s  / raw_data = %s / restrict_by_val = %s"%(self.split_columns, self.raw_data, self.restrict_by_val)
        print "  + vars (separated-coalesced-in_table) = %s - %s - %s "%(self.current_param_db.separated_vars, self.current_param_db.coalesced_vars, self.current_param_db.in_table_vars)


if __name__ == '__main__':
    cmd_line = ResultCommandParser()
    if len(sys.argv) == 1:
        cmd_line.cmdloop()
    else:
        cmd_line.onecmd(" ".join(sys.argv[1:]))
        


 