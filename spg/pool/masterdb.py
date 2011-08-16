from spg import  CONFIG_DIR, TIMEOUT, VAR_PATH

import sqlite3 as sql
import spg.utils as utils

from spg.parameter import ParameterEnsemble

######
######    def update_dbs_info(self):   # 
######        for i in self.dbs.keys():
######            self.update_db_info(i)
######
######    def update_db_info(self,db_fullname): 
######            
######            curr_sql = SQLHelper(db_fullname)
######            sel = curr_sql.select_fetchall("SELECT status, COUNT(*) FROM run_status GROUP BY status")
######            
######            res = {'D':0, 'R':0, 'E':0}
######            ac = 0
######            for (k,v) in sel :
######                res[k] = int(v)
######                ac += int(v)
######                #:::~    'N': not run yet
######                #:::~    'R': running
######                #:::~    'D': successfully run (done)
######                #:::~    'E': run but with non-zero error code
######            self.db_master.execute("UPDATE dbs " 
######                                    "SET total_combinations = ?, done_combinations = ?,"
######                                    "running_combinations =  ? , error_combinations = ? "
######                                    "WHERE full_name = ?", (ac, res['D'], res['R'], res['E'],db_fullname))
######            
###    (id INTEGER PRIMARY KEY, full_name CHAR(256), path CHAR(256), 
###     db_name CHAR(256), status CHAR(1), 
###     total_combinations INTEGER, done_combinations INTEGER, 
###     running_combinations INTEGER, error_combinations INTEGER, 


class MasterDB:

    def __init__(self,  connection = None):
        if not connection:
            self.connection = sql.connect("%s/spg_pool.sqlite"%VAR_PATH)
        else:
            self.connection = connection
            
        self.cursor = self.connection.cursor()
        
        self.result_dbs = {} 
        self.update_result_dbs()


    def execute_query(self, query):
        ret = [i for i in self.cursor.execute(query)]
        return ret
        

    def execute_query_fetchone(self, query):
        ret = self.cursor.execute(query).fetchone()
        return ret
        
    def update_result_dbs(self): # These are the dbs that are registered and running
        #self.dbs = {} 
        ParameterEnsemble.normalising = 0.
####         res = self.cursor.execute("SELECT id, full_name, weight, queue FROM dbs WHERE status = 'R'")
        res = self.cursor.execute("SELECT id, full_name, weight, queue FROM dbs ")
      #  vec = [(id, full_name, weight, queue, status) for (id, full_name, weight, queue, status) in res]
        vec = [i for i in res]
    #    print self.dbs
        
        for (id, full_name, weight, queue, status) in vec:
            if full_name in self.result_dbs.keys():
                self.result_dbs[full_name].id = id
                self.result_dbs[full_name].queue = queue
                self.result_dbs[full_name].status = status
                self.result_dbs[full_name].weight = weight
                
#                print full_name, self.dbs[full_name].weight
                continue
         ###   utils.newline_msg("INF","new db registered... '%s'"%full_name)
            new_db = ParameterEnsemble(full_name, id, weight, queue, status)
            self.result_dbs[full_name] = new_db
    #    print self.dbs
   


    def update_results_stat(self, param_db):
        
        param_db.update_status()
        res = self.cursor.execute("SELECT * FROM dbs WHERE full_name = ?",(param_db.full_name,)).fetchone()
#       print res
        if res == None:
            self.cursor.execute(
                    "INSERT INTO dbs (full_name,total_values_set, total_combinations, done_combinations, running_combinations, error_combinations, status) VALUES (?,?,?,?,?,?,?)",
                    (param_db.full_name,param_db.stat_values_set_with_rep, param_db.stat_values_set, param_db.stat_processes_done, param_db.stat_processes_running, param_db.stat_processes_error, "S"  ))
        else:
            self.cursor.execute(
                    "UPDATE dbs SET total_values_set = ? , total_combinations = ?, done_combinations = ?, running_combinations = ?, error_combinations = ? WHERE full_name = ? ",
                    (param_db.stat_values_set_with_rep, param_db.stat_values_set, param_db.stat_processes_done, param_db.stat_processes_running, param_db.stat_processes_error, param_db.full_name ))
        if param_db.stat_processes_not_run == 0:
            self.cursor.execute("UPDATE dbs SET status = ? WHERE full_name = ? ",('D',param_db.full_name))
            
        self.connection.commit()


    def synchronise_master(self):
        for i in self.result_dbs:
            self.update_results_stat(i.full_name)



