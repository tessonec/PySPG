from spg import  TIMEOUT, VAR_PATH

import sqlite3 as sql
import spg.utils as utils

from spg.parameter import ParameterEnsemble


class MasterDB:

    def __init__(self,  connection = None, EnsembleConstructor = ParameterEnsemble):
        if not connection:
            self.connection = sql.connect("%s/spg_pool.sqlite"%VAR_PATH, timeout = TIMEOUT)
        else:
            self.connection = connection
            
        self.EnsembleConstructor = EnsembleConstructor
        self.cursor = self.connection.cursor()
        self.__init_db()
        self.result_dbs = {} 
        self.initialise_result_dbs()

    def __init_db(self):
    
        #:::~ status can be either 
        #:::~    'S': stopped
        #:::~    'R': running
        #:::~    'F': finished
        self.cursor.execute("CREATE TABLE IF NOT EXISTS dbs "
                       "(id INTEGER PRIMARY KEY, full_name CHAR(256), path CHAR(256), db_name CHAR(256), status CHAR(1), total_values_set INTEGER, "
                       " total_combinations INTEGER, done_combinations INTEGER, running_combinations INTEGER, error_combinations INTEGER, "
                       " weight FLOAT, queue CHAR(64))")
    
        #:::~ status can be either 
        #:::~    'S': stopped
        #:::~    'R': running
        self.cursor.execute("CREATE TABLE IF NOT EXISTS queues "
                       "(id INTEGER PRIMARY KEY, name CHAR(64), max_jobs INTEGER, status CHAR(1))")
    
        self.cursor.execute("CREATE TABLE IF NOT EXISTS running "
                       "(id INTEGER PRIMARY KEY, job_id CHAR(64), dbs_id INTEGER, params_id INTEGER)")
    
        self.cursor.execute("CREATE TABLE IF NOT EXISTS infiles "
                          "(id INTEGER PRIMARY KEY, last INTEGER)")
        
        self.connection.commit()

    def execute_query(self, query, *args):
        ret = [i for i in self.cursor.execute(query, args)]
        self.connection.commit()
        return ret
        

    def execute_query_fetchone(self, query, *args):
        ret = self.cursor.execute(query, args).fetchone()
        self.connection.commit()
        return ret
        
    def initialise_result_dbs(self, status = None): # These are the dbs that are registered and running
        self.result_dbs = {} 
        if status:
            res = self.cursor.execute("SELECT id, full_name, weight, queue, status FROM dbs  WHERE status = ?",status)
        else:  
            res = self.cursor.execute("SELECT id, full_name, weight, queue, status FROM dbs ")
        vec = [i for i in res]
        
        for (id, full_name, weight, queue, status) in vec:
            if full_name in self.result_dbs.keys():
                self.result_dbs[full_name].id = id
                self.result_dbs[full_name].queue = queue
                self.result_dbs[full_name].status = status
                self.result_dbs[full_name].weight = weight
                
                continue
            try:
                new_db = self.EnsembleConstructor(full_name, id, weight, queue, status)
                self.result_dbs[full_name] = new_db
            except:
                self.result_dbs[full_name] = None
   


    def update_result_db(self, param_db):
        
        param_db.update_status()
        res = self.cursor.execute("SELECT * FROM dbs WHERE full_name = ?",(param_db.full_name,)).fetchone()
#       print res
        if res == None:
            self.cursor.execute(
                    "INSERT INTO dbs (full_name,total_values_set, total_combinations, done_combinations, running_combinations, error_combinations, status, weight , queue ) VALUES (?,?,?,?,?,?,?,?,?)",
                    (param_db.full_name,param_db.stat_values_set_with_rep, param_db.stat_values_set, param_db.stat_processes_done, param_db.stat_processes_running, param_db.stat_processes_error, param_db.status , param_db.weight , param_db.queue))
        else:
            self.cursor.execute(
                    "UPDATE dbs SET total_values_set = ? , total_combinations = ?, done_combinations = ?, running_combinations = ?, error_combinations = ?, status = ? , weight = ?, queue = ? WHERE full_name = ? ",
                    (param_db.stat_values_set_with_rep, param_db.stat_values_set, param_db.stat_processes_done, param_db.stat_processes_running, param_db.stat_processes_error, param_db.full_name , param_db.status, param_db.weight, param_db.queue))
        if param_db.stat_processes_not_run == 0:
            self.cursor.execute("UPDATE dbs SET status = ? WHERE full_name = ? ",('D',param_db.full_name))
            
        self.connection.commit()


    def synchronise_master(self):
        for i in self.result_dbs:
            try:
                self.update_result_db(self.result_dbs[i])
            except: pass



