#!/usr/bin/env python3




# from spg import RUN_DIR

import sys, os.path
import cmd

import re, fnmatch
from setuptools.command.saveopts import saveopts

import spg.utils as utils
from spg.simulation import ParameterEnsemble
from spg.master import SPGMasterDB
from spg.simulation import MultIteratorDBBuilder, ParameterEnsemble

# :::~ TODO: Remove unnecessary current_param_db, turn it into a string





class BaseSPGCommandLine(cmd.Cmd):
    """This is a basic command line for SPG based programs. It contains basic functionality"""
 
    def __init__(self, EnsembleConstructor = ParameterEnsemble):
        cmd.Cmd.__init__(self)
        self.EnsembleConstructor = EnsembleConstructor 


    def parse_command_line(self, st):
        """returns command, the flags set under a command and the arguments"""

        st = st.strip().split()
        cmd = []
        flags = {}
        
        
        for ic in st:
            if ic[:2] == "--":
                st = ic[2:]
                if "=" in st:
                    k,v = st.split("=")
                    flags[k] = v
                else:
                    flags[st] = None
            else:
                cmd.append( ic )
        return flags, cmd


    def get_db(self, c):
        """it returns the db name (or None) of a database identified either from its id or """

        try:
                full_name, path, base_name, extension = utils.translate_name(c.strip())
                db_name = "%s/%s.spgql" % (path, base_name)
                sim_name = "%s/%s.spg" % (path, base_name)
        except:
                utils.newline_msg("ERR", "results db '%s' doesn't exist." % c)
                return None

        return self.EnsembleConstructor(db_name, init_db=True)




    def do_ls(self, c):

        full_ls = fnmatch.filter(os.listdir("."), "*.spgql")
        full_ls.extend( fnmatch.filter( os.listdir("."), "*.spg" ) )

        ls_res_db = set()
        ls_keys = set()

        for el in full_ls:
            full_name, path, base_name, extension = utils.translate_name(el)
            full_base = "%s/%s"%(path, base_name)
            if full_base not in ls_keys:
                ls_res_db.add(utils.shorten_name(full_name))
                ls_keys.add( full_base )
        if c:
            ls_res_db = fnmatch.filter(ls_res_db, c )
        if ls_res_db:
            print(" --- cwd matches found")
            for i in sorted( ls_res_db  ):
                print("     : %s "% i)


    def complete_load(self, text, line, begidx, endidx):
        fullnames = set(fnmatch.filter(os.listdir("."), ".spgql"))
        basenames = set()
        for f in fullnames:
            b,e = os.path.splitext( f )
            basenames.add( b )
        for f in fnmatch.filter(os.listdir("."), "*.spg"):
            b, e = os.path.splitext(f)
            if b not in basenames:
                basenames.add(b)
                fullnames.add(f)


        if text:
            return [f
                       for f in sorted(fullnames)
                       if f.startswith(text)
                       ]
        else:
            return sorted(fullnames)




    def do_EOF(self, line):
        return True

    def do_shell(self, line):
        """Runs a shell command"""
        output = os.popen(line).read()
        print(output)

    def do_cd(self,line):
        """ Changes into a given directory """
        try:
            os.chdir(line)
        except:
            utils.newline_msg("DIR", "no directory named '%s'"%line, 2)

    def complete_cd(self, text, line, begidx, endidx):    
        completions =  [x for x in os.listdir(".") if os.path.isdir(x)]
        if text:
            completions = [ f
                            for f in completions
                            if f.startswith(text)
                            ]
        return completions


    def do_run_script(self,c):
        """executes a script file with commands accepted in this cmdline parser"""
        if not os.path.exists(c):
            utils.newline_msg("FIL", "file doesn't exist")
            return
        for l in open(c):
            l = l.strip()
            if not l: continue 
            if l[0] == "#": continue
            
            self.onecmd(l.strip())










