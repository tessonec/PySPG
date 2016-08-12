#!/usr/bin/python


import spg.utils as utils
from spg.simulation import MultIteratorDBBuilder, ParameterEnsemble
# from spg.master import SPGMasterDB
from spg.cmdline import SPGDBCommandLine
# from spg import VAR_PATH, RUN_DIR
import spg.utils as utils

#import sqlite3 as sql
import sys, optparse
import os, os.path


import fnmatch
#
#
# class SPGDBCommandLine(DBCommandLine):
#     """DB command handler"""
#
#
#     def __init__(self):
#         DBCommandLine.__init__(self)
#         self.prompt = "| spg-db :::~ "
#     #    self.possible_keys = ['weight', 'repeat',  'status', 'queue']
#
#         self.possible_keys = ['weight', 'queue']
#
#     def do_init(self, c):
#         """init [--flag ...] PARAMETERS_NAME|DB_NAME [VAR1=VALUE1[:VAR2=VALUE2]]
#         Generates a new database out of a simulation.dat
#         FLAGS::: --purge:         deletes the spgql database, if it already exists
#                  --repeat=REPEAT  repeats the parameter generation REPEAT times
#         """
#         if len(c.strip()) == 0:
#             utils.newline_msg("WRN", "init called without arguments")
#             return
#         flags,c = self.parse_command_line(c)
#         if len(c) == 0:
#             utils.newline_msg("WRN", "init called without database")
#             return
#
#         i_arg = c[0]
#
#         full_name, path, base_name, extension = utils.translate_name(i_arg)
#             # print "do_init::: ",self.translate_name(i_arg)
#         db_name = "%s/%s.spgql" % (path, base_name)
#         sim_name = "%s/%s.spg" % (path, base_name)
#         if os.path.exists(db_name) and "purge" not in flags:
#             utils.newline_msg("ERR", "database '%s' already exists. Cannot init it twice"%utils.shorten_name(db_name))
#             return
#         if not os.path.exists(sim_name):
#             utils.newline_msg("ERR", "configuration '%s' doesn't exist. Cannot init it"%utils.shorten_name(sim_name))
#             return
#
#         if "purge" in flags:
#
#             self.do_deregister(i_arg)
#             try:
#                 os.remove(db_name)
#             except:
#                 utils.newline_msg("WRN", "database '%s' could not be removed... skipping"%db_name)
#
#         if 'repeat' in flags:
#             repeat = int(flags['repeat'])
#         else:
#             repeat = 1
#
#         parser = MultIteratorDBBuilder(db_name=db_name)
#         parser.init_db(  )
#         parser.fill_status(repeat = repeat )
#
#         self.current_param_db = ParameterEnsemble( db_name , init_db=True)
#         self.current_param_db.repeat = repeat
#
#         if len(c) >1: self.do_set( ":".join( c[1:] ) )
#         self.master_db.write_ensemble_to_master(self.current_param_db)
#
#         self.master_db.update_list_ensemble_dbs()
#
#         print " **-- init       - %d: '%s'   " % (self.current_param_db.id, self.current_param_db.full_name)
#
#
#     def complete_init(self, text, line, begidx, endidx):
#
#         completions = fnmatch.filter( os.listdir("."), ".spgql" )
#         completions.extend( fnmatch.filter( os.listdir("."), "*.spg" ) )
#         if text:
#             completions = [ f
#                             for f in completions
#                             if f.startswith(text)
#                             ]
#         return completions
#
#     def do_register(self,c):
#         """registers a given results database into the master database"""
#         flags, db_name = self.parse_cmd_line(c)
#         if db_name is None :
# #            utils.newline_msg("ERR", "no database supplied nor currently set... skipping")
#             return
#
#         if self.master_db.result_dbs.has_key( db_name ):
#             utils.newline_msg("WRN", "skipping... database '%s' is already registered"%utils.shorten_name( db_name ), 2)
#             return
#
#         self.current_param_db = ParameterEnsemble( db_name, init_db=True )
#
#         self.master_db.write_ensemble_to_master(self.current_param_db)
#         self.master_db.update_list_ensemble_dbs()
#         print " *--- registered - %d: '%s'   "%( self.current_param_db.id ,  self.current_param_db.full_name )
#
#     def complete_register(self, text, line, begidx, endidx):
#
#         return self.complete_init(text, line, begidx, endidx)
#
#     def do_clean(self, c):
#         """clean [-flag ...] PARAMETERS_NAME|DB_NAME [VAR1=VALUE1[:VAR2=VALUE2]]
#            if not arguments are given  sets all the rows in run_status with status R, E to N
#            FLAGS::: --all: sets all the rows in run_status to N  """
#         #:::~ OK, as of 13.10.11
#
#         flags, db_name = self.parse_cmd_line(c)
#         if db_name is None :
# #            utils.newline_msg("ERR", "no database supplied nor currently set... skipping")
#             return
#
#         ensemble = self.get_db_from_cmdline(db_name)
#
#         if "all" in flags:
#             ensemble.execute_query('UPDATE run_status SET status = "N"  ')
#         else :
#             ensemble.execute_query('UPDATE run_status SET status = "N" WHERE status ="R" OR status ="E" ')
#
#
#     def complete_clean(self, text, line, begidx, endidx):
#
#         return self.complete_init(text, line, begidx, endidx)
#
#     def parse_cmd_line(self, c):
#         # :::~ FIXME! name confusing with parse_command_line
#         try:
#             flags, [db_name] = self.parse_command_line(c)
#         except:
#             utils.newline_msg("ERR", "a single file was expected or could not parse flags" )
#             return flags, None
#
#         if db_name.isdigit():
#             id = int(db_name)
#             rdb = self.master_db.result_dbs
#             filtered = [x for x in rdb if rdb[x]['id'] == id]
#             if filtered:
#                 db_name = filtered[0]
#             else:
#                 utils.newline_msg("ERR", "database with id '%s' doesn't exist." % db_name)
#                 return flags, None
#         else:
#             if not db_name:
#                 db_name = self.current_param_db.full_name
#             else:
#
#                 full_name, path, base_name, extension = utils.translate_name(db_name)
#                 # print "do_init::: ",self.translate_name(i_arg)
#                 db_name = "%s/%s.spgql" % (path, base_name)
#                 # sim_name = "%s/%s.spg" % (path, base_name)
#                 if not os.path.exists(db_name):
#                     utils.newline_msg("ERR", "database with name '%s' doesn't exist." % db_name)
#                     return flags, None
#         return flags, db_name
#
#     def do_deregister(self, c):
#         """remove current_db|FILENAME|_ID_
#            deregisters a simulation file simulations. Does not remove them from disk except --purge is used
#            FLAGS::: --purge:         deletes the spgql database, if it already exists"""
#
#         flags, db_name = self.parse_cmd_line(c)
#         if db_name is None :
#             utils.newline_msg("ERR", "no database supplied nor currently set... skipping")
#             return
#
# #        ensemble = self.get_db_from_cmdline(db_name)
#
#         if not self.current_param_db is None and self.current_param_db.full_name == db_name:
#             self.current_param_db = None
#
#         if "purge" in flags and os.path.exists(db_name):
#             os.remove(db_name)
#
#         self.master_db.query_master_db("DELETE FROM dbs WHERE full_name = ?", db_name )
#         if self.master_db.result_dbs.has_key(db_name):
#             del self.master_db.result_dbs[db_name]
#         # :::~ FIXME
#         self.master_db.synchronise_master_db()
#
#     def complete_deregister(self, text, line, begidx, endidx):
#
#         return self.complete_init(text, line, begidx, endidx)
#
#
#     def do_set(self, c):
#         """set  VAR1=VALUE1 VAR2=VALUE2
#         sets some values in the currently loaded database
#         FLAGS::: --help, the possible keys are printed """
#
#         # print c
#         flags, c = self.parse_command_line(c)
#
#
#         if "help" in flags:
#             print utils.newline_msg("HELP", " possible_keys = %s"%self.possible_keys )
#             return
#
#         if not self.current_param_db:
#             utils.newline_msg("WRN", "not database loaded... skipping")
#             return
#
#         for iarg in c:
#             ret = utils.parse_to_dict(iarg, allowed_keys=self.possible_keys)
#             if not ret:
#                 utils.newline_msg("ERR", "'%s' not understood"%iarg)
#                 return
#
#             #if k == "repeat": continue # repeat is not in the master db (should it be added)
#             for k in ret:
#                 self.current_param_db.__dict__[k] = ret[k]
#                 self.master_db.query_master_db('UPDATE dbs SET %s= ? WHERE id = ?' % k, ret[k], self.current_param_db.id)
#
#
#     def __set_status(self, c, st):
#         # if not c:
#         #     ls_res_db = [ self.current_param_db.full_name ]
#         # else:
#         #     ls_res_db = self.filter_db_list( filter = c )
#         # if not ls_res_db: return
#         #
#         # for i in ls_res_db:
#
#         flags, db_name = self.parse_cmd_line(c)
#         if db_name is None :
#             utils.newline_msg("ERR", "no database supplied nor currently set... skipping")
#             return
#
#         ensemble = self.get_db_from_cmdline(db_name)
#         ensemble.status = st
#
#         print " +--- status -  '%s' : %s  " % (db_name, st)
#
#         self.master_db.query_master_db('UPDATE dbs SET status= ? WHERE full_name = ?', st, db_name)
#     #
#     # def do_stop(self, c):
#     #     """stops the currently loaded registered database"""
#     #     self.__set_status(c, 'S')
#     #
#     def do_start(self, c):
#         """starts the currently loaded registered database"""
#         self.__set_status(c, 'R')
#
#     def do_pause(self, c):
#          """pauses the currently loaded registered database"""
#          self.__set_status(c, 'P')
#
#     def do_set_jobs(self, c):
#         """sets the maximum number of jobs running concurrently
#            usage: N_JOBS"""
#         c = c.split()
#         if len(c) == 1:
#             max_jobs = int(c[0])
#             self.master_db.query_master_db('UPDATE queues SET max_jobs= ? WHERE name = "default"', max_jobs)
#
#     def do_get_jobs(self,c):
#         """returns the number of jobs that would concurrently run in a multi-threaded run"""
#         nj, = self.master_db.query_master_fetchone('SELECT max_jobs FROM queues WHERE name = "default"')
#         print " +--- no_jobs = %d "%nj
#
#
#     def do_info(self, c):
#         """info REGEXP
#            prints the information of the results databases, filtered by a regular expression, or its id """
#
#         flags, db_name = self.parse_cmd_line(c)
#         if db_name is None :
#             #utils.newline_msg("ERR", "no database supplied nor currently set... skipping")
#             return
#
#         ensemble = self.get_db_from_cmdline(db_name)
#
#         db_status = ensemble.get_updated_status()
#
#         param_db_id = self.master_db.query_master_fetchone("SELECT id FROM dbs WHERE full_name = ?", db_name)
#         if param_db_id is None:
#             param_db_id = "X"
#         else:
#             [param_db_id,] = param_db_id
#
#
#
#         print " ---%5s: %s" % (param_db_id , utils.shorten_name(db_name))
#         frac_done = float(db_status['process_done']) / float(db_status['value_set'])
#
#         n_repet = db_status['value_set_with_rep'] / db_status['value_set']
#
#         print "   -+ status = %s /  weight: %5.5f "%(ensemble.status, ensemble.weight)
#         print "   -+ total  = %d*%d / done: %d (%.5f) - running: %d - error: %d " % (
#             db_status['value_set'], n_repet, db_status['process_done'], frac_done,
#             db_status['process_running'],db_status['process_error'])
#         try:
#             print "   -+ time   = %f / mean: %f - min: %f - max: %f"%(db_status['total_run_time'],db_status['avg_run_time'],db_status['min_run_time'],db_status['max_run_time'])
#         except:
# 	    pass

if __name__ == '__main__':
    cmd_line = SPGDBCommandLine()

    if len(sys.argv) == 1:
        cmd_line.cmdloop()
    else:
        cmd_line.onecmd(" ".join(sys.argv[1:]))
        


