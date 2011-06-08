#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 16:20:26 2011

@author: -
"""

from subprocess import Popen, PIPE


  #print cmd
  
class ProcessPool:
    def __init__(self):
        self.running_default = []
        self.running_long = []
        self.running_short = []

        self.jobs_default = 20
        self.jobs_long = 5
        self.jobs_short = 2
        
        
    def update_process_list(self):
        cmd = "qstat"
        proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        output = proc.stdout
        proc.wait()

        ret_code = proc.returncode
        all_processes = []

        self.running_default = filter( lambda (job_id, status, queue): status == "R" and queue == "default", all_processes)
        self.running_long = filter( lambda (job_id, status, queue): status == "R" and queue == "long", all_processes)
        self.running_short = filter( lambda (job_id, status, queue): status == "R" and queue == "short", all_processes)


        for l in output:
            content = l.split()
            try:
                job_id = int( content[0].split(".")[0] )
                status = content[4]
                queue =  content[5]
            except: 
                continue
            all_processes.append( ( job_id, status, queue ) )
        self.running_default = filter( lambda (job_id, status, queue): status == "R" and queue == "default", all_processes)
        self.running_long = filter( lambda (job_id, status, queue): status == "R" and queue == "long", all_processes)
        self.running_short = filter( lambda (job_id, status, queue): status == "R" and queue == "short", all_processes)


if __name__ == "__main__":
    
     pp = ProcessPool()
     pp.update_process_list()
     
     print pp.running_default
     print pp.running_long
     print pp.running_short
     