class SPGDBCommandLine(BaseSPGCommandLine):
    """A command handler which interfaces a master DB"""
 
    def __init__(self, EnsembleConstructor = ParameterEnsemble):
        BaseSPGCommandLine.__init__(self, EnsembleConstructor)
        self.prompt = "| spg-db :::~ "
        # self.current_param_db = None
        self.master_db =  SPGMasterDB(EnsembleConstructor = EnsembleConstructor)


    def filter_db_list(self, ls = None, filter = None):
        if ls == None:
            ls = list(self.master_db.result_dbs.keys())
        if  re.match("^\d+?$", filter): #:::~ Is filter an integer???
            id = int(filter)
            rdb = self.master_db.result_dbs
            filtered = [ x for x in ls if x in rdb and rdb[x] is not None and rdb[x]['id'] == id  ]
            return filtered

        if filter:
                ret = fnmatch.filter(ls, filter)
        else:
                ret = ls
        return sorted( ret )

    # def get_db(self, c):
    #     """it returns the db name (or None) of a database identified either from its id or """
    #     db_name = c.strip()
    #     if db_name.isdigit():
    #         id = int( db_name )
    #         rdb = self.master_db.result_dbs
    #         filtered = [x for x in rdb if rdb[x] is not None and rdb[x]['id'] == id]
    #         if filtered:
    #             db_name = filtered[0]
    #         else:
    #             utils.newline_msg("ERR", "database with id '%s' doesn't exist." % c)
    #             return None
    #
    #     full_name, path, base_name, extension = utils.translate_name(db_name)
    #     db_name = "%s/%s.spgql" % (path, base_name)
    #     sim_name = "%s/%s.spg" % (path, base_name)
    #     if not os.path.exists(db_name) and not os.path.exists(sim_name):
    #         utils.newline_msg("ERR", "database with name '%s' doesn't exist." % c)
    #         return None
    #     return self.EnsembleConstructor(db_name, init_db=True)
    #     #
    #     #     # if self.master_db.result_dbs.has_key(db_name):
    #     #     #     return self.master_db.result_dbs[db_name]
    #     #     # else:
    #     #     #     utils.newline_msg("WRN", "database '%s' is not registered, loading it anyhow" %  db_name )
    #     # return None
    #

    def get_flags_and_db(self, c,init_db = True):

        flags, args =  self.parse_command_line(c)
        # if len(args)== 1:
        #     utils.newline_msg("ERR", "a single file was expected or could not parse flags")
        #     return flags, args, None

        db_name = args[-1]
        args = args[:-1]


        if db_name.isdigit():
            id = int(db_name)
            rdb = self.master_db.result_dbs
            filtered = [x for x in rdb if rdb[x]['id'] == id]
            if filtered:
                db_name = filtered[0]
            else:
                utils.newline_msg("ERR", "database with id '%s' doesn't exist." % db_name)
                return flags, args.append(db_name), None
        else:
                full_name, path, base_name, extension = utils.translate_name(db_name)
                # print "do_init::: ",self.translate_name(i_arg)
                db_name = "%s/%s.spgql" % (path, base_name)
                # sim_name = "%s/%s.spg" % (path, base_name)
                if not os.path.exists(db_name):
                    utils.newline_msg("ERR", "database with name '%s' doesn't exist." % utils.shorten_name(db_name))
                    return flags, args.append(db_name), None

        return flags, args, self.EnsembleConstructor(db_name, init_db)


    def do_ls(self, c):
        """ls REGEXP|DB_ID
        lists the databases already registered in the master database and the possible ones found in the current directory"""

        ls_res_db = self.filter_db_list( filter = c )

        if ls_res_db: 
            print(" --- registered dbs") 
            for i in sorted( ls_res_db  ):
                # :::~FIXME workaround for non-existing dbs
                curr_db = self.master_db.result_dbs[i]
                short_name = utils.shorten_name(i)

                try:
                    print("%5d: %s (%5.5f)"%(curr_db['id'], short_name  , curr_db['weight'] ))
                except:
                    print("%5d: %s "%(curr_db['id'],  short_name ))

        BaseSPGCommandLine.do_ls(self, c )

    # def do_load(self,c):
    #     """load DB_NAME|DB_ID
    #     loads one of the registered databases from the master"""
    #     c = c.split()
    #     if len(c) >1:
    #         utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
    #         return
    #     ret = self.get_db_from_cmdline(c[0])
    #     if ret:
    #         self.current_param_db = ret
    #         print " --- loaded db '%s'"% utils.shorten_name(self.current_param_db.full_name)
    #     # else:
    #     #     utils.newline_msg("ERR", "db does not exist", 2)

    def do_init(self, c):
        """init [--flag ...] PARAMETERS_NAME|DB_NAME [VAR1=VALUE1[:VAR2=VALUE2]]
        Generates a new database out of a simulation.dat
        FLAGS::: --purge:         deletes the spgql database, if it already exists
                 --repeat=REPEAT  repeats the parameter generation REPEAT times
        """

        flags, db_arg = self.parse_command_line(c)
        if len(db_arg) != 1:
            utils.newline_msg("WRN", "init must be called with a database", 2)
            return
        db_arg = db_arg[0]
        # i_arg = c[0]

        full_name, path, base_name, extension = utils.translate_name(db_arg)
        # print "do_init::: ",self.translate_name(i_arg)
        full_db_name = "%s/%s.spgql" % (path, base_name)
        sim_name = "%s/%s.spg" % (path, base_name)
        if os.path.exists(full_db_name) and "purge" not in flags:
            utils.newline_msg("ERR", "database '%s' already exists. Cannot init it twice" % utils.shorten_name(full_db_name), 2)
            return
        if not os.path.exists(sim_name):
            utils.newline_msg("ERR", "configuration '%s' doesn't exist. Cannot init it" % utils.shorten_name(sim_name), 2)
            return

        if "purge" in flags:
            try:
                self.do_deregister(db_arg)
                os.remove(full_db_name)
            except:
                utils.newline_msg("WRN", "database '%s' could not be removed... skipping" % full_db_name)

        if 'repeat' in flags:
            repeat = int(flags['repeat'])
        else:
            repeat = 1

        parser = MultIteratorDBBuilder(db_name=full_db_name)
        parser.init_db()
        parser.fill_status(repeat=repeat)

        current_param_db = ParameterEnsemble(full_db_name, init_db=True)
        current_param_db.repeat = repeat

        # if len(c) > 1: self.do_set(":".join(c[1:]))
        self.master_db.write_ensemble_to_master(current_param_db)

        self.master_db.update_list_ensemble_dbs()

        print(" **-- init       - %d: '%s'   " % (current_param_db.id, utils.shorten_name(current_param_db.full_name)))

    def complete_init(self, text, line, begidx, endidx):

        completions = fnmatch.filter(os.listdir("."), ".spgql")
        completions.extend(fnmatch.filter(os.listdir("."), "*.spg"))
        if text:
            completions = [f
                           for f in completions
                           if f.startswith(text)
                           ]
        return completions

    def do_register(self, c):
        """registers a given results database into the master database"""
        flags, cmds, ensemble = self.get_flags_and_db(c)
        if ensemble  is None:
            # utils.newline_msg("ERR", "no database supplied ... skipping")
            return

        if ensemble.full_name in self.master_db.result_dbs:
            utils.newline_msg("WRN", "skipping... database '%s' is already registered" % utils.shorten_name(ensemble.full_name), 2)
            return

