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

        self.running = {} 
        self.n_jobs = {"default":20, "short":3, "long":5}

        
        
    def update_process_list(self):
        cmd = "qstat"
        proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        output = proc.stdout
        proc.wait()

        ret_code = proc.returncode
        all_processes = []


        for i_q in self.running:
            self.running[i_q] = []
            
        for l in output:
            content = l.split()
            try:
                job_id = int( content[0].split(".")[0] )
                status = content[4]
                queue =  content[5]
                if status == "R":
                    self.running[queue].append( job_id ) 
            except: 
                continue



if __name__ == "__main__":
    
     pp = ProcessPool()
     pp.update_process_list()
     
     print pp.running
     