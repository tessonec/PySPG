# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 22:22:19 2011

@author: -
"""

import params, utils

import os.path
from subprocess import Popen, PIPE
import sqlite3 as sql

CONFIG_DIR = params.CONFIG_DIR
VAR_PATH = os.path.abspath(params.CONFIG_DIR+"/../var/spg")
BINARY_PATH = os.path.abspath(params.CONFIG_DIR+"/../bin")

class DBInfo:
    normalising = 0.
    def __init__(self, full_name = "", path= "", db_name= "", id=-1, weight=1.,queue = 'any'):
       self.full_name = full_name
       self.path = full_name
       self.db_name = db_name
       self.weight = weight
       self.id = id
       self.queue = 'any'
       DBInfo.normalising += weight

    def set_db(self, db):
        self.connection = db
        self.cursor = db.cursor()

    def update_master_db( self, process_id, running_id ):
#        job_id CHAR(64), 
###             id_dbs INTEGER, id_params INTEGER UPDATE run_status SET status ="R" WHERE id 
        self.cursor.execute("UPDATE running SET job_id = ?, params_id = ? WHERE id_dbs = ? " , (process_id, running_id, self.id) )
        self.connection.commit()


class Queue:
    def __init__(self, name, max_jobs):
        self.name = name
        self.jobs = max_jobs
        self.processes = []

    def set_db(self, db):
        self.connection = db
        self.cursor = db.cursor()
        
    def populate_processes( self, new_jobs ):
        for i in range(new_jobs):
            cmd = "qsub -q %s %s/spg-worker.py"%(self.name, BINARY_PATH)
            proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
#            output = proc.stdout
            proc.wait()

    def kill_processes( self, n_jobs ):
        for i in sorted(self.processes)[:n_jobs] :
            cmd = "qdel "%(i)
            proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
 #           output = proc.stdout
            proc.wait()
            self.cursor.execute("DELETE FROM running WHERE job_id = ?" , i)
        self.connection.commit()


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
        
        self.dbs = {} 
        self.queues = {}
        self.reload_master_info()
#        self.update_process_list()

    def reload_master_info(self):
        
       self.conn_master = sql.connect("%s/running.sqlite"%VAR_PATH)
       self.cur_master  = self.conn_master.cursor()
       
       res = self.cur_master.execute("SELECT name, max_jobs FROM queues WHERE status = 'R'")

       for (name, max_jobs) in res:
           
           self.queues[name] = Queue(name, max_jobs)
           self.queues[name].set_db(self.conn_master)

       res = self.cur_master.execute("SELECT id, full_name, path, db_name, weight, queue FROM dbs WHERE status = 'R'")

       for (id, full_name, path, db_name, weight, queue) in res:
           self.dbs[full_name] = DBInfo(full_name, path, db_name,id, weight, queue)


    def update_worker_info(self):

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


    def update_dbs_info(self):

        for i in self.dbs[full_name]:
            curr_db = self.dbs[i]
            
            curr_conn = sql.connect( curr_db.full_name )
            curr_cur = curr_conn.cursor()
            
            curr_cur.execute("SELECT status, COUNT(*) FROM run_status GROUP BY status")
            
            res = {}
            ac = 0
            for (k,v) in curr_cur:
                res[k] = int(v)
                ac += int(v)
                #:::~    'N': not run yet
                #:::~    'R': running
                #:::~    'D': successfully run (done)
                #:::~    'E': run but with non-zero error code
            self.cur_master.execute("UPDATE dbs" 
                                    "SET total_combinations = ?, done_combinations = ?,"
                                    "running_combinations =  ? , error_combinations = ?, "
                                    "WHERE id = ?", (ac, res['D'], res['R'], res['E'],i.id))
        self.conn_master.commit()
###    (id INTEGER PRIMARY KEY, full_name CHAR(256), path CHAR(256), 
###     db_name CHAR(256), status CHAR(1), 
###     total_combinations INTEGER, done_combinations INTEGER, 
###     running_combinations INTEGER, error_combinations INTEGER, 
            


###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################



class DBExecutor():
    def __init__(self, db_name, timeout = 60):
        self.connection =  sql.connect(db_name, timeout = timeout)
#        self.connection.row_factory = sql.Row
        self.cursor = self.connection.cursor()
        self.db_name = db_name

        self.values = {}
        self.directory_vars = None
        self.__init_db()

        self.stdout_contents = params.contents_in_output(self.command)


    def __init_db(self):

        #:::~ Table with the name of the executable
        self.cursor.execute( "SELECT name FROM executable " )
        self.command = self.cursor.fetchone()[0]

#        #:::~ Table with the constant values
#        self.cursor.execute( "SELECT name,value FROM constants " )
#        for k, v in self.cursor:
#        #    self.constants[k] = v
#            self.values[k] = v
#            
        
#        #:::~ get the names of the columns
#        self.cursor.execute("PRAGMA table_info(variables)")
#        self.entities = [ i[1] for i in self.cursor.fetchall() ]
#        self.entities = self.entities[1:]

        #:::~ get the names of the columns
        self.cursor.execute("SELECT name FROM entities ORDER BY id")
        self.entities = [ i[0] for i in self.cursor ]
#        self.entities = self.entities[1:]


        #:::~ get the names of the outputs
        self.cursor.execute("PRAGMA table_info(results)")
        self.output_column = [ i[1] for i in self.cursor.fetchall() ]
        self.output_column = self.output_column[1:]
        
#        print self.entities
        
    def __iter__(self):
        return self

    def next(self):
        
        self.cursor.execute(
                    "SELECT r.id, r.values_set_id, %s FROM run_status AS r, values_set AS v "% ", ".join(["v.%s"%i for i in self.entities]) +
                    "WHERE r.status = 'N' AND v.id = r.values_set_id ORDER BY r.id LIMIT 1" 
                   )
                   
        res = self.cursor.fetchone()
        if res == None:
          raise StopIteration
#        print res    
#        res = list(res)
        self.current_run_id  = res[0]
        self.current_variables_id  = res[1]
        self.cursor.execute( 'UPDATE run_status SET status ="R" WHERE id = %d'%self.current_run_id  )
        self.connection.commit()          
#        print res.keys(), dir(res)
        for i in range(len(self.entities)):
            self.values[ self.entities[i] ] = res[i+2]
        return self.values

    def generate_tree(self, dir_vars = None):
        if dir_vars:
            self.directory_vars = dir_vars
        else:
            self.directory_vars =  self.entities 

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
#        print cmd
        proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        proc.wait()
        ret_code = proc.returncode
#        ret_code = 0
        output = [i.strip() for i in proc.stdout.readline().split()]
#        output = ["1" for i in self.output_column[1:] ]
#        print ret_code, "-->", output
        os.remove(configuration_filename)
        if self.directory_vars:
            os.chdir(pwd)
#        print self.output_column
        if ret_code == 0:
           self.cursor.execute( 'UPDATE run_status SET status ="D" WHERE id = %d'%self.current_run_id )
           all_d = [self.current_variables_id]
           all_d.extend( output )
           cc = 'INSERT INTO results ( %s) VALUES (%s) '%( ", ".join(self.output_column) , ", ".join([str(i) for i in all_d]) )
 #          print cc
           self.cursor.execute( cc )
           self.connection.commit()
        else:
           #:::~ status can be either 
           #:::~    'N': not run
           #:::~    'R': running
           #:::~    'D': successfully run (done)
           #:::~    'E': run but with non-zero error code
           self.cursor.execute( 'UPDATE run_status SET status ="E" WHERE id = %d'%self.current_run_id )
           self.connection.commit()


    def create_trees(self):
        ret = self.cursor.execute("SELECT * FROM entities WHERE name LIKE 'store_%'")
        return ret is not None
