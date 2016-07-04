#!/usr/bin/python



# from spg import RUN_DIR

import sys, os.path
import cmd

import re, fnmatch
from setuptools.command.saveopts import saveopts

import spg.utils as utils
from spg.simulation import ParameterEnsemble
from spg.master import SPGMasterDB


# TODO: Remove unnecessary current_param_db, turn it into a string





class BaseSPGCommandLine(cmd.Cmd):
    """This is a basic command line for SPG based programs. It contains basic functionality"""
 
    def __init__(self, EnsembleConstructor = ParameterEnsemble):
        cmd.Cmd.__init__(self)
        self.EnsembleConstructor = EnsembleConstructor 


    def parse_command_line(self, st):
        """returns command the flags set under a command and the arguments"""

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


    def get_db_from_cmdline(self, c):
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
            print " --- cwd matches found"
            for i in sorted( ls_res_db  ):
                print "     : %s "% i


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



    def do_load(self,c):
        """load DB_NAME|DB_ID 
        loads one of the registered databases from the master"""
        c = c.split()
        if len(c) >1:
            utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
            return

        ret = self.get_db_from_cmdline(c[0])

        if ret:
            self.current_param_db = ret 
            print " --- loaded '%s'"% self.current_param_db.full_name
        else:    
            utils.newline_msg("ERR", "'%s' does not exist"%ret, 2)

    def do_EOF(self, line):
        return True

    def do_shell(self, line):
        """Runs a shell command"""
        output = os.popen(line).read()
        print output

    def do_cd(self,line):
        """ Changes into a given directory """
        try:
            os.chdir(line)
        except:
            utils.newline_msg("DIR", "no directory named '%s'"%line, 2)

    def complete_cd(self, text, line, begidx, endidx):    
        completions =  filter(lambda x: os.path.isdir(x) , os.listdir(".") )
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










class DBCommandLine(BaseSPGCommandLine):
    """A command handler which interfaces a master DB"""
 
    def __init__(self, EnsembleConstructor = ParameterEnsemble):
        BaseSPGCommandLine.__init__(self, EnsembleConstructor)

        self.current_param_db = None
        self.master_db =  SPGMasterDB(EnsembleConstructor = EnsembleConstructor)


    #
    # def update_active_result_db(self, c):
    #     c = c.strip()
    #     if not c: return
    #     try:
    #         full_name, path, base_name, extension = utils.translate_name(c)
    #         db_name = "%s/%s.spgql" % (path, base_name)
    #         sim_name = "%s/%s.spg" % (path, base_name)
    #
    #     except:
    #         utils.newline_msg("ERR", "results db '%s' doesn't exist. Cannot load it" )
    #         return
    #
    #     if os.path.exists( db_name ):
    #         self.current_param_db = ParameterEnsemble( db_name )
    #     elif os.path.exists( sim_name ) and not os.path.exists( db_name ):
    #         self.current_param_db = ParameterEnsemble( db_name , db_init = False)
    #     return
    #
    def filter_db_list(self, ls = None, filter = None):
        if ls == None:
            ls = self.master_db.result_dbs.keys()
        if  re.match("^\d+?$", filter): #:::~ Is filter an integer???
            id = int(filter)
            rdb = self.master_db.result_dbs
            filtered = [ x for x in ls if rdb.has_key(x) and rdb[x] is not None and rdb[x]['id'] == id  ]
            return filtered

        if filter:
                ret = fnmatch.filter(ls, filter)
        else:
                ret = ls
        return sorted( ret )

    def get_db_from_cmdline(self, c):
        """it returns the db name (or None) of a database identified either from its id or """
        db_name = c.strip()
        if db_name.isdigit():
            id = int( db_name )
            rdb = self.master_db.result_dbs
            filtered = [x for x in rdb if rdb[x] is not None and rdb[x]['id'] == id]
            if filtered:
                db_name = filtered[0]
            else:
                utils.newline_msg("ERR", "database with id '%s' doesn't exist." % c)
                return None

        full_name, path, base_name, extension = utils.translate_name(db_name)
        db_name = "%s/%s.spgql" % (path, base_name)
        sim_name = "%s/%s.spg" % (path, base_name)
        if not os.path.exists(db_name) and not os.path.exists(sim_name):
            utils.newline_msg("ERR", "database with name '%s' doesn't exist." % c)
            return None
        return self.EnsembleConstructor(db_name, init_db=True)
        #
        #     # if self.master_db.result_dbs.has_key(db_name):
        #     #     return self.master_db.result_dbs[db_name]
        #     # else:
        #     #     utils.newline_msg("WRN", "database '%s' is not registered, loading it anyhow" %  db_name )
        # return None

    def do_ls(self, c):
        """ls REGEXP|DB_ID
        lists the databases already registered in the master database and the possible ones found in the current directory"""

        ls_res_db = self.filter_db_list( filter = c )

        if ls_res_db: 
            print " --- registered dbs" 
            for i in sorted( ls_res_db  ):
                # :::~FIXME workaround for non-existing dbs
                curr_db = self.master_db.result_dbs[i]
                short_name = utils.shorten_name(i)

                try:
                    print "%5d: %s (%5.5f)"%(curr_db['id'], short_name  , curr_db['weight'] )
                except:
                    print "%5d: %s "%(curr_db['id'],  short_name )

        BaseSPGCommandLine.do_ls(self, c )

    def do_load(self,c):
        """load DB_NAME|DB_ID 
        loads one of the registered databases from the master"""
        c = c.split()
        if len(c) >1:
            utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
            return
        ret = self.get_db_from_cmdline(c[0])
        if ret:
            self.current_param_db = ret
            print " --- loaded db '%s'"% utils.shorten_name(self.current_param_db.full_name)
        # else:
        #     utils.newline_msg("ERR", "db does not exist", 2)


