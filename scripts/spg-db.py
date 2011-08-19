#!/usr/bin/python

import cmd

import spg.utils as utils
from spg.parameter import EnsembleBuilder, ParameterEnsemble
from spg.master import MasterDB

from spg import VAR_PATH, RUN_DIR

import sqlite3 as sql
import sys, optparse
import os, os.path


import fnmatch


class DBCommandParser(cmd.Cmd):
    """DB command handler"""

 
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "| spg-db :::~ "
        self.possible_keys = ['weight', 'repeat',  'status', 'queue']
#        self.values = {'repeat': 1, 'sql_retries': 1, 'timeout' : 60, 'weight': 1}

#        self.doc_header = "default values: %s"%(self.values )
        self.current_param_db = None 
        self.master_db =  MasterDB()


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
        #  print ">", full_name
        path, st = os.path.split(full_name)
#        if path:
#            os.chdir(path)
        if ".sqlite" in st:
            par_name = st.replace("results","").replace(".sqlite","")
            par_name = "parameters%s.dat"%par_name
#            return self.__lengthen_name( "%s/%s"%(path,par_name) ), self.__lengthen_name( "%s/%s"%(path,st) )
            return  "%s/%s"%(path,par_name) , "%s/%s"%(path,st)
        else:
            db_name = st.replace("parameters","").replace(".dat","")
            db_name = "results%s.sqlite"%db_name
            #return self.__lengthen_name( "%s/%s"%(path,st) ), self.__lengthen_name( "%s/%s"%(path,db_name) )
            return  "%s/%s"%(path,st) ,  "%s/%s"%(path,db_name) 
            
    def __update_active_result_db(self, c):
        c = c.strip()
        if not c: return 

        param_name, db_name = self.__translate_name(c)
        if os.path.exists( db_name ):
           self.current_param_db = ParameterEnsemble( db_name )
#           self.values["weight"] = self.current_param_db.weight 
        if os.path.exists( param_name ) and not os.path.exists( db_name ):
           self.current_param_db = ParameterEnsemble( db_name , db_init = False)
#           self.current_param_db.weight = self.values["weight"]
        
        db_id = self.master_db.execute_query_fetchone( "SELECT id FROM dbs WHERE full_name = ? ", full_name)
        if db_id is not None:
            (self.current_param_db,) = db_id

        return   
        
    def __filter_db_list(self, ls = None, filter = None):
#        if not filter and not ls:
#            try: 
#                return [ self.current_param_db.full_name ]
#            except: 
#                return None
        if ls == None:
            ls = self.master_db.result_dbs.keys()
        ret = [ self.__shorten_name(i) for i in ls ]
        if filter:
            ret = fnmatch.filter(ret, filter) 
              
        return sorted( [ self.__lengthen_name( i ) for i in ret ] )

    def __complete(self, text):    
        completions = self.master_db.result_dbs.keys()
        if text:
            completions = [ f
                            for f in completions
                            if f.startswith(text)
                            ]
        return completions
        
    def do_init(self, c):
        """build PARAMETERS_NAME|DB_NAME [VAR1=VALUE1[:VAR2=VALUE2]]
        Generates a new database out of a parameters.dat"""
        c = c.split()
        i_arg = c[0]
        i_arg, db_name = self.__translate_name(i_arg)
        if self.master_db.result_dbs.has_key( db_name ):
            utils.newline_msg("WRN", "results db '%s' already registered"%self.__shorten_name( db_name ), 2)
            return 

        self.current_param_db = ParameterEnsemble( db_name, init_db = False ) #, weight = self.values['weight'] )
        if len(c) >1: self.do_set( ":".join( c[1:] ) )

        parser = EnsembleBuilder( stream = open(i_arg), db_name=db_name  )
#        if 'executable' in self.values.keys():
#            parser.command = self.values['executable']
        parser.init_db(  )
        parser.fill_status(repeat = self.current_param_db.repeat ) 
#     __init__(full_name , id=-1, weight, queue , status, init_db = True):
        self.master_db.update_result_db( self.current_param_db )
        self.current_param_db.id = self.master_db.cursor.lastrowid
        self.master_db.initialise_result_dbs()

    def complete_init(self, text, line, begidx, endidx):    
        completions = fnmatch.filter( os.listdir("."), "results*.sqlite" )
        completions.extend( fnmatch.filter( os.listdir("."), "parameters*.dat" ) )
