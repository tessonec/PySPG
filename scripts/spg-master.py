#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 16:20:26 2011

@author: -
"""

from subprocess import Popen, PIPE



import os, os.path

import sqlite3 as sql
  
 
import spg
import spg.params as params
import spg.utils as utils 
  
  
VAR_PATH = os.path.abspath(params.CONFIG_DIR+"/../var/spg")
BINARY_PATH = os.path.abspath(params.CONFIG_DIR+"/../bin")

class DBInfo:
   normalising = 0.
   def __init__(self, full_name = "", path= "", db_name= "", id=-1, weight=1.):
       self.full_name = full_name
       self.path = full_name
       self.db_name = db_name
       self.weight = weight
       DBInfo.id = id
       
       DBInfo.normalising += weight


class Queue:
    def __init__(self, name, max_jobs):
        self.name = name
        self.jobs = max_jobs
        self.processes = []
    
       



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
        self.update_process_list()

    def reload_master_info(self):
        
       self.conn_master = sql.connect("%s/running.sqlite"%VAR_PATH)
       self.cur_master  = self.conn_master.cursor()
       
       res = self.cur_master.execute("SELECT name, max_jobs FROM queues WHERE status = 'R'")

       for (name, max_jobs) in res:
           
           self.queues[name] = Queue(name, max_jobs)

       res = self.cur_master.execute("SELECT id, full_name, path, db_name, weight FROM dbs WHERE status = 'R'")

       for (id, full_name, path, db_name, weight) in res:
           self.dbs[full_name] = DBInfo(full_name, path, db_name,id, weight)


    def update_process_list(self):

        proc = Popen("qstat", shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE )
        output = proc.stdout
        proc.wait()

#        ret_code = proc.returncode

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



if __name__ == "__main__":
    
     pp = ProcessPool()
     pp.update_process_list()
     
     for i_j in pp.queues:
         print i_j, pp.queues[i_j].processes
     