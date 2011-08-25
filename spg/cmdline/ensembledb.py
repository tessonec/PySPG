#!/usr/bin/python

import cmd

import spg.utils as utils
from spg.parameter import ParameterEnsemble
from spg.master import MasterDB

from spg import RUN_DIR

import sys, os.path


import fnmatch


class BaseDBCommandParser(cmd.Cmd):
    """DB command handler"""

 
    def __init__(self, EnsembleConstructor = ParameterEnsemble):
        cmd.Cmd.__init__(self)
        self.current_param_db = None 
        self.master_db =  MasterDB(EnsembleConstructor = EnsembleConstructor)


    def __shorten_name(self, st):
        return os.path.relpath(st,RUN_DIR)

    def __lengthen_name(self, st):
        return "%s/%s"%(RUN_DIR, st)

    def __translate_name( self,st):
        """translates the parameters filename and the  database name 
           into the other and viceversa (returns a duple: param_name, db_name)"""
        full_name = os.path.realpath( st )
        if not os.path.exists(full_name):
            full_name = self.__lengthen_name(full_name)
        if not os.path.exists(full_name):
            utils.newline_msg("ERR","database '%s' does not exist"%st)
            sys.exit(2)
        path, st = os.path.split(full_name)
        if ".sqlite" in st:
            par_name = st.replace("results","").replace(".sqlite","")
            par_name = "parameters%s.dat"%par_name
            return  "%s/%s"%(path,par_name) , "%s/%s"%(path,st)
        else:
            db_name = st.replace("parameters","").replace(".dat","")
            db_name = "results%s.sqlite"%db_name
            return  "%s/%s"%(path,st) ,  "%s/%s"%(path,db_name) 
            
    def __update_active_result_db(self, c):
        c = c.strip()
        if not c: return 

        param_name, db_name = self.__translate_name(c)
        if os.path.exists( db_name ):
            self.current_param_db = ParameterEnsemble( db_name )
        elif os.path.exists( param_name ) and not os.path.exists( db_name ):
            self.current_param_db = ParameterEnsemble( db_name , db_init = False)
        return   
        
    def __filter_db_list(self, ls = None, filter = None):

        if ls == None:
            ls = self.master_db.result_dbs.keys()
        ret = [ self.__shorten_name(i) for i in ls ]
        if filter:
            ret = fnmatch.filter(ret, filter) 
              
        return sorted( [ self.__lengthen_name( i ) for i in ret ] )

    def __get_db_from_cmdline(self, c):
        """it returns the db name (or None) of a database identified either from its id or """
        try: 
            id = int(c)
            filtered = filter(lambda x: x.id == id, self.master_db.result_dbs.values() )
            if filtered:
                return filtered[0] 
        except:
            foo, db_name = self.__translate_name(c)
            if self.master_db.result_dbs.has_key(db_name):
                return self.master_db.result_dbs[db_name]
        return None

    def __complete(self, text):    
        completions = self.master_db.result_dbs.keys()
        if text:
            completions = [ f
                            for f in completions
                            if f.startswith(text)
                            ]
        return completions
        
    def do_ls(self, c):
        """lists the databases already registered in the master database and the possible ones found in the current directory"""

        ls_res_db = self.__filter_db_list( filter = c ) 
        if ls_res_db: 
            print "--- registered dbs" 
            for i in sorted( ls_res_db  ):
                #print "%5d: %s"%(i_id, i_name)
                curr_db = self.master_db.result_dbs[i]
                try:
                    print "%5d: %s (%5.5f)"%(curr_db.id, self.__shorten_name( curr_db.full_name ), curr_db.weight )
                except:
                    print "%5d: %s (%5s)"%(curr_db.id, self.__shorten_name( curr_db.full_name ), curr_db.weight )
                    
        ls_res_db = fnmatch.filter( os.listdir("."), "results*.sqlite" )
        ls_res_db.extend( fnmatch.filter( os.listdir("."), "parameter*.dat" ) )
        ls_res_db = self.__filter_db_list(  ls_res_db, filter = c )
        if ls_res_db:
            print "--- cwd dbs"
            for i in sorted( ls_res_db  ):
                print "     : %s "%self.__shorten_name(i)
             
                
    def do_load(self,c):
        """loads one of the registered databases from the master"""
        c = c.split()
        if len(c) >1:
            utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
            return
        ret = self.__get_db_from_cmdline(c[0])
        if ret:
            self.current_param_db = ret 
            print " --- loaded db '%s'"%self.__shorten_name( self.current_param_db.full_name )
        else:    
            utils.newline_msg("ERR", "db does not exist", 2)


    def complete_load(self, text, line, begidx, endidx):
        return self.__complete(text)

    def do_info(self, c):
        """prints the information of the results database """
        if not c:
            if not self.current_param_db:
                return
            else:
                ls_res_db = [ self.current_param_db.full_name ]
        else:
            ls_res_db = self.__filter_db_list( filter = c )
        if not ls_res_db: return
        
        for i in ls_res_db: 
            curr_db = self.master_db.result_dbs[i]
        
            self.master_db.update_result_db( curr_db )
        
            print "%5d: %s"%( curr_db.id, os.path.relpath(curr_db.full_name,RUN_DIR) )
            frac_done =  float(curr_db.stat_processes_done) / float(curr_db.stat_values_set)
            
            n_repet = curr_db.stat_values_set_with_rep/ curr_db.stat_values_set
            
            print "     [status: %s] TOTAL: %d (*%d) - D: %d (%.5f) - R: %d - E: %d / w=%5.5f queue=%s  "%(curr_db.status, curr_db.stat_values_set,n_repet , curr_db.stat_processes_done, frac_done, curr_db.stat_processes_running,  curr_db.stat_processes_error, curr_db.weight, curr_db.queue ) 

    
    def do_EOF(self, line):
        return True

    def do_shell(self, line):
        """Runs a shell command"""
        output = os.popen(line).read()
        print output

    def do_cd(self,line):
        try:
            os.chdir(line)
        except:
            utils.newline_msg("dir", "no directory named '%s'"%line, 2)

    def complete_cd(self, text, line, begidx, endidx):    
        completions =  filter(lambda x: os.path.isdir(x) , os.listdir(".") )
        if text:
            completions = [ f
                            for f in completions
                            if f.startswith(text)
                            ]
        return completions




