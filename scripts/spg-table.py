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
        self.prompt = "| spg-table :::~ "
        
#        self.possible_keys = set( [ "raw_data", "split_colums", "restrict_by_val", "table", "split_columns", "sep"] )

        self.sep = ","

        self.current_param_db = None



    def do_load(self,c):
        """load DB_NAME|DB_ID
        loads one of the registered databases from the master"""
        flags, args = self.parse_command_line(c)
        if len(args) >1:
            utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
            return

        ret = self.get_db(args[0])

        if ret:
            self.current_param_db = ret
            print " --- loaded: '%s'"% utils.shorten_name(ret.full_name)
            os.chdir(self.current_param_db.path)
        else:
            utils.newline_msg("ERR", "'%s' does not exist"%ret, 2)


    def do_set_separator(self, c):
        """
        Usage:
            set_sep SEPARATOR
        Sets the separator for the output tables. It accepts two special values 'blank' and 'tab' with obvious effect

        """

        if c == "blank":
            self.sep = " "
        elif c == "tab":
            self.sep = "\t"
        else:
            self.sep = c


    def do_import_output_table(self, c):
        """
        Usage:
            import_output_table table_name.csv database.spqql
        Loads the results output in table_name.csv into database.spgql

        """

        flags, args = self.parse_command_line(c)


        if not self.current_param_db:
            if len(args) != 2:
                utils.newline_msg("WRN", "database not loaded nor provided. skipping",2)
                return

            self.current_param_db = self.get_db(args[1])
        elif len(args) > 1:
            utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
            return


        self.current_param_db.update_results_from_data( args[0], sep = self.sep )
    #
    # def do_export_output_csv(self, c):
    #     """save_csv [-flag1 -flag2] f1 f2 g3
    #        saves the table values in ascii format
    #        FLAGS::: -raw:        do not average values for same parameter set
    #     """
    #     flags, cs = self.parse_command_line(c)
    #     if "sep" in flags:
    #         if flags["sep"] == "blank":
    #             self.sep = " "
    #         else:
    #             self.sep = flags["sep"]
    #
    #     for c in cs:
    #         self.do_load(c)
    #         if "raw_data" in flags:
    #             self.do_set("raw_data=True")
    #         self.do_setup_vars_in_table("--all")
    #         if "only-id" in flags:
    #             self.do_save_table("--header --only-id %s"  % c)
    #         else:
    #             self.do_save_table("--header %s" % c)

    def do_save_input_table(self,c):
        flags, args = self.parse_command_line(c)


        if not  self.current_param_db:
            if len(args) == 0:
                utils.newline_msg("WRN", "database not loaded nor provided. skipping", 2)
                return
            elif len(args) > 1:
                utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
                return
            else:
                self.do_load(args[0])
        else:
            if len(args) > 0:
                utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
                return


        if "sep" in flags:
            self.do_set_separator( flags["sep"] )

        self.do_setup_vars_in_table("--all")
        header, data = self.current_param_db.values_set_table()

        output_fname = utils.fix_filename("%s/%s_valueset.csv" % (self.current_param_db.path, self.current_param_db.base_name))
        print "  +- table:  '%s'" % output_fname
        writer = csv.writer(open(output_fname, "w"), delimiter=self.sep, lineterminator="\n")

        writer.writerow(header)
        writer.writerows(data)


    def do_save_table(self,c):
       """save_table [-flag1 -flag2] 
          saves the table values in ascii format. default is averaging column values by variable values
          FLAGS::: --noheader:    does not output column names in the output file
                   --raw:         raw  values without average
                   --full:        all simulation ids and variables are output in table (implies raw)
                   --id:          only the id is output
                   --sep:         column separator ('blank' for space)
       """
       flags, args = self.parse_command_line(c)

       if not self.current_param_db:
           if len(args) == 0:
               utils.newline_msg("WRN", "database not loaded nor provided. skipping", 2)
               return
           elif len(args) > 1:
               utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
               return
           else:
               self.do_load(args[0])
       else:
           if len(args) > 0:
               utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
               return

       if len( set([ 'raw', "full", "id" ]).intersection( flags ) ) > 1:
           utils.newline_msg("ERR", "only one flag [raw, full, id] can be active at a time" )
           return
       table_selector = "grouped_vars"
       if "raw" in flags:
           table_selector = "raw_vars"
       elif "id" in flags:
           table_selector = "only_uid"
       elif "full" in flags:
           table_selector = "full"

       if "sep" in flags:
           self.do_set_separator(flags["sep"])

       for outer_params in self.current_param_db:
           for table in self.current_param_db.table_columns.keys():
               # print i
               gen_d = utils.generate_string(outer_params, self.current_param_db.separated_vars, joining_string = "/" )
               if gen_d:
                   gen_d+= "/"

               gen_s = utils.generate_string(outer_params, self.current_param_db.coalesced_vars, joining_string="_")

               output_fname = utils.fix_filename("%s%s_%s-%s.csv" % (gen_d, self.current_param_db.base_name, table, gen_s))

               d,f = os.path.split(output_fname)
               if d != "" and not os.path.exists(d): os.makedirs(d)

               header, data= self.current_param_db.result_table(table = table , table_selector = table_selector)

               print "  +- table:  '%s'" % (output_fname)

               writer = csv.writer(open(output_fname, "w"), delimiter=self.sep, lineterminator="\n")
               if  not( "noheader" in flags or "append"  in flags):
                   writer.writerow( header )
               writer.writerows( data )
    #           np.savetxt( output_file, data )

    def do_setup_vars_in_table(self,c):
        """sets up the variables that output into the table as independent columns
           save_table [-single_flag] 
           FLAGS::: --all:        puts all variables in the output_table
                    --restore:    puts only the last variable in the output_table
          """
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... it must be loaded first",2)
            return
        flags, args = self.parse_command_line(c)
        if "all" in flags:
            self.current_param_db.setup_vars_in_table(",".join(self.current_param_db.variables) )
        elif "restore" in flags:
            self.current_param_db.setup_vars_in_table(self.current_param_db.variables[-1])
        else:    
            self.current_param_db.setup_vars_in_table( args[0] )


    def do_setup_vars_separated(self,c):
        """sets up which variables are going to have a separated directory
           save_table [-single_flag] 
           FLAGS::: -restore:    puts only the last variable in the output_table 
                    -empty:      sets nothing as separated variables   """
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... it must be loaded first",2)
            return
        flags, args = self.parse_command_line(c)
        if "restore" in flags:
            self.current_param_db.setup_vars_separated(",".join(self.current_param_db.variables[:-1]))
        elif "empty" in flags:
            self.current_param_db.setup_vars_separated("")
        else:    
            self.current_param_db.setup_vars_separated(args[0])


    def do_setup_vars_coalesced(self,c):
        """sets up which variables are coalesced into the same file
           save_table [-single_flag] 
           FLAGS::: -restore:    puts only the last variable in the output_table 
                    -empty:      sets nothing as separated variables  """
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... it must be loaded first",2)
            return
        flags, args = self.parse_command_line(c)

        if ("restore" in flags) or ("empty" in flags):
            self.current_param_db.setup_vars_coalesced("")
        # elif "empty" in flags:
        #     self.current_param_db.setup_vars_coalesced("")
        else:    
            self.current_param_db.setup_vars_coalesced(args[0])
        

    def do_setup_output_column(self,c):
        """sets which columns to generate output from"""
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... it must be loaded first",2)
            return
        flags, args = self.parse_command_line(c)
        cols = args[0].split(",")
        if not set(cols).issubset(  self.current_param_db.table_columns[self.table] ):
            utils.newline_msg("ERR", "the column(s) is (are) not in the output: %s"%( set(cols) - set(  self.current_param_db.table_columns[self.table] )) )
        self.table_columns = cols

    def do_set_as_var(self,c):
        """ Sets a (set of) non-variables as variable """
        if not self.current_param_db:
            utils.newline_msg("WRN", "current db not set... it must be loaded first",2)
            return
        flags, args = self.parse_command_line(c)
        ls_vars = args[0].split(",")
        if not set(ls_vars).issubset( set(self.current_param_db.entities) ):
            utils.newline_msg("VAR", "the variables '%s' are not recognised"%set(ls_vars)-set(self.current_param_db.entities) )
            return
        for v in ls_vars:
            self.current_param_db.query_master_db('UPDATE entities SET varies=1 WHERE name = ?', v)
        self.current_param_db.init_db()

    def do_set_table(self, c):
        """sets the output table
        sets a value in the currently loaded database
        If key = sep (separator for csv table) "blank" means a single space"""
        c = c.strip()

        if c == "help":
            utils.newline_msg("HELP", " possible_keys = %s"%self.possible_keys )
            return 
        
        if not self.current_param_db: 
            utils.newline_msg("WRN", "current db not set... skipping",2)
            return 
        
        if c not in self.current_param_db.table_columns.keys():
            utils.newline_msg("ERR", "table '%s' not among the ones found in the DB: (%s)"%(c, ", ".join(self.current_param_db.table_columns.keys())) )
            return
        self.table_columns = self.current_param_db.table_columns[ c ][1:]

    def do_conf(self,c):
        """prints the current configuration"""

        flags, args = self.parse_command_line(c)

        if not self.current_param_db:
            if len(args) == 0:
                utils.newline_msg("WRN", "database not loaded nor provided. skipping", 2)
                return
            elif len(args) > 1:
                utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
                return
            else:
                self.do_load(args[0])
        else:
            if len(args) > 0:
                utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
                return

        print " -- db: %s"%( os.path.relpath( self.current_param_db.full_name , ".") )
        print "  + variables = %s "%( ", ".join(self.current_param_db.variables ) )
        print "  + entities = %s "%( ", ".join(self.current_param_db.entities ) )
        
        print "  + tables found: %s "%(", ".join(self.current_param_db.table_columns.keys()))
        print "  + vars (separated-coalesced-in_table) = %s - %s - %s "%(self.current_param_db.separated_vars, self.current_param_db.coalesced_vars, self.current_param_db.vars_in_table)


if __name__ == '__main__':
    cmd_line = SPGResultsCommandLine()
    if len(sys.argv) == 1:
        cmd_line.cmdloop()
    else:
        cmd_line.onecmd(" ".join(sys.argv[1:]))
        


 