#        print completions, os.path.realpath(".")
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
        i_arg, db_name = self.__translate_name(i_arg)
        if self.master_db.result_dbs.has_key( db_name ):
            utils.newline_msg("WRN", "results db '%s' already registered"%self.__shorten_name( db_name ), 2)
            return 

        self.current_param_db = ParameterEnsemble( db_name ) #, weight = self.values['weight'] )
        if len(c) >1: 
            self.do_set( ":".join( c[1:] ) )

        self.master_db.update_result_db( self.current_param_db )
        self.current_param_db.id = self.master_db.cursor.lastrowid
        self.master_db.initialise_result_dbs()
        print " *--- registered '%s'with id=%d  "%(   self.current_param_db.full_name, self.current_param_db.id )
        
#    def clean_status(self):
#        """Sets the run_status to None of all the run processes"""
#        self.cursor.execute('UPDATE run_status SET status = "N" WHERE status ="R"')
#        self.connection.commit()
#
#    def clean_all_status(self):
#        """Sets the run_status to None of all the processes"""
#        self.cursor.execute('UPDATE run_status SET status = "N" ')
#        self.connection.commit()

    def do_clean(self, c):
        """cleans the results database by setting the R into N"""
        if self.current_param_db:
            self.current_param_db.execute_query('UPDATE run_status SET status = "N" WHERE status ="R"')
#        for i_arg in c.split():
#            i_arg, db_name = self.__translate_name(i_arg)
#            parser = EnsembleBuilder( stream = open(i_arg), db_name=db_name , timeout = self.values['timeout'] )
#            parser.clean_status()


    def do_clean_all(self, c):
        """cleans the results database by setting all into N"""
        if self.current_param_db:
            self.current_param_db.execute_query('UPDATE run_status SET status = "N" ')

    def do_ls(self, c):
        """lists the databases already registered in the master database and the possible ones found in the current directory"""

        ls_res_db = self.__filter_db_list( filter = c ) 
        if not ls_res_db: return
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
        if len(ls_res_db) >0:
            print "--- cwd dbs"
            for i in sorted( ls_res_db  ):
                print "     : %s "%self.__shorten_name(i)
             
        
        
    def do_load(self,c):
        """loads one of the registered databases from the master"""
        c = c.split()
        if len(c) >1:
            utils.newline_msg("ERR", "only one db can be loaded at a time", 2)
            return
        try: 
            id = int(c[0])
            self.current_param_db = filter(lambda x: x.id == id, self.master_db.result_dbs.values() )[0]
        except:
            i_arg = c[0]
            i_arg, db_name = self.__translate_name(i_arg)
    #       print i_arg, db_name
            if self.master_db.result_dbs.has_key( db_name ):
                self.current_param_db = self.master_db.result_dbs[db_name]
                print " --- loaded db '%s'"%self.__shorten_name( self.current_param_db.full_name )
#            elif os.path.exists( db_name ) or os.path.exists( i_arg ):
#                parser = EnsembleBuilder( stream = open(i_arg), db_name=db_name , timeout = self.values['timeout'] )
#                self.current_param_db = ParameterEnsemble( db_name )
#                utils.newline_msg("msg", "loaded db '%s'/'%s'"%( self.__shorten_name( db_name ), self.__shorten_name( i_arg ) ), 2)
            else:    
                utils.newline_msg("ERR", "db does not exist", 2)
#        parser = EnsembleBuilder( stream = open(i_arg), db_name=db_name , timeout = self.values['timeout'] )
        
