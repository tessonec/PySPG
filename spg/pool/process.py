from spg import  params



import os.path
from subprocess import Popen, PIPE
import sqlite3 as sql

VAR_PATH = os.path.abspath(params.CONFIG_DIR+"/../var/spg")
BINARY_PATH = os.path.abspath(params.CONFIG_DIR+"/../bin")
TIMEOUT = 120

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
            cmd = "qdel %s"%(i)
            proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
            proc.wait()
#            self.master_db.execute("DELETE FROM running WHERE job_id = ?" , i)

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

        self.queues = {}
        self.db_master = sql.connect("%s/spg_pool.sqlite"%VAR_PATH)
        self.cur_master = self.db_master.cursor()

        self.update_queue_info()

    def update_queue_info(self): # These are the queues available to launch the processes in
        self.queues = {}
        res = self.cur_master.execute("SELECT name, max_jobs FROM queues WHERE status = 'R'")
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
            


