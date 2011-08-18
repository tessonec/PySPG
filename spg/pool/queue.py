
from subprocess import Popen, PIPE
import sqlite3 as sql
from spg import BINARY_PATH, VAR_PATH


class Queue:
    def __init__(self, name, max_jobs):
        self.name = name
        self.jobs = max_jobs
        self.waiting_processes = 100
        self.processes = []
        self.last_finished_processes = 0


    def normalise_processes(self):
        running_proc = len( self.processes )
        if running_proc > self.jobs :
            self.kill_processes( running_proc - self.jobs )
        elif running_proc < self.jobs :
            self.populate_processes( self.jobs - running_proc  )

    def populate_processes( self, new_jobs ):
        """How many processes to populate"""
        for i in range(new_jobs):
            cmd = "qsub -q %s %s/spg-worker.py"%(self.name, BINARY_PATH)
            proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
            proc.wait()

    def kill_processes( self, n_jobs = None):
        if not n_jobs: 
            n_jobs = len(self.processes)
        for i in sorted(self.processes)[:n_jobs] :
            cmd = "qdel %s"%(i)
            proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
            proc.wait()
#            self.master_db.execute("DELETE FROM running WHERE job_id = ?" , i)

    def update_worker_info(self):  # These are the spg-worker instances in the queueing system
        proc = Popen("qstat", shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        output = proc.stdout
        proc.wait()
        # 9640.bruetli spg-worker.py tessonec 22:53:44 R default  
        self.processes = []
        for l in output:
            content = l.split()
            try:
                job_id = int( content[0].split(".")[0] )
#                status = content[4]
                if  self.name ==  content[5]:
                    self.processes.append( job_id ) 
            except: 
                continue



###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################


###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################




#
#class ProcessPool:
#    def __init__(self, queue_name =None):
#        self.queue = queue_name
#        self.update_time = 60 * 1
#
#
#        self.update_queue_info()
#
#    def update_queue_info(self): # These are the queues available to launch the processes in
#        self.queues = {}
#        res = self.connection.execute("SELECT name, max_jobs FROM queues WHERE status = 'R'")
#        for (name, max_jobs) in res:
#            self.queues[name] = Queue(name, max_jobs)
##           self.queues[name].set_db(self.db_master)


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
            