#        if 'executable' in self.values.keys():
#            parser.command = self.values['executable']
#        parser.init_db(retry = self.values['sql_retries'])
        
        
#    def do_load(self,c):

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

    def do_remove(self, c):
        """removes one results database from the registered ones"""
        if not c:
            ls_res_db = [ self.current_param_db.full_name ]
        else:
            ls_res_db = self.__filter_db_list( filter = c )
        if not ls_res_db: return
        
        for i in ls_res_db: 
            self.master_db.execute_query("DELETE FROM dbs WHERE full_name = ?", i  )
        self.master_db.update_result_dbs()
 
    def complete_remove(self, text, line, begidx, endidx):
        return self.__complete(text)
    
    def do_set(self, c):
        """sets a VAR1=VALUE1[:VAR2=VALUE2]
        sets a value in the currently loaded database """
        ret = utils.parse_to_dict(c, allowed_keys=self.possible_keys)
#        for k in ret:
#            self.values[k] = ret[k]
#            print "%s = %s" %(k,ret[k])
        if self.current_param_db:
            if ret.has_key('weight'):
                self.current_param_db.weight = ret["weight"]
                self.master_db.execute_query( 'UPDATE dbs SET weight= ? WHERE id = ?', self.current_param_db.weight, self.current_param_db.id  )
            if ret.has_key('status'):
                self.current_param_db.status = ret["status"]
                self.master_db.execute_query( 'UPDATE dbs SET status= ? WHERE id = ?', self.current_param_db.status, self.current_param_db.id  )
            if ret.has_key('repeat'):
                self.current_param_db.repeat = ret["repeat"]
            if ret.has_key('queue'):
                self.current_param_db.queue = ret["queue"]
                self.master_db.execute_query( 'UPDATE dbs SET queue= ? WHERE id = ?', self.current_param_db.queue, self.current_param_db.id  )
#                self.master_db.execute( 'UPDATE dbs SET status="%s" WHERE id = %s'% ( self.current_param_db.status, self.current_param_db.id ) )
           
#        self.doc_header = "default values: %s"%(self.values )

    def __set_status(self, c, st):
        if not c:
            ls_res_db = [ self.current_param_db.full_name ]
        else:
            ls_res_db = self.__filter_db_list( filter = c )
        if not ls_res_db: return
        
        for i in ls_res_db: 
            self.current_param_db.status = st
            self.master_db.execute( 'UPDATE dbs SET status= ? WHERE id = ?', st, self.current_param_db.id  )

    def do_stop(self, c):
        """stops the currently loaded registered database"""
        self.__set_status(c, 'S')
                
    def do_start(self, c):
        """starts the currently loaded registered database"""
        self.__set_status(c, 'R')
                
    def do_pause(self, c):
         """pauses the currently loaded registered database"""
         self.__set_status(c, 'P')
                
   # def default(self, line):
   #     return True        
    
    def do_EOF(self, line):
        return True

    def do_shell(self, line):
        "Run a shell command"
#        print "running shell command:", line
        output = os.popen(line).read()
        print output
 #       self.last_output = output

    def do_cd(self,line):
        try:
            os.chdir(line)
        except:
            utils.newline_msg("dir", "no directory named '%s'"%line, 2)

    def complete_cd(self, text, line, begidx, endidx):    
        completions =  filter(lambda x: os.path.isdir(x) , os.listdir(".") )
    #    print completions 
#      #  print completions, os.path.realpath(".")
   #     print '\n\n>>>%s<<<\n\n'%( text, line, begidx, endidx )
        if text:
            completions = [ f
                            for f in completions
                            if f.startswith(text)
                            ]
        return completions
#        if not text:
#            completions = self.FRIENDS[:]
#        else:
#            completions = [ f
#                            for f in self.FRIENDS
#                            if f.startswith(text)
#                            ]
#        return completions

#    def do_EOF(self, line):
#        return True
    

if __name__ == '__main__':
    cmd_line = DBCommandParser()
    if len(sys.argv) == 1:
        cmd_line.cmdloop()
    else:
        cmd_line.onecmd(" ".join(sys.argv[1:]))
        
#       "usage: %prog [options] CMD VERB NAME {params}\n"
#       "commands NAME {params}: \n"
#       "   init PARAMETERS_NAME|DB_NAME \n"
#       "        params :: executable=EXE_NAME , repeat=REPEAT, sql_retries=1\n"
#       "   clean-all PARAMETERS_NAME|DB_NAME \n"
#       "   clean PARAMETERS_NAME|DB_NAME \n"
#       "   remove PARAMETERS_NAME|DB_NAME \n"







