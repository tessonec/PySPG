
from subprocess import Popen, PIPE
import sqlite3 as sql
from spg import BINARY_PATH


class Queue:
    queue_type = "base" 
    ENVIRONMENT = {}
      
    
    def __init__(self, name, max_workers, workers_sleep = 5):
        self.name = name
        self.max_workers = max_workers
        self.workers= []
        self.workers_sleep = workers_sleep 
        
#        self.ENVIRONMENT["SPG_HOME"]=SPG_HOME
        self.ENVIRONMENT["SPG_QUEUE_TYPE"]=self.queue_type
        self.ENVIRONMENT["SPG_QUEUE_NAME"]=self.name
        self.ENVIRONMENT["SPG_WORKERS_SLEEP"]=str(workers_sleep)


    def normalise_workers(self):
        """it returns the difference between processes after normalisation minus the previously existing jobs"""
        n_workers = len( self.workers)
#        print running_proc
        if n_workers > self.max_workers :
            self.kill_workers( n_workers - self.max_workers )

        elif n_workers < self.max_workers :
            self.spawn_workers( self.max_workers - n_workers  )
        return self.max_workers-n_workers 
        

    def spawn_workers( self, new_jobs ):
        """How many processes to populate"""
        for i in range(new_jobs):
            cmd = ["%s/spg-worker.py"%BINARY_PATH]
       #     print cmd
#            proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
#            proc = Popen(cmd,  shell = True,stdin = PIPE, stdout = PIPE, stderr = PIPE, env = self.ENVIRONMENT )
            proc = Popen(cmd,  shell = True, env = self.ENVIRONMENT )
            self.workers.append(proc)
#            proc.wait()


    def kill_workers(self, n_jobs = None):
        tbr = []
        if not n_jobs: 
            for proc in self.workers:
                proc.kill() 
                proc.wait()
                tbr.append(proc)
        else:
            for proc in self.workers[:n_jobs] :
                proc.kill() 
                proc.wait()
                tbr.append(proc)
        for proc in tbr:
            self.workers.remove(proc)

#            self.master_db.execute("DELETE FROM running WHERE job_id = ?" , i)

    def update_worker_info(self):  # These are the spg-worker instances in the queueing system
        tbr = [ p for p in self.workers if p.poll() is not None]
      #  print "Queue::update_worker_info", tbr
        for proc in tbr:
            self.workers.remove(proc)


