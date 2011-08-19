from subprocess import Popen, PIPE
import sqlite3 as sql
from spg import BINARY_PATH, VAR_PATH

from queue import Queue


class TorqueQueue(Queue):

    def populate_processes( self, new_jobs ):
        for i in range(new_jobs):
            cmd = "qsub -q %s %s/spg-worker.py --queue=%s"%(self.name, BINARY_PATH, self.name)
            proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
            self.processes.append(proc)
#            proc.wait()

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


