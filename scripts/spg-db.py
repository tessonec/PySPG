#!/usr/bin/python


import spg.utils as utils
from spg.simulation import EnsembleDBBuilder, ParameterEnsemble
# from spg.master import SPGMasterDB
from spg.cmdline import DBCommandLine
# from spg import VAR_PATH, RUN_DIR
import spg.utils as utils

#import sqlite3 as sql
import sys #, optparse
import os, os.path


import fnmatch


class SPGDBCommandLine(DBCommandLine):
    """DB command handler"""

 
    def __init__(self):
        DBCommandLine.__init__(self)
        self.prompt = "| spg-db :::~ "
        self.possible_keys = ['weight', 'repeat',  'status', 'queue']



    def do_init(self, c):
        """init [-flag ...] PARAMETERS_NAME|DB_NAME [VAR1=VALUE1[:VAR2=VALUE2]]
        Generates a new database out of a simulation.dat
        FLAGS::: -skip-master: the new results.sqlite is created, but gets not registered in master
                 -purge:       deletes the results.sqlite db, if it already existed 
        """
        
        flags,c = self.parse_command_line(c)
        i_arg = c[0]
        
        full_name, path, base_name, extension = utils.translate_name(i_arg)
            # print "do_init::: ",self.translate_name(i_arg)
        db_name = "%s/%s.spgql" % (path, base_name)
        sim_name = "%s/%s.spg" % (path, base_name)
        if os.path.exists(db_name) and "purge" not in flags:
            utils.newline_msg("ERR", "database '%s' already exists. Cannot init it twice"%os.path.relpath(db_name, "."))
            return
        if not os.path.exists(sim_name):
            utils.newline_msg("ERR", "configuration '%s' doesn't exist. Cannot init it"%os.path.relpath(sim_name, "."))
            return

        if "purge" in flags:
            try:
                os.remove(db_name)
            except:
                utils.newline_msg("WRN", "database '%s' could not be removed... skipping"%db_name)

            self.do_remove(i_arg)


        if len(c) >1: self.do_set( ":".join( c[1:] ) )
        if 'repeat' in flags:
            repeat = int(flags['repeat'])
        else:
            repeat = 1

        parser = EnsembleDBBuilder(stream = open(sim_name), db_name=db_name)
        parser.init_db(  )
        parser.fill_status(repeat = repeat )

        self.current_param_db = ParameterEnsemble( db_name )
        self.current_param_db.repeat = repeat


        if not "skip-master" in  flags:
            self.master_db.write_ensemble_to_master(self.current_param_db)
            self.current_param_db.id = self.master_db.cursor.lastrowid
            self.master_db.update_list_ensemble_dbs()



    def complete_init(self, text, line, begidx, endidx):    
        
        completions = fnmatch.filter( os.listdir("."), ".spgql" )
        completions.extend( fnmatch.filter( os.listdir("."), "*.spg" ) )
        if text:
            completions = [ f
                            for f in completions
                            if f.startswith(text)
                            ]
        return completions
        
    def do_register(self,c):
        """registers a given results database into the master database"""
        c = c.split()
        i_arg = c[0]
        try: 
            full_name, path, base_name, extension = utils.translate_name(i_arg)
            db_name = "%s/%s.spgql" % (path, base_name)
            sim_name = "%s/%s.spg" % (path, base_name)

        except:
            utils.newline_msg("WRN", "database '%s' already registered"%self.shorten_name( db_name ), 2)
            return 

        self.current_param_db = ParameterEnsemble( db_name ) 
        if len(c) >1: 
            self.do_set( ":".join( c[1:] ) )

        self.master_db.write_ensemble_to_master(self.current_param_db)
        self.current_param_db.id = self.master_db.cursor.lastrowid
        self.master_db.update_list_ensemble_dbs()
        print " *--- registered '%s' with id=%d  "%(   self.current_param_db.full_name, self.current_param_db.id )
        

    def do_clean(self, c):
        """clean [-flag ...] PARAMETERS_NAME|DB_NAME [VAR1=VALUE1[:VAR2=VALUE2]]
           if not arguments are given  sets all the rows in run_status with status R, E to N
           FLAGS::: --all: sets all the rows in run_status to N  """
        #:::~ OK, as of 13.10.11

        flags, c = self.parse_command_line(c)

        if len(c) > 0:
            i_arg = c[0]

            try:
                full_name, path, base_name, extension = utils.translate_name(i_arg)
                # print "do_init::: ",self.translate_name(i_arg)
                db_name = "%s/%s.spgql" % (path, base_name)
                sim_name = "%s/%s.spg" % (path, base_name)
                self.current_param_db = ParameterEnsemble(db_name)
            except:
                utils.newline_msg("ERR", "results db '%s' doesn't exist. Cannot load it")
                return

        if not self.current_param_db:
                utils.newline_msg("WRN", "current db not set... skipping")
                return
                
        if "all" in flags:
            self.current_param_db.execute_query('UPDATE run_status SET status = "N"  ')
        else :
            self.current_param_db.execute_query('UPDATE run_status SET status = "N" WHERE status ="R" OR status ="E" ')
            

    def do_remove(self, c):
        """removes some results.sqlite databases (can be filtered through regular expressions, or by id) from the list of registered dbs"""
        #:::~ OK, as of 13.10.11
        if not c:
            ls_res_db = [ self.current_param_db.full_name ]
        else:
            ls_res_db = self.filter_db_list( filter = c )
        if not ls_res_db: return

        self.current_param_db = None
        
        for i in ls_res_db: 
            # print i
            self.master_db.query_master_db("DELETE FROM dbs WHERE full_name = ?", i)
            del self.master_db.result_dbs[i]
        self.master_db.synchronise_masted_db()
 
  #  def complete_remove(self, text, line, begidx, endidx):
         #:::~ FIXME: doesn't work. Why?
  #      return self.complete(text)
    
    def do_set(self, c):
        """set  VAR1=VALUE1[:VAR2=VALUE2]
        sets some values in the currently loaded database
        FLAGS::: -help, the possible keys are printed """
        
        
        flags, c = self.parse_command_line(c)
        c = c[0]
        
        if "help" in flags:
            print utils.newline_msg("HELP", " possible_keys = %s"%self.possible_keys )
            return 
            
        if not self.current_param_db: 
            utils.newline_msg("WRN", "current db not set... skipping")
            return 
        
        ret = utils.parse_to_dict(c, allowed_keys=self.possible_keys)
        if not ret: 
            return
        
        for k in ret.keys():
            self.current_param_db.__dict__[k] = ret[k]
            if k == "repeat": continue # repeat is not in the master db (should it be added)
            self.master_db.query_master_db('UPDATE dbs SET %s= ? WHERE id = ?' % k, ret[k], self.current_param_db.id)


    def __set_status(self, c, st):
        if not c:
            ls_res_db = [ self.current_param_db.full_name ]
        else:
            ls_res_db = self.filter_db_list( filter = c )
        if not ls_res_db: return
        
        for i in ls_res_db: 
            self.current_param_db.status = st
            self.master_db.query_master_db('UPDATE dbs SET status= ? WHERE id = ?', st, self.current_param_db.id)

    def do_stop(self, c):
        """stops the currently loaded registered database"""
        self.__set_status(c, 'S')
                
    def do_start(self, c):
        """starts the currently loaded registered database"""
        self.__set_status(c, 'R')
                
    def do_pause(self, c):
         """pauses the currently loaded registered database"""
         self.__set_status(c, 'P')

    def do_set_jobs(self, c):
        """sets the maximum number of jobs running concurrently
           usage: N_JOBS"""
        c = c.split()
        if len(c) == 1:
            max_jobs = int(c[0])
            self.master_db.query_master_db('UPDATE queues SET max_jobs= ? WHERE name = "default"', max_jobs)

    def do_get_jobs(self,c):

        nj, = self.master_db.query_master_fetchone('SELECT max_jobs FROM queues WHERE name = "default"')
        print " +--- no_jobs = %d "%nj


    def do_info(self, c):
        """info REGEXP
           prints the information of the results databases, filtered by a regular expression, or its id """
        if not c:
            if not self.current_param_db:
                return
            else:
                ls_res_db = [self.current_param_db.full_name]
        else:
            ls_res_db = self.filter_db_list(filter=c)
        if not ls_res_db: return

        for i in ls_res_db:
            curr_db = self.master_db.result_dbs[i]

            self.master_db.write_ensemble_to_master(curr_db)

            print " ---%5d: %s" % (curr_db.id, os.path.relpath(curr_db.full_name, "."))
            frac_done = float(curr_db.stat_processes_done) / float(curr_db.stat_values_set)

            n_repet = curr_db.stat_values_set_with_rep / curr_db.stat_values_set

            print "   -+ status: %s /  weight: %5.5f "%(curr_db.status, curr_db.weight)
            print "   -+ total = %d*%d / D: %d (%.5f) - R: %d - E: %d " % (
            curr_db.stat_values_set, n_repet, curr_db.stat_processes_done, frac_done,
            curr_db.stat_processes_running, curr_db.stat_processes_error)


if __name__ == '__main__':
    cmd_line = SPGDBCommandLine()
    if len(sys.argv) == 1:
        cmd_line.cmdloop()
    else:
        cmd_line.onecmd(" ".join(sys.argv[1:]))
        


