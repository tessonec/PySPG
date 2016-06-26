#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 11:37:27 2011

@author: Claudio Tessone - <claudio.tessone@uzh.ch>
"""

#from spg import  CONFIG_DIR
import spg.utils as utils
from spg.cmdline import BaseSPGCommandLine
from spg.simulation import ResultsDBQuery
import spg.utils as utils

import numpy as np
import math as m
#from matplotlib import rc
#import matplotlib.pyplot as plt
#import matplotlib.pylab as plb
import sqlite3 as sql
import sys, optparse
import os, os.path
import fnmatch, csv

class SPGResultsCommandLine(BaseSPGCommandLine):
    """Results command handler"""

    def __init__(self):
        BaseSPGCommandLine.__init__(self, EnsembleConstructor = ResultsDBQuery)
        self.prompt = "| spg-results :::~ "
        
        self.possible_keys = set( [ "raw_data", "split_colums", "restrict_by_val", "table", "split_columns", "sep"] )
        self.output_column = []
        self.raw_data = False
        self.split_columns = False
        self.restrict_by_val = False # was True
        self.table  = "results" # default value
        self.sep = ","

        self.autoscale = None


    def do_load(self,c):
        """loads a results_database"""
        BaseSPGCommandLine.do_load(self, c)
        self.output_column = self.current_param_db.output_column['results'][1:]
        
        os.chdir( self.current_param_db.path )


    def do_import_output_csv(self, c):

        flags, cs = self.parse_command_line(c)
        if "sep" in flags:
            if flags["sep"] == "blank":
                self.sep = " "
            else:
                self.sep = flags["sep"]

        self.current_param_db.update_results_from_data( cs[0], sep = self.sep )

    def do_export_output_csv(self, c):
        """save_csv [-flag1 -flag2] f1 f2 g3
           saves the table values in ascii format
           FLAGS::: -raw:        do not average values for same parameter set
        """
        flags, cs = self.parse_command_line(c)
        if "sep" in flags:
            if flags["sep"] == "blank":
                self.sep = " "
            else:
                self.sep = flags["sep"]

        for c in cs:
            self.do_load(c)
            if "raw_data" in flags:
                self.do_set("raw_data=True")
            self.do_setup_vars_in_table("--all")
            if "only-id":
                self.do_save_table("--header --only-id %s"  % c)
            else:
                self.do_save_table("--header %s" % c)

    def do_export_input_csv(self,c):
        flags, cs = self.parse_command_line(c)
        if "sep" in flags:
            if flags["sep"] == "blank":
                self.sep = " "
            else:
                self.sep = flags["sep"]

        for c in cs:
            self.do_load(c)

            self.do_setup_vars_in_table("--all")
            header, data = self.current_param_db.values_set_table()

            output_fname = utils.fix_filename("%s/%s_valueset.csv" % (self.current_param_db.path, self.current_param_db.base_name))
            print "    table: %s" % output_fname
            writer = csv.writer(open(output_fname, "w"), delimiter=self.sep, lineterminator="\n")

            writer.writerow(header)
            writer.writerows(data)


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
       #

       for i in self.current_param_db:
         if self.split_columns:
           for column in self.output_column:
        #      print ":::", self.output_column
              gen_d = utils.generate_string(i, self.current_param_db.separated_vars, joining_string = "/" )
              if gen_d :  gen_d+= "/"
              gen_s = utils.generate_string(i, self.current_param_db.coalesced_vars, joining_string = "_" )
              output_fname = utils.fix_filename(  "%s%s-%s-%s.csv"%(gen_d, self.table, column, gen_s) )
              d,f = os.path.split(output_fname)
              if d != "" and not os.path.exists(d): os.makedirs(d)

              writer = csv.writer(open(output_fname, open_type), delimiter=self.sep, lineterminator="\n")
              if "header" in flags and "append" not in flags:
                  writer.writerow(
                      self.current_param_db.table_header(table=self.table, output_column=self.output_column) )
              data = self.current_param_db.result_table(restrict_to_values = i, table = self.table, raw_data = self.raw_data, restrict_by_val = self.restrict_by_val, output_column = [column] )

              writer.writerows(data)
         else:

           
           gen_d = utils.generate_string(i, self.current_param_db.separated_vars, joining_string = "/" )
           if gen_d:  gen_d+= "/"

           output_fname = utils.fix_filename( "%s%s_%s.csv"%(gen_d, self.current_param_db.base_name, self.table ) )


           d,f = os.path.split(output_fname)
           if d != "" and not os.path.exists(d): os.makedirs(d)
#           output_file = open(output_fname , open_type)
           if "only-id" in flags:
               header, data= self.current_param_db.result_id_table(table = self.table )

           else:
               data = self.current_param_db.result_table(restrict_to_values = i, table = self.table, raw_data = self.raw_data, restrict_by_val = self.restrict_by_val, output_column = self.output_column )
               header = self.current_param_db.table_header(table = self.table, output_column= self.output_column )
           print "    table: %s"%output_fname

#           print data, header

           writer = csv.writer(open(output_fname, open_type), delimiter=self.sep, lineterminator="\n")
           if "header" in flags and "append" not in flags:
               writer.writerow( header )
           writer.writerows( data )
#           np.savetxt( output_file, data )

    def do_setup_vars_in_table(self,c):
        """sets up the variables that output into the table as independent columns
           save_table [-single_flag] 
           FLAGS::: -all:        puts all variables in the output_table 
                   -restore:    puts only the last variable in the output_table
          """
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return
        flags,c = self.parse_command_line(c)
        if "all" in flags:
            self.current_param_db.setup_vars_in_table(",".join(self.current_param_db.variables) )
        elif "restore" in flags:
            self.current_param_db.setup_vars_in_table(self.current_param_db.variables[-1])
        else:    
            self.current_param_db.setup_vars_in_table(c)


    def do_setup_vars_separated(self,c):
        """sets up which variables are going to have a separated directory
           save_table [-single_flag] 
           FLAGS::: -restore:    puts only the last variable in the output_table 
                    -empty:      sets nothing as separated variables   """
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return
        flags,c = self.parse_command_line(c)
        if "restore" in flags:
            self.current_param_db.setup_vars_separated(",".join(self.current_param_db.variables[:-1]))
        elif "empty" in flags:
            self.current_param_db.setup_vars_separated("")
        else:    
            self.current_param_db.setup_vars_separated(c)


    def do_setup_vars_coalesced(self,c):
        """sets up which variables are coalesced into the same file
           save_table [-single_flag] 
           FLAGS::: -restore:    puts only the last variable in the output_table 
                    -empty:      sets nothing as separated variables  """
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return

        flags,c = self.parse_command_line(c)
        if "restore" or "empty" in flags:
            self.current_param_db.setup_vars_coalesced("")
        elif "empty" in flags:
            self.current_param_db.setup_vars_coalesced("")
        else:    
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
            self.current_param_db.query_master_db('UPDATE entities SET varies=1 WHERE name = ?', v)
        self.current_param_db.init_db()

    def do_set(self, c):
        """sets a VAR1=VALUE1[:VAR2=VALUE2]
        sets a value in the currently loaded database
        If key = sep (separator for csv table) "blank" means a single space"""

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
            if k == "sep":
                if v == "blank":
                    self.sep = " "
                else:
                    self.sep = v
                return
            self.__dict__[k] = ret[k]

    def do_conf(self,c):
        """prints the current configuration"""
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... skipping")
            return
        print " -- db: %s"%( os.path.relpath( self.current_param_db.full_name , ".") )
        print "  + variables = %s "%( ", ".join(self.current_param_db.variables ) )
        print "  + entities = %s "%( ", ".join(self.current_param_db.entities ) )
        
        print "  + table   = %s (tables found: %s) "%(self.table, ", ".join(self.current_param_db.output_column.keys())) 
        print "  + columns = %s "%( ", ".join( self.current_param_db.output_column[self.table]  ) )
        print "  + split_columns = %s  / raw_data = %s / restrict_by_val = %s"%(self.split_columns, self.raw_data, self.restrict_by_val)
        print "  + vars (separated-coalesced-in_table) = %s - %s - %s "%(self.current_param_db.separated_vars, self.current_param_db.coalesced_vars, self.current_param_db.in_table_vars)


if __name__ == '__main__':
    cmd_line = SPGResultsCommandLine()
    if len(sys.argv) == 1:
        cmd_line.cmdloop()
    else:
        cmd_line.onecmd(" ".join(sys.argv[1:]))
        


 