from spg import BINARY_PATH, VAR_PATH

from base import Queue


from subprocess import Popen, PIPE
import sqlite3 as sql
import os

class TorqueQueue(Queue):
    queue_type = "torque" 

    def spawn_workers( self, new_jobs ):
        print "spawning workers: ", new_jobs
        for i in range(new_jobs):
            cmd = "qsub -q %s %s/spg-worker.py"%(self.name, BINARY_PATH, self.name)
            proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
#            self.workers.append(proc)
            proc.wait()

    def kill_workers( self, n_jobs = None):
        print "killing workers: ", n_jobs
        if not n_jobs: 
            for i in self.workers:
                cmd = "qdel %s"%(i)
                proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
                proc.wait()
        else:
            for i in self.workers[:n_jobs]:
                cmd = "qdel %s"%(i)
                proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
                proc.wait()
#            self.master_db.execute("DELETE FROM running WHERE job_id = ?" , i)

    def update_worker_info(self):  # These are the spg-worker instances in the queueing system
        proc = Popen("qstat", shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        output = proc.stdout
        proc.wait()
        # 9640.bruetli spg-worker.py tessonec 22:53:44 R default  
        self.workers = []
        for l in output:
            content = l.split()
            try:
                job_id = int( content[0].split(".")[0] )
#                status = content[4]
                if  self.name ==  content[5]:
                    self.workers.append( job_id ) 
            except: 
                continue

        print "number of workers: ", len(self.workers)



def get_queue_name():
    return os.environ("PBS_O_QUEUE")
    