#        current_param_db = ParameterEnsemble(db_name, init_db=True)

        self.master_db.write_ensemble_to_master(ensemble )
        self.master_db.update_list_ensemble_dbs()
        print(" *--- registered - %d: '%s'   " % (ensemble.id, utils.shorten_name(ensemble.full_name) ))

    def complete_register(self, text, line, begidx, endidx):

        return self.complete_init(text, line, begidx, endidx)

    def do_clean(self, c):
        """clean [-flag ...] PARAMETERS_NAME|DB_NAME [VAR1=VALUE1[:VAR2=VALUE2]]
           if not arguments are given  sets all the rows in run_status with status R, E to N
           FLAGS::: --all: sets all the rows in run_status to N  """
        #:::~ OK, as of 13.10.11

        flags, cmds, ensemble = self.get_flags_and_db(c)
        # ensemble = self.get_db(db_name)
        if ensemble is None:
            # utils.newline_msg("ERR", "database not found... aborting")
            return


        if "all" in flags:
            ensemble.execute_query('UPDATE run_status SET status = "N"  ')
        else:
            ensemble.execute_query('UPDATE run_status SET status = "N" WHERE status ="R" OR status ="E" ')

    def complete_clean(self, text, line, begidx, endidx):

        return self.complete_init(text, line, begidx, endidx)


    def do_deregister(self, c):
        """remove current_db|FILENAME|_ID_
           deregisters a simulation file simulations. Does not remove them from disk except --purge is used
           FLAGS::: --purge:         deletes the spgql database, if it already exists"""

        flags, cmds, ensemble = self.get_flags_and_db(c,init_db=False)
        if ensemble is None:
            # utils.newline_msg("ERR", "no database supplied nor currently set... skipping")
            return

        # ensemble = self.get_db_from_cmdline(db_name)

        # if not self.current_param_db is None and self.current_param_db.full_name == db_name:
        #     self.current_param_db = None

        if "purge" in flags and os.path.exists(ensemble.full_name):
            os.remove(ensemble.full_name)

        self.master_db.query_master_db("DELETE FROM dbs WHERE full_name = ?", ensemble.full_name)
        if ensemble.full_name in self.master_db.result_dbs:
            del self.master_db.result_dbs[ensemble.full_name]
        # :::~ FIXME
        self.master_db.synchronise_master_db()

    def complete_deregister(self, text, line, begidx, endidx):

        return self.complete_init(text, line, begidx, endidx)

    def do_set_weight(self, c):
        flags, args, ensemble = self.get_flags_and_db(c)
     #   print flags, args, ensemble

        if ensemble == None:
            return

        try:
            new_weight = float(args[0])
        except:
            utils.newline_msg("ERR", "cannot parse weight")
            return
       # print "UPDATE dbs SET weight=%f WHERE full_name = '%s' " %  ( new_weight, ensemble.full_name )
        try:
            self.master_db.query_master_db("UPDATE dbs SET weight=%f WHERE full_name = '%s' " %  ( new_weight, ensemble.full_name ) )
        except:
            utils.newline_msg("ERR", "cannot parse command")
            return
        self.master_db.update_list_ensemble_dbs()



    # def do_set(self, c):
    #     """set  VAR1=VALUE1 VAR2=VALUE2
    #     sets some values in the currently loaded database
    #     FLAGS::: --help, the possible keys are printed """
    #
    #     # print c
    #     flags, c = self.parse_command_line(c)
    #
    #     if "help" in flags:
    #         print utils.newline_msg("HELP", " possible_keys = %s" % self.possible_keys)
    #         return
    #
    #     if not self.current_param_db:
    #         utils.newline_msg("WRN", "not database loaded... skipping")
    #         return
    #
    #     for iarg in c:
    #         ret = utils.parse_to_dict(iarg, allowed_keys=self.possible_keys)
    #         if not ret:
    #             utils.newline_msg("ERR", "'%s' not understood" % iarg)
    #             return
    #
    #         # if k == "repeat": continue # repeat is not in the master db (should it be added)
    #         for k in ret:
    #             self.current_param_db.__dict__[k] = ret[k]
    #             self.master_db.query_master_db('UPDATE dbs SET %s= ? WHERE id = ?' % k, ret[k],
    #                                            self.current_param_db.id)

    def __set_status(self, c, st):
        # if not c:
        #     ls_res_db = [ self.current_param_db.full_name ]
        # else:
        #     ls_res_db = self.filter_db_list( filter = c )
        # if not ls_res_db: return
        #
        # for i in ls_res_db:

        flags, cmds, ensemble = self.get_flags_and_db(c)

        # ensemble = self.get_db(db_name)
        if ensemble is None:
            # utils.newline_msg("ERR", "database not found... aborting")
            return

        ensemble.status = st

        print(" +---  '%s' [status : %s ]" % (utils.shorten_name(ensemble.full_name), st))
        self.master_db.query_master_db('UPDATE dbs SET status= ? WHERE full_name = ?', st, ensemble.full_name)

    #
    # def do_stop(self, c):
    #     """stops the currently loaded registered database"""
    #     self.__set_status(c, 'S')
    #
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

    def do_get_jobs(self, c):
        """returns the number of jobs that would concurrently run in a multi-threaded run"""
        nj, = self.master_db.query_master_fetchone('SELECT max_jobs FROM queues WHERE name = "default"')
        print(" +--- no_jobs = %d " % nj)

    def do_info(self, c):
        """info REGEXP
           prints the information of the results databases, filtered by a regular expression, or its id """

        flags, cmds, ensemble = self.get_flags_and_db(c)
        # ensemble = self.get_db(db_name)
        if ensemble is None:
            # utils.newline_msg("ERR", "database not found... aborting")
            return

        db_status = ensemble.get_updated_status()

        param_db_id = self.master_db.query_master_fetchone("SELECT id, status, weight FROM dbs WHERE full_name = ?", ensemble.full_name)
        if param_db_id is None:
            param_db_id = "X"
        else:
            [param_db_id, status, weight] = param_db_id

        print(" ---%5s: %s" % (param_db_id, utils.shorten_name(ensemble.full_name)))
        frac_done = float(db_status['process_done']) / float(db_status['value_set'])

        n_repet = db_status['value_set_with_rep'] / db_status['value_set']

        print("   -+ status = %s /  weight: %5.5f " % (status, weight))
        print("   -+ total  = %d*%d / done: %d (%.5f) - running: %d - error: %d " % (
            db_status['value_set'], n_repet, db_status['process_done'], frac_done,
            db_status['process_running'], db_status['process_error']))
        try:
            print("   -+ time   = %f / mean: %f - min: %f - max: %f" % (
            db_status['total_run_time'], db_status['avg_run_time'], db_status['min_run_time'],
            db_status['max_run_time']))
        except:
            pass