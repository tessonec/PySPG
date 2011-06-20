# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 22:22:19 2011

@author: -
"""

import params, utils

import os.path, pickle, random
from subprocess import Popen, PIPE
import sqlite3 as sql

VAR_PATH = os.path.abspath(params.CONFIG_DIR+"/../var/spg")
BINARY_PATH = os.path.abspath(params.CONFIG_DIR+"/../bin")
TIMEOUT = 120

################################################################################
################################################################################
################################################################################

class PickledData:
    def __init__(self, fname):
        self.command = None
        self.path = None
        self.db_name = None

        self.id = fname
        self.values = {}
        self.current_run_id = None
        self.variables = []
        self.output = ""
        self.return_code  = None


    def load(self, src = 'queued'):
        full_name = "%s/%s/%s"%(VAR_PATH,src,self.id) 
        vals = pickle.load( open(full_name)  )
        self.__dict__ = vals.__dict__

        os.remove( full_name )

    def dump(self,src = 'run'):
          full_name = "%s/%s/%s"%(VAR_PATH,src,self.id)
          pickle.dump( open(full_name, "w" ), self  )


    def store_in_db(self):

          conn = sql.connect("%s/%s"%(self.path,self.db_name))
          cursor = conn.cursor()

          #:::~ get the names of the outputs
          fa = cursor.execute("PRAGMA table_info(results)")
          output_column = [ i[1] for i in fa ]
          output_column = self.output_column[1:]
            
          if self.return_code == 0:
             cursor.execute( 'UPDATE run_status SET status ="D" WHERE id = %d'%self.current_run_id )
             all_d = [self.current_variables_id]
             all_d.extend( self.output )
             cc = 'INSERT INTO results ( %s) VALUES (%s) '%( ", ".join(output_column) , ", ".join([str(i) for i in all_d]) )
             cursor.execute( cc )
          else:
                #:::~ status can be either 
                #:::~    'N': not run
                #:::~    'R': running
                #:::~    'D': successfully run (done)
                #:::~    'E': run but with non-zero error code
             cursor.execute( 'UPDATE run_status SET status ="E" WHERE id = %d'%self.current_run_id )
               #self.connection.commit()
            
          conn.commit()
          conn.close()
          del cursor
          del conn
          self.last_finished_processes  += 1
        

################################################################################
################################################################################

class PickledExecutor(PickledData):
    def __init__(self, fname):
        PickledData.__init__(fname)


    def create_tree(self):
        for k in self.values:
          if k.find("store_") != -1: return True
        return False

    def launch_process(self):
        os.chdir(self.path)

        if self.create_tree():
            dir_n = utils.replace_list(self.variables, self.values, separator = "/")
            if not os.path.exists(dir_n): 
                os.makedirs(dir_n)
            os.chdir(dir_n)

        configuration_filename = "input_%s_%d.dat"%(self.db_name, self.current_run_id)
        fconf = open(configuration_filename,"w")
        for k in self.values.keys():
            print >> fconf, k, utils.replace_string(self.values[k], self.values) 
        fconf.close()

        cmd = "%s/%s -i %s"%(BINARY_PATH, self.command, configuration_filename )
        proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        proc.wait()
        self.return_code = proc.returncode
        self.output = [i.strip() for i in proc.stdout.readline().split()]
        os.remove(configuration_filename)





################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################




class ParameterExtractor():
    def __init__(self, db_name):
        self.db_name = db_name
        
        self.values = {}
        self.directory_vars = None
        self.__init_db()

        self.stdout_contents = params.contents_in_output(self.command)


    def __init_db(self):

        sql_db = sql.connect(self.db_name, timeout = TIMEOUT)

        #:::~ Table with the name of the executable
        (self.command, ) = sql_db.execute( "SELECT name FROM executable " ).fetchone()

        #:::~ get the names of the columns
        sel = sql_db.execute("SELECT name FROM entities ORDER BY id")
        self.entities = [ i[0] for i in sel ]

        #:::~ get the names of the outputs
        fa = self.sql_db.execute("PRAGMA table_info(results)")
        self.output_column = [ i[1] for i in fa ]
        self.output_column = self.output_column[1:]
        sql_db.close()
        del sql_db
        
    def __iter__(self):
        return self

    def next(self):
        sql_db = sql.connect(self.db_name, timeout = TIMEOUT)
        res = sql_db.execute(
                    "SELECT r.id, r.values_set_id, %s FROM run_status AS r, values_set AS v "% ", ".join(["v.%s"%i for i in self.entities]) +
                    "WHERE r.status = 'N' AND v.id = r.values_set_id ORDER BY r.id LIMIT 1" 
                   ).fetchone()
        if res == None:
          raise StopIteration

        self.current_run_id  = res[0]
        self.current_variables_id  = res[1]
        self.sql_db.execute( 'UPDATE run_status SET status ="R" WHERE id = %d'%self.current_run_id  )
        
        for i in range( len(self.entities) ):
            self.values[ self.entities[i] ] = res[i+2]
        return self.values

        sql_db.close()
        del sql_db

    

################################################################################
################################################################################



class ParameterDB(ParameterExtractor):
    normalising = 0.
    def __init__(self, full_name = "", path= "", db_name= "", id=-1, weight=1.,queue = 'any'):
       ParameterExtractor.__init__(full_name)
       self.full_name = full_name
       self.path = path
       self.db_name = db_name
       self.weight = weight
       self.id = id
       self.queue = 'any'
       ParameterDB.normalising += weight



################################################################################
################################################################################

class DBExecutor(ParameterExtractor):
    def __init__(self, db_name):
        ParameterExtractor.__init__(db_name)
           
    def launch_process(self):
        pwd = os.path.abspath(".")
        if self.directory_vars:
            dir = utils.replace_list(self.directory_vars, self.values, separator = "/")
            if not os.path.exists(dir): os.makedirs(dir)
            os.chdir(dir)
        configuration_filename = "input_%s_%d.dat"%(self.db_name, self.current_run_id)
        fconf = open(configuration_filename,"w")
        
        for k in self.values.keys():
            print >> fconf, k, utils.replace_string(self.values[k], self.values) 
        fconf.close()
        
        cmd = "%s/%s -i %s"%(BINARY_PATH, self.command, configuration_filename )
        proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        proc.wait()
        ret_code = proc.returncode
        output = [i.strip() for i in proc.stdout.readline().split()]
        os.remove(configuration_filename)
        if self.directory_vars:
            os.chdir(pwd)
        
        sql_db = sql.connect(self.db_name, timeout = TIMEOUT)
        if ret_code == 0:
           sql_db.execute( 'UPDATE run_status SET status ="D" WHERE id = %d'%self.current_run_id )
           all_d = [self.current_variables_id]
           all_d.extend( output )
           cc = 'INSERT INTO results ( %s) VALUES (%s) '%( ", ".join(self.output_column) , ", ".join([str(i) for i in all_d]) )
           sql_db.execute( cc )
        else:
           #:::~ status can be either 
           #:::~    'N': not run
           #:::~    'R': running
           #:::~    'D': successfully run (done)
           #:::~    'E': run but with non-zero error code
           sql_db.execute( 'UPDATE run_status SET status ="E" WHERE id = %d'%self.current_run_id )
        sql_db.close()
        del sql_db


    def create_trees(self):
        sql_db = sql.connect(self.db_name, timeout = TIMEOUT)
        ret = sql_db.select("SELECT * FROM entities WHERE name LIKE 'store_%'").fetchone()
        
        sql_db.close()
        del sql_db
        return ret is not None


    def generate_tree(self, dir_vars = None):
        sql_db = sql.connect(self.db_name, timeout = TIMEOUT)
        if dir_vars:
           self.directory_vars = dir_vars
        else:
           res = self.sql_db.execute("SELECT name FROM entities WHERE varies = 1 ORDER BY id")
           self.directory_vars  = [ i[0] for i in res ]
        sql_db.close()
        del sql_db
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################


class Queue:
    def __init__(self, name, max_jobs):
        self.name = name
        self.jobs = max_jobs
        self.processes = []

    def populate_processes( self, new_jobs ):
        for i in range(new_jobs):
            cmd = "qsub -q %s %s/spg-worker.py"%(self.name, BINARY_PATH)
            proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
            proc.wait()

    def kill_processes( self, n_jobs ):
        for i in sorted(self.processes)[:n_jobs] :
            cmd = "qdel "%(i)
            proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
            proc.wait()
            self.master_db.execute("DELETE FROM running WHERE job_id = ?" , i)


    def normalise_processes(self):
        running_proc = len( self.processes )
        if running_proc > self.jobs :
            self.kill_processes( running_proc - self.jobs )
        elif running_proc < self.jobs :
            self.populate_processes( self.jobs - running_proc  )



###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################




class ProcessPool:
    def __init__(self):
        self.update_time = 60 * 1
        self.waiting_processes = 100
        self.last_finished_processes = 0

        self.dbs = {} 
        self.queues = {}
        self.db_master = sql.connect("%s/running.sqlite"%VAR_PATH)
        self.update_queue_info()
        self.get_registered_dbs()
#        self.update_process_list()

    def get_registered_dbs(self): # These are the dbs that are registered and running
        self.dbs = {} 
        ParameterDB.normalising = 0.
        res = self.db_master.execute("SELECT id, full_name, path, db_name, weight, queue FROM dbs WHERE status = 'R'")
        for (id, full_name, path, db_name, weight, queue) in res:
            self.dbs[full_name] = ParameterDB(full_name, path, db_name,id, weight, queue)

    def update_queue_info(self): # These are the queues available to launch the processes in
        self.queues = {}
        res = self.db_master.execute("SELECT name, max_jobs FROM queues WHERE status = 'R'")
        for (name, max_jobs) in res:
            self.queues[name] = Queue(name, max_jobs)
#           self.queues[name].set_db(self.db_master)

    def update_worker_info(self):  # These are the spg-worker instances in the queueing system
        proc = Popen("qstat", shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        output = proc.stdout
        proc.wait()

        for i_q in self.queues:
            self.queues[i_q].processes = []

        for l in output:
            content = l.split()
            try:
                job_id = int( content[0].split(".")[0] )
                status = content[4]
                queue =  content[5]
                if status == "R":
                    self.queues[queue].processes.append( job_id ) 
            except: 
                continue


    def harvest_data(self):
        self.last_finished_processes  = 0
        for i_d in os.listdir("%s/run"%(VAR_PATH) ):
            pd = PickledData(id)
            pd.load(src='run')
            pd.store_in_db()
 


    def generate_new_process(self):
        db_fits = False
        while not db_fits :
            rnd = ParameterDB.normalising * random.random()
            ls_dbs = sorted( self.dbs.keys() )
            curr_db = self.pop()
            ac = self.dbs[ curr_db ].weight
            
            while rnd > ac:
                curr_db = ls_dbs.pop()
                ac += self.dbs[ curr_db ].weight


        return  self.dbs[ curr_db ]


    def initialise_infiles(self):
        to_run_processes =  self.waiting_processes - len(os.listdir("%s/queued"%(VAR_PATH) ) ) 
        for i in range(to_run_processes):
            self.generate_new_process(  )
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
            


###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